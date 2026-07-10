from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "telemetry.py"
TODAY = "2026-07-10"


class TelemetryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.vault = root / "vault"
        self.transcripts = root / "transcripts"
        self.transcripts.mkdir()

    @property
    def ledger(self) -> Path:
        return self.vault / "Ledgers" / "Telemetry Ledger.csv"

    def execute(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--vault",
                str(self.vault),
                "--today",
                TODAY,
                *args,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if check and result.returncode != 0:
            self.fail(f"telemetry failed ({result.returncode}):\n{result.stdout}\n{result.stderr}")
        return result

    def write_transcript(self, name: str, events: list[dict[str, object]]) -> Path:
        path = self.transcripts / name
        path.write_text(json.dumps({"events": events}), encoding="utf-8")
        return path

    def rows(self) -> list[dict[str, str]]:
        with self.ledger.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def metrics(self) -> dict[str, str]:
        return {row["metric"]: row["value"] for row in self.rows()}

    def test_extracts_dispositions_tools_fixture_reads_and_guard_rules(self):
        self.write_transcript(
            "trial.json",
            [
                {"type": "tool_call", "tool": "read_file", "args": {"path": "fixture/live.json"}},
                {"type": "tool_call", "tool": "search", "args": {"pattern": "truth"}},
                {"type": "guard_denied", "tool": "write_file", "rule": "protected-path-write"},
                {"type": "answer", "content": "done"},
                {"type": "tool_call", "tool": "read_file", "args": {"path": "fixture/late.json"}},
                {"type": "disposition", "label": "done"},
            ],
        )
        result = self.execute("--transcript-dir", str(self.transcripts))
        self.assertIn("rows written=5", result.stdout)
        self.assertEqual(
            self.metrics(),
            {
                "disposition.done": "1",
                "fixture_reads_before_first_answer": "1",
                "guard_denied.protected-path-write": "1",
                "tool.read_file": "2",
                "tool.search": "1",
            },
        )

    def test_no_sources_writes_nothing_and_exits_zero(self):
        result = self.execute()
        self.assertEqual(result.returncode, 0)
        self.assertFalse(self.vault.exists())
        self.assertIn("no evidence found", result.stdout)
        self.assertIn("rows written=0", result.stdout)

    def test_same_day_rerun_skips_existing_keys(self):
        self.write_transcript("trial.json", [{"type": "disposition", "label": "done"}])
        first = self.execute("--transcript-dir", str(self.transcripts))
        original = self.ledger.read_bytes()
        second = self.execute("--transcript-dir", str(self.transcripts))
        self.assertEqual(self.ledger.read_bytes(), original)
        self.assertIn("rows written=2", first.stdout)
        self.assertIn("rows written=0", second.stdout)
        self.assertIn("existing keys skipped=2", second.stdout)

    def test_malformed_transcript_warns_and_does_not_crash(self):
        (self.transcripts / "bad.json").write_text("not json", encoding="utf-8")
        self.write_transcript("good.json", [{"type": "disposition", "label": "watch"}])
        result = self.execute("--transcript-dir", str(self.transcripts))
        self.assertEqual(result.returncode, 0)
        self.assertIn("warnings=1", result.stdout)
        self.assertIn("WARNING: skipped malformed transcript", result.stderr)
        self.assertEqual(self.metrics()["disposition.watch"], "1")

    def test_only_malformed_transcript_writes_nothing(self):
        (self.transcripts / "bad.json").write_text("{}", encoding="utf-8")
        result = self.execute("--transcript-dir", str(self.transcripts))
        self.assertEqual(result.returncode, 0)
        self.assertFalse(self.vault.exists())
        self.assertIn("no evidence found", result.stdout)
        self.assertIn("warnings=1", result.stdout)

    def test_dry_run_writes_nothing(self):
        self.write_transcript("trial.json", [{"type": "disposition", "label": "done"}])
        result = self.execute("--transcript-dir", str(self.transcripts), "--dry-run")
        self.assertFalse(self.vault.exists())
        self.assertIn("DRY RUN: rows planned=2", result.stdout)
        self.assertIn("rows written=0", result.stdout)

    def test_rolls_up_recert_results_and_metabolism_screams(self):
        recert = Path(self.temporary.name) / "recert.csv"
        recert.write_text(
            "date,scenario,model,reasoning,arm,result,failure_reason\n"
            "2026-07-10,01,m,r,treatment,pass,\n"
            "2026-07-10,02,m,r,treatment,fail,no answer\n"
            "2026-07-10,03,m,r,treatment,pass,\n",
            encoding="utf-8",
        )
        metabolism = Path(self.temporary.name) / "metabolism.csv"
        metabolism.write_text(
            "date,routed,deduped,decayed,skipped,screams\n"
            "2026-07-09,1,0,0,0,0\n"
            "2026-07-10,0,0,1,1,2\n",
            encoding="utf-8",
        )
        self.execute(
            "--recert-log", str(recert), "--metabolism-ledger", str(metabolism)
        )
        self.assertEqual(
            self.metrics(), {"result.fail": "1", "result.pass": "2", "screams": "2"}
        )


if __name__ == "__main__":
    unittest.main()
