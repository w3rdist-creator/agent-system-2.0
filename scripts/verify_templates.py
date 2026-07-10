#!/usr/bin/env python3
"""Deterministically validate all nine Release 1.0 templates and their examples."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DISPOSITIONS = {
    "act", "watch", "no-action", "no-edge", "blocked", "done", "merge",
    "defer", "kill", "needs-human", "apply", "reject", "supported",
}
HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
METADATA = re.compile(r"<!--\s*(.*?)\s*-->", re.DOTALL)


@dataclass(frozen=True)
class MarkdownSchema:
    filename: str
    headings: tuple[str, ...]


MARKDOWN_SCHEMAS = {
    "improvement-proposal": MarkdownSchema(
        "improvement-proposal.md",
        (
            "Problem observed", "Evidence", "Who should notice improvement",
            "Proposed destination", "What it replaces or merges",
            "Context, storage, and review cost", "Blast radius",
            "Verification method", "Kill or rollback condition",
            "Why a simpler location is insufficient", "Disposition",
        ),
    ),
    "loop-contract": MarkdownSchema(
        "loop-contract.md",
        (
            "Owner", "Consumer", "Trigger", "Output", "Expected heartbeat",
            "Budgets", "Blast radius", "Review cadence", "Kill condition",
            "Replacement or predecessor", "Usefulness and demand populations",
        ),
    ),
    "source-note": MarkdownSchema(
        "source-note.md",
        (
            "Source coordinate", "Source state", "Source fact",
            "Interpretation allowed", "Interpretation forbidden",
            "Next evidence required", "Declared decision authority",
            "Caveats and strongest objection", "Disposition", "Provenance links",
        ),
    ),
    "decision-packet": MarkdownSchema(
        "decision-packet.md",
        (
            "Decision ID and date", "Owner and consumer", "Decision question",
            "Evidence and uncertainty", "Authority boundary",
            "Alternatives considered", "Decision and disposition", "Decision delta",
            "Verification and rollback", "Parked-state fields",
        ),
    ),
    "belief-revision": MarkdownSchema(
        "belief-revision.md",
        (
            "Belief ID", "Prior state", "New evidence", "Revision event",
            "Current state", "Decision delta", "Standing-doctrine update rule",
            "Revision history",
        ),
    ),
    "two-layer-report": MarkdownSchema(
        "two-layer-report.md",
        (
            "Report identity", "Decision surface", "Evidence surface",
            "Verification status", "Risks and rollback", "Next review",
        ),
    ),
    "project-handoff": MarkdownSchema(
        "project-handoff.md",
        (
            "Project identity", "Objective and current state", "Completed work",
            "Decisions and rationale", "Verification evidence",
            "Open risks and blockers", "Authority and safety boundaries",
            "Next action and acceptance", "Rollback or recovery",
        ),
    ),
}

JSON_REQUIRED: dict[str, dict[str, type]] = {
    "task-packet": {
        "_template": dict, "packet_id": str, "created_at": str, "owner": str,
        "consumer": str, "objective": str, "authority": dict, "scope": dict,
        "deliverables": list, "acceptance_checks": list, "dependencies": list,
        "risks": list, "due_or_review_at": str, "return_contract": str,
    },
    "result-packet": {
        "_template": dict, "packet_id": str, "task_packet_id": str,
        "completed_at": str, "status": str, "summary": str, "artifacts": list,
        "checks": list, "deviations": list, "blockers": list,
        "next_disposition": str, "owner_review_required": bool,
    },
}


def sections(text: str) -> dict[str, str]:
    matches = list(HEADING.finditer(text))
    result: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result[match.group(1)] = text[match.end():end]
    return result


def _nonempty(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def markdown_template_errors(path: Path, name: str, schema: MarkdownSchema) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    frontmatter = FRONTMATTER.match(text)
    if not frontmatter or "license: CC BY 4.0" not in frontmatter.group(1):
        errors.append("missing CC BY 4.0 frontmatter")
    metadata_match = METADATA.search(text, frontmatter.end() if frontmatter else 0)
    metadata = metadata_match.group(1) if metadata_match else ""
    for label in ("template", "consumer", "owner", "replacement-rationale"):
        if not re.search(rf"(?m)^\s*{re.escape(label)}:\s*\S.+$", metadata):
            errors.append(f"missing header metadata: {label}")
    if not re.search(rf"(?m)^\s*template:\s*{re.escape(name)}\s*$", metadata):
        errors.append(f"template header does not identify {name}")
    parsed = sections(text)
    for heading in schema.headings:
        if heading not in parsed:
            errors.append(f"missing field: {heading}")
    return errors


def markdown_instance_errors(path: Path, schema: MarkdownSchema) -> list[str]:
    parsed = sections(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for heading in schema.headings:
        if heading not in parsed:
            errors.append(f"missing field: {heading}")
            continue
        if not COMMENT.sub("", parsed[heading]).strip():
            errors.append(f"empty field: {heading}")
    return errors


def json_packet_errors(path: Path, packet_type: str, *, template: bool) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return ["packet root must be an object"]
    errors: list[str] = []
    for key, expected in JSON_REQUIRED[packet_type].items():
        if key not in data:
            errors.append(f"missing field: {key}")
        elif not isinstance(data[key], expected):
            errors.append(f"field {key} must be {expected.__name__}")
        elif not _nonempty(data[key]):
            errors.append(f"empty field: {key}")
    meta = data.get("_template", {})
    if isinstance(meta, dict):
        for key in ("license", "template", "consumer", "owner", "replacement_rationale"):
            if not _nonempty(meta.get(key)):
                errors.append(f"missing packet template metadata: {key}")
        expected_name = packet_type if template else f"{packet_type}-example"
        if meta.get("template") != expected_name:
            errors.append(f"packet template metadata must identify {expected_name}")
        if meta.get("license") != "CC BY 4.0":
            errors.append("packet license must be CC BY 4.0")
    if packet_type == "task-packet":
        authority = data.get("authority", {})
        scope = data.get("scope", {})
        for key in ("allowed", "forbidden"):
            if not isinstance(authority.get(key), list) or not authority[key]:
                errors.append(f"authority.{key} must be a non-empty list")
        for key in ("inputs", "write_paths", "out_of_scope"):
            if not isinstance(scope.get(key), list) or not scope[key]:
                errors.append(f"scope.{key} must be a non-empty list")
    else:
        if data.get("status") not in DISPOSITIONS:
            errors.append("status must use the disposition vocabulary")
        if data.get("next_disposition") not in DISPOSITIONS:
            errors.append("next_disposition must use the disposition vocabulary")
        for index, check in enumerate(data.get("checks", [])):
            if not isinstance(check, dict):
                errors.append(f"checks[{index}] must be an object")
                continue
            for key in ("command_or_method", "outcome", "evidence"):
                if not _nonempty(check.get(key)):
                    errors.append(f"checks[{index}].{key} is required")
    return errors


def template_checks(root: Path = ROOT) -> list[tuple[Path, list[str]]]:
    checks: list[tuple[Path, list[str]]] = []
    for name, schema in MARKDOWN_SCHEMAS.items():
        path = root / "templates" / schema.filename
        errors = ["missing template"] if not path.is_file() else markdown_template_errors(path, name, schema)
        checks.append((path, errors))
    for name in JSON_REQUIRED:
        path = root / "templates" / f"{name}.json"
        errors = ["missing template"] if not path.is_file() else json_packet_errors(path, name, template=True)
        checks.append((path, errors))
    return checks


def example_checks(path: Path, root: Path = ROOT) -> list[tuple[Path, list[str]]]:
    checks: list[tuple[Path, list[str]]] = []
    base = path.resolve()
    for name, schema in MARKDOWN_SCHEMAS.items():
        candidates: list[Path] = []
        directory_example = base / name / "example.md" if base.is_dir() else Path()
        if base.is_dir() and directory_example.is_file():
            candidates.append(directory_example)
        if base.is_dir() and name in {"improvement-proposal", "loop-contract"}:
            candidates.extend(sorted(base.glob(f"{name}--*.md")))
        if base.is_file() and (base.parent.name == name or base.name.startswith(f"{name}--")):
            candidates.append(base)
        for candidate in dict.fromkeys(candidates):
            checks.append((candidate, markdown_instance_errors(candidate, schema)))
    for name in JSON_REQUIRED:
        candidate = base / name / "example.json" if base.is_dir() else base
        if candidate.is_file() and (base.is_dir() or base.parent.name == name):
            checks.append((candidate, json_packet_errors(candidate, name, template=False)))
    return checks


def validate_all(example_path: Path | None = None, root: Path = ROOT) -> list[tuple[Path, list[str]]]:
    path = example_path or root / "examples"
    checks = template_checks(root) + example_checks(path, root)
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=ROOT / "examples")
    args = parser.parse_args()
    checks = validate_all(args.path)
    failures = 0
    for path, errors in checks:
        display = path.resolve().relative_to(ROOT) if path.exists() and ROOT in path.resolve().parents else path
        if errors:
            failures += 1
            print(f"FAIL: {display}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS: {display}")
    print(f"Validated {len(checks)} template/example artifact(s); failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
