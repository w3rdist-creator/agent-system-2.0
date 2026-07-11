from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

from scripts.verify_private_markers import (
    SENSITIVE_FILENAME_RE,
    findings_for_text,
    has_sensitive_tree_filename,
)


ROOT = Path(__file__).resolve().parents[1]


class PrivacyScannerTests(unittest.TestCase):
    def test_each_private_marker_class_is_caught(self):
        cases = {
            "absolute personal path": "/Us" + "ers/alice/private.txt",
            "email address": "alice" + "@example.org",
            "phone number": "212" + "-555-0199",
            "API key or token": "sk-" + "A" * 24,
            "private hostname": "build" + ".internal",
            "private key block": "-----BEGIN " + "PRIVATE KEY-----",
            "session/state/auth filename in patch stream": "diff --git a/" + "session.json b/session.json",
        }
        for expected, marker in cases.items():
            with self.subTest(expected=expected):
                findings = findings_for_text(marker, "fixture", [])
                self.assertTrue(any(expected in finding for finding in findings), findings)

    def test_external_denylist_marker_is_caught(self):
        findings = findings_for_text("A project codename appears here", "fixture", ["project codename"])
        self.assertTrue(any("external denylist term" in finding for finding in findings))

    def test_sensitive_filename_class_is_caught(self):
        filename = "sess" + "ion.json"
        self.assertIsNotNone(SENSITIVE_FILENAME_RE.search(filename))

    def test_public_evaluation_state_fixture_is_the_only_path_exception(self):
        fixture = Path(
            "evaluations/scenarios/01-stale-context-live-source/"
            "fixture/queue-service/state.json"
        )
        self.assertFalse(has_sensitive_tree_filename(fixture))
        self.assertTrue(has_sensitive_tree_filename(Path("other/fixture/state.json")))

        allowed_patch = f"+++ b/{fixture.as_posix()}"
        self.assertEqual(findings_for_text(allowed_patch, "fixture", []), [])
        other_patch = "+++ b/other/fixture/state.json"
        self.assertTrue(findings_for_text(other_patch, "fixture", []))

    def test_repository_passes_privacy_scan(self):
        result = subprocess.run(
            ["python3", str(ROOT / "scripts" / "verify_private_markers.py"), str(ROOT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
