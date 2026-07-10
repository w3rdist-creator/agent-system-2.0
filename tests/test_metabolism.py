from __future__ import annotations

import csv
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "metabolism.py"


def capture(body: str, *, route: str | None = None, note_date: str | None = None) -> str:
    fields = ["---", "type: capture"]
    if route is not None:
        fields.append(f"route: {route}")
    if note_date is not None:
        fields.append(f"date: {note_date}")
    fields.extend(["---", "", "# Capture", "", body, ""])
    return "\n".join(fields)


class MetabolismTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.vault = Path(self.temporary.name) / "vault"
        for folder in (
            "Inbox", "Sources", "Knowledge", "Raw", "Projects", "Decisions",
            "Experiments", "Reviews", "Reports", "Areas", "Clippings",
        ):
            (self.vault / folder).mkdir(parents=True, exist_ok=True)

    def write(self, relative: str, text: str) -> Path:
        path = self.vault / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def execute(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--vault", str(self.vault), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if check and result.returncode != 0:
            self.fail(f"metabolism failed ({result.returncode}):\n{result.stdout}\n{result.stderr}")
        return result

    def snapshot(self) -> dict[str, bytes]:
        return {
            path.relative_to(self.vault).as_posix(): path.read_bytes()
            for path in self.vault.rglob("*")
            if path.is_file()
        }

    def test_route_moves_note(self):
        source = self.write("Inbox/Routed.md", capture("Evidence.", route="Sources"))
        result = self.execute("--today", "2026-07-10")
        destination = self.vault / "Sources" / "Routed.md"
        self.assertFalse(source.exists())
        self.assertEqual(destination.read_text(encoding="utf-8"), capture("Evidence.", route="Sources"))
        self.assertIn("ROUTE:", result.stdout)

    def test_missing_and_invalid_routes_stay_and_are_reported(self):
        missing = self.write("Inbox/Missing.md", capture("Missing route."))
        invalid = self.write("Inbox/Invalid.md", capture("Invalid route.", route="Daily"))
        result = self.execute("--today", "2026-07-10")
        self.assertTrue(missing.exists())
        self.assertTrue(invalid.exists())
        self.assertEqual(result.stdout.count("SKIP:"), 2)
        self.assertIn("route='<missing>'", result.stdout)
        self.assertIn("route='Daily'", result.stdout)

    def test_destination_collision_uses_incoming_and_preserves_destination(self):
        existing = self.write("Sources/Collision.md", capture("Existing."))
        original = existing.read_bytes()
        incoming_text = capture("New routed content.", route="Sources")
        source = self.write("Inbox/Collision.md", incoming_text)
        self.execute("--today", "2026-07-10")
        self.assertEqual(existing.read_bytes(), original)
        self.assertFalse(source.exists())
        self.assertEqual(
            (self.vault / "Sources" / "Collision.md.incoming").read_text(encoding="utf-8"),
            incoming_text,
        )

    def test_exact_duplicate_moves_to_archive_with_content_preserved(self):
        first = self.write("Inbox/A.md", capture("Same body."))
        duplicate_text = capture("Same body.", route="Sources")
        duplicate = self.write("Inbox/B.md", duplicate_text)
        self.execute("--today", "2026-07-10")
        archived = self.vault / "Archive" / "Duplicates" / "B.duplicate-2026-07-10.md"
        self.assertTrue(first.exists())
        self.assertFalse(duplicate.exists())
        self.assertEqual(archived.read_text(encoding="utf-8"), duplicate_text)

    def test_note_identical_to_route_destination_is_archived(self):
        destination_text = capture("Same body.")
        self.write("Sources/Same.md", destination_text)
        source_text = capture("Same body.", route="Sources")
        self.write("Inbox/Same.md", source_text)
        self.execute("--today", "2026-07-10")
        self.assertEqual((self.vault / "Sources" / "Same.md").read_text(encoding="utf-8"), destination_text)
        archived = self.vault / "Archive" / "Duplicates" / "Same.duplicate-2026-07-10.md"
        self.assertEqual(archived.read_text(encoding="utf-8"), source_text)
        self.assertFalse((self.vault / "Sources" / "Same.md.incoming").exists())

    def test_decay_queues_once_and_today_is_deterministic(self):
        note = self.write("Inbox/Old.md", capture("Old.", note_date="2026-06-25"))
        first = self.execute("--today", "2026-07-10", "--max-age-days", "14")
        queue = self.vault / "Queues" / "Resolve Queue.md"
        first_text = queue.read_text(encoding="utf-8")
        self.assertTrue(note.exists())
        self.assertIn("DECAY:", first.stdout)
        self.assertEqual(first_text.count("**ID:** METABOLISM-"), 1)
        second = self.execute("--today", "2026-07-10", "--max-age-days", "14")
        self.assertEqual(queue.read_text(encoding="utf-8"), first_text)
        self.assertIn("keep existing Resolve Queue entry", second.stdout)

    def test_decay_falls_back_to_mtime(self):
        note = self.write("Inbox/Mtime.md", capture("Old by mtime."))
        timestamp = datetime(2026, 6, 1, 12, 0).timestamp()
        os.utime(note, (timestamp, timestamp))
        self.execute("--today", "2026-07-10", "--max-age-days", "14")
        self.assertIn("Inbox/Mtime.md", (self.vault / "Queues" / "Resolve Queue.md").read_text(encoding="utf-8"))

    def test_queue_over_cap_exits_one_and_names_counts(self):
        self.write("Inbox/One.md", capture("One."))
        result = self.execute("--today", "2026-07-10", "--queue-cap", "0", check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("SCREAM: Inbox count 1 (cap 0)", result.stderr)
        self.assertIn("Resolve Queue entry count 0 (cap 0)", result.stderr)

    def test_dry_run_writes_nothing_and_prints_plan(self):
        self.write("Inbox/Routed.md", capture("Route me.", route="Sources"))
        self.write("Inbox/Old.md", capture("Old.", note_date="2026-01-01"))
        before = self.snapshot()
        result = self.execute("--dry-run", "--today", "2026-07-10")
        self.assertEqual(self.snapshot(), before)
        self.assertIn("PLAN ROUTE:", result.stdout)
        self.assertIn("PLAN DECAY:", result.stdout)
        self.assertIn("PLAN LEDGER:", result.stdout)

    def test_ledger_row_has_correct_counts(self):
        self.write("Inbox/Route.md", capture("Route.", route="Sources"))
        self.write("Inbox/A-Keep.md", capture("Keep."))
        self.write("Inbox/Z-Dupe.md", capture("Keep.", route="Knowledge"))
        self.write("Inbox/Old.md", capture("Old.", note_date="2026-01-01"))
        self.execute("--today", "2026-07-10")
        ledger = self.vault / "Ledgers" / "Metabolism Ledger.csv"
        with ledger.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(
            rows,
            [{
                "date": "2026-07-10", "routed": "1", "deduped": "1",
                "decayed": "1", "skipped": "2", "screams": "0",
            }],
        )

    def test_no_data_says_so_and_writes_nothing(self):
        before = self.snapshot()
        result = self.execute("--today", "2026-07-10")
        self.assertEqual(self.snapshot(), before)
        self.assertIn("NO DATA", result.stdout)


if __name__ == "__main__":
    unittest.main()
