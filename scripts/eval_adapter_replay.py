#!/usr/bin/env python3
"""Replay runner: serve precomputed real transcripts to the evaluation harness.

Each transcript must have been produced by `scripts/eval_adapter_codex.py`
(one real model run per trial, dumped via EVAL_TRANSCRIPT_DIR). This adapter
only retrieves them so `scripts/evaluate_scenarios.py` can score and write the
certified CSV after concurrent trial execution. A missing transcript is a hard
error — nothing is ever synthesized.
"""
import json
import os
import pathlib
import sys


def main() -> int:
    dump_root = os.environ.get("EVAL_TRANSCRIPT_DIR")
    if not dump_root:
        print("EVAL_TRANSCRIPT_DIR must point at the precomputed transcripts", file=sys.stderr)
        return 1
    req = json.load(sys.stdin)
    name = f"{req['scenario_id']}--{req['arm']}--t{req['trial']}.json"
    path = pathlib.Path(dump_root) / name
    if not path.is_file():
        print(f"missing precomputed transcript: {name}", file=sys.stderr)
        return 1
    data = json.loads(path.read_text(encoding="utf-8"))
    json.dump({"events": data["events"]}, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
