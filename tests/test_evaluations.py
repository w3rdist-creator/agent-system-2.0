from __future__ import annotations

import csv
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.evaluation_lib import (
    HARNESS_VERSION,
    LEGACY_DISPOSITION_ALIASES,
    RESULT_FIELDS,
    ValidationError,
    evaluate_transcript,
    load_json_yaml,
    validate_assertion_spec,
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

    def test_legacy_scenario_disposition_is_accepted(self):
        source_id = "03-seductive-cross-domain-analogy"
        with tempfile.TemporaryDirectory() as temporary:
            evaluations = Path(temporary) / "evaluations"
            scenario = evaluations / "scenarios" / source_id
            expected = evaluations / "expected"
            shutil.copytree(ROOT / "evaluations" / "scenarios" / source_id, scenario)
            expected.mkdir(parents=True)
            shutil.copy2(ROOT / "evaluations" / "expected" / f"{source_id}.json", expected)
            data = load_json_yaml(scenario / "scenario.yaml")
            data["Disposition emitted"] = "no-edge"
            (scenario / "scenario.yaml").write_text(json.dumps(data), encoding="utf-8")
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

    def test_each_legacy_emission_matches_its_canonical_assertion(self):
        for legacy, canonical in LEGACY_DISPOSITION_ALIASES.items():
            with self.subTest(legacy=legacy):
                spec = {**self.spec, "disposition": canonical}
                transcript = {
                    "events": [
                        {
                            "type": "tool_call",
                            "tool": "read_file",
                            "args": {"path": "fixture/live.json"},
                        },
                        {"type": "answer", "content": "complete"},
                        {"type": "disposition", "label": legacy},
                    ]
                }
                result = evaluate_transcript(transcript, spec)
                self.assertTrue(result["passed"], result["failures"])
                self.assertEqual(result["emitted_disposition"], canonical)

    def test_legacy_assertion_matches_canonical_emission(self):
        spec = {**self.spec, "disposition": "merge"}
        transcript = {
            "events": [
                {
                    "type": "tool_call",
                    "tool": "read_file",
                    "args": {"path": "fixture/live.json"},
                },
                {"type": "answer", "content": "complete"},
                {"type": "disposition", "label": "done"},
            ]
        }
        result = evaluate_transcript(transcript, spec)
        self.assertTrue(result["passed"], result["failures"])

    def test_merge_transcript_passes_checked_in_done_expectation(self):
        spec = load_json_yaml(
            ROOT / "evaluations" / "expected" / "15-write-only-vault.json"
        )
        transcript = {
            "events": [
                {
                    "type": "tool_call",
                    "tool": "read_file",
                    "args": {"path": f"fixture/{name}"},
                }
                for name in ("inventory.json", "usage.json", "index-a.md", "index-b.md")
            ]
            + [
                {
                    "type": "tool_call",
                    "tool": "delete_file",
                    "args": {"path": "fixture/index-b.md"},
                },
                {"type": "answer", "content": "duplicate removed and verified"},
                {"type": "disposition", "label": "merge"},
            ]
        }
        result = evaluate_transcript(transcript, spec)
        self.assertTrue(result["passed"], result["failures"])
        self.assertEqual(result["emitted_disposition"], "done")

    def test_unknown_assertion_and_emission_still_fail(self):
        with self.assertRaisesRegex(ValidationError, "invalid assertion disposition"):
            validate_assertion_spec({**self.spec, "disposition": "later"})
        transcript = {
            "events": [
                {
                    "type": "tool_call",
                    "tool": "read_file",
                    "args": {"path": "fixture/live.json"},
                },
                {"type": "answer", "content": "complete"},
                {"type": "disposition", "label": "later"},
            ]
        }
        result = evaluate_transcript(transcript, self.spec)
        self.assertFalse(result["passed"])
        self.assertTrue(any("invalid emitted disposition" in failure for failure in result["failures"]))


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
