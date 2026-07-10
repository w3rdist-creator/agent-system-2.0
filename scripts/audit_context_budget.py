#!/usr/bin/env python3
"""Audit routed-context budgets with an honest four-characters/token estimate.

This approximation is ``ceil(len(text) / 4)`` on Unicode characters. It is
stable and provider-neutral, but it is not claimed to match any model's exact
tokenizer. The checked-in baseline permits growth of at most the larger of 5%
or 20 approximate tokens per tracked value; hard ceilings always take priority.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "evaluations" / "context-budget-baseline.json"
METHOD = "ceil(len(text)/4) Unicode characters per approximate token"
RELATIVE_TOLERANCE = 0.05
MINIMUM_TOLERANCE = 20
CORE_FILES = (
    "agent/SOUL.md",
    "skills/core/capability-router/SKILL.md",
    "skills/level-0-categories.yaml",
    "skills/core/evidence-first-operating-style/SKILL.md",
)
TRIGGER_LOADED_CORE_FILES = (
    "skills/core/source-grounding/SKILL.md",
    "skills/core/knowledge-metabolism/SKILL.md",
    "skills/core/loop-governance/SKILL.md",
    "skills/core/vault-operations/SKILL.md",
)
LEVEL_ZERO_PATH = "skills/level-0-categories.yaml"
LEVEL_ZERO_CEILING = 400
CORE_CEILING = 3_000


def approximate_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)


def measure_file(relative: str) -> int:
    return approximate_tokens((ROOT / relative).read_text(encoding="utf-8"))


def current_measurements() -> dict[str, object]:
    files = {relative: measure_file(relative) for relative in CORE_FILES}
    return {
        "method": METHOD,
        "regression_tolerance": {
            "relative": RELATIVE_TOLERANCE,
            "minimum_tokens": MINIMUM_TOLERANCE,
        },
        "files": files,
        "core_total": sum(files.values()),
        "hard_ceilings": {
            "level_zero": LEVEL_ZERO_CEILING,
            "core_total": CORE_CEILING,
        },
    }


def hard_limit_errors(measurements: dict[str, object]) -> list[str]:
    files = measurements["files"]
    assert isinstance(files, dict)
    errors: list[str] = []
    level_zero = files[LEVEL_ZERO_PATH]
    core_total = measurements["core_total"]
    if level_zero > LEVEL_ZERO_CEILING:
        errors.append(
            f"Level 0 is {level_zero} tokens; ceiling is {LEVEL_ZERO_CEILING}"
        )
    if core_total > CORE_CEILING:
        errors.append(f"operational core is {core_total} tokens; ceiling is {CORE_CEILING}")
    return errors


def allowed_value(baseline_value: int) -> int:
    tolerance = max(MINIMUM_TOLERANCE, math.ceil(baseline_value * RELATIVE_TOLERANCE))
    return baseline_value + tolerance


def regression_errors(
    measurements: dict[str, object], baseline: dict[str, object]
) -> list[str]:
    errors: list[str] = []
    if baseline.get("method") != METHOD:
        errors.append("baseline approximation method does not match this auditor")

    current_files = measurements["files"]
    baseline_files = baseline.get("files")
    if not isinstance(current_files, dict) or not isinstance(baseline_files, dict):
        return errors + ["baseline files table is missing or invalid"]

    for relative, current in current_files.items():
        old = baseline_files.get(relative)
        if not isinstance(old, int):
            errors.append(f"baseline is missing tracked file {relative}")
        elif current > allowed_value(old):
            errors.append(
                f"{relative} regressed from {old} to {current}; allowed maximum is "
                f"{allowed_value(old)}"
            )

    old_total = baseline.get("core_total")
    current_total = measurements["core_total"]
    if not isinstance(old_total, int):
        errors.append("baseline core_total is missing or invalid")
    elif isinstance(current_total, int) and current_total > allowed_value(old_total):
        errors.append(
            f"core_total regressed from {old_total} to {current_total}; allowed maximum is "
            f"{allowed_value(old_total)}"
        )
    return errors


def report_level_one() -> None:
    registries = sorted((ROOT / "skills" / "categories").glob("*/registry.yaml"))
    if not registries:
        print("Level 1 registries: none present (Phase 3 pending)")
        return
    print("Level 1 registry costs:")
    costs: list[tuple[int, str]] = []
    for path in registries:
        relative = str(path.relative_to(ROOT))
        cost = approximate_tokens(path.read_text(encoding="utf-8"))
        costs.append((cost, relative))
        print(f"  {relative}: {cost}")
    largest_cost, largest_path = max(costs)
    print(f"Largest Level 1 registry: {largest_path} ({largest_cost})")


def report_trigger_loaded_core() -> None:
    """Report on-demand core bodies without charging them to startup."""

    print("Trigger-loaded core costs (reported separately; excluded from startup total):")
    total = 0
    for relative in TRIGGER_LOADED_CORE_FILES:
        cost = measure_file(relative)
        total += cost
        print(f"  {relative}: {cost}")
    print(f"Trigger-loaded core total: {total}")


def print_measurements(measurements: dict[str, object]) -> None:
    print(f"Approximation: {METHOD}")
    files = measurements["files"]
    assert isinstance(files, dict)
    for relative, tokens in files.items():
        print(f"{relative}: {tokens}")
    print(f"Level 0: {files[LEVEL_ZERO_PATH]} / {LEVEL_ZERO_CEILING}")
    print(f"Operational core: {measurements['core_total']} / {CORE_CEILING}")
    print(
        "Regression tolerance: max(5% of baseline, 20 approximate tokens) per value; "
        "hard ceilings are never relaxed"
    )
    report_trigger_loaded_core()
    report_level_one()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("core",), required=True)
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="replace the checked-in baseline with current passing measurements",
    )
    args = parser.parse_args()

    try:
        measurements = current_measurements()
    except OSError as exc:
        print(f"FAIL: cannot read context artifact: {exc}", file=sys.stderr)
        return 1

    print_measurements(measurements)
    errors = hard_limit_errors(measurements)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    if args.write_baseline:
        BASELINE_PATH.write_text(
            json.dumps(measurements, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"PASS: wrote baseline {BASELINE_PATH.relative_to(ROOT)}")
        return 0

    try:
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: baseline unavailable or invalid: {exc}")
        print("Run with --write-baseline only after reviewing the current measurements.")
        return 1

    errors.extend(regression_errors(measurements, baseline))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print(f"PASS: context budgets and {BASELINE_PATH.relative_to(ROOT)} regression gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
