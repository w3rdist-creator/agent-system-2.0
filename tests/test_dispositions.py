from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

from scripts.evaluation_lib import DISPOSITIONS


ROOT = Path(__file__).resolve().parents[1]


class DispositionVocabularyTests(unittest.TestCase):
    def test_closed_set_is_the_plan_set(self):
        self.assertEqual(
            DISPOSITIONS,
            {
                "act",
                "watch",
                "no-action",
                "no-edge",
                "blocked",
                "done",
                "merge",
                "defer",
                "kill",
                "needs-human",
            },
        )

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

    def test_methodology_prints_exact_shared_vocabulary(self):
        text = (ROOT / "evaluations" / "README.md").read_text(encoding="utf-8")
        match = re.search(r"```text\n([^`]+)```", text)
        self.assertIsNotNone(match)
        documented = {item.strip() for item in match.group(1).split("|")}
        self.assertEqual(documented, DISPOSITIONS)


if __name__ == "__main__":
    unittest.main()
