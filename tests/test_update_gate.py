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
            source_repo = Path(temporary) / "source"
            repo = Path(temporary) / "repo"
            env = os.environ.copy()
            env.update(
                {
                    "GIT_AUTHOR_NAME": "Evidence First Test",
                    "GIT_AUTHOR_EMAIL": "contributors",
                    "GIT_COMMITTER_NAME": "Evidence First Test",
                    "GIT_COMMITTER_EMAIL": "contributors",
                }
            )

            subprocess.run(
                ["git", "clone", "--no-hardlinks", "-q", str(ROOT), str(source_repo)],
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.run_git(
                source_repo,
                env,
                "commit",
                "-q",
                "--allow-empty",
                "-m",
                "synthetic public base",
            )
            base = self.run_git(source_repo, env, "rev-parse", "HEAD").stdout.strip()
            loose_object = source_repo / ".git" / "objects" / base[:2] / base[2:]
            self.assertTrue(
                loose_object.is_file(), f"expected fresh loose object: {loose_object}"
            )
            self.run_git(source_repo, env, "tag", "phase-h-test-base")

            subprocess.run(
                ["git", "clone", "--no-hardlinks", "-q", str(source_repo), str(repo)],
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )

            for source in ROOT.iterdir():
                if source.name in {".git", "_build", "__pycache__"}:
                    continue
                destination = repo / source.name
                if source.is_dir():
                    shutil.copytree(
                        source,
                        destination,
                        dirs_exist_ok=True,
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
    def run_git(
        repo: Path, env: dict[str, str], *arguments: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *arguments],
            cwd=repo,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
