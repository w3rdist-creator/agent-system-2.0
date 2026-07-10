from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "hermes-home"


class Phase6ScriptTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.hermes_home = self.root / "hermes-home"
        self.vault = self.root / "vault"
        shutil.copytree(FIXTURE, self.hermes_home)
        (self.hermes_home / "bin" / "hermes").chmod(0o755)
        self.env = os.environ.copy()
        self.env["PATH"] = f"{self.hermes_home / 'bin'}{os.pathsep}{self.env['PATH']}"

    def run_script(self, name: str, *arguments: str, check: bool = True, env=None):
        result = subprocess.run(
            ["bash", str(ROOT / "scripts" / name), *map(str, arguments)],
            cwd=ROOT,
            env=env or self.env,
            text=True,
            capture_output=True,
        )
        if check and result.returncode:
            self.fail(
                f"{name} exited {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        return result

    def install(self, configure: bool = True):
        result = self.run_script(
            "install.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        if configure:
            self.perform_manual_config_addition()
        return result

    def perform_manual_config_addition(self):
        """Simulate the operator's documented manual skills.external_dirs step."""
        config = self.hermes_home / "config.yaml"
        external = self.hermes_home / "distributions" / "evidence-first" / "skills"
        lines = config.read_text(encoding="utf-8").splitlines()
        anchor = next(i for i, line in enumerate(lines) if line.strip() == "external_dirs:")
        lines.insert(anchor + 1, f"    - {external}")
        config.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def manifest(self):
        path = self.vault / ".evidence-first" / "install-manifest.json"
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def snapshot(path: Path):
        if not path.exists():
            return None
        return {
            item.relative_to(path).as_posix(): item.read_bytes()
            for item in path.rglob("*")
            if item.is_file()
        }
