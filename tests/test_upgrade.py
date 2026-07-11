from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

from tests.phase6_support import Phase6ScriptTestCase, ROOT


class UpgradeTests(Phase6ScriptTestCase):
    def run_from(self, root: Path, name: str, *arguments: object, check: bool = True):
        result = subprocess.run(
            ["bash", str(root / "scripts" / name), *map(str, arguments)],
            cwd=root,
            env=self.env,
            text=True,
            capture_output=True,
        )
        if check and result.returncode:
            self.fail(
                f"{name} exited {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        return result

    def prepare_old_release(self) -> tuple[Path, Path]:
        old = self.root / "old-release"
        shutil.copytree(
            ROOT,
            old,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        added_in_new = old / "vault-template" / "Archive" / "Archive Map.md"
        added_in_new.unlink()
        changed_in_new = old / "agent" / "AUTHORITY_BOUNDARIES.md"
        changed_in_new.write_text(
            changed_in_new.read_text(encoding="utf-8") + "\nold release marker\n",
            encoding="utf-8",
        )
        retired = old / "vault-template" / "Retired by upgrade.md"
        retired.write_text("old distribution file\n", encoding="utf-8")
        return old, retired

    def test_manifest_to_manifest_upgrade_preserves_user_changes(self):
        old, _ = self.prepare_old_release()
        self.run_from(
            old,
            "install.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        self.perform_manual_config_addition()

        manifest_path = self.vault / ".evidence-first" / "install-manifest.json"
        old_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        old_manifest["manifest_schema_version"] = 1
        manifest_path.write_text(json.dumps(old_manifest, indent=2) + "\n", encoding="utf-8")

        modified = self.hermes_home / "distributions" / "evidence-first" / "agent" / "SOUL.md"
        user_content = modified.read_bytes() + b"\nuser modification\n"
        modified.write_bytes(user_content)
        bytecode = (
            self.hermes_home
            / "distributions"
            / "evidence-first"
            / "enforcement"
            / "__pycache__"
            / "completion.cpython-39.pyc"
        )
        bytecode.parent.mkdir()
        bytecode.write_bytes(b"dummy bytecode")
        config = self.hermes_home / "config.yaml"
        config_before = config.read_bytes()

        vault_before = self.snapshot(self.vault)
        home_before = self.snapshot(self.hermes_home)
        dry = self.run_script(
            "upgrade.sh",
            "--dry-run",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        self.assertIn("PLAN preserved-with-incoming", dry.stdout)
        self.assertIn("UPGRADE REPORT:", dry.stdout)
        self.assertEqual(self.snapshot(self.vault), vault_before)
        self.assertEqual(self.snapshot(self.hermes_home), home_before)

        result = self.run_script(
            "upgrade.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        self.assertIn("preserved-with-incoming=1", result.stdout)
        self.assertIn("CONFIG: unchanged", result.stdout)
        self.assertFalse(bytecode.exists())
        self.assertEqual(modified.read_bytes(), user_content)
        self.assertEqual(
            modified.with_name("SOUL.md.incoming").read_bytes(),
            (ROOT / "agent" / "SOUL.md").read_bytes(),
        )
        self.assertEqual(
            (self.vault / "Archive" / "Archive Map.md").read_bytes(),
            (ROOT / "vault-template" / "Archive" / "Archive Map.md").read_bytes(),
        )
        self.assertEqual(
            (
                self.hermes_home
                / "distributions"
                / "evidence-first"
                / "agent"
                / "AUTHORITY_BOUNDARIES.md"
            ).read_bytes(),
            (ROOT / "agent" / "AUTHORITY_BOUNDARIES.md").read_bytes(),
        )
        self.assertFalse((self.vault / "Retired by upgrade.md").exists())
        self.assertEqual(config.read_bytes(), config_before)

        manifest = self.manifest()
        self.assertEqual(manifest["manifest_schema_version"], 2)
        modified_entry = next(
            item for item in manifest["files"] if item["path"] == str(modified.resolve())
        )
        self.assertEqual(modified_entry["sha256"], self.file_hash(modified))
        self.assertEqual(
            modified_entry["superseded_by_incoming"], str(modified.resolve()) + ".incoming"
        )
        verified = self.run_script(
            "verify-install.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        self.assertIn("PASS", verified.stdout)

    def test_upgrade_without_prior_install_refuses(self):
        result = self.run_script(
            "upgrade.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(
            result.stderr,
            "ERROR: install manifest not found; run install.sh before upgrade\n",
        )
        self.assertFalse(self.vault.exists())

    @staticmethod
    def file_hash(path: Path) -> str:
        import hashlib

        return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    import unittest

    unittest.main()
