#!/usr/bin/env python3
"""Run narrow live evaluation smoke checks and append honest recert rows."""

from __future__ import annotations

import argparse
import csv
from datetime import date
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVALUATIONS = ROOT / "evaluations"
HARNESS = ROOT / "scripts" / "evaluate_scenarios.py"
ADAPTER = ROOT / "scripts" / "eval_adapter_codex.py"
LOG = EVALUATIONS / "results" / "recert-log.csv"
FIELDS = ("date", "scenario", "model", "reasoning", "arm", "result", "failure_reason")
TRIAL_PREFIX = "TRIAL_RESULT "


def scenario_ids() -> list[str]:
    return sorted(path.name for path in (EVALUATIONS / "scenarios").iterdir() if path.is_dir())


def codex_defaults() -> dict[str, Any]:
    config = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "config.toml"
    if not config.is_file():
        return {}
    try:
        import tomllib

        with config.open("rb") as handle:
            parsed = tomllib.load(handle)
        return parsed if isinstance(parsed, dict) else {}
    except (ImportError, OSError, ValueError):
        # Python versions without tomllib still support the two top-level
        # scalar keys needed here. Stop at the first TOML table.
        values: dict[str, str] = {}
        pattern = re.compile(r'^\s*(model|model_reasoning_effort)\s*=\s*["\']([^"\']+)["\']\s*(?:#.*)?$')
        for line in config.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lstrip().startswith("["):
                break
            match = pattern.match(line)
            if match:
                values[match.group(1)] = match.group(2)
        return values


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="recert.sh",
        usage="recert.sh [--scenario ID] [--model MODEL] [--reasoning EFFORT] [--full]",
        description="Run a treatment-arm recertification smoke check.",
    )
    parser.add_argument("--scenario")
    parser.add_argument("--model")
    parser.add_argument("--reasoning")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    if args.full and args.scenario:
        parser.error("--full and --scenario cannot be combined")
    return args


def append_row(path: Path, row: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    if exists:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
        if header != list(FIELDS):
            raise RuntimeError(f"recert log header does not match the required schema: {path}")
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def failure_message(completed: subprocess.CompletedProcess[str]) -> str:
    lines = [line.strip() for line in completed.stderr.splitlines() if line.strip()]
    if lines:
        return lines[-1].removeprefix("ERROR: ")
    return f"evaluation harness exited {completed.returncode} without an error message"


def run_trial(scenario: str, model: str, reasoning: str, runner: str) -> dict[str, str]:
    env = {**os.environ, "EVAL_MODEL": model, "EVAL_REASONING": reasoning}
    command = [
        sys.executable,
        str(HARNESS),
        str(EVALUATIONS),
        "--scenario",
        scenario,
        "--arm",
        "treatment",
        "--trials",
        "1",
        "--runner",
        "command",
        "--runner-command",
        runner,
    ]
    completed = subprocess.run(command, text=True, capture_output=True, env=env, cwd=ROOT)
    if completed.returncode != 0:
        return {"result": "error", "failure_reason": failure_message(completed)}

    records = []
    for line in completed.stdout.splitlines():
        if line.startswith(TRIAL_PREFIX):
            try:
                records.append(json.loads(line[len(TRIAL_PREFIX) :]))
            except json.JSONDecodeError as exc:
                return {"result": "error", "failure_reason": f"invalid harness trial result: {exc}"}
    if len(records) != 1:
        return {
            "result": "error",
            "failure_reason": f"harness emitted {len(records)} trial results; expected exactly 1",
        }
    record = records[0]
    if record.get("scenario") != scenario or record.get("arm") != "treatment":
        return {"result": "error", "failure_reason": "harness trial identity did not match request"}
    failures = record.get("failures", [])
    if record.get("passed") is True:
        return {"result": "pass", "failure_reason": ""}
    if not isinstance(failures, list):
        failures = ["harness returned malformed failure detail"]
    return {"result": "fail", "failure_reason": "; ".join(str(item) for item in failures)}


def main() -> int:
    args = parse_args()
    defaults = codex_defaults()
    model = args.model or os.environ.get("EVAL_MODEL") or defaults.get("model")
    reasoning = (
        args.reasoning
        or os.environ.get("EVAL_REASONING")
        or defaults.get("model_reasoning_effort")
        or "low"
    )
    if not isinstance(model, str) or not model.strip():
        print(
            "ERROR: no Codex default model found; set it in ~/.codex/config.toml, "
            "EVAL_MODEL, or --model",
            file=sys.stderr,
        )
        return 2
    model = model.strip()
    reasoning = str(reasoning).strip()

    available = scenario_ids()
    if len(available) != 16:
        print(f"ERROR: expected 16 scenario directories, found {len(available)}", file=sys.stderr)
        return 2
    if args.scenario and args.scenario not in available:
        print(f"ERROR: unknown scenario: {args.scenario}", file=sys.stderr)
        return 2
    today = date.today()
    if args.full:
        selected = available
    elif args.scenario:
        selected = [args.scenario]
    else:
        selected = [available[(today.timetuple().tm_yday - 1) % len(available)]]

    runner = os.environ.get("EVAL_RUNNER_COMMAND")
    if not runner:
        runner = shlex.join([sys.executable, str(ADAPTER)])
    log_path = Path(os.environ.get("RECERT_LOG", LOG))
    passed = 0
    for scenario in selected:
        outcome = run_trial(scenario, model, reasoning, runner)
        row = {
            "date": today.isoformat(),
            "scenario": scenario,
            "model": model,
            "reasoning": reasoning,
            "arm": "treatment",
            **outcome,
        }
        try:
            append_row(log_path, row)
        except (OSError, RuntimeError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        if outcome["result"] == "pass":
            passed += 1
        else:
            print(f"{scenario}: {outcome['result'].upper()}: {outcome['failure_reason']}", file=sys.stderr)

    print(f"RECERT: {passed}/{len(selected)} passed ({model}, {today.isoformat()})")
    return 0 if passed == len(selected) else 1


if __name__ == "__main__":
    raise SystemExit(main())
