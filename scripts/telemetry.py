#!/usr/bin/env python3
"""Collect machine-produced evidence into the vault telemetry ledger."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import date
import hashlib
import json
from pathlib import Path
import sys
from typing import Iterable

from evaluation_lib import ValidationError, fixture_reads_before_first_answer, normalize_transcript


LEDGER_HEADER = ("date", "source", "metric", "value")


class TelemetryError(RuntimeError):
    """Raised when a named telemetry source cannot be read safely."""


def metric_name(prefix: str, value: object) -> str | None:
    return f"{prefix}.{value}" if isinstance(value, str) and value else None


def transcript_metrics(path: Path) -> Counter[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        events = normalize_transcript(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, ValidationError) as exc:
        raise TelemetryError(str(exc)) from exc

    metrics: Counter[str] = Counter()
    for event in events:
        event_type = event.get("type")
        if event_type == "disposition":
            name = metric_name("disposition", event.get("label"))
        elif event_type == "tool_call":
            name = metric_name("tool", event.get("tool"))
        elif event_type == "guard_denied":
            name = metric_name("guard_denied", event.get("rule"))
        else:
            name = None
        if name:
            metrics[name] += 1
    metrics["fixture_reads_before_first_answer"] = len(
        fixture_reads_before_first_answer(events)
    )
    return metrics


def csv_rows(path: Path, required: Iterable[str]) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = tuple(reader.fieldnames or ())
            missing = sorted(set(required) - set(fields))
            if missing:
                raise TelemetryError(
                    f"{path}: missing required column(s): {', '.join(missing)}"
                )
            return list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise TelemetryError(f"{path}: {exc}") from exc


def recert_metrics(path: Path) -> Counter[str]:
    metrics: Counter[str] = Counter()
    for row in csv_rows(path, ("result",)):
        name = metric_name("result", row.get("result"))
        if name:
            metrics[name] += 1
    return metrics


def metabolism_metrics(path: Path) -> Counter[str]:
    rows = csv_rows(path, ("screams",))
    total = 0
    for number, row in enumerate(rows, 2):
        try:
            screams = int(row["screams"])
        except (TypeError, ValueError) as exc:
            raise TelemetryError(f"{path}:{number}: screams must be an integer") from exc
        if screams < 0:
            raise TelemetryError(f"{path}:{number}: screams must be non-negative")
        total += screams
    return Counter({"screams": total}) if rows else Counter()


def existing_keys(path: Path) -> set[tuple[str, str, str]]:
    if not path.exists():
        return set()
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != LEDGER_HEADER:
                raise TelemetryError(
                    f"{path}: header does not match {','.join(LEDGER_HEADER)}"
                )
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise TelemetryError(f"{path}: {exc}") from exc
    return {(row["date"], row["source"], row["metric"]) for row in rows}


def source_id(kind: str, path: Path) -> str:
    """Name an explicit source without persisting its host filesystem path."""

    digest = hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:12]
    return f"{kind}:{path.name}#{digest}"


def append_rows(path: Path, rows: list[tuple[str, str, str, int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not path.exists()
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        if needs_header:
            writer.writerow(LEDGER_HEADER)
        writer.writerows(rows)


def run(
    vault: Path,
    *,
    transcript_dirs: list[Path],
    recert_log: Path | None,
    metabolism_ledger: Path | None,
    dry_run: bool,
    today: date,
) -> int:
    collected: list[tuple[str, str, int]] = []
    found: list[str] = []
    empty: list[str] = []
    warnings: list[str] = []

    for directory_number, directory in enumerate(transcript_dirs, 1):
        source_group = f"transcripts[{directory_number}]"
        if not directory.is_dir():
            empty.append(f"{source_group} (missing: {directory})")
            continue
        paths = sorted(directory.glob("*.json"))
        if not paths:
            empty.append(f"{source_group} (no JSON transcripts: {directory})")
            continue
        yielded = False
        for path in paths:
            try:
                metrics = transcript_metrics(path)
            except TelemetryError as exc:
                warnings.append(f"{path}: {exc}")
                continue
            source = f"{source_id('transcript-dir', directory)}/{path.name}"
            collected.extend((source, metric, value) for metric, value in sorted(metrics.items()))
            yielded = True
        (found if yielded else empty).append(source_group)

    for label, path, collector in (
        ("recert", recert_log, recert_metrics),
        ("metabolism", metabolism_ledger, metabolism_metrics),
    ):
        if path is None:
            continue
        if not path.is_file():
            empty.append(f"{label} (missing: {path})")
            continue
        metrics = collector(path)
        if not metrics:
            empty.append(f"{label} (no rows: {path})")
            continue
        found.append(label)
        source = source_id(label, path)
        collected.extend((source, metric, value) for metric, value in sorted(metrics.items()))

    print(f"SOURCES FOUND: {len(found)}" + (f" ({', '.join(found)})" if found else ""))
    print(f"SOURCES EMPTY: {len(empty)}" + (f" ({'; '.join(empty)})" if empty else ""))
    for warning in warnings:
        print(f"WARNING: skipped malformed transcript: {warning}", file=sys.stderr)

    if not collected:
        print(
            f"NO DATA: no evidence found; warnings={len(warnings)}, rows written=0; wrote nothing"
        )
        return 0

    ledger = vault / "Ledgers" / "Telemetry Ledger.csv"
    keys = existing_keys(ledger)
    rows: list[tuple[str, str, str, int]] = []
    skipped = 0
    day = today.isoformat()
    for source, metric, value in collected:
        key = (day, source, metric)
        if key in keys:
            skipped += 1
            continue
        keys.add(key)
        rows.append((day, source, metric, value))

    if dry_run:
        print(
            f"DRY RUN: rows planned={len(rows)}, existing keys skipped={skipped}, "
            f"warnings={len(warnings)}, rows written=0"
        )
    else:
        if rows:
            append_rows(ledger, rows)
        print(
            f"TELEMETRY: rows written={len(rows)}, existing keys skipped={skipped}, "
            f"warnings={len(warnings)}"
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, type=Path)
    parser.add_argument("--transcript-dir", action="append", default=[], type=Path)
    parser.add_argument("--recert-log", type=Path)
    parser.add_argument("--metabolism-ledger", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    try:
        return run(
            args.vault.expanduser().resolve(),
            transcript_dirs=[path.expanduser().resolve() for path in args.transcript_dir],
            recert_log=args.recert_log.expanduser().resolve() if args.recert_log else None,
            metabolism_ledger=(
                args.metabolism_ledger.expanduser().resolve()
                if args.metabolism_ledger
                else None
            ),
            dry_run=args.dry_run,
            today=args.today,
        )
    except (TelemetryError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
