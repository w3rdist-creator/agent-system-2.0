#!/usr/bin/env python3
"""CLI runner contract for one completion policy decision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

try:
    from .completion import evaluate_completion
    from .guards import load_policy
except ImportError:  # Direct invocation: python3 enforcement/completion_gate.py
    from completion import evaluate_completion
    from guards import load_policy


def malformed(reason: str) -> dict[str, str]:
    return {"decision": "deny", "rule": "malformed-input", "reason": reason}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", default=str(Path(__file__).with_name("policy.yaml")))
    args = parser.parse_args()

    try:
        envelope = json.load(sys.stdin)
    except (UnicodeError, json.JSONDecodeError) as exc:
        result = malformed(f"stdin is not one JSON envelope: {exc}")
    else:
        try:
            policy = load_policy(args.policy)
        except ValueError as exc:
            result = malformed(str(exc))
        else:
            result = evaluate_completion(envelope, policy)

    json.dump(result, sys.stdout, ensure_ascii=False, sort_keys=True)
    sys.stdout.write("\n")
    if result["decision"] == "allow":
        return 0
    return 3 if result["rule"] == "malformed-input" else 2


if __name__ == "__main__":
    raise SystemExit(main())
