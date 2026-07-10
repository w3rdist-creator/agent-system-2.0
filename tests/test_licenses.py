from __future__ import annotations

from pathlib import Path
import unittest

from scripts.verify_licenses import validate


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "licenses"


class LicenseFixtureTests(unittest.TestCase):
    def test_missing_license_fails(self):
        errors = validate([FIXTURES / "missing"], root=ROOT, include_ledger=False)
        self.assertTrue(errors)
        self.assertTrue(any("missing license" in error for error in errors))

    def test_present_license_passes(self):
        errors = validate([FIXTURES / "present"], root=ROOT, include_ledger=False)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
