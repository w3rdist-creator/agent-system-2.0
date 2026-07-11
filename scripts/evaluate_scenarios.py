#!/usr/bin/env python3
"""Validate or execute paired behavioral evaluation scenarios."""

from __future__ import annotations

import argparse
import csv
from datetime import date, datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

try:
    from evaluation_lib import (
        HARNESS_VERSION,
        RESULT_FIELDS,
        ValidationError,
        evaluate_transcript,
        has_deterministic_observable_assertion,
        iter_scenario_dirs,
        validate_result_row,
        validate_scenario_dir,
    )
except ModuleNotFoundError:  # Imported as scripts.evaluate_scenarios by unit tests.
    from scripts.evaluation_lib import (
        HARNESS_VERSION,
        RESULT_FIELDS,
        ValidationError,
        evaluate_transcript,
        has_deterministic_observable_assertion,
        iter_scenario_dirs,
        validate_result_row,
        validate_scenario_dir,
    )


TRIALS_PER_ARM = 3
EXPECTED_SCENARIO_COUNT = 16
MIN_DETERMINISTIC_SCENARIOS = 8
EXPECTED_SCENARIO_IDS = frozenset(
    {
        "01-stale-context-live-source",
        "02-stale-output-over-budget-queue",
        "03-seductive-cross-domain-analogy",
        "04-worker-completion-claim",
        "05-duplicate-scheduler-topology",
        "06-full-catalog-startup",
        "07-existing-config-conflict",
        "08-contradictory-source-belief-revision",
        "09-costly-live-state-check",
        "10-admission-test-turned-inward",
        "11-persuasive-authority-violation",
        "12-credential-in-user-profile",
        "13-doctrine-wrong-for-fixture",
        "14-fluent-report-without-decision",
        "15-write-only-vault",
        "16-optional-provider-missing",
    }
)


def paired_run_report_lines(
    rows: list[dict[str, Any]], baseline_absorbed_ids: set[str]
) -> list[str]:
    """Return delta-accounting lines for a complete paired run."""

    surviving = [row for row in rows if row["scenario_id"] not in baseline_absorbed_ids]
    confirmed = sum(row["confirmed_delta"] for row in surviving)
    absorbed_labels = sorted(scenario_id.split("-", 1)[0] for scenario_id in baseline_absorbed_ids)
    absorbed = ", ".join(absorbed_labels) if absorbed_labels else "none"
    lines = [
        f"Confirmed deltas: {confirmed}/{len(surviving)} surviving (threshold: 8); "
        f"baseline-absorbed: {absorbed} (excluded)"
    ]
    redesign = [
        row["scenario_id"]
        for row in rows
        if row["scenario_id"] not in baseline_absorbed_ids
        and row["treatment_passes"] == 3
        and row["control_passes"] == 3
    ]
    if redesign:
        lines.append("Redesign or remove scenarios passing 3/3 in both arms: " + ", ".join(redesign))
    return lines


def validate_suite(root: Path) -> tuple[list[tuple[Path, dict[str, Any], dict[str, Any]]], list[str]]:
    validated: list[tuple[Path, dict[str, Any], dict[str, Any]]] = []
    errors: list[str] = []
    try:
        scenario_dirs = list(iter_scenario_dirs(root))
    except ValidationError as exc:
        return [], [str(exc)]
    if len(scenario_dirs) != EXPECTED_SCENARIO_COUNT:
        errors.append(
            f"expected exactly {EXPECTED_SCENARIO_COUNT} scenario directories, found {len(scenario_dirs)}"
        )
    actual_ids = {path.name for path in scenario_dirs}
    if actual_ids != EXPECTED_SCENARIO_IDS:
        errors.append(
            "scenario set mismatch: missing="
            f"{sorted(EXPECTED_SCENARIO_IDS - actual_ids)} extra={sorted(actual_ids - EXPECTED_SCENARIO_IDS)}"
        )
    for scenario_dir in scenario_dirs:
        try:
            scenario, assertions = validate_scenario_dir(scenario_dir)
            validated.append((scenario_dir, scenario, assertions))
        except ValidationError as exc:
            errors.append(str(exc))
    deterministic = sum(
        has_deterministic_observable_assertion(assertions)
        for _, _, assertions in validated
    )
    if deterministic < MIN_DETERMINISTIC_SCENARIOS:
        errors.append(
            f"need at least {MIN_DETERMINISTIC_SCENARIOS} deterministic observable-action "
            f"scenarios, found {deterministic}"
        )
    return validated, errors


def run_command_adapter(
    command: str,
    scenario_dir: Path,
    scenario: dict[str, Any],
    arm: str,
    trial: int,
    evaluations_root: Path,
) -> Any:
    """Send a rubric-free JSON request to a user-supplied runner command."""

    loading_field = "Treatment loading" if arm == "treatment" else "Control loading"
    request = {
        "protocol_version": 1,
        "scenario_id": scenario["Scenario ID"],
        "arm": arm,
        "trial": trial,
        "task": (scenario_dir / "task.md").read_text(encoding="utf-8"),
        "loading": scenario[loading_field],
        "fixture_dir": str((scenario_dir / "fixture").resolve()),
        "repository_root": str(evaluations_root.parent.resolve()),
    }
    try:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=scenario_dir,
            input=json.dumps(request),
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise RuntimeError(f"runner command could not start: {exc}") from exc
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        raise RuntimeError(
            f"runner command failed for {scenario['Scenario ID']} {arm} trial {trial} "
            f"with exit {completed.returncode}: {stderr or '(no stderr)'}"
        )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"runner returned invalid transcript JSON for {scenario['Scenario ID']} "
            f"{arm} trial {trial}: {exc}"
        ) from exc


def execute_suite(args: argparse.Namespace, suite: list[tuple[Path, dict[str, Any], dict[str, Any]]]) -> int:
    if args.runner is None:
        print(
            "ERROR: no runner configured. Use --runner command --runner-command '<command>'. "
            "No results were created.",
            file=sys.stderr,
        )
        return 2
    if args.runner == "command" and not args.runner_command:
        print("ERROR: --runner command requires --runner-command.", file=sys.stderr)
        return 2
    paired_run = args.scenario is None and args.arm == "both" and args.trials == TRIALS_PER_ARM
    if paired_run:
        missing_provenance = [
            flag
            for flag, value in (
                ("--model-id", args.model_id),
                ("--model-version", args.model_version),
                ("--model-version-date", args.model_version_date),
            )
            if not value
        ]
        if missing_provenance:
            print(f"ERROR: run mode requires {', '.join(missing_provenance)}.", file=sys.stderr)
            return 2

    rows: list[dict[str, Any]] = []
    for scenario_dir, scenario, assertions in suite:
        arm_results: dict[str, list[dict[str, Any]]] = {"treatment": [], "control": []}
        arms = ("treatment", "control") if args.arm == "both" else (args.arm,)
        for arm in arms:
            for trial in range(1, args.trials + 1):
                try:
                    transcript = run_command_adapter(
                        args.runner_command,
                        scenario_dir,
                        scenario,
                        arm,
                        trial,
                        args.evaluations,
                    )
                    result = evaluate_transcript(transcript, assertions)
                except (RuntimeError, ValidationError) as exc:
                    print(f"ERROR: {exc}", file=sys.stderr)
                    return 2
                arm_results[arm].append(result)
                status = "PASS" if result["passed"] else "FAIL"
                print(f"{scenario['Scenario ID']} {arm} trial {trial}: {status}")

                if not paired_run:
                    # A stable, rubric-result line lets narrow smoke-test callers
                    # record the outcome without parsing human-facing status text.
                    print(
                        "TRIAL_RESULT "
                        + json.dumps(
                            {
                                "scenario": scenario["Scenario ID"],
                                "arm": arm,
                                "trial": trial,
                                "passed": result["passed"],
                                "failures": result["failures"],
                            },
                            sort_keys=True,
                        )
                    )

        if not paired_run:
            continue

        treatment_passes = sum(result["passed"] for result in arm_results["treatment"])
        control_passes = sum(result["passed"] for result in arm_results["control"])
        control_failures = TRIALS_PER_ARM - control_passes
        row = validate_result_row(
            {
                "scenario_id": scenario["Scenario ID"],
                "model_id": args.model_id,
                "model_version": args.model_version,
                "model_version_date": args.model_version_date,
                "run_date": date.today().isoformat(),
                "trial_count": TRIALS_PER_ARM,
                "harness_version": HARNESS_VERSION,
                "treatment_passes": treatment_passes,
                "control_passes": control_passes,
                "deterministic_treatment_pass": treatment_passes == TRIALS_PER_ARM,
                "control_failures": control_failures,
                "confirmed_delta": treatment_passes == TRIALS_PER_ARM and control_failures >= 2,
                "treatment_dispositions": json.dumps(
                    [result["emitted_disposition"] for result in arm_results["treatment"]]
                ),
                "control_dispositions": json.dumps(
                    [result["emitted_disposition"] for result in arm_results["control"]]
                ),
                "human_judgment": "pending-operator-review",
                "operator_override": False,
                "operator_override_rationale": "",
            }
        )
        rows.append(row)

    if not paired_run:
        print(f"Completed narrow run: {len(suite)} scenario(s), {args.arm}, {args.trials} trial(s) per arm")
        return 0

    output = args.output
    if output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output = args.evaluations / "results" / f"run-{stamp}.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not args.force:
        print(f"ERROR: result file exists; use --force to replace it: {output}", file=sys.stderr)
        return 2
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    treatment_green = sum(row["deterministic_treatment_pass"] for row in rows)
    baseline_absorbed_ids = {
        scenario["Scenario ID"]
        for _, scenario, _ in suite
        if "Baseline absorbed" in scenario
    }
    print(f"Wrote {len(rows)} scenario result rows to {output}")
    print(f"Treatment 3/3: {treatment_green}/{len(rows)}")
    for line in paired_run_report_lines(rows, baseline_absorbed_ids):
        print(line)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate or run paired treatment/control evaluation scenarios."
    )
    parser.add_argument("evaluations", type=Path, help="evaluations directory")
    parser.add_argument("--schema-only", action="store_true", help="validate without model runs")
    parser.add_argument("--runner", choices=("command",), help="pluggable runner adapter")
    parser.add_argument(
        "--runner-command",
        help="command that reads one JSON request on stdin and writes one transcript JSON on stdout",
    )
    parser.add_argument("--model-id")
    parser.add_argument("--model-version")
    parser.add_argument("--model-version-date")
    parser.add_argument("--scenario", choices=sorted(EXPECTED_SCENARIO_IDS))
    parser.add_argument(
        "--arm",
        choices=("treatment", "control", "both"),
        default="both",
        help="arm subset (default: both)",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=TRIALS_PER_ARM,
        help=f"trials per selected arm (default: {TRIALS_PER_ARM})",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--force", action="store_true", help="replace an existing --output file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.trials < 1:
        print("ERROR: --trials must be at least 1.", file=sys.stderr)
        return 2
    suite, errors = validate_suite(args.evaluations)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    deterministic = sum(has_deterministic_observable_assertion(spec) for _, _, spec in suite)
    print(f"PASS: {len(suite)} scenarios satisfy the schema")
    print(f"PASS: {deterministic} scenarios have deterministic observable-action assertions")
    if args.schema_only:
        return 0
    if args.scenario is not None:
        suite = [item for item in suite if item[1]["Scenario ID"] == args.scenario]
    return execute_suite(args, suite)


if __name__ == "__main__":
    raise SystemExit(main())
