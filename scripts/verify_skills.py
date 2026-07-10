#!/usr/bin/env python3
"""Validate routed skill metadata, registries, category caps, and mechanical doctrine overlap.

Duplicate-doctrine detection compares normalized word n-grams inside paragraph blocks.
The default window is 8 words and the default containment threshold is 0.85.
This catches literal and near-literal reuse only; paraphrase-level duplication remains a
human-review item and is intentionally outside this script's authority.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re
import sys


REQUIRED_FIELDS = {"name", "description", "category", "source_rows", "license", "triggers"}
REQUIRED_CORE = {
    "capability-router",
    "evidence-first-operating-style",
    "source-grounding",
    "knowledge-metabolism",
    "loop-governance",
    "vault-operations",
}
DESCRIPTION_LIMIT = 350
CATEGORY_CAP = 20
DEFAULT_NGRAM_WINDOW = 8
DEFAULT_OVERLAP_THRESHOLD = 0.85
WORD_RE = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)*")


def parse_frontmatter(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n?", text, flags=re.DOTALL)
    if not match:
        raise ValueError("missing frontmatter")
    raw = match.group(1).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"frontmatter must be a JSON-compatible YAML mapping: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data, text[match.end():]


def source_coordinates(root: Path) -> set[str]:
    path = root / "source-packages" / "public-file-dispositions.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        return {
            f"{row['source_repo']}:{row['source_path']}"
            for row in csv.DictReader(handle)
        }


def load_level_zero(root: Path) -> list[dict[str, str]]:
    data = json.loads((root / "skills" / "level-0-categories.yaml").read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Level 0 must be a list")
    return data


def doctrine_blocks(path: Path, body: str, ngram_window: int) -> list[tuple[str, set[tuple[str, ...]]]]:
    blocks: list[tuple[str, set[tuple[str, ...]]]] = []
    for index, block in enumerate(re.split(r"\n\s*\n", body), 1):
        words = WORD_RE.findall(block.lower())
        if len(words) < max(20, ngram_window * 2):
            continue
        ngrams = {
            tuple(words[offset : offset + ngram_window])
            for offset in range(len(words) - ngram_window + 1)
        }
        if ngrams:
            blocks.append((f"{path}:{index}", ngrams))
    return blocks


def duplicate_doctrine_errors(
    root: Path, ngram_window: int, threshold: float
) -> list[str]:
    candidates: list[tuple[Path, str]] = []
    candidates.append((root / "agent" / "SOUL.md", (root / "agent" / "SOUL.md").read_text(encoding="utf-8")))
    for path in sorted((root / "skills" / "core").glob("*/SKILL.md")):
        try:
            _, body = parse_frontmatter(path)
        except ValueError:
            body = path.read_text(encoding="utf-8")
        candidates.append((path, body))
    for pattern in ("skills/categories/*/registry.yaml", "templates/*", "docs/*.md"):
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                candidates.append((path, path.read_text(encoding="utf-8")))

    blocks: list[tuple[Path, str, set[tuple[str, ...]]]] = []
    for path, body in candidates:
        relative = path.relative_to(root)
        blocks.extend((relative, label, grams) for label, grams in doctrine_blocks(relative, body, ngram_window))

    errors: list[str] = []
    for left in range(len(blocks)):
        left_path, left_label, left_grams = blocks[left]
        for right in range(left + 1, len(blocks)):
            right_path, right_label, right_grams = blocks[right]
            if left_path == right_path:
                continue
            overlap = len(left_grams & right_grams) / min(len(left_grams), len(right_grams))
            if overlap >= threshold:
                errors.append(
                    f"duplicate doctrine {overlap:.2f} >= {threshold:.2f}: "
                    f"{left_label} and {right_label}"
                )
    return errors


def validate_catalog(
    root: Path,
    *,
    ngram_window: int = DEFAULT_NGRAM_WINDOW,
    overlap_threshold: float = DEFAULT_OVERLAP_THRESHOLD,
) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    root = root.resolve()
    skills_root = root / "skills"
    skill_paths = sorted(skills_root.glob("core/*/SKILL.md")) + sorted(
        skills_root.glob("library/*/*/SKILL.md")
    )
    coordinates = source_coordinates(root)
    metadata_by_path: dict[str, dict[str, object]] = {}

    for path in skill_paths:
        relative = path.relative_to(root).as_posix()
        try:
            metadata, _ = parse_frontmatter(path)
        except (OSError, ValueError) as exc:
            errors.append(f"{relative}: {exc}")
            continue
        metadata_by_path[relative] = metadata
        missing = REQUIRED_FIELDS - set(metadata)
        if missing:
            errors.append(f"{relative}: missing frontmatter fields {sorted(missing)}")
        name = metadata.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            errors.append(f"{relative}: invalid skill name {name!r}")
        elif path.parent.name != name:
            errors.append(f"{relative}: folder and skill name differ")
        description = metadata.get("description")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{relative}: description must be a non-empty string")
        elif len(description) > DESCRIPTION_LIMIT:
            errors.append(f"{relative}: description is {len(description)} chars; limit is {DESCRIPTION_LIMIT}")
        category = metadata.get("category")
        if not isinstance(category, str) or not category:
            errors.append(f"{relative}: category must be a non-empty string")
        for field in ("source_rows", "triggers"):
            value = metadata.get(field)
            if not isinstance(value, list) or (field == "triggers" and not value):
                errors.append(f"{relative}: {field} must be a {'non-empty ' if field == 'triggers' else ''}list")
            elif not all(isinstance(item, str) and item.strip() for item in value):
                errors.append(f"{relative}: {field} contains a non-string or empty value")
        source_rows = metadata.get("source_rows")
        if isinstance(source_rows, list):
            for coordinate in source_rows:
                if isinstance(coordinate, str) and coordinate not in coordinates:
                    errors.append(f"{relative}: unknown source_rows coordinate {coordinate!r}")
        if not isinstance(metadata.get("license"), str) or not str(metadata.get("license", "")).strip():
            errors.append(f"{relative}: license must be a non-empty string")

    try:
        categories = load_level_zero(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return errors + [f"skills/level-0-categories.yaml: {exc}"], {}
    category_names = [item.get("name") for item in categories if isinstance(item, dict)]
    if len(category_names) != len(set(category_names)):
        errors.append("Level 0 contains duplicate categories")

    reachability = {path: 0 for path in metadata_by_path}
    counts: dict[str, int] = {}
    registry_paths = sorted((skills_root / "categories").glob("*/registry.yaml"))
    registry_categories = {path.parent.name for path in registry_paths}
    expected_categories = set(category_names)
    if registry_categories != expected_categories:
        errors.append(
            f"registry categories differ from Level 0: missing={sorted(expected_categories - registry_categories)} "
            f"extra={sorted(registry_categories - expected_categories)}"
        )

    for registry in registry_paths:
        relative = registry.relative_to(root).as_posix()
        try:
            data = json.loads(registry.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relative}: invalid JSON-compatible YAML: {exc}")
            continue
        category = registry.parent.name
        if data.get("category") != category:
            errors.append(f"{relative}: category does not match directory")
        entries = data.get("skills")
        if not isinstance(entries, list):
            errors.append(f"{relative}: skills must be a list")
            continue
        counts[category] = len(entries)
        if len(entries) > CATEGORY_CAP:
            errors.append(f"{relative}: {len(entries)} skills exceeds cap {CATEGORY_CAP}")
        seen_names: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != {"name", "description", "path"}:
                errors.append(f"{relative}: registry entry must contain name, description, and path")
                continue
            name, description, target = entry["name"], entry["description"], entry["path"]
            if name in seen_names:
                errors.append(f"{relative}: duplicate registry skill {name!r}")
            seen_names.add(name)
            if not isinstance(description, str) or len(description) > DESCRIPTION_LIMIT:
                errors.append(f"{relative}: invalid description for {name!r}")
            if not isinstance(target, str) or target not in metadata_by_path:
                errors.append(f"{relative}: missing skill target {target!r}")
                continue
            reachability[target] += 1
            metadata = metadata_by_path[target]
            if metadata.get("name") != name:
                errors.append(f"{relative}: name differs from {target}")
            if metadata.get("description") != description:
                errors.append(f"{relative}: description differs from {target}")
            if metadata.get("category") != category:
                errors.append(f"{relative}: category differs from {target}")

    for path, count in reachability.items():
        if count != 1:
            errors.append(f"{path}: reachable from {count} registries; expected exactly 1")
    core_names = {
        metadata.get("name")
        for path, metadata in metadata_by_path.items()
        if path.startswith("skills/core/")
    }
    if core_names != REQUIRED_CORE:
        errors.append(f"core skill set mismatch: expected {sorted(REQUIRED_CORE)}, found {sorted(core_names)}")

    map_path = root / "agent" / "SOUL-scenario-map.yaml"
    try:
        mapping = json.loads(map_path.read_text(encoding="utf-8"))
        soul_lines = [line.strip() for line in (root / "agent" / "SOUL.md").read_text(encoding="utf-8").splitlines() if line.strip()]
        mapped = [item.get("line") for item in mapping if isinstance(item, dict)]
        if mapped != soul_lines or any(not item.get("scenarios") for item in mapping):
            errors.append("agent/SOUL-scenario-map.yaml does not map every stance line in order")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot validate SOUL scenario map: {exc}")

    errors.extend(duplicate_doctrine_errors(root, ngram_window, overlap_threshold))
    return errors, counts


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Mechanical boundary: normalized paragraph n-grams detect literal/near-literal reuse only; "
            "human Phase 7 review owns paraphrase-level doctrine duplication."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("paths", nargs="+", help="agent and skills roots (used to locate the repository root)")
    parser.add_argument(
        "--ngram-window",
        type=int,
        default=DEFAULT_NGRAM_WINDOW,
        help=f"normalized word n-gram window (default: {DEFAULT_NGRAM_WINDOW})",
    )
    parser.add_argument(
        "--overlap-threshold",
        type=float,
        default=DEFAULT_OVERLAP_THRESHOLD,
        help=f"smaller-block n-gram containment threshold (default: {DEFAULT_OVERLAP_THRESHOLD})",
    )
    args = parser.parse_args()
    root = Path.cwd().resolve()
    if args.ngram_window < 2 or not 0 < args.overlap_threshold <= 1:
        parser.error("--ngram-window must be >=2 and --overlap-threshold must be in (0, 1]")
    errors, counts = validate_catalog(
        root,
        ngram_window=args.ngram_window,
        overlap_threshold=args.overlap_threshold,
    )
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"Skill verification failed with {len(errors)} error(s).")
        return 1
    total = sum(counts.values())
    empty = sum(count == 0 for count in counts.values())
    print(f"PASS: {total} skills are each reachable from exactly one of {len(counts)} registries")
    print(f"PASS: category cap {CATEGORY_CAP}; largest category has {max(counts.values(), default=0)} skills")
    print(f"PASS: required metadata, description limits, source coordinates, and {len(REQUIRED_CORE)} core skills")
    print(f"PASS: SOUL stance lines are scenario-mapped; {empty} empty registries contain no filler skills")
    print(
        f"PASS: mechanical duplicate-doctrine scan window={args.ngram_window} "
        f"threshold={args.overlap_threshold:.2f}; paraphrase review remains human"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
