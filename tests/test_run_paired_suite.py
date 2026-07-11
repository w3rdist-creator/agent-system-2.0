from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import scripts.run_paired_suite as run_paired_suite


STUB_ADAPTER = """#!/usr/bin/env python3
import json
from pathlib import Path
import sys

request = json.load(sys.stdin)
log = Path(__file__).with_name("attempts.jsonl")
with log.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps({key: request[key] for key in ("scenario_id", "arm", "trial")}) + "\\n")
if request["arm"] == "control" and request["trial"] == 2:
    print("intentional crash", file=sys.stderr)
    raise SystemExit(7)
json.dump({"events": [{"type": "answer", "content": "stub"}]}, sys.stdout)
"""


class PairedSuiteDriverTests(unittest.TestCase):
    def test_stub_adapter_resume_trial_coverage_worker_cap_and_crash_isolation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scenario = root / "evaluations" / "scenarios" / "01-stub"
            (scenario / "fixture").mkdir(parents=True)
            (scenario / "task.md").write_text("Do the task.\n", encoding="utf-8")
            (scenario / "scenario.yaml").write_text(
                json.dumps({"Treatment loading": [], "Control loading": []}),
                encoding="utf-8",
            )
            adapter = root / "stub_adapter.py"
            adapter.write_text(STUB_ADAPTER, encoding="utf-8")
            transcripts = root / "transcripts"
            transcripts.mkdir()
            cached = transcripts / "01-stub--treatment--t1.json"
            cached.write_text('{"events": []}\n', encoding="utf-8")

            stdout = io.StringIO()
            with mock.patch.object(run_paired_suite, "ROOT", root), contextlib.redirect_stdout(stdout):
                result = run_paired_suite.main(
                    [
                        "--model",
                        "stub-model",
                        "--reasoning",
                        "test",
                        "--trials",
                        "3",
                        "--transcript-dir",
                        str(transcripts),
                        "--workers",
                        "1",
                        "--adapter",
                        str(adapter),
                    ]
                )

            self.assertEqual(result, 1)
            attempts = [
                json.loads(line)
                for line in (root / "attempts.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(len(attempts), 5)
            self.assertNotIn(
                {"scenario_id": "01-stub", "arm": "treatment", "trial": 1}, attempts
            )
            self.assertIn(
                {"scenario_id": "01-stub", "arm": "control", "trial": 3}, attempts
            )
            self.assertIn("6 trials, 1 workers", stdout.getvalue())
            self.assertIn("COMPLETE errors=1", stdout.getvalue())
            self.assertIn("scripts/eval_adapter_replay.py", stdout.getvalue())
            self.assertEqual(
                {
                    path.name
                    for path in transcripts.glob("01-stub--*--t*.json")
                    if "--error-" not in path.name
                },
                {
                    "01-stub--treatment--t1.json",
                    "01-stub--treatment--t2.json",
                    "01-stub--treatment--t3.json",
                    "01-stub--control--t1.json",
                    "01-stub--control--t3.json",
                },
            )
            errors = list(transcripts.glob("01-stub--control--t2--error-*.json"))
            self.assertEqual(len(errors), 1)
            self.assertIn("adapter exit 7", errors[0].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
