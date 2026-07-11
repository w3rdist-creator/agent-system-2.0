from __future__ import annotations

import json

from tests.phase6_support import Phase6ScriptTestCase


class InstallerTests(Phase6ScriptTestCase):
    def test_dry_run_writes_nothing_and_shows_reference_command(self):
        before_home = self.snapshot(self.hermes_home)
        result = self.run_script(
            "install.sh",
            "--dry-run",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        self.assertEqual(self.snapshot(self.hermes_home), before_home)
        self.assertFalse(self.vault.exists())
        self.assertIn("PLAN config: MANUAL ADDITION REQUIRED", result.stdout)
        self.assertIn("skills.external_dirs", result.stdout)
        self.assertIn("DRY RUN", result.stdout)

    def test_unsupported_version_refuses_before_writing(self):
        env = self.env.copy()
        env["FAKE_HERMES_VERSION"] = "Hermes Agent v0.19.0"
        before_home = self.snapshot(self.hermes_home)
        result = self.run_script(
            "install.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
            check=False,
            env=env,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsupported Hermes version", result.stderr)
        self.assertEqual(self.snapshot(self.hermes_home), before_home)
        self.assertFalse(self.vault.exists())

    def test_conflict_writes_incoming_and_preserves_original(self):
        self.vault.mkdir()
        original = b"user-owned home\n"
        (self.vault / "Home.md").write_bytes(original)
        self.install()
        self.assertEqual((self.vault / "Home.md").read_bytes(), original)
        self.assertTrue((self.vault / "Home.md.incoming").is_file())
        entry = next(
            item for item in self.manifest()["files"] if item["path"].endswith("Home.md.incoming")
        )
        self.assertEqual(entry["original_state"], "preexisting")
        self.assertEqual(entry["component"], "vault-base")

    def test_manifest_has_schema_hashes_states_and_components(self):
        self.install()
        manifest = self.manifest()
        self.assertEqual(manifest["manifest_schema_version"], 2)
        self.assertEqual(manifest["strategy"], "reference-first")
        self.assertEqual(manifest["hermes_compatibility"], "0.18.x")
        self.assertEqual(manifest["external_dirs_index"], 1)
        self.assertTrue(manifest["files"])
        for entry in manifest["files"]:
            self.assertEqual(
                set(entry),
                {"path", "original_state", "sha256", "component"},
            )
            self.assertIn(entry["original_state"], {"absent", "preexisting"})
            self.assertEqual(len(entry["sha256"]), 64)
            int(entry["sha256"], 16)
        self.assertTrue(any(item["component"] == "hermes-distribution" for item in manifest["files"]))
        self.assertTrue(any(item["component"] == "vault-base" for item in manifest["files"]))

    def test_verify_install_detects_hash_drift(self):
        self.install()
        clean = self.run_script(
            "verify-install.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        self.assertIn("PASS", clean.stdout)
        target = self.hermes_home / "distributions" / "evidence-first" / "agent" / "SOUL.md"
        target.write_text(target.read_text(encoding="utf-8") + "\nmodified\n", encoding="utf-8")
        drifted = self.run_script(
            "verify-install.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
            check=False,
        )
        self.assertNotEqual(drifted.returncode, 0)
        self.assertIn("hash mismatch", drifted.stdout)

    def test_install_never_edits_config_and_verify_fails_closed_until_manual_step(self):
        config = self.hermes_home / "config.yaml"
        before = config.read_bytes()
        result = self.install(configure=False)
        self.assertEqual(config.read_bytes(), before)
        self.assertIn("MANUAL CONFIG ADDITION REQUIRED", result.stdout)
        unconfigured = self.run_script(
            "verify-install.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
            check=False,
        )
        self.assertNotEqual(unconfigured.returncode, 0)
        self.assertIn("config entry missing", unconfigured.stdout)
        self.perform_manual_config_addition()
        configured = self.run_script(
            "verify-install.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        self.assertIn("PASS", configured.stdout)

    def test_fixture_hermes_refuses_list_append_like_real_hermes(self):
        import subprocess

        result = subprocess.run(
            [
                str(self.hermes_home / "bin" / "hermes"),
                "config",
                "set",
                "skills.external_dirs.1",
                "/tmp/appended",
            ],
            env={**self.env, "HERMES_HOME": str(self.hermes_home)},
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("list assignment index out of range", result.stderr)

    def test_pack_listing_shows_status_and_triggers(self):
        result = self.run_script("list-packs.sh")
        self.assertIn("research\tshipped\t", result.stdout)
        self.assertIn("context-spine\tinert\t", result.stdout)
        self.assertIn("separately passing corpus review", result.stdout)

    def test_inert_pack_refuses_with_activation_trigger(self):
        self.install()
        result = self.run_script(
            "install-pack.sh",
            "context-spine",
            "--vault",
            self.vault,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("inert", result.stderr)
        self.assertIn("separately passing corpus review", result.stderr)

    def test_both_shipped_packs_extend_the_install_manifest(self):
        self.install()
        for pack in ("research", "agent-ops"):
            self.run_script("install-pack.sh", pack, "--vault", self.vault)
        manifest = self.manifest()
        self.assertEqual(manifest["installed_packs"], ["research", "agent-ops"])
        components = {item["component"] for item in manifest["files"]}
        self.assertIn("pack:research", components)
        self.assertIn("pack:agent-ops", components)


if __name__ == "__main__":
    import unittest

    unittest.main()
