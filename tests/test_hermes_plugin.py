# SPDX-License-Identifier: MIT
# Copyright (c) 2026 contributors
from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import sys
import types
from unittest import mock

from tests.phase6_support import Phase6ScriptTestCase, ROOT


PLUGIN_SOURCE = ROOT / "enforcement" / "hermes-plugin" / "__init__.py"


class FixtureToolLoop:
    """Minimal Hermes-contract loop: a block directive becomes the tool result."""

    def __init__(self):
        self.hooks = {}
        self.executed = []

    def register_hook(self, name, callback):
        self.hooks[name] = callback

    def call(self, tool_name, args, session_id="fixture-session"):
        directive = self.hooks["pre_tool_call"](
            tool_name=tool_name,
            args=args,
            session_id=session_id,
            tool_call_id="fixture-call",
        )
        if (
            isinstance(directive, dict)
            and directive.get("action") == "block"
            and isinstance(directive.get("message"), str)
            and directive["message"]
        ):
            return {"executed": False, "result": directive["message"]}
        self.executed.append((tool_name, args))
        return {"executed": True, "result": "fixture tool executed"}


class HermesPluginTests(Phase6ScriptTestCase):
    def load_plugin(self):
        distribution = self.hermes_home / "distributions" / "evidence-first" / "enforcement"
        distribution.mkdir(parents=True)
        for name in ("guards.py", "completion.py", "policy.yaml"):
            shutil.copyfile(ROOT / "enforcement" / name, distribution / name)

        constants = types.ModuleType("hermes_constants")
        constants.get_hermes_home = lambda: self.hermes_home
        spec = importlib.util.spec_from_file_location("evidence_first_fixture_plugin", PLUGIN_SOURCE)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        with mock.patch.dict(
            sys.modules, {"hermes_constants": constants}
        ), mock.patch.dict(
            "os.environ", {"EVIDENCE_FIRST_VAULT": str(self.vault)}, clear=False
        ):
            spec.loader.exec_module(module)
        module.LOG_PATH = self.root / "fixture-enforcement-log.jsonl"
        return module

    def test_plugin_guard_fires_inside_fixture_tool_loop(self):
        plugin = self.load_plugin()
        loop = FixtureToolLoop()
        plugin.register(loop)

        protected = loop.call(
            "write_file",
            {"path": str(plugin.HERMES_HOME / "bin" / "forbidden")},
        )
        self.assertFalse(protected["executed"])
        self.assertIn("protected-path-write", protected["result"])

        allowed = loop.call(
            "write_file",
            {"path": str(self.vault / "Notes" / "allowed.md"), "content": "note"},
        )
        self.assertTrue(allowed["executed"])

        credential = loop.call(
            "send_message",
            {"content": "sk-" + "F" * 24},
        )
        self.assertFalse(credential["executed"])
        self.assertIn("credential-echo:openai-api-key", credential["result"])

        bare_parked = "Disposition: watch"
        transformed = loop.hooks["transform_llm_output"](
            response_text=bare_parked, session_id="fixture-session"
        )
        self.assertIsInstance(transformed, str)
        self.assertIn("parked-state surface missing", transformed)

    def test_install_uninstall_round_trip_covers_plugin_target_root(self):
        install = self.install()
        plugin = self.hermes_home / "plugins" / "evidence-first-enforcement"
        self.assertIn(
            "MANUAL PLUGIN ENABLE REQUIRED: hermes plugins enable evidence-first-enforcement",
            install.stdout,
        )
        self.assertIn("MANUAL GATEWAY RESTART REQUIRED", install.stdout)
        self.assertEqual(
            (plugin / "vault-path.txt").read_text(encoding="utf-8"),
            f"{self.vault.resolve()}\n",
        )
        self.assertTrue((plugin / "__init__.py").is_file())
        self.assertTrue((plugin / "plugin.yaml").is_file())
        plugin_entries = [
            item for item in self.manifest()["files"] if item["component"].startswith("hermes-plugin")
        ]
        self.assertEqual(len(plugin_entries), 3)

        verified = self.run_script(
            "verify-install.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        self.assertIn("PASS", verified.stdout)
        self.run_script(
            "uninstall.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        self.assertFalse(plugin.exists())

    def test_preexisting_plugin_receives_incoming_proposals(self):
        plugin = self.hermes_home / "plugins" / "evidence-first-enforcement"
        plugin.mkdir(parents=True)
        original = b"operator plugin\n"
        (plugin / "__init__.py").write_bytes(original)
        (plugin / "plugin.yaml").write_text("name: operator-plugin\n", encoding="utf-8")

        self.install()
        self.assertEqual((plugin / "__init__.py").read_bytes(), original)
        self.assertTrue((plugin / "__init__.py.incoming").is_file())
        self.assertTrue((plugin / "plugin.yaml.incoming").is_file())
        self.assertEqual(
            (plugin / "vault-path.txt").read_text(encoding="utf-8"),
            f"{self.vault.resolve()}\n",
        )

    def test_upgrade_preserves_modified_plugin_and_vault_state_with_incoming(self):
        self.install()
        plugin = self.hermes_home / "plugins" / "evidence-first-enforcement"
        module = plugin / "__init__.py"
        vault_state = plugin / "vault-path.txt"
        module_bytes = module.read_bytes() + b"\n# operator modification\n"
        module.write_bytes(module_bytes)
        vault_state.write_text("/operator/selected/vault\n", encoding="utf-8")

        result = self.run_script(
            "upgrade.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        self.assertIn(f"PRESERVED WITH INCOMING: {module.resolve()}", result.stdout)
        self.assertIn(f"PRESERVED WITH INCOMING: {vault_state.resolve()}", result.stdout)
        self.assertEqual(module.read_bytes(), module_bytes)
        self.assertEqual(
            module.with_name("__init__.py.incoming").read_bytes(),
            PLUGIN_SOURCE.read_bytes(),
        )
        self.assertEqual(vault_state.read_text(encoding="utf-8"), "/operator/selected/vault\n")
        self.assertEqual(
            vault_state.with_name("vault-path.txt.incoming").read_text(encoding="utf-8"),
            f"{self.vault.resolve()}\n",
        )


if __name__ == "__main__":
    import unittest

    unittest.main()
