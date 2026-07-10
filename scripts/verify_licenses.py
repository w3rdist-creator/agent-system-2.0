#!/usr/bin/env python3
"""Verify artifact licensing, source attribution, and accepted-source license closure."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re
import sys


ACCEPTED = {"copy", "adapt", "merge"}
EMPTY_VALUES = {"", "pending", "unknown", "none", "n/a"}


def markdown_license(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---", text, flags=re.DOTALL)
    if not match:
        return None
    raw = match.group(1).strip()
    try:
        data = json.loads(raw)
        value = data.get("license") if isinstance(data, dict) else None
        return value if isinstance(value, str) and value.strip() else None
    except json.JSONDecodeError:
        for line in raw.splitlines():
            key, separator, value = line.partition(":")
            if separator and key.strip() == "license" and value.strip():
                return value.strip().strip("'\"")
    return None


def artifact_errors(inputs: list[Path]) -> list[str]:
    errors: list[str] = []
    for base in inputs:
        if not base.exists():
            errors.append(f"missing input path: {base}")
            continue
        paths = [base] if base.is_file() else sorted(base.rglob("*"))
        for path in paths:
            if not path.is_file() or path.name == ".gitkeep":
                continue
            require = path.name == "SKILL.md" or path.name == "PACK.md" or "templates" in path.parts
            if not require:
                continue
            license_value: str | None = None
            if path.suffix.lower() in {".md", ".yaml", ".yml", ""}:
                license_value = markdown_license(path)
            elif path.suffix.lower() == ".json":
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    value = data.get("license") if isinstance(data, dict) else None
                    license_value = value if isinstance(value, str) and value.strip() else None
                except (OSError, json.JSONDecodeError):
                    license_value = None
            elif path.suffix.lower() in {".csv", ".tsv"}:
                delimiter = "," if path.suffix.lower() == ".csv" else "\t"
                try:
                    with path.open(encoding="utf-8", newline="") as handle:
                        header = next(csv.reader(handle, delimiter=delimiter), [])
                    license_value = "field" if "license" in header else None
                except OSError:
                    license_value = None
            if not license_value:
                errors.append(f"{path}: missing license frontmatter or field")
    return errors


def ledger_errors(root: Path) -> list[str]:
    path = root / "source-packages" / "public-file-dispositions.csv"
    errors: list[str] = []
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        return [f"cannot read source ledger: {exc}"]
    by_coordinate = {f"{row['source_repo']}:{row['source_path']}": row for row in rows}
    for line, row in enumerate(rows, 2):
        disposition = row.get("disposition", "")
        if disposition not in ACCEPTED:
            continue
        for field in ("license", "attribution", "new_path"):
            value = row.get(field, "").strip().lower()
            if value in EMPTY_VALUES:
                errors.append(f"{path}:{line}: {disposition} row lacks {field}")
        license_value = row.get("license", "").lower()
        if "unverified" in license_value or "unknown" in license_value:
            errors.append(f"{path}:{line}: accepted third-party artifact lacks a verified license")

    for skill in sorted((root / "skills").rglob("SKILL.md")):
        text = skill.read_text(encoding="utf-8")
        match = re.match(r"\A---\s*\n(.*?)\n---", text, flags=re.DOTALL)
        if not match:
            continue
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        for coordinate in data.get("source_rows", []):
            row = by_coordinate.get(coordinate)
            if row is None:
                errors.append(f"{skill}: source row {coordinate!r} is absent from the ledger")
            elif row.get("disposition") not in ACCEPTED:
                errors.append(
                    f"{skill}: source row {coordinate!r} has non-shipping disposition "
                    f"{row.get('disposition')!r}"
                )
    return errors


def validate(inputs: list[Path], root: Path | None = None, *, include_ledger: bool = True) -> list[str]:
    root = (root or Path.cwd()).resolve()
    errors = artifact_errors(inputs)
    if include_ledger:
        errors.extend(ledger_errors(root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    errors = validate(args.paths)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"License verification failed with {len(errors)} error(s).")
        return 1
    print(f"PASS: licenses present across {len(args.paths)} requested artifact roots")
    print("PASS: every copy/adapt/merge source row has license, attribution, and destination")
    print("PASS: no accepted vendored third-party artifact has an unverified license")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
