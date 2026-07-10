from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Phase7ReleaseContractTests(unittest.TestCase):
    def test_public_document_set_exists(self):
        required = {
            "README.md",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "docs/Architecture.md",
            "docs/Admission-and-Exclusion-Policy.md",
            "docs/Token-and-Context-Budget.md",
            "docs/Source-Consolidation.md",
            "docs/Sanitization-and-Publication.md",
            "docs/Deferred-Capability-Roadmap.md",
            "docs/Opus-Review-Disposition.md",
            "docs/Publication-Commands.md",
            ".github/workflows/verify.yml",
            "scripts/export-public.sh",
        }
        missing = sorted(path for path in required if not (ROOT / path).is_file())
        self.assertEqual(missing, [])

    def test_license_has_split_notice_without_pending_confirmation(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("MIT", license_text)
        self.assertIn("CC BY 4.0", license_text)
        self.assertNotIn("confirm", license_text.casefold())
        self.assertNotIn("pending", license_text.casefold())

    def test_ci_runs_dev_gate_on_linux_and_macos(self):
        workflow = (ROOT / ".github" / "workflows" / "verify.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("ubuntu-latest", workflow)
        self.assertIn("macos-latest", workflow)
        self.assertIn("bash scripts/dev-gate.sh", workflow)
        self.assertNotIn("publication-gate.sh", workflow)

    def test_export_contract_is_fresh_one_commit_without_remote(self):
        exporter = (ROOT / "scripts" / "export-public.sh").read_text(encoding="utf-8")
        self.assertIn("evidence-first-hermes-distribution-public", exporter)
        self.assertIn("--exclude=.git/", exporter)
        self.assertIn("--exclude=_build/", exporter)
        self.assertIn("init -b main", exporter)
        self.assertIn("Release 1.0 candidate", exporter)
        self.assertIn("publication-gate.sh", exporter)
        self.assertNotIn("remote add", exporter)
        self.assertNotIn("push", exporter)


if __name__ == "__main__":
    unittest.main()
