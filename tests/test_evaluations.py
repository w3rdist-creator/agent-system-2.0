from __future__ import annotations

import csv
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.evaluation_lib import (
    HARNESS_VERSION,
    RESULT_FIELDS,
    ValidationError,
    evaluate_transcript,
    load_json_yaml,
    validate_result_row,
    validate_scenario_dir,
)


ROOT = Path(__file__).resolve().parents[1]


class ScenarioSchemaTests(unittest.TestCase):
    def test_broken_scenario_is_rejected(self):
        source_id = "01-stale-context-live-source"
        with tempfile.TemporaryDirectory() as temporary:
            evaluations = Path(temporary) / "evaluations"
            scenario = evaluations / "scenarios" / source_id
            expected = evaluations / "expected"
            shutil.copytree(ROOT / "evaluations" / "scenarios" / source_id, scenario)
            expected.mkdir(parents=True)
            shutil.copy2(ROOT / "evaluations" / "expected" / f"{source_id}.json", expected)
            data = load_json_yaml(scenario / "scenario.yaml")
            del data["Observable action forbidden"]
            (scenario / "scenario.yaml").write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "missing schema fields"):
                validate_scenario_dir(scenario)


class TraceAssertionTests(unittest.TestCase):
    def setUp(self):
        self.spec = {
            "scenario_id": "synthetic",
            "deterministic": True,
            "required_events": [
                {"type": "tool_call", "tool": "read_file", "args": {"path": "fixture/live.json"}}
            ],
            "forbidden_events": [{"type": "tool_call", "tool": "write_file"}],
            "event_order": [
                {"type": "tool_call", "tool": "read_file"},
                {"type": "answer"},
            ],
            "required_file_reads_before_answer": ["fixture/live.json"],
            "disposition": "done",
        }

    def test_trace_assertions_pass_a_valid_transcript(self):
        transcript = json.loads(
            (ROOT / "tests" / "fixtures" / "transcript-pass.json").read_text(encoding="utf-8")
        )
        result = evaluate_transcript(transcript, self.spec)
        self.assertTrue(result["passed"], result["failures"])

    def test_trace_assertions_fail_prose_without_prior_action(self):
        transcript = json.loads(
            (ROOT / "tests" / "fixtures" / "transcript-fail.json").read_text(encoding="utf-8")
        )
        result = evaluate_transcript(transcript, self.spec)
        self.assertFalse(result["passed"])
        self.assertTrue(any("before answer" in failure or "ordered event" in failure for failure in result["failures"]))


class ResultsSchemaTests(unittest.TestCase):
    def test_results_schema_round_trips_through_csv(self):
        row = {
            "scenario_id": "synthetic",
            "model_id": "model-family",
            "model_version": "snapshot-1",
            "model_version_date": "2026-07-10",
            "run_date": "2026-07-10",
            "trial_count": 3,
            "harness_version": HARNESS_VERSION,
            "treatment_passes": 3,
            "control_passes": 1,
            "deterministic_treatment_pass": True,
            "control_failures": 2,
            "confirmed_delta": True,
            "treatment_dispositions": '["done", "done", "done"]',
            "control_dispositions": '["done", "blocked", "blocked"]',
            "human_judgment": "pending-operator-review",
            "operator_override": False,
            "operator_override_rationale": "",
        }
        normalized = validate_result_row(row)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
                writer.writeheader()
                writer.writerow(normalized)
            with path.open(encoding="utf-8", newline="") as handle:
                loaded = next(csv.DictReader(handle))
        self.assertEqual(validate_result_row(loaded), normalized)


if __name__ == "__main__":
    unittest.main()
