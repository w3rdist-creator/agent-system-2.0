#!/usr/bin/env python3
"""Run and persist a resumable paired evaluation suite without scoring it."""

from __future__ import annotations

import argparse
import concurrent.futures as futures
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ADAPTER = Path("scripts/eval_adapter_codex.py")


def iter_jobs(root: Path, trials: int) -> Iterable[tuple[Path, dict[str, Any], str, str, int]]:
    """Yield every scenario/arm/trial request in stable order."""

    for scenario_dir in sorted((root / "evaluations" / "scenarios").iterdir()):
        manifest_path = scenario_dir / "scenario.yaml"
        if not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for arm, field in (("treatment", "Treatment loading"), ("control", "Control loading")):
            for trial in range(1, trials + 1):
                yield scenario_dir, manifest, arm, field, trial


def transcript_name(scenario_id: str, arm: str, trial: int) -> str:
    return f"{scenario_id}--{arm}--t{trial}.json"


def record_error(transcript_dir: Path, name: str, message: str) -> None:
    """Preserve a timestamped machine-readable adapter error beside transcripts."""

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = transcript_dir / f"{name[:-5]}--error-{stamp}.json"
    path.write_text(
        json.dumps({"transcript": name, "error": message}, indent=2) + "\n",
        encoding="utf-8",
    )


def run_one(
    job: tuple[Path, dict[str, Any], str, str, int],
    *,
    root: Path,
    adapter: Path,
    transcript_dir: Path,
    model: str,
    reasoning: str,
) -> tuple[str, str]:
    """Run one uncached adapter request and persist its validated JSON stdout."""

    scenario_dir, manifest, arm, field, trial = job
    name = transcript_name(scenario_dir.name, arm, trial)
    output = transcript_dir / name
    if output.is_file():
        return name, "cached"
    request = {
        "protocol_version": 1,
        "scenario_id": scenario_dir.name,
        "arm": arm,
        "trial": trial,
        "task": (scenario_dir / "task.md").read_text(encoding="utf-8"),
        "loading": manifest[field],
        "fixture_dir": str((scenario_dir / "fixture").resolve()),
        "repository_root": str(root),
    }
    try:
        completed = subprocess.run(
            [sys.executable, str(adapter)],
            input=json.dumps(request),
            text=True,
            capture_output=True,
            cwd=scenario_dir,
            env={
                **os.environ,
                "EVAL_MODEL": model,
                "EVAL_REASONING": reasoning,
            },
            check=False,
        )
    except OSError as exc:
        message = f"could not start adapter: {exc}"
        record_error(transcript_dir, name, message)
        return name, f"ERROR {message}"
    if completed.returncode != 0:
        detail = completed.stderr.strip()[-500:] or "(no stderr)"
        message = f"adapter exit {completed.returncode}: {detail}"
        record_error(transcript_dir, name, message)
        return name, f"ERROR {message}"
    try:
        transcript = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        message = f"invalid transcript JSON: {exc}"
        record_error(transcript_dir, name, message)
        return name, f"ERROR {message}"
    if not isinstance(transcript, dict) or not isinstance(transcript.get("events"), list):
        message = "transcript JSON must be an object with an events list"
        record_error(transcript_dir, name, message)
        return name, f"ERROR {message}"
    if not output.exists():
        with output.open("x", encoding="utf-8") as handle:
            json.dump(transcript, handle, indent=1, ensure_ascii=False)
            handle.write("\n")
    return name, "done"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--reasoning", required=True)
    parser.add_argument("--trials", type=int, required=True)
    parser.add_argument("--transcript-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.trials != 3 and args.trials < 10:
        print("ERROR: --trials must be 3 or at least 10 for a paired suite.", file=sys.stderr)
        return 2
    if args.workers < 1:
        print("ERROR: --workers must be at least 1.", file=sys.stderr)
        return 2
    adapter = args.adapter if args.adapter.is_absolute() else ROOT / args.adapter
    transcript_dir = (
        args.transcript_dir
        if args.transcript_dir.is_absolute()
        else ROOT / args.transcript_dir
    )
    if not adapter.is_file():
        print(f"ERROR: adapter does not exist: {adapter}", file=sys.stderr)
        return 2
    transcript_dir.mkdir(parents=True, exist_ok=True)
    jobs = list(iter_jobs(ROOT, args.trials))
    print(
        f"{len(jobs)} trials, {args.workers} workers, model={args.model} "
        f"reasoning={args.reasoning}",
        flush=True,
    )
    errors = 0
    with futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        calls = [
            executor.submit(
                run_one,
                job,
                root=ROOT,
                adapter=adapter,
                transcript_dir=transcript_dir,
                model=args.model,
                reasoning=args.reasoning,
            )
            for job in jobs
        ]
        for call in calls:
            name, status = call.result()
            print(f"{status:7} {name}", flush=True)
            errors += status.startswith("ERROR")
    replay_command = shlex.join(
        [
            "python3",
            "scripts/evaluate_scenarios.py",
            "evaluations",
            "--runner",
            "command",
            "--runner-command",
            "python3 scripts/eval_adapter_replay.py",
            "--trials",
            str(args.trials),
            "--model-id",
            args.model,
            "--model-version",
            "MODEL_VERSION",
            "--model-version-date",
            "YYYY-MM-DD",
        ]
    )
    print(f"COMPLETE errors={errors}", flush=True)
    print(
        "Score with: "
        f"EVAL_TRANSCRIPT_DIR={shlex.quote(str(transcript_dir))} {replay_command}",
        flush=True,
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
