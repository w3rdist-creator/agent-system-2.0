#!/usr/bin/env python3
"""Route, deduplicate, decay, and report on an Evidence-First vault Inbox."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import hashlib
import os
from pathlib import Path
import re
import shutil
import sys


ROUTE_FOLDERS = frozenset(
    {
        "Sources", "Knowledge", "Raw", "Projects", "Decisions",
        "Experiments", "Reviews", "Reports", "Areas", "Clippings",
    }
)
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
FIELD = re.compile(r"(?m)^([A-Za-z][A-Za-z0-9_-]*):\s*(.*?)\s*$")
QUEUE_ID = re.compile(r"(?m)^- \*\*ID:\*\*\s*(\S+)\s*$")
LEDGER_HEADER = ("date", "routed", "deduped", "decayed", "skipped", "screams")


class MetabolismError(RuntimeError):
    """Raised when preservation-first processing cannot proceed safely."""


@dataclass(frozen=True)
class Note:
    path: Path
    text: str
    metadata: dict[str, str]
    body_hash: str


@dataclass(frozen=True)
class Move:
    source: Path
    destination: Path
    kind: str


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}, text
    metadata = {
        key.casefold(): unquote(value)
        for key, value in FIELD.findall(match.group(1))
    }
    return metadata, text[match.end():]


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def normalized_body(body: str) -> str:
    return "\n".join(line.rstrip() for line in body.splitlines()).rstrip()


def read_note(path: Path) -> Note:
    text = path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(text)
    digest = hashlib.sha256(normalized_body(body).encode("utf-8")).hexdigest()
    return Note(path, text, metadata, digest)


def incoming_destination(target: Path) -> Path:
    return target.with_name(target.name + ".incoming")


def duplicate_destination(vault: Path, source: Path, today: date) -> Path:
    name = f"{source.stem}.duplicate-{today.isoformat()}{source.suffix}"
    target = vault / "Archive" / "Duplicates" / name
    return target if not target.exists() else incoming_destination(target)


def note_date(note: Note) -> date:
    raw = note.metadata.get("date")
    if raw:
        try:
            return date.fromisoformat(raw)
        except ValueError:
            pass
    return datetime.fromtimestamp(note.path.stat().st_mtime).date()


def queue_id(vault: Path, note: Note) -> str:
    relative = note.path.relative_to(vault).as_posix()
    suffix = hashlib.sha256(relative.encode("utf-8")).hexdigest()[:12].upper()
    return f"METABOLISM-{suffix}"


def queue_template() -> str:
    return """---
license: CC BY 4.0
type: queue
---

# Resolve Queue

- **Maximum unresolved backlog:** set by the metabolism command's `--queue-cap`
- **Owner:** `w3rdist-creator`
- **Review cadence:** weekly while any card is unresolved

Each one-screen card records a stable ID, first/last seen, owner, evidence, decision needed,
return condition, and status. Adding reviewers or capacity is not a resolution.
"""


def queue_card(vault: Path, note: Note, today: date) -> str:
    relative = note.path.relative_to(vault).as_posix()
    return f"""

## Decayed inbox item — {relative}

- **ID:** {queue_id(vault, note)}
- **First/last seen:** {today.isoformat()} / {today.isoformat()}
- **Owner:** `w3rdist-creator`
- **Evidence:** `{relative}` exceeded its Inbox age budget
- **Decision needed:** route, use `done` after a verified merge, use `watch` with a return condition, or `kill` the capture
- **Return condition:** remove this card after recording the resulting state change
- **Status:** unresolved
"""


def queue_entry_ids(text: str) -> set[str]:
    return set(QUEUE_ID.findall(text))


def markdown_notes(inbox: Path) -> list[Note]:
    if not inbox.is_dir():
        return []
    return [read_note(path) for path in sorted(inbox.rglob("*.md")) if path.is_file()]


def plan_moves(vault: Path, notes: list[Note], today: date) -> tuple[list[Move], list[Note], int]:
    moves: list[Move] = []
    duplicate_paths: set[Path] = set()
    by_hash: dict[str, list[Note]] = {}
    for note in notes:
        by_hash.setdefault(note.body_hash, []).append(note)
    for matches in by_hash.values():
        for duplicate in matches[1:]:
            destination = duplicate_destination(vault, duplicate.path, today)
            moves.append(Move(duplicate.path, destination, "DEDUPE"))
            duplicate_paths.add(duplicate.path)

    survivors = [note for note in notes if note.path not in duplicate_paths]
    skipped = 0
    remaining: list[Note] = []
    for note in survivors:
        route = note.metadata.get("route")
        if route not in ROUTE_FOLDERS or not (vault / route).is_dir():
            skipped += 1
            remaining.append(note)
            continue
        target = vault / route / note.path.name
        if target.is_file() and read_note(target).body_hash == note.body_hash:
            destination = duplicate_destination(vault, note.path, today)
            moves.append(Move(note.path, destination, "DEDUPE"))
            continue
        destination = target if not target.exists() else incoming_destination(target)
        moves.append(Move(note.path, destination, "ROUTE"))
    return moves, remaining, skipped


def validate_moves(moves: list[Move]) -> None:
    destinations: set[Path] = set()
    for move in moves:
        if move.destination.exists():
            raise MetabolismError(
                f"conflict proposal already exists; refusing to overwrite: {move.destination}"
            )
        if move.destination in destinations:
            raise MetabolismError(f"two operations target the same path: {move.destination}")
        destinations.add(move.destination)


def move_file(move: Move) -> None:
    move.destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(move.source), str(move.destination))


def append_queue(path: Path, cards: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else queue_template()
    path.write_text(existing.rstrip() + "".join(cards) + "\n", encoding="utf-8")


def append_ledger(path: Path, today: date, counts: dict[str, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not path.exists()
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        if needs_header:
            writer.writerow(LEDGER_HEADER)
        writer.writerow([today.isoformat(), *(counts[key] for key in LEDGER_HEADER[1:])])


def run(vault: Path, *, dry_run: bool, max_age_days: int, queue_cap: int, today: date) -> int:
    if max_age_days < 0 or queue_cap < 0:
        raise MetabolismError("--max-age-days and --queue-cap must be non-negative")
    inbox = vault / "Inbox"
    notes = markdown_notes(inbox)
    if not notes:
        print(f"NO DATA: no Markdown notes found in {inbox}; wrote nothing")
        return 0

    moves, remaining_before_decay, skipped = plan_moves(vault, notes, today)
    validate_moves(moves)
    moved_sources = {move.source for move in moves}
    remaining = [note for note in remaining_before_decay if note.path not in moved_sources]
    cutoff = today - timedelta(days=max_age_days)
    decayed = [note for note in remaining if note_date(note) < cutoff]

    queue_path = vault / "Queues" / "Resolve Queue.md"
    queue_text = queue_path.read_text(encoding="utf-8") if queue_path.exists() else queue_template()
    existing_ids = queue_entry_ids(queue_text)
    new_cards = [queue_card(vault, note, today) for note in decayed if queue_id(vault, note) not in existing_ids]
    queue_count = len(existing_ids) + len(new_cards)
    inbox_count = len(remaining)
    screams = int(inbox_count > queue_cap) + int(queue_count > queue_cap)
    counts = {
        "routed": sum(move.kind == "ROUTE" for move in moves),
        "deduped": sum(move.kind == "DEDUPE" for move in moves),
        "decayed": len(decayed),
        "skipped": skipped,
        "screams": screams,
    }

    prefix = "PLAN " if dry_run else ""
    for move in moves:
        print(f"{prefix}{move.kind}: {move.source} -> {move.destination}")
    for note in remaining_before_decay:
        route = note.metadata.get("route", "<missing>")
        print(f"{prefix}SKIP: {note.path} (route={route!r})")
    for note in decayed:
        action = "append Resolve Queue entry" if queue_id(vault, note) not in existing_ids else "keep existing Resolve Queue entry"
        print(f"{prefix}DECAY: {note.path} ({action})")

    if dry_run:
        if new_cards:
            print(f"PLAN QUEUE: append {len(new_cards)} entr{'y' if len(new_cards) == 1 else 'ies'} to {queue_path}")
        print(f"PLAN LEDGER: append run record to {vault / 'Ledgers' / 'Metabolism Ledger.csv'}")
    else:
        for move in moves:
            move_file(move)
        if new_cards:
            append_queue(queue_path, new_cards)
        append_ledger(vault / "Ledgers" / "Metabolism Ledger.csv", today, counts)

    print(
        "METABOLISM: "
        + ", ".join(f"{key}={value}" for key, value in counts.items())
        + f", inbox={inbox_count}, resolve_queue={queue_count}"
    )
    if screams:
        print(
            f"SCREAM: Inbox count {inbox_count} (cap {queue_cap}); "
            f"Resolve Queue entry count {queue_count} (cap {queue_cap})",
            file=sys.stderr,
        )
        return 1
    print(f"HEALTHY: Inbox count {inbox_count}; Resolve Queue entry count {queue_count}; cap {queue_cap}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-age-days", type=int, default=14)
    parser.add_argument("--queue-cap", type=int, default=25)
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    try:
        return run(
            args.vault.expanduser().resolve(),
            dry_run=args.dry_run,
            max_age_days=args.max_age_days,
            queue_cap=args.queue_cap,
            today=args.today,
        )
    except (MetabolismError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
