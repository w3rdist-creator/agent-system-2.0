from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

from scripts.evaluation_lib import (
    DISPOSITIONS,
    LEGACY_DISPOSITION_ALIASES,
    normalize_disposition,
)


ROOT = Path(__file__).resolve().parents[1]


class DispositionVocabularyTests(unittest.TestCase):
    def test_closed_set_is_the_plan_set(self):
        self.assertEqual(
            DISPOSITIONS,
            {
                "act",
                "watch",
                "no-action",
                "blocked",
                "done",
                "kill",
                "needs-human",
            },
        )

    def test_legacy_aliases_normalize_to_canonical_labels(self):
        self.assertEqual(
            LEGACY_DISPOSITION_ALIASES,
            {"merge": "done", "defer": "watch", "no-edge": "no-action"},
        )
        for legacy, canonical in LEGACY_DISPOSITION_ALIASES.items():
            with self.subTest(legacy=legacy):
                self.assertEqual(normalize_disposition(legacy), canonical)
                self.assertIn(normalize_disposition(legacy), DISPOSITIONS)

    def test_unknown_label_does_not_normalize_into_the_closed_set(self):
        self.assertEqual(normalize_disposition("later"), "later")
        self.assertNotIn(normalize_disposition("later"), DISPOSITIONS)

    def test_all_scenario_and_assertion_dispositions_use_shared_set(self):
        scenario_values = set()
        for path in (ROOT / "evaluations" / "scenarios").glob("*/scenario.yaml"):
            scenario_values.add(json.loads(path.read_text(encoding="utf-8"))["Disposition emitted"])
        assertion_values = set()
        for path in (ROOT / "evaluations" / "expected").glob("*.json"):
            assertion_values.add(json.loads(path.read_text(encoding="utf-8"))["disposition"])
        self.assertTrue(scenario_values <= DISPOSITIONS)
        self.assertTrue(assertion_values <= DISPOSITIONS)
        self.assertEqual(scenario_values, assertion_values)
        self.assertEqual(scenario_values, DISPOSITIONS)

    def test_methodology_prints_exact_shared_vocabulary(self):
        text = (ROOT / "evaluations" / "README.md").read_text(encoding="utf-8")
        match = re.search(r"```text\n([^`]+)```", text)
        self.assertIsNotNone(match)
        documented = {item.strip() for item in match.group(1).split("|")}
        self.assertEqual(documented, DISPOSITIONS)

    def test_rejected_scenario_three_candidate_uses_kill(self):
        scenario_id = "03-seductive-cross-domain-analogy"
        scenario = json.loads(
            (ROOT / "evaluations" / "scenarios" / scenario_id / "scenario.yaml").read_text(
                encoding="utf-8"
            )
        )
        assertion = json.loads(
            (ROOT / "evaluations" / "expected" / f"{scenario_id}.json").read_text(
                encoding="utf-8"
            )
        )
        task = (ROOT / "evaluations" / "scenarios" / scenario_id / "task.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("candidate", task.lower())
        self.assertIn("promotion", task.lower())
        self.assertEqual(scenario["Disposition emitted"], "kill")
        self.assertEqual(assertion["disposition"], "kill")


if __name__ == "__main__":
    unittest.main()
