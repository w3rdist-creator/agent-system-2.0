from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class UpdateGateTests(unittest.TestCase):
    def test_repository_snapshot_passes_with_synthetic_base(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            env = os.environ.copy()
            env.update(
                {
                    "GIT_AUTHOR_NAME": "Evidence First Test",
                    "GIT_AUTHOR_EMAIL": "contributors",
                    "GIT_COMMITTER_NAME": "Evidence First Test",
                    "GIT_COMMITTER_EMAIL": "contributors",
                }
            )

            self.run_git(repo, env, "init", "-q", "-b", "main")
            self.run_git(repo, env, "commit", "-q", "--allow-empty", "-m", "synthetic public base")
            self.run_git(repo, env, "tag", "phase-h-test-base")

            for source in ROOT.iterdir():
                if source.name in {".git", "_build", "__pycache__"}:
                    continue
                destination = repo / source.name
                if source.is_dir():
                    shutil.copytree(
                        source,
                        destination,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                    )
                else:
                    shutil.copy2(source, destination)

            self.run_git(repo, env, "add", "-A")
            self.run_git(repo, env, "commit", "-q", "-m", "release snapshot")
            completed = subprocess.run(
                [
                    "sh",
                    "scripts/update-gate.sh",
                    "--base",
                    "phase-h-test-base",
                    "--version",
                    "1.1.0",
                    "--skip-dev-gate",
                ],
                cwd=repo,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(
                completed.returncode,
                0,
                f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )
            self.assertIn("TEST ONLY: skipped recursive development gate", completed.stdout)
            self.assertIn("PASS: update gate verified", completed.stdout)

    @staticmethod
    def run_git(repo: Path, env: dict[str, str], *arguments: str) -> None:
        subprocess.run(
            ["git", *arguments],
            cwd=repo,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
