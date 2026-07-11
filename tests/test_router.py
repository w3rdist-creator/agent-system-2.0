from __future__ import annotations

import json
import math
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def approximate_tokens(text: str) -> int:
    """Use the repository's documented conservative four-characters/token estimate."""

    return math.ceil(len(text) / 4)


class RouterContractTests(unittest.TestCase):
    def test_level_zero_parses_and_stays_bounded(self):
        path = ROOT / "skills" / "level-0-categories.yaml"
        categories = json.loads(path.read_text(encoding="utf-8"))

        self.assertIsInstance(categories, list)
        self.assertGreater(len(categories), 0)
        self.assertLessEqual(len(categories), 15)
        self.assertEqual(len({item["name"] for item in categories}), len(categories))
        for item in categories:
            self.assertEqual(set(item), {"name", "scope", "escalation"})
            self.assertTrue(all(isinstance(value, str) and value.strip() for value in item.values()))

        self.assertLessEqual(approximate_tokens(path.read_text(encoding="utf-8")), 400)

    def test_soul_word_count_is_bounded(self):
        text = (ROOT / "agent" / "SOUL.md").read_text(encoding="utf-8")
        words = re.findall(r"\b[\w’-]+\b", text, flags=re.UNICODE)
        self.assertLessEqual(len(words), 900)

    def test_soul_scenario_map_covers_every_nonblank_line(self):
        soul_lines = [
            line.strip()
            for line in (ROOT / "agent" / "SOUL.md").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        mapping = json.loads(
            (ROOT / "agent" / "SOUL-scenario-map.yaml").read_text(encoding="utf-8")
        )
        mapped_lines = [entry["line"] for entry in mapping]

        self.assertEqual(mapped_lines, soul_lines)
        self.assertEqual(len(mapped_lines), len(set(mapped_lines)))

        existing_ids = {
            path.parent.name
            for path in (ROOT / "evaluations" / "scenarios").glob("*/scenario.yaml")
        }
        self.assertEqual(len(existing_ids), 16)
        for entry in mapping:
            self.assertTrue(set(entry) <= {"line", "scenarios", "pruning_candidate"})
            self.assertTrue({"line", "scenarios"} <= set(entry))
            self.assertIsInstance(entry["scenarios"], list)
            self.assertTrue(entry["scenarios"])
            self.assertTrue(set(entry["scenarios"]) <= existing_ids)
            candidate = entry.get("pruning_candidate")
            if candidate is not None:
                self.assertEqual(
                    set(candidate),
                    {"baseline_absorbed_scenarios", "model", "reasoning", "date"},
                )
                self.assertTrue(candidate["baseline_absorbed_scenarios"])
                self.assertTrue(
                    set(candidate["baseline_absorbed_scenarios"]) <= set(entry["scenarios"])
                )
                self.assertTrue(
                    all(candidate[field] for field in ("model", "reasoning", "date"))
                )

    def test_all_core_skills_exist_at_declared_paths(self):
        for relative in (
            "skills/core/capability-router/SKILL.md",
            "skills/core/evidence-first-operating-style/SKILL.md",
            "skills/core/source-grounding/SKILL.md",
            "skills/core/knowledge-metabolism/SKILL.md",
            "skills/core/loop-governance/SKILL.md",
            "skills/core/vault-operations/SKILL.md",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_scenario_manifests_use_exact_phase_two_paths(self):
        loaded_paths: set[str] = set()
        for path in (ROOT / "evaluations" / "scenarios").glob("*/scenario.yaml"):
            scenario = json.loads(path.read_text(encoding="utf-8"))
            loaded_paths.update(scenario["Treatment loading"])

        self.assertIn("agent/SOUL.md", loaded_paths)
        self.assertIn("agent/AUTHORITY_BOUNDARIES.md", loaded_paths)
        self.assertIn("agent/USER_PROFILE_TEMPLATE.md", loaded_paths)
        self.assertIn("skills/core/capability-router/SKILL.md", loaded_paths)
        self.assertIn("skills/core/evidence-first-operating-style/SKILL.md", loaded_paths)
        self.assertIn("skills/level-0-categories.yaml", loaded_paths)


if __name__ == "__main__":
    unittest.main()
