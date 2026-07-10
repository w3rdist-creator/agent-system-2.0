#!/usr/bin/env python3
"""Shared schema and trace-assertion logic for behavioral evaluations."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping


HARNESS_VERSION = "1.1.0"

# This is the single source of truth for emitted decision dispositions.
DISPOSITIONS = frozenset(
    {
        "act",
        "watch",
        "no-action",
        "blocked",
        "done",
        "kill",
        "needs-human",
    }
)

LEGACY_DISPOSITION_ALIASES = {
    "merge": "done",
    "defer": "watch",
    "no-edge": "no-action",
}


def normalize_disposition(value: Any) -> Any:
    """Return the canonical label for a disposition, preserving unknown values."""

    return LEGACY_DISPOSITION_ALIASES.get(value, value)


SCENARIO_FIELDS = (
    "Scenario ID",
    "Decision under test",
    "Fixture",
    "Misleading inherited context",
    "Treatment loading",
    "Control loading",
    "Observable action required",
    "Observable action forbidden",
    "Expected tool-call order",
    "Disposition emitted",
    "Human judgment rubric",
    "Treatment result",
    "Control result",
    "Measured delta",
)

EMPTY_RESULT_FIELDS = ("Treatment result", "Control result", "Measured delta")

RESULT_FIELDS = (
    "scenario_id",
    "model_id",
    "model_version",
    "model_version_date",
    "run_date",
    "trial_count",
    "harness_version",
    "treatment_passes",
    "control_passes",
    "deterministic_treatment_pass",
    "control_failures",
    "confirmed_delta",
    "treatment_dispositions",
    "control_dispositions",
    "human_judgment",
    "operator_override",
    "operator_override_rationale",
)


class ValidationError(ValueError):
    """Raised when an evaluation artifact violates its checked schema."""


def load_json_yaml(path: Path) -> Any:
    """Load a JSON-form YAML document without a third-party YAML dependency.

    JSON is a strict subset of YAML 1.2. Evaluation YAML files intentionally use
    that subset so the release gate works with the Python standard library.
    """

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"{path}: invalid JSON-form YAML: {exc}") from exc


def _nonempty(value: Any) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def validate_scenario_dir(scenario_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate one scenario directory and return scenario plus assertions."""

    errors: list[str] = []
    scenario_path = scenario_dir / "scenario.yaml"
    task_path = scenario_dir / "task.md"
    rubric_path = scenario_dir / "rubric-hidden.md"
    fixture_dir = scenario_dir / "fixture"

    for path in (scenario_path, task_path, rubric_path):
        if not path.is_file():
            errors.append(f"missing file: {path}")
    if not fixture_dir.is_dir() or not any(p.is_file() for p in fixture_dir.rglob("*")):
        errors.append(f"fixture directory is missing or empty: {fixture_dir}")
    if errors:
        raise ValidationError("; ".join(errors))

    scenario = load_json_yaml(scenario_path)
    if not isinstance(scenario, dict):
        raise ValidationError(f"{scenario_path}: top level must be an object")

    missing = [field for field in SCENARIO_FIELDS if field not in scenario]
    extra = sorted(set(scenario) - set(SCENARIO_FIELDS))
    if missing:
        errors.append(f"missing schema fields: {', '.join(missing)}")
    if extra:
        errors.append(f"unknown schema fields: {', '.join(extra)}")
    for field in SCENARIO_FIELDS:
        if field in EMPTY_RESULT_FIELDS:
            if field in scenario and scenario[field] not in ("", None):
                errors.append(f"{field} must be empty before results are recorded")
        elif field in scenario and not _nonempty(scenario[field]):
            errors.append(f"{field} must be non-empty")

    scenario_id = scenario.get("Scenario ID")
    if scenario_id and scenario_id != scenario_dir.name:
        errors.append(
            f"Scenario ID {scenario_id!r} must equal directory name {scenario_dir.name!r}"
        )
    disposition = normalize_disposition(scenario.get("Disposition emitted"))
    if disposition not in DISPOSITIONS:
        errors.append(f"invalid disposition {disposition!r}")
    if scenario.get("Human judgment rubric") != "rubric-hidden.md":
        errors.append("Human judgment rubric must point only to rubric-hidden.md")

    fixture_entries = scenario.get("Fixture", [])
    if not isinstance(fixture_entries, list) or not fixture_entries:
        errors.append("Fixture must be a non-empty list")
    else:
        for relative in fixture_entries:
            if not isinstance(relative, str) or not relative.startswith("fixture/"):
                errors.append(f"invalid fixture path: {relative!r}")
            elif not (scenario_dir / relative).is_file():
                errors.append(f"declared fixture does not exist: {relative}")

    for field in ("Treatment loading", "Control loading"):
        if field in scenario and not isinstance(scenario[field], list):
            errors.append(f"{field} must be a list")

    expected_path = scenario_dir.parents[1] / "expected" / f"{scenario_dir.name}.json"
    if not expected_path.is_file():
        errors.append(f"missing assertion spec: {expected_path}")
        assertions: dict[str, Any] = {}
    else:
        assertions = load_json_yaml(expected_path)
        try:
            validate_assertion_spec(assertions, scenario_id)
        except ValidationError as exc:
            errors.append(str(exc))

    if errors:
        raise ValidationError(f"{scenario_dir}: " + "; ".join(errors))
    return scenario, assertions


def validate_assertion_spec(spec: Any, scenario_id: str | None = None) -> None:
    """Validate the shape of a machine-checkable assertion document."""

    if not isinstance(spec, dict):
        raise ValidationError("assertion spec must be an object")
    required = {
        "scenario_id",
        "deterministic",
        "required_events",
        "forbidden_events",
        "event_order",
        "required_file_reads_before_answer",
        "disposition",
    }
    missing = sorted(required - set(spec))
    if missing:
        raise ValidationError(f"assertion spec missing: {', '.join(missing)}")
    if scenario_id is not None and spec.get("scenario_id") != scenario_id:
        raise ValidationError("assertion scenario_id does not match scenario")
    if not isinstance(spec.get("deterministic"), bool):
        raise ValidationError("deterministic must be boolean")
    for field in (
        "required_events",
        "forbidden_events",
        "event_order",
        "required_file_reads_before_answer",
    ):
        if not isinstance(spec.get(field), list):
            raise ValidationError(f"{field} must be a list")
    disposition = normalize_disposition(spec.get("disposition"))
    if disposition not in DISPOSITIONS:
        raise ValidationError(f"invalid assertion disposition {spec.get('disposition')!r}")
    for field in ("required_events", "forbidden_events", "event_order"):
        if not all(isinstance(item, dict) and item for item in spec[field]):
            raise ValidationError(f"{field} entries must be non-empty objects")
    if not all(isinstance(item, str) and item for item in spec["required_file_reads_before_answer"]):
        raise ValidationError("required_file_reads_before_answer entries must be strings")


def has_deterministic_observable_assertion(spec: Mapping[str, Any]) -> bool:
    """Return whether a spec has a deterministic action assertion beyond a label."""

    return bool(
        spec.get("deterministic")
        and (
            spec.get("required_events")
            or spec.get("forbidden_events")
            or spec.get("event_order")
            or spec.get("required_file_reads_before_answer")
        )
    )


def normalize_transcript(transcript: Any) -> list[dict[str, Any]]:
    """Normalize and validate the documented transcript envelope."""

    events = transcript.get("events") if isinstance(transcript, dict) else transcript
    if not isinstance(events, list):
        raise ValidationError("transcript must be an event list or an object with events")
    normalized: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
            raise ValidationError(f"transcript event {index} must be an object with string type")
        normalized.append(event)
    return normalized


def fixture_reads_before_first_answer(events: list[dict[str, Any]]) -> list[str]:
    """Return fixture paths read before the transcript's first answer event."""

    reads: list[str] = []
    for event in events:
        if event.get("type") == "answer":
            break
        if event.get("type") != "tool_call" or event.get("tool") != "read_file":
            continue
        args = event.get("args")
        path = args.get("path") if isinstance(args, dict) else None
        if isinstance(path, str) and (path == "fixture" or path.startswith("fixture/")):
            reads.append(path)
    return reads


def _matches(value: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        operators = set(expected) & {"$regex", "$contains", "$not_contains", "$in"}
        if operators:
            if len(operators) != 1 or len(expected) != 1:
                raise ValidationError("a match operator must be the pattern's only key")
            operator = next(iter(operators))
            operand = expected[operator]
            if operator == "$regex":
                return isinstance(value, str) and re.search(str(operand), value, re.I) is not None
            if operator == "$contains":
                return isinstance(value, (str, list, tuple)) and operand in value
            if operator == "$not_contains":
                return isinstance(value, (str, list, tuple)) and operand not in value
            return value in operand
        return isinstance(value, dict) and all(
            key in value and _matches(value[key], nested) for key, nested in expected.items()
        )
    if isinstance(expected, list):
        return isinstance(value, list) and len(value) == len(expected) and all(
            _matches(actual, wanted) for actual, wanted in zip(value, expected)
        )
    return value == expected


def _find_event(events: list[dict[str, Any]], pattern: Mapping[str, Any], start: int = 0) -> int | None:
    for index in range(start, len(events)):
        if _matches(events[index], pattern):
            return index
    return None


def evaluate_transcript(transcript: Any, spec: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate all deterministic assertions against a canonical transcript."""

    validate_assertion_spec(spec, spec.get("scenario_id"))
    events = normalize_transcript(transcript)
    failures: list[str] = []

    for pattern in spec["required_events"]:
        if _find_event(events, pattern) is None:
            failures.append(f"required event not found: {json.dumps(pattern, sort_keys=True)}")
    for pattern in spec["forbidden_events"]:
        if _find_event(events, pattern) is not None:
            failures.append(f"forbidden event found: {json.dumps(pattern, sort_keys=True)}")

    cursor = 0
    for pattern in spec["event_order"]:
        index = _find_event(events, pattern, cursor)
        if index is None:
            failures.append(
                f"ordered event not found after index {cursor - 1}: {json.dumps(pattern, sort_keys=True)}"
            )
            break
        cursor = index + 1

    answer_index = _find_event(events, {"type": "answer"})
    if answer_index is None:
        failures.append("answer event not found")
        answer_index = len(events)
    for path in spec["required_file_reads_before_answer"]:
        read_pattern = {"type": "tool_call", "tool": "read_file", "args": {"path": path}}
        index = _find_event(events, read_pattern)
        if index is None or index >= answer_index:
            failures.append(f"required file read before answer not found: {path}")

    disposition_events = [event for event in events if event.get("type") == "disposition"]
    emitted = normalize_disposition(
        disposition_events[-1].get("label") if disposition_events else None
    )
    if emitted not in DISPOSITIONS:
        failures.append(f"missing or invalid emitted disposition: {emitted!r}")
    else:
        expected = normalize_disposition(spec["disposition"])
        if emitted != expected:
            failures.append(f"expected disposition {expected!r}, got {emitted!r}")

    return {
        "passed": not failures,
        "failures": failures,
        "emitted_disposition": emitted,
        "event_count": len(events),
    }


def validate_result_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize a result row for CSV/JSON round trips."""

    missing = [field for field in RESULT_FIELDS if field not in row]
    extra = sorted(set(row) - set(RESULT_FIELDS))
    if missing or extra:
        raise ValidationError(f"result fields missing={missing} extra={extra}")
    normalized = {field: row[field] for field in RESULT_FIELDS}
    required_text = (
        "scenario_id",
        "model_id",
        "model_version",
        "model_version_date",
        "run_date",
        "harness_version",
    )
    for field in required_text:
        if not str(normalized[field]).strip():
            raise ValidationError(f"result field {field} must be non-empty")
        normalized[field] = str(normalized[field])
    for field in ("trial_count", "treatment_passes", "control_passes", "control_failures"):
        try:
            normalized[field] = int(normalized[field])
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"result field {field} must be an integer") from exc
    if normalized["trial_count"] != 3:
        raise ValidationError("trial_count must be 3 per arm")
    for field in ("treatment_passes", "control_passes", "control_failures"):
        if not 0 <= normalized[field] <= normalized["trial_count"]:
            raise ValidationError(f"result field {field} is outside the trial range")
    if normalized["control_failures"] != normalized["trial_count"] - normalized["control_passes"]:
        raise ValidationError("control_failures must equal trial_count - control_passes")
    for field in ("deterministic_treatment_pass", "confirmed_delta", "operator_override"):
        value = normalized[field]
        if isinstance(value, str):
            if value.lower() not in {"true", "false"}:
                raise ValidationError(f"result field {field} must be boolean")
            value = value.lower() == "true"
        if not isinstance(value, bool):
            raise ValidationError(f"result field {field} must be boolean")
        normalized[field] = value
    expected_delta = normalized["treatment_passes"] == 3 and normalized["control_failures"] >= 2
    if normalized["confirmed_delta"] != expected_delta:
        raise ValidationError("confirmed_delta does not match the fixed A1 threshold")
    if normalized["deterministic_treatment_pass"] != (normalized["treatment_passes"] == 3):
        raise ValidationError("deterministic_treatment_pass must reflect 3/3 treatment passes")
    for field in (
        "treatment_dispositions",
        "control_dispositions",
        "human_judgment",
        "operator_override_rationale",
    ):
        normalized[field] = str(normalized[field])
    return normalized


def iter_scenario_dirs(evaluations_root: Path) -> Iterable[Path]:
    scenarios = evaluations_root / "scenarios"
    if not scenarios.is_dir():
        raise ValidationError(f"missing scenarios directory: {scenarios}")
    yield from sorted(path for path in scenarios.iterdir() if path.is_dir())
