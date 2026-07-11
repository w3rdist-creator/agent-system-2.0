#!/usr/bin/env python3
"""Pure-standard-library completion policy evaluation."""

from __future__ import annotations

import re
from typing import Any


def verdict(decision: str, rule: str | None, reason: str) -> dict[str, str | None]:
    return {"decision": decision, "rule": rule, "reason": reason}


def _malformed(reason: str) -> dict[str, str | None]:
    return verdict("deny", "malformed-input", reason)


def _completion_policy(policy: Any) -> tuple[set[str], dict[str, str], set[str], list[str]]:
    if not isinstance(policy, dict):
        raise ValueError("policy must be an object")
    completion = policy.get("completion")
    if not isinstance(completion, dict):
        raise ValueError("completion must be an object")

    dispositions = completion.get("dispositions")
    aliases = completion.get("legacy_aliases")
    parked = completion.get("parked_dispositions")
    patterns = completion.get("parked_state_patterns")
    if not isinstance(dispositions, list) or not dispositions or not all(
        isinstance(item, str) and item for item in dispositions
    ):
        raise ValueError("completion dispositions must be a non-empty string list")
    if not isinstance(aliases, dict) or not all(
        isinstance(alias, str)
        and alias
        and isinstance(canonical, str)
        and canonical in dispositions
        for alias, canonical in aliases.items()
    ):
        raise ValueError("completion legacy_aliases must map strings to dispositions")
    if not isinstance(parked, list) or not all(item in dispositions for item in parked):
        raise ValueError("completion parked_dispositions must contain only dispositions")
    if not isinstance(patterns, dict) or set(patterns) != {
        "state_change_or_trigger",
        "decay_or_review_date",
    } or not all(isinstance(pattern, str) and pattern for pattern in patterns.values()):
        raise ValueError("completion parked_state_patterns must contain both required patterns")

    ordered_patterns = [
        patterns["state_change_or_trigger"],
        patterns["decay_or_review_date"],
    ]
    for pattern in ordered_patterns:
        re.compile(pattern)
    return set(dispositions), aliases, set(parked), ordered_patterns


def evaluate_completion(envelope: dict, policy: dict) -> dict[str, str | None]:
    """Return an allow/deny verdict for one final-answer envelope."""

    try:
        if not isinstance(envelope, dict) or set(envelope) != {"disposition", "content"}:
            return _malformed("envelope must contain exactly disposition and content")
        disposition = envelope.get("disposition")
        content = envelope.get("content")
        if not isinstance(disposition, str) or not disposition or not isinstance(content, str):
            return _malformed("disposition must be a non-empty string and content must be a string")
        dispositions, aliases, parked, patterns = _completion_policy(policy)
    except (TypeError, ValueError, re.error) as exc:
        return _malformed(f"policy is invalid: {exc}")

    normalized = aliases.get(disposition, disposition)
    if normalized not in dispositions:
        return _malformed("disposition is not a canonical label or legacy alias")
    if normalized in parked and not all(re.search(pattern, content) for pattern in patterns):
        return verdict(
            "deny",
            "parked-state-surface",
            "parked disposition requires state-change/trigger and decay/review-date surfaces",
        )
    return verdict("allow", None, "no completion rule matched")
