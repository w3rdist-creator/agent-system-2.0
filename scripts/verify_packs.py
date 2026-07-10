#!/usr/bin/env python3
"""Validate the Phase 5 pack manifest, pack contracts, seed provenance, and examples."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re
import sys

try:
    from .verify_templates import json_packet_errors
except ImportError:  # Direct script execution.
    from verify_templates import json_packet_errors


PACK_NAMES = (
    "research",
    "agent-ops",
    "context-spine",
    "deep-timeline",
    "markets-research-only",
    "product-os",
    "personal-os",
    "learning-os",
    "software-delivery",
    "simulation-lab",
)
SHIPPED = {"research", "agent-ops"}
INERT = set(PACK_NAMES) - SHIPPED
INERT_FIELDS = (
    "Purpose",
    "Source paths and pinned commits",
    "Known useful mechanisms",
    "Missing consumer evidence",
    "Activation trigger",
    "Owner if activated",
    "Expected review cost",
    "Seed-content source requirement",
    "Kill condition",
)
PATTERN_HEADINGS = (
    "Observations in two independently sourced domains",
    "Explicit causal mechanism",
    "Falsifiable prediction",
    "Strongest objection and rival explanation",
    "Strategic-interaction and Goodhart check",
    "Creative-to-empirical firewall",
    "Constructive counterweight",
    "Non-applicability",
    "Provenance",
    "Disposition and decision delta",
)
PATTERN_METADATA = (
    "license",
    "type",
    "pattern_id",
    "status",
    "source_rows",
    "domain_a",
    "domain_b",
    "reviewed_at",
    "reviewed_by",
)
CORE_PATHS = (
    "research/vault/Research/Queues/Source Queue.md",
    "research/vault/Raw/Research/Source Snapshot - Source to Synthesis.md",
    "research/vault/Raw/Research/Source Snapshot - Loop Scoreboard.md",
    "research/vault/Research/Sources/Source Note - Source to Synthesis.md",
    "research/vault/Research/Sources/Source Note - Loop Scoreboard.md",
    "research/vault/Research/Ledgers/Claim Evidence Ledger.csv",
    "research/vault/Research/Patterns/Pattern Note Template.md",
    "research/vault/Research/Patterns/Pattern - Bounded Selection Pressure.md",
    "research/vault/Research/Reviews/Review - Bounded Selection Pressure.md",
    "research/vault/Research/System/Search Merge and Non-Connection Rule.md",
    "agent-ops/vault/Agent Ops/System/Health Usefulness Governance Scorecard.md",
    "agent-ops/vault/Agent Ops/Queues/Resolve Queue.md",
    "agent-ops/vault/Agent Ops/System/Verification Gate.md",
    "agent-ops/vault/Agent Ops/System/Single Scheduler Ownership.md",
    "agent-ops/vault/Agent Ops/Packets/Task Packet - Scheduler Review.json",
    "agent-ops/vault/Agent Ops/Packets/Result Packet - Scheduler Review.json",
    "agent-ops/vault/Agent Ops/Ledgers/Loop Scoreboard.csv",
    "agent-ops/vault/Agent Ops/Reports/Two-Layer Report - Scheduler Review.md",
    "agent-ops/vault/Agent Ops/Reviews/Review - Single Scheduler Seed.md",
)
DEFERRABLE_PATHS = (
    "research/vault/Research/Methods/Strategic Interaction and Goodhart Check.md",
    "research/vault/Research/System/Creative-to-Empirical Firewall.md",
    "research/vault/Research/Reviews/Constructive Counterweight Template.md",
    "research/vault/Research/Ledgers/Citation Use Log.csv",
    "agent-ops/vault/Agent Ops/Ledgers/Prediction Calibration Ledger.csv",
    "agent-ops/vault/Agent Ops/Ledgers/Operator Correction Ledger.csv",
    "agent-ops/vault/Agent Ops/Reviews/Failure Review Template.md",
)
SOURCE_NOTE_FIELDS = (
    "Source fact",
    "Interpretation allowed",
    "Interpretation forbidden",
    "Next evidence required",
    "Declared decision authority",
)
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def _frontmatter_json(text: str) -> dict[str, object] | None:
    match = FRONTMATTER.match(text)
    if not match:
        return None
    raw = match.group(1).strip()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _section_bodies(text: str) -> dict[str, str]:
    matches = list(HEADING.finditer(text))
    return {
        match.group(1): text[match.end() : matches[index + 1].start() if index + 1 < len(matches) else len(text)].strip()
        for index, match in enumerate(matches)
    }


def validate_pattern_note(path: Path, *, template: bool) -> list[str]:
    if not path.is_file():
        return ["missing pattern artifact"]
    text = path.read_text(encoding="utf-8")
    metadata = _frontmatter_json(text)
    errors: list[str] = []
    if metadata is None:
        errors.append("pattern frontmatter must be one JSON object")
    else:
        for field in PATTERN_METADATA:
            value = metadata.get(field)
            if value in (None, "", []):
                errors.append(f"missing pattern metadata: {field}")
        if metadata.get("license") != "CC BY 4.0":
            errors.append("pattern license must be CC BY 4.0")
        rows = metadata.get("source_rows")
        if not isinstance(rows, list) or len(rows) < 2:
            errors.append("pattern must name at least two source rows")
        elif not template and len({str(row).split(":", 1)[0] for row in rows}) < 2:
            errors.append("pattern example must use two independently sourced repositories")
    sections = _section_bodies(text)
    for heading in PATTERN_HEADINGS:
        if heading not in sections:
            errors.append(f"missing pattern field: {heading}")
        elif not sections[heading]:
            errors.append(f"empty pattern field: {heading}")
    return errors


def _ledger_rows(root: Path) -> dict[str, dict[str, str]]:
    path = root / "source-packages" / "public-file-dispositions.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {f"{row['source_repo']}:{row['source_path']}": row for row in rows}


def _seed_provenance_errors(root: Path, accepted: set[str]) -> tuple[list[str], int]:
    errors: list[str] = []
    checked = 0
    for pack in SHIPPED:
        for path in sorted((root / "packs" / pack).rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".md", ".json"}:
                continue
            text = path.read_text(encoding="utf-8")
            marked = bool(re.search(r'(?m)^seed:\s*true\s*$', text))
            if path.suffix.lower() == ".md":
                metadata = _frontmatter_json(text)
                if metadata is not None:
                    marked = metadata.get("seed") is True
            if path.suffix.lower() == ".json":
                try:
                    marked = json.loads(text).get("seed") is True
                except (json.JSONDecodeError, AttributeError):
                    pass
            if not marked:
                continue
            checked += 1
            coordinates = sorted(coordinate for coordinate in accepted if coordinate in text)
            if not coordinates:
                errors.append(f"{path.relative_to(root)}: seed artifact has no accepted source row")
    return errors, checked


def _csv_source_errors(path: Path, accepted: set[str]) -> list[str]:
    errors: list[str] = []
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or "source_rows" not in (rows[0].keys() if rows else ()):
        return [f"{path}: missing source_rows column or seed row"]
    for line, row in enumerate(rows, 2):
        coordinates = [item.strip() for item in row.get("source_rows", "").split(";") if item.strip()]
        if not coordinates:
            errors.append(f"{path}:{line}: no source rows")
        for coordinate in coordinates:
            if coordinate not in accepted:
                errors.append(f"{path}:{line}: source row is absent or non-shipping: {coordinate}")
    return errors


def validate_packs(root: Path) -> tuple[list[str], dict[str, int]]:
    root = root.resolve()
    pack_root = root / "packs"
    errors: list[str] = []
    stats = {"packs": 0, "seed_artifacts": 0, "patterns": 0}

    manifest_path = pack_root / "manifest.yaml"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        manifest = {}
        errors.append(f"packs/manifest.yaml: must be JSON-compatible YAML: {exc}")
    entries = manifest.get("packs", {}) if isinstance(manifest, dict) else {}
    if not isinstance(entries, dict):
        entries = {}
        errors.append("packs/manifest.yaml: packs must be an object")
    if set(entries) != set(PACK_NAMES):
        errors.append(f"packs/manifest.yaml: expected exactly {len(PACK_NAMES)} named packs")
    for name in PACK_NAMES:
        entry = entries.get(name, {})
        expected = "shipped" if name in SHIPPED else "inert"
        if not isinstance(entry, dict) or entry.get("status") != expected:
            errors.append(f"packs/manifest.yaml: {name} must have status {expected}")
            continue
        for field in ("owner", "activation_trigger", "kill_condition"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                errors.append(f"packs/manifest.yaml: {name} missing {field}")
        stats["packs"] += 1
    corpus = manifest.get("corpus", {}) if isinstance(manifest, dict) else {}
    if not isinstance(corpus, dict) or corpus.get("disposition") != "contract-only":
        errors.append("packs/manifest.yaml: corpus disposition must be contract-only")

    for name in PACK_NAMES:
        pack_file = pack_root / name / "PACK.md"
        if not pack_file.is_file():
            errors.append(f"packs/{name}/PACK.md: missing")
            continue
        text = pack_file.read_text(encoding="utf-8")
        if name in INERT:
            for field in INERT_FIELDS:
                if not re.search(rf"(?m)^- \*\*{re.escape(field)}:\*\*\s+\S", text):
                    errors.append(f"packs/{name}/PACK.md: missing inert field {field}")

    for relative in CORE_PATHS + DEFERRABLE_PATHS:
        if not (pack_root / relative).is_file():
            errors.append(f"packs/{relative}: missing required Phase 5 artifact")

    for name in SHIPPED:
        if not (pack_root / name / "vault").is_dir():
            errors.append(f"packs/{name}: missing installable vault payload")

    rows = _ledger_rows(root)
    accepted = {
        coordinate for coordinate, row in rows.items()
        if row.get("disposition") in {"copy", "adapt", "merge"}
    }
    provenance_errors, seed_count = _seed_provenance_errors(root, accepted)
    errors.extend(provenance_errors)
    stats["seed_artifacts"] = seed_count
    for relative in (
        "research/vault/Research/Ledgers/Claim Evidence Ledger.csv",
        "agent-ops/vault/Agent Ops/Ledgers/Loop Scoreboard.csv",
    ):
        path = pack_root / relative
        if path.is_file():
            errors.extend(_csv_source_errors(path, accepted))

    source_notes = (
        pack_root / "research/vault/Research/Sources/Source Note - Source to Synthesis.md",
        pack_root / "research/vault/Research/Sources/Source Note - Loop Scoreboard.md",
    )
    for path in source_notes:
        if not path.is_file():
            continue
        sections = _section_bodies(path.read_text(encoding="utf-8"))
        for field in SOURCE_NOTE_FIELDS:
            if not sections.get(field, "").strip():
                errors.append(f"{path.relative_to(root)}: missing or empty authority field {field}")

    for relative, template in (
        ("research/vault/Research/Patterns/Pattern Note Template.md", True),
        ("research/vault/Research/Patterns/Pattern - Bounded Selection Pressure.md", False),
    ):
        path = pack_root / relative
        pattern_errors = validate_pattern_note(path, template=template)
        errors.extend(f"{path.relative_to(root)}: {error}" for error in pattern_errors)
        if not pattern_errors:
            stats["patterns"] += 1

    for relative, packet_type in (
        ("agent-ops/vault/Agent Ops/Packets/Task Packet - Scheduler Review.json", "task-packet"),
        ("agent-ops/vault/Agent Ops/Packets/Result Packet - Scheduler Review.json", "result-packet"),
    ):
        path = pack_root / relative
        if path.is_file():
            errors.extend(
                f"{path.relative_to(root)}: {error}"
                for error in json_packet_errors(path, packet_type, template=False)
            )

    context = pack_root / "context-spine" / "PACK.md"
    if context.is_file():
        text = context.read_text(encoding="utf-8").casefold()
        for phrase in (
            "context spine ⊃ deep timeline",
            "adversarial canon",
            "bounded retrieval",
            "provenance",
            "caution",
            "freshness",
            "no wholesale startup load",
            "1.1",
        ):
            if phrase not in text:
                errors.append(f"packs/context-spine/PACK.md: missing corpus contract phrase {phrase!r}")
        if (pack_root / "context-spine" / "corpus").exists():
            errors.append("packs/context-spine/corpus: payload forbidden by Contract-only disposition")

    return errors, stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=Path.cwd(), type=Path)
    args = parser.parse_args()
    errors, stats = validate_packs(args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"Pack verification failed with {len(errors)} error(s).")
        return 1
    print("PASS: manifest declares exactly 2 shipped and 8 inert packs with lifecycle fields")
    print(f"PASS: {stats['seed_artifacts']} seed artifact(s) map to accepted public source rows")
    print(f"PASS: {stats['patterns']} pattern artifact(s) satisfy the two-domain pattern contract")
    print("PASS: Research and Agent Ops core and deferrable artifacts are installable vault payloads")
    print("PASS: Contract-only corpus architecture and retrieval interface ship without payloads")
    return 0


if __name__ == "__main__":
    sys.exit(main())
