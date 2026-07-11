from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from enforcement.completion import evaluate_completion
from enforcement.guards import load_policy
from scripts import eval_adapter_codex, eval_adapter_replay
from scripts.evaluation_lib import DISPOSITIONS, LEGACY_DISPOSITION_ALIASES, normalize_transcript


ROOT = Path(__file__).resolve().parents[1]
POLICY = load_policy(ROOT / "enforcement" / "policy.yaml")


class CompletionGateTests(unittest.TestCase):
    def check(self, disposition, content):
        return evaluate_completion(
            {"disposition": disposition, "content": content}, POLICY
        )

    def cli(self, envelope: str):
        return subprocess.run(
            [sys.executable, str(ROOT / "enforcement" / "completion_gate.py")],
            input=envelope,
            text=True,
            capture_output=True,
            cwd=ROOT,
        )

    def test_policy_vocabulary_mirrors_evaluation_library(self):
        completion = POLICY["completion"]
        self.assertEqual(set(completion["dispositions"]), set(DISPOSITIONS))
        self.assertEqual(completion["legacy_aliases"], LEGACY_DISPOSITION_ALIASES)
        self.assertEqual(completion["canonical_source"], "scripts/evaluation_lib.py")

    def test_parked_patterns_mirror_scenarios_09_and_14(self):
        expected_patterns = []
        for number in ("09", "14"):
            path = next((ROOT / "evaluations" / "expected").glob(f"{number}-*.json"))
            spec = json.loads(path.read_text(encoding="utf-8"))
            patterns = [
                event["content"]["$regex"]
                for event in spec["required_events"]
                if event.get("type") == "answer"
                and isinstance(event.get("content"), dict)
                and event["content"].get("$regex")
                in {"state.change|trigger", "decay|review date"}
            ]
            expected_patterns.append({f"(?i){pattern}" for pattern in patterns})
        policy_patterns = set(POLICY["completion"]["parked_state_patterns"].values())
        self.assertEqual(expected_patterns, [policy_patterns, policy_patterns])

    def test_watch_requires_both_parked_state_fields(self):
        for content in (
            "Review date: 2026-08-01.",
            "Trigger: the upstream state changes.",
            "No parked metadata.",
        ):
            with self.subTest(content=content):
                self.assertEqual(self.check("watch", content)["rule"], "parked-state-surface")
        allowed = self.check(
            "watch", "Trigger: upstream changes. Review date: 2026-08-01."
        )
        self.assertEqual(allowed["decision"], "allow")

    def test_no_action_and_defer_receive_the_same_check(self):
        self.assertEqual(
            self.check("no-action", "Review date: tomorrow.")["rule"],
            "parked-state-surface",
        )
        for disposition in ("no-action", "defer"):
            with self.subTest(disposition=disposition):
                result = self.check(
                    disposition, "State-change trigger: new evidence. Decay: 2026-08-01."
                )
                self.assertEqual(result["decision"], "allow")

    def test_non_parked_dispositions_are_unaffected(self):
        for disposition in ("done", "act", "blocked", "kill", "needs-human", "merge"):
            with self.subTest(disposition=disposition):
                self.assertEqual(self.check(disposition, "brief")["decision"], "allow")

    def test_unknown_and_malformed_envelopes_fail_closed(self):
        self.assertEqual(self.check("invented", "text")["rule"], "malformed-input")
        for envelope in (
            {},
            {"disposition": "done"},
            {"disposition": "done", "content": 1},
            {"disposition": "done", "content": "ok", "extra": True},
        ):
            with self.subTest(envelope=envelope):
                result = evaluate_completion(envelope, POLICY)
                self.assertEqual(result["rule"], "malformed-input")

    def test_cli_exit_codes_and_malformed_stdin(self):
        allowed = self.cli(json.dumps({"disposition": "done", "content": "complete"}))
        denied = self.cli(json.dumps({"disposition": "watch", "content": "parked"}))
        malformed = self.cli("not-json")
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertEqual(denied.returncode, 2, denied.stderr)
        self.assertEqual(malformed.returncode, 3, malformed.stderr)
        self.assertEqual(json.loads(malformed.stdout)["rule"], "malformed-input")

    def test_completion_denied_event_is_schema_compatible(self):
        events = normalize_transcript(
            {"events": [{"type": "completion_denied", "rule": "parked-state-surface"}]}
        )
        self.assertEqual(events[0]["type"], "completion_denied")

    def test_codex_adapter_appends_denial_after_disposition(self):
        reply = json.dumps(
            {"tool": None, "args": None, "answer": "parked", "disposition": "watch"}
        )
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            eval_adapter_codex, "ENFORCE", True
        ), mock.patch.object(eval_adapter_codex, "GUARD_POLICY", POLICY), mock.patch.object(
            eval_adapter_codex, "call_codex", return_value=reply
        ):
            events = eval_adapter_codex.run_trial("", "", "task", Path(tmp), "test")
        self.assertEqual(
            events,
            [
                {"type": "answer", "content": "parked"},
                {"type": "disposition", "label": "watch"},
                {"type": "completion_denied", "rule": "parked-state-surface"},
            ],
        )

    def test_replay_adapter_appends_denial_after_disposition(self):
        events = eval_adapter_replay.enforce_events(
            [
                {"type": "answer", "content": "parked"},
                {"type": "disposition", "label": "no-action"},
            ],
            {"fixture_dir": str(ROOT)},
        )
        self.assertEqual(events[-1]["type"], "completion_denied")
        self.assertEqual(events[-2]["type"], "disposition")


if __name__ == "__main__":
    unittest.main()
