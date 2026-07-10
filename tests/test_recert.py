from __future__ import annotations

import csv
from datetime import date
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
RECERT = ROOT / "scripts" / "recert.sh"
RECERT_HELPER = ROOT / "scripts" / "recert.py"
HARNESS = ROOT / "scripts" / "evaluate_scenarios.py"


STUB_RUNNER = r"""
import json
import os
import sys

request = json.load(sys.stdin)
mode = os.environ.get("STUB_MODE", "fail")
if mode == "crash":
    print("stub runner exploded", file=sys.stderr)
    raise SystemExit(7)
if mode == "pass":
    events = [
        {"type": "tool_call", "tool": "read_file", "args": {"path": "fixture/live-status.json"}},
        {"type": "tool_call", "tool": "read_file", "args": {"path": "fixture/operations-policy.md"}},
        {"type": "answer", "content": "operator decision required"},
        {"type": "disposition", "label": "needs-human"},
    ]
else:
    events = []
json.dump({"events": events}, sys.stdout)
"""


class RecertTests(unittest.TestCase):
    def test_shell_entrypoint_and_helper_ship_together(self):
        self.assertTrue(RECERT.is_file())
        self.assertTrue(RECERT_HELPER.is_file())

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        temporary = Path(self.temporary.name)
        self.log = temporary / "recert-log.csv"
        self.runner = temporary / "stub_runner.py"
        self.runner.write_text(textwrap.dedent(STUB_RUNNER), encoding="utf-8")
        self.base_env = {
            **os.environ,
            "EVAL_MODEL": "stub-model",
            "EVAL_REASONING": "medium",
            "EVAL_RUNNER_COMMAND": f"{sys.executable} {self.runner}",
            "RECERT_LOG": str(self.log),
        }

    def tearDown(self):
        self.temporary.cleanup()

    def run_recert(self, *arguments: str, mode: str = "fail") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["sh", str(RECERT), *arguments],
            cwd=ROOT,
            env={**self.base_env, "STUB_MODE": mode},
            text=True,
            capture_output=True,
        )

    def rows(self) -> list[dict[str, str]]:
        with self.log.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def test_appends_correct_pass_and_fail_rows(self):
        passed = self.run_recert("--scenario", "01-stale-context-live-source", mode="pass")
        self.assertEqual(passed.returncode, 0, passed.stderr)
        self.assertIn("RECERT: 1/1 passed (stub-model,", passed.stdout)

        failed = self.run_recert("--scenario", "01-stale-context-live-source", mode="fail")
        self.assertEqual(failed.returncode, 1)
        rows = self.rows()
        self.assertEqual([row["result"] for row in rows], ["pass", "fail"])
        self.assertEqual(rows[0]["date"], date.today().isoformat())
        self.assertEqual(rows[0]["scenario"], "01-stale-context-live-source")
        self.assertEqual(rows[0]["model"], "stub-model")
        self.assertEqual(rows[0]["reasoning"], "medium")
        self.assertEqual(rows[0]["arm"], "treatment")
        self.assertEqual(rows[0]["failure_reason"], "")
        self.assertIn("answer event not found", rows[1]["failure_reason"])

    def test_runner_crash_records_error_and_exits_nonzero(self):
        completed = self.run_recert(
            "--scenario", "01-stale-context-live-source", mode="crash"
        )
        self.assertEqual(completed.returncode, 1)
        row = self.rows()[0]
        self.assertEqual(row["result"], "error")
        self.assertIn("stub runner exploded", row["failure_reason"])
        self.assertIn("RECERT: 0/1 passed", completed.stdout)

    def test_day_of_year_rotation_is_deterministic(self):
        first = self.run_recert()
        second = self.run_recert()
        self.assertEqual(first.returncode, 1)
        self.assertEqual(second.returncode, 1)
        expected = sorted(path.name for path in (ROOT / "evaluations" / "scenarios").iterdir())[
            (date.today().timetuple().tm_yday - 1) % 16
        ]
        self.assertEqual([row["scenario"] for row in self.rows()], [expected, expected])

    def test_scenario_override_is_respected(self):
        completed = self.run_recert("--scenario", "16-optional-provider-missing")
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(self.rows()[0]["scenario"], "16-optional-provider-missing")

    def test_schema_only_harness_stays_green(self):
        completed = subprocess.run(
            [sys.executable, str(HARNESS), "evaluations", "--schema-only"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("PASS: 16 scenarios satisfy the schema", completed.stdout)


if __name__ == "__main__":
    unittest.main()
