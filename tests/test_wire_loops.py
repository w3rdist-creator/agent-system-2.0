from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "wire-loops.sh"


def tree_snapshot(root: Path) -> dict[str, tuple[str, str]]:
    snapshot: dict[str, tuple[str, str]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            snapshot[relative] = ("dir", "")
        elif path.is_file():
            snapshot[relative] = (
                "file",
                hashlib.sha256(path.read_bytes()).hexdigest(),
            )
    return snapshot


class WireLoopsTests(unittest.TestCase):
    def test_prints_three_absolute_loops_and_changes_nothing(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = Path(temporary)
            vault = fixture / "vault"
            clone = fixture / "clone"
            hermes_home = fixture / "hermes-home"
            for path in (vault, clone, hermes_home):
                path.mkdir()
            (vault / "keep.md").write_text("operator content\n", encoding="utf-8")
            before = tree_snapshot(fixture)

            completed = subprocess.run(
                [
                    "sh",
                    str(SCRIPT),
                    "--vault",
                    str(vault),
                    "--clone",
                    str(clone),
                    "--hermes-home",
                    str(hermes_home),
                ],
                cwd=fixture,
                text=True,
                capture_output=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            output = completed.stdout
            self.assertIn(str(clone.resolve() / "scripts" / "metabolism.py"), output)
            self.assertIn(str(clone.resolve() / "scripts" / "recert.sh"), output)
            self.assertIn(str(clone.resolve() / "scripts" / "telemetry.py"), output)
            self.assertIn(str(vault.resolve()), output)
            self.assertIn(str(hermes_home.resolve()), output)
            self.assertIn("EVAL_TRANSCRIPT_DIR", output)
            self.assertIn("5 3 * * *", output)
            self.assertIn("25 3 * * *", output)
            self.assertIn("50 3 * * *", output)
            self.assertIn("this tool prints; you paste", output)
            self.assertEqual(tree_snapshot(fixture), before)

    def test_invalid_arguments_fail(self):
        completed = subprocess.run(
            ["sh", str(SCRIPT), "--unknown"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("ERROR: unknown argument", completed.stderr)


if __name__ == "__main__":
    unittest.main()
