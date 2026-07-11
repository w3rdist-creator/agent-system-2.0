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

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from enforcement.guards import evaluate as evaluate_guard
from enforcement.guards import load_policy as load_guard_policy
from enforcement.completion import evaluate_completion


def enforce_events(events: list[dict], request: dict) -> list[dict]:
    """Apply opt-in tool and completion checks to replayed model events."""

    policy = load_guard_policy(REPO_ROOT / "enforcement" / "policy.yaml")
    context = {
        "hermes_home": os.environ.get("HERMES_HOME", str(pathlib.Path.home() / ".hermes")),
        "vault": str(request.get("fixture_dir", pathlib.Path.cwd())),
    }
    guarded = []
    answer = None
    for event in events:
        if event.get("type") == "answer" and isinstance(event.get("content"), str):
            answer = event["content"]
            guarded.append(event)
            continue
        if event.get("type") == "disposition" and isinstance(event.get("label"), str):
            guarded.append(event)
            if answer is not None:
                completion = evaluate_completion(
                    {"content": answer, "disposition": event["label"]}, policy
                )
                if completion["decision"] == "deny":
                    guarded.append(
                        {"type": "completion_denied", "rule": completion["rule"]}
                    )
            continue
        if event.get("type") != "tool_call":
            guarded.append(event)
            continue
        result = evaluate_guard(
            {"tool": event.get("tool"), "args": event.get("args", {})}, policy, context
        )
        if result["decision"] == "deny":
            guarded.append(
                {
                    "type": "guard_denied",
                    "tool": event.get("tool"),
                    "rule": result["rule"],
                }
            )
        else:
            guarded.append(event)
    return guarded


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
    events = data["events"]
    if os.environ.get("EVAL_ENFORCE") == "1":
        events = enforce_events(events, req)
    json.dump({"events": events}, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
