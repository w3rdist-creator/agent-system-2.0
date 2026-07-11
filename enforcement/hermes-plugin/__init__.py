# SPDX-License-Identifier: MIT
# Copyright (c) 2026 contributors
"""Hermes adapter for the Evidence First enforcement policy."""

from __future__ import annotations

import importlib.util
import json
import logging
import os
from pathlib import Path
import re
import shlex
import sys
from datetime import datetime, timezone
from typing import Any


logger = logging.getLogger(__name__)


def _hermes_home() -> Path:
    """Resolve the active, profile-aware Hermes home with a standalone fallback."""
    try:
        from hermes_constants import get_hermes_home

        return Path(get_hermes_home()).expanduser().resolve()
    except Exception:
        configured = os.environ.get("HERMES_HOME")
        return Path(configured or "~/.hermes").expanduser().resolve()


PLUGIN_DIR = Path(__file__).resolve().parent
HERMES_HOME = _hermes_home()
ENFORCEMENT_DIR = HERMES_HOME / "distributions/evidence-first/enforcement"
POLICY_PATH = ENFORCEMENT_DIR / "policy.yaml"
LOG_PATH = PLUGIN_DIR / "enforcement-log.jsonl"
VAULT_PATH_FILE = PLUGIN_DIR / "vault-path.txt"
_DISABLED_WARNING = (
    "[evidence-first] WARNING: enforcement disabled because the installed policy "
    "or vault path could not be loaded"
)


def _resolve_vault_path() -> Path:
    configured = os.environ.get("EVIDENCE_FIRST_VAULT", "").strip()
    if not configured:
        try:
            configured = VAULT_PATH_FILE.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise ValueError("vault path is not configured") from exc
    if not configured:
        raise ValueError("vault path is empty")
    expanded = os.path.expandvars(configured)
    return Path(expanded).expanduser().resolve()


def _load_installed_module(module_name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load installed enforcement module: {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_guards = None
_completion = None
_policy = None
_vault_path = None
_init_error: str | None = None

try:
    _vault_path = _resolve_vault_path()
    _guards = _load_installed_module(
        "evidence_first_installed_guards", ENFORCEMENT_DIR / "guards.py"
    )
    _completion = _load_installed_module(
        "evidence_first_installed_completion", ENFORCEMENT_DIR / "completion.py"
    )
    _policy = _guards.load_policy(POLICY_PATH)
except Exception as exc:  # pragma: no cover - exercised only by a broken installation
    _init_error = f"{type(exc).__name__}: {exc}"
    # A broken installation must be conspicuous, but must not brick every tool
    # call in the operator's agent. Actual policy verdicts below always act.
    logger.critical("%s (%s)", _DISABLED_WARNING, _init_error, exc_info=True)


_DISPOSITION_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:#{1,6}\s*)?(?:\*\*)?disposition(?:\*\*)?"
    r"\s*(?::|[-—])(?:\*\*)?\s*(?:\*\*|`)?"
    r"(act|watch|no-action|blocked|done|kill|needs-human|merge|defer|no-edge)\b"
)
_MUTATING_SHELL_RE = re.compile(
    r"(?:^|\s)\d*>>?(?!=)|(?:^|[;&|]\s*)(?:rm|mv|cp|mkdir|touch|install|truncate|tee|"
    r"sed\s+-i|perl\s+-i|chmod|chown|ln)\b"
)
_RAW_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:\$\{HOME\}|\$HOME|~|/)[^\s'\";|&<>]+"
)
_PATCH_PATH_RE = re.compile(
    r"(?m)^\*\*\* (?:Add|Update|Delete) File:\s*(.+?)\s*$"
)


def _append_telemetry(session_id: str, tool: str, rule: str) -> None:
    """Append the intentionally small, secret-free heartbeat record."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id or "",
        "tool": tool,
        "rule": rule,
    }
    try:
        with LOG_PATH.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, separators=(",", ":")) + "\n")
    except Exception as exc:
        logger.debug("evidence-first telemetry append failed: %s", exc, exc_info=True)


def _shell_path_candidates(command: str) -> list[str]:
    candidates: list[str] = []
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        tokens = []
    tokens.extend(match.group(0) for match in _RAW_PATH_RE.finditer(command))
    for token in tokens:
        value = token.strip("(),[]{}")
        if value.startswith(("/", "~/", "$HOME/", "${HOME}/")):
            value = value.replace("${HOME}", str(Path.home()), 1)
            value = os.path.expandvars(os.path.expanduser(value))
            if value not in candidates:
                candidates.append(value)
    return candidates


def _guard_envelope(tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Map Hermes write surfaces to terms and path keys understood by guards.py."""
    mapped_tool = tool_name
    mapped_args = dict(args)

    if tool_name == "patch":
        mapped_tool = "edit"
        patch_text = args.get("patch")
        if isinstance(patch_text, str):
            paths = [match.group(1) for match in _PATCH_PATH_RE.finditer(patch_text)]
            if paths:
                mapped_args["_evidence_first_paths"] = paths
    elif tool_name == "terminal":
        command = args.get("command")
        if isinstance(command, str) and _MUTATING_SHELL_RE.search(command):
            mapped_tool = "write_terminal"
            paths = _shell_path_candidates(command)
            if paths:
                mapped_args["_evidence_first_paths"] = paths

    return {"tool": mapped_tool, "args": mapped_args}


def pre_tool_call(**kwargs: Any) -> dict[str, str] | None:
    if _policy is None or _guards is None or _vault_path is None:
        return None
    tool_name = kwargs.get("tool_name")
    args = kwargs.get("args")
    if not isinstance(tool_name, str) or not isinstance(args, dict):
        return None
    try:
        result = _guards.evaluate(
            _guard_envelope(tool_name, args),
            _policy,
            {"hermes_home": str(HERMES_HOME), "vault": str(_vault_path)},
        )
    except Exception as exc:
        logger.debug("evidence-first evaluation failed: %s", exc, exc_info=True)
        return None
    if result.get("decision") != "deny":
        return None
    rule = str(result.get("rule") or "unspecified-rule")
    reason = str(result.get("reason") or "policy denied this tool call")
    _append_telemetry(str(kwargs.get("session_id") or ""), tool_name, rule)
    return {
        "action": "block",
        "message": f"[evidence-first] blocked by {rule}: {reason}",
    }


def _extract_disposition(response_text: str) -> str | None:
    match = _DISPOSITION_RE.search(response_text)
    return match.group(1).lower() if match else None


def transform_llm_output(**kwargs: Any) -> str | None:
    response_text = kwargs.get("response_text")
    if not isinstance(response_text, str) or not response_text:
        return None
    if _policy is None or _completion is None:
        _append_telemetry(
            str(kwargs.get("session_id") or ""),
            "transform_llm_output",
            "policy-unreadable",
        )
        return response_text + "\n\n" + _DISABLED_WARNING

    disposition = _extract_disposition(response_text)
    if disposition is None:
        return None
    try:
        result = _completion.evaluate_completion(
            {"disposition": disposition, "content": response_text}, _policy
        )
    except Exception as exc:
        logger.debug("evidence-first completion evaluation failed: %s", exc, exc_info=True)
        return None
    if result.get("decision") != "deny" or result.get("rule") != "parked-state-surface":
        return None

    rule = "parked-state-surface"
    _append_telemetry(
        str(kwargs.get("session_id") or ""), "transform_llm_output", rule
    )
    annotation = (
        "[evidence-first] parked-state surface missing: include both "
        "state_change_condition/trigger and review_or_decay_date."
    )
    return response_text + "\n\n" + annotation


def on_session_start(**kwargs: Any) -> None:
    if _init_error is not None:
        logger.critical("%s (%s)", _DISABLED_WARNING, _init_error)
        print(_DISABLED_WARNING, file=sys.stderr, flush=True)


def register(ctx: Any) -> None:
    ctx.register_hook("pre_tool_call", pre_tool_call)
    ctx.register_hook("transform_llm_output", transform_llm_output)
    ctx.register_hook("on_session_start", on_session_start)
