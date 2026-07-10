from __future__ import annotations

from tests.phase6_support import Phase6ScriptTestCase


class UninstallerTests(Phase6ScriptTestCase):
    def test_user_file_and_parent_directory_are_preserved(self):
        self.install()
        user_file = self.vault / "Sources" / "user-owned.md"
        user_file.write_text("user content\n", encoding="utf-8")
        self.run_script(
            "uninstall.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        self.assertEqual(user_file.read_text(encoding="utf-8"), "user content\n")
        self.assertTrue(user_file.parent.is_dir())

    def test_modified_distribution_file_is_preserved_with_warning(self):
        self.install()
        target = self.hermes_home / "distributions" / "evidence-first" / "agent" / "SOUL.md"
        target.write_text(target.read_text(encoding="utf-8") + "\nuser modification\n", encoding="utf-8")
        result = self.run_script(
            "uninstall.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        self.assertTrue(target.is_file())
        self.assertIn("WARNING", result.stdout)
        self.assertIn(str(target), result.stdout)

    def test_only_empty_directories_are_removed(self):
        self.install()
        empty_after_removal = self.vault / "Archive"
        nonempty_after_removal = self.vault / "Sources"
        (nonempty_after_removal / "mine.md").write_text("mine\n", encoding="utf-8")
        self.run_script(
            "uninstall.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        self.assertFalse(empty_after_removal.exists())
        self.assertTrue(nonempty_after_removal.is_dir())
        self.assertTrue((nonempty_after_removal / "mine.md").is_file())

    def test_uninstall_never_edits_config_and_prints_exact_manual_instruction(self):
        self.install()
        config = self.hermes_home / "config.yaml"
        installed_config = config.read_bytes()
        result = self.run_script(
            "uninstall.sh",
            "--vault",
            self.vault,
            "--hermes-home",
            self.hermes_home,
        )
        self.assertEqual(config.read_bytes(), installed_config)
        self.assertIn("MANUAL CONFIG REMOVAL REQUIRED", result.stdout)
        self.assertIn("skills.external_dirs[1]", result.stdout)
        self.assertIn(str(self.hermes_home / "distributions" / "evidence-first" / "skills"), result.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()
