from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
from unittest import mock

from enforcement.guards import evaluate, load_policy
from scripts.evaluation_lib import normalize_transcript
from scripts import eval_adapter_codex, eval_adapter_replay
from tests.phase6_support import Phase6ScriptTestCase


ROOT = Path(__file__).resolve().parents[1]
POLICY = load_policy(ROOT / "enforcement" / "policy.yaml")


class EnforcementTests(Phase6ScriptTestCase):
    def context(self, declared_cap=None):
        return {
            "hermes_home": str(self.hermes_home),
            "vault": str(self.vault),
            "declared_cap": declared_cap,
        }

    def check(self, tool, args, declared_cap=None):
        return evaluate({"tool": tool, "args": args}, POLICY, self.context(declared_cap))

    def cli(self, envelope: str, *extra: str):
        return subprocess.run(
            [
                "python3",
                str(ROOT / "enforcement" / "pre_tool_use.py"),
                "--hermes-home",
                str(self.hermes_home),
                "--vault",
                str(self.vault),
                *extra,
            ],
            input=envelope,
            text=True,
            capture_output=True,
            cwd=ROOT,
        )

    def test_config_write_is_denied_directly_and_through_traversal(self):
        direct = self.check("write_file", {"path": str(self.hermes_home / "config.yaml")})
        traversed = self.check(
            "edit_file", {"path": str(self.hermes_home / "scratch" / ".." / "config.yaml")}
        )
        self.assertEqual(direct["rule"], "protected-path-write")
        self.assertEqual(traversed["rule"], "protected-path-write")

    def test_namespaced_tool_and_path_style_argument_are_protected(self):
        result = self.check(
            "filesystem.write_file",
            {"destinationPath": str(self.hermes_home / "bin" / "helper")},
        )
        self.assertEqual(result["rule"], "protected-path-write")

    def test_vault_content_write_is_allowed_but_manifest_write_is_denied(self):
        content = self.check("append_file", {"path": str(self.vault / "Notes" / "mine.md")})
        manifest = self.check(
            "copy_file", {"destination": str(self.vault / ".evidence-first" / "record.json")}
        )
        self.assertEqual(content["decision"], "allow")
        self.assertEqual(manifest["rule"], "protected-path-write")

    def test_read_class_tool_is_not_path_blocked(self):
        result = self.check("read_file", {"path": str(self.hermes_home / "config.yaml")})
        self.assertEqual(result["decision"], "allow")

    def test_credentials_are_denied_for_write_and_send_without_echo(self):
        fake_key = "sk-" + "F" * 24
        for tool, args in (
            ("write_file", {"path": "notes.md", "content": fake_key}),
            ("send_message", {"recipient": "operator", "content": fake_key}),
        ):
            with self.subTest(tool=tool):
                result = self.check(tool, args)
                self.assertEqual(result["decision"], "deny")
                self.assertTrue(str(result["rule"]).startswith("credential-echo:"))
                self.assertNotIn(fake_key, result["reason"])
                self.assertNotIn(fake_key, json.dumps(result))

    def test_assignment_free_password_mention_is_allowed(self):
        result = self.check("send_message", {"content": "Never share your password with anyone."})
        self.assertEqual(result["decision"], "allow")

    def test_structured_secret_assignment_is_denied(self):
        result = self.check("send_message", {"password": "fixture-value-123"})
        self.assertEqual(result["decision"], "deny")
        self.assertEqual(result["rule"], "credential-echo:assigned-secret")

    def test_retrieval_cap_and_declared_override(self):
        self.assertEqual(self.check("search", {"limit": 26})["rule"], "retrieval-cap")
        self.assertEqual(self.check("search", {"limit": 25})["decision"], "allow")
        self.assertEqual(self.check("search", {"top_k": 40}, declared_cap=40)["decision"], "allow")

    def test_cli_exit_codes_and_malformed_stdin(self):
        allowed = self.cli(json.dumps({"tool": "search", "args": {"limit": 25}}))
        denied = self.cli(json.dumps({"tool": "search", "args": {"max_results": 26}}))
        malformed = self.cli("not-json")
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertEqual(denied.returncode, 2, denied.stderr)
        self.assertEqual(malformed.returncode, 3, malformed.stderr)
        self.assertEqual(json.loads(malformed.stdout)["rule"], "malformed-input")

    def test_installed_clis_disable_bytecode_before_sibling_imports(self):
        for name in ("pre_tool_use.py", "completion_gate.py"):
            with self.subTest(name=name):
                tree = ast.parse((ROOT / "enforcement" / name).read_text(encoding="utf-8"))
                assignments = [
                    node
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Assign)
                    and any(
                        isinstance(target, ast.Attribute)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == "sys"
                        and target.attr == "dont_write_bytecode"
                        for target in node.targets
                    )
                    and isinstance(node.value, ast.Constant)
                    and node.value.value is True
                ]
                sibling_imports = [
                    node
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom)
                    and node.module in {"completion", "guards"}
                ]
                self.assertEqual(len(assignments), 1)
                self.assertTrue(sibling_imports)
                self.assertLess(assignments[0].lineno, min(node.lineno for node in sibling_imports))

    def test_guard_denied_event_is_schema_compatible(self):
        events = normalize_transcript(
            {"events": [{"type": "guard_denied", "tool": "write_file", "rule": "protected-path-write"}]}
        )
        self.assertEqual(events[0]["type"], "guard_denied")

    def test_codex_adapter_returns_guard_error_before_execution(self):
        replies = iter(
            [
                json.dumps(
                    {
                        "tool": "write_file",
                        "args": {"path": ".evidence-first/install-manifest.json", "content": "changed"},
                        "answer": None,
                        "disposition": None,
                    }
                ),
                json.dumps(
                    {"tool": None, "args": None, "answer": "blocked", "disposition": "blocked"}
                ),
            ]
        )
        prompts = []

        def reply(prompt, _workdir):
            prompts.append(prompt)
            return next(replies)

        with mock.patch.object(eval_adapter_codex, "ENFORCE", True), mock.patch.object(
            eval_adapter_codex, "GUARD_POLICY", POLICY
        ), mock.patch.object(eval_adapter_codex, "call_codex", side_effect=reply):
            events = eval_adapter_codex.run_trial("", "", "task", self.vault, "test")
        self.assertEqual(events[0]["type"], "guard_denied")
        self.assertEqual(events[0]["rule"], "protected-path-write")
        self.assertIn("denied by pre-tool-use guard: protected-path-write", prompts[1])
        self.assertFalse((self.vault / ".evidence-first" / "install-manifest.json").exists())

    def test_replay_adapter_replaces_denied_call_with_guard_event(self):
        events = eval_adapter_replay.enforce_events(
            [
                {
                    "type": "tool_call",
                    "tool": "delete_file",
                    "args": {"path": str(self.vault / ".evidence-first" / "record.json")},
                },
                {"type": "answer", "content": "done"},
            ],
            {"fixture_dir": str(self.vault)},
        )
        self.assertEqual(
            events[0],
            {"type": "guard_denied", "tool": "delete_file", "rule": "protected-path-write"},
        )
        self.assertEqual(events[1]["type"], "answer")

    def test_install_and_uninstall_round_trip_tracks_enforcement(self):
        install = self.install()
        self.assertIn("ENFORCEMENT: Hermes plugin payload will be installed", install.stdout)
        self.assertIn("MANUAL PLUGIN ENABLE REQUIRED", install.stdout)
        installed = self.hermes_home / "distributions" / "evidence-first" / "enforcement"
        for name in ("policy.yaml", "completion.py", "completion_gate.py"):
            with self.subTest(name=name):
                self.assertTrue((installed / name).is_file())
        entries = [item for item in self.manifest()["files"] if "/enforcement/" in item["path"]]
        installed_names = {Path(item["path"]).name for item in entries}
        self.assertTrue({"policy.yaml", "completion.py", "completion_gate.py"} <= installed_names)
        completion = subprocess.run(
            ["python3", str(installed / "completion_gate.py")],
            input=json.dumps(
                {
                    "disposition": "watch",
                    "content": "Trigger: evidence changes. Review date: 2026-08-01.",
                }
            ),
            text=True,
            capture_output=True,
            cwd=ROOT,
        )
        self.assertEqual(completion.returncode, 0, completion.stderr)
        bytecode = installed / "__pycache__" / "completion.cpython-39.pyc"
        bytecode.parent.mkdir()
        bytecode.write_bytes(b"dummy bytecode")
        result = self.run_script(
            "uninstall.sh", "--vault", self.vault, "--hermes-home", self.hermes_home
        )
        self.assertFalse(installed.exists())
        self.assertNotIn(str(bytecode), result.stdout)

    def test_uninstall_preserves_modified_enforcement_file(self):
        self.install()
        target = self.hermes_home / "distributions" / "evidence-first" / "enforcement" / "policy.yaml"
        target.write_text(target.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        result = self.run_script(
            "uninstall.sh", "--vault", self.vault, "--hermes-home", self.hermes_home
        )
        self.assertTrue(target.is_file())
        self.assertIn(f"modified distribution-owned file preserved: {target.resolve()}", result.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()
