#!/usr/bin/env python3
"""Pure-standard-library pre-tool-use policy evaluation."""

from __future__ import annotations

import fnmatch
import json
import os
from pathlib import Path
import re
from typing import Any, Iterable


WRITE_SEMANTICS = frozenset(
    {"append", "copy", "create", "delete", "edit", "mkdir", "move", "remove", "rename", "unlink", "write"}
)
PATH_KEYS = frozenset(
    {"destination", "directory", "dir", "file", "filename", "path", "source", "src", "target", "to"}
)
LIMIT_KEYS = frozenset({"limit", "max_results", "result_limit", "top_k"})


def verdict(decision: str, rule: str | None, reason: str) -> dict[str, str | None]:
    return {"decision": decision, "rule": rule, "reason": reason}


def _malformed(reason: str) -> dict[str, str | None]:
    return verdict("deny", "malformed-input", reason)


def load_policy(path: str | Path) -> dict[str, Any]:
    """Load a JSON-form YAML policy, raising a non-secret-bearing ValueError."""

    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"policy is unreadable or invalid: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("policy top level must be an object")
    return data


def _tool_terms(name: str) -> set[str]:
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return {term for term in re.split(r"[^A-Za-z0-9]+", expanded.lower()) if term}


def _is_write_tool(name: str) -> bool:
    return bool(_tool_terms(name) & WRITE_SEMANTICS)


def _normalized_key(key: Any) -> str:
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(key))
    return re.sub(r"[^a-z0-9]+", "_", expanded.lower()).strip("_")


def _walk_args(
    value: Any, keys: frozenset[str], suffixes: tuple[str, ...] = ()
) -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = _normalized_key(key)
            if normalized in keys or normalized.endswith(suffixes):
                yield normalized, nested
            yield from _walk_args(nested, keys, suffixes)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk_args(nested, keys, suffixes)


def _lexical_path(raw: str, context: dict[str, Any]) -> str:
    substituted = raw
    for placeholder, key in (("<hermes-home>", "hermes_home"), ("<vault>", "vault")):
        value = context.get(key)
        if isinstance(value, str) and value:
            substituted = substituted.replace(placeholder, value)
    substituted = os.path.expanduser(substituted)
    if not os.path.isabs(substituted):
        base = context.get("vault")
        if not isinstance(base, str) or not base:
            base = os.getcwd()
        substituted = os.path.join(base, substituted)
    return os.path.normpath(os.path.abspath(substituted))


def _protected_patterns(policy: dict[str, Any], context: dict[str, Any]) -> list[str]:
    raw_patterns = policy.get("protected_paths")
    if not isinstance(raw_patterns, list) or not all(isinstance(item, str) for item in raw_patterns):
        raise ValueError("protected_paths must be a string list")
    required = {
        "<hermes-home>": context.get("hermes_home"),
        "<vault>": context.get("vault"),
    }
    patterns = []
    for raw in raw_patterns:
        pattern = raw
        for placeholder, value in required.items():
            if placeholder in pattern:
                if not isinstance(value, str) or not value:
                    raise ValueError(f"context is missing {placeholder[1:-1].replace('-', '_')}")
                pattern = pattern.replace(placeholder, value)
        patterns.append(os.path.normpath(os.path.abspath(os.path.expanduser(pattern))))
    return patterns


def _matches_protected(path: str, pattern: str) -> bool:
    if pattern.endswith(os.sep + "**"):
        root = pattern[: -len(os.sep + "**")]
        return path == root or path.startswith(root + os.sep)
    return fnmatch.fnmatchcase(path, pattern)


def _validate_policy(policy: Any) -> tuple[dict[str, str], int]:
    if not isinstance(policy, dict):
        raise ValueError("policy must be an object")
    credential_patterns = policy.get("credential_patterns")
    caps = policy.get("caps")
    if not isinstance(credential_patterns, dict) or not all(
        isinstance(name, str) and isinstance(pattern, str)
        for name, pattern in credential_patterns.items()
    ):
        raise ValueError("credential_patterns must map names to regex strings")
    if not isinstance(caps, dict):
        raise ValueError("caps must be an object")
    default_cap = caps.get("default_retrieval_limit")
    if isinstance(default_cap, bool) or not isinstance(default_cap, int) or default_cap < 0:
        raise ValueError("default_retrieval_limit must be a non-negative integer")
    for pattern in credential_patterns.values():
        re.compile(pattern)
    return credential_patterns, default_cap


def evaluate(envelope: dict, policy: dict, context: dict) -> dict[str, str | None]:
    """Return an allow/deny verdict for one tool-call envelope.

    The guard covers only protected writes, credential echo, and retrieval caps.
    It is deliberately not a general permission system.
    """

    try:
        if not isinstance(envelope, dict) or set(envelope) != {"tool", "args"}:
            return _malformed("envelope must contain exactly tool and args")
        tool = envelope.get("tool")
        args = envelope.get("args")
        if not isinstance(tool, str) or not tool or not isinstance(args, dict):
            return _malformed("envelope tool must be a non-empty string and args must be an object")
        if not isinstance(context, dict):
            return _malformed("context must be an object")
        credential_patterns, default_cap = _validate_policy(policy)
        protected = _protected_patterns(policy, context)
    except (TypeError, ValueError, re.error) as exc:
        return _malformed(f"policy or context is invalid: {exc}")

    serialized = json.dumps(args, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for name, pattern in credential_patterns.items():
        if re.search(pattern, serialized):
            return verdict("deny", f"credential-echo:{name}", f"arguments match credential rule {name}")

    if _is_write_tool(tool):
        for _, raw in _walk_args(
            args, PATH_KEYS, ("_path", "_paths", "_file", "_dir", "_directory")
        ):
            values = raw if isinstance(raw, list) else [raw]
            for value in values:
                if not isinstance(value, str):
                    continue
                candidate = _lexical_path(value, context)
                if any(_matches_protected(candidate, pattern) for pattern in protected):
                    return verdict(
                        "deny",
                        "protected-path-write",
                        "write-class tool targets a protected path",
                    )

    declared = context.get("declared_cap")
    if declared is None:
        cap = default_cap
    elif isinstance(declared, bool) or not isinstance(declared, int) or declared < 0:
        return _malformed("declared_cap must be a non-negative integer")
    else:
        cap = declared
    for key, value in _walk_args(args, LIMIT_KEYS, ("_limit",)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if value > cap:
            return verdict(
                "deny",
                "retrieval-cap",
                f"requested {key} {value} exceeds approved cap {cap}",
            )

    return verdict("allow", None, "no enforced rule matched")
