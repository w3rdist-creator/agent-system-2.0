#!/usr/bin/env python3
"""Verify wikilink resolution, mandatory vault maps, and the Raw provenance boundary."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import re
import sys


WIKILINK = re.compile(r"\[\[([^\[\]]+?)\]\]")
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---", re.DOTALL)
TYPE_LINE = re.compile(r"(?m)^type:\s*([^\n]+?)\s*$")
ACTIVE_TYPES = {
    "capture", "source-note", "grounded-claim", "mechanism", "belief-revision",
    "project", "decision", "review", "experiment", "report",
}
MANDATORY_LANDINGS = {
    "Raw": "Raw Map.md",
    "Inbox": "Inbox Map.md",
    "Clippings": "Clippings Map.md",
    "Sources": "Sources Map.md",
    "Knowledge": "Knowledge Map.md",
    "Areas": "Areas Map.md",
    "Projects": "Projects Map.md",
    "Decisions": "Decisions Map.md",
    "Experiments": "Experiments Map.md",
    "Ledgers": "Ledgers Map.md",
    "Reports": "Reports Map.md",
    "Reviews": "Reviews Map.md",
    "Daily": "Daily Map.md",
    "Dashboards": "Dashboards Map.md",
    "Archive": "Archive Map.md",
    "System": "System Rules.md",
    "Queues": "Queues Map.md",
}


def markdown_files(roots: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for root in roots:
        if root.is_file() and root.suffix.lower() == ".md":
            paths.append(root.resolve())
        elif root.is_dir():
            paths.extend(path.resolve() for path in root.rglob("*.md"))
    return sorted(set(paths))


def build_index(roots: list[Path], files: list[Path]) -> dict[str, set[Path]]:
    index: dict[str, set[Path]] = defaultdict(set)
    directory_roots = [root.resolve() for root in roots if root.is_dir()]
    for path in files:
        index[path.stem.casefold()].add(path)
        for root in directory_roots:
            try:
                relative = path.relative_to(root).with_suffix("").as_posix()
            except ValueError:
                continue
            index[relative.casefold()].add(path)
    return index


def note_type(text: str) -> str | None:
    frontmatter = FRONTMATTER.match(text)
    if not frontmatter:
        return None
    match = TYPE_LINE.search(frontmatter.group(1))
    return match.group(1).strip() if match else None


def resolve_target(raw_target: str, index: dict[str, set[Path]]) -> set[Path]:
    target = raw_target.split("#", 1)[0].strip().replace("\\", "/")
    if target.lower().endswith(".md"):
        target = target[:-3]
    return index.get(target.casefold(), set())


def validate_links(roots: list[Path]) -> tuple[list[str], int, int]:
    roots = [root.resolve() for root in roots]
    files = markdown_files(roots)
    index = build_index(roots, files)
    errors: list[str] = []
    checked = 0
    vault_root = next((root for root in roots if root.name == "vault-template" and root.is_dir()), None)

    if vault_root:
        for folder, landing in MANDATORY_LANDINGS.items():
            directory = vault_root / folder
            if not directory.is_dir():
                errors.append(f"vault-template/{folder}: missing mandatory layer")
            elif not (directory / landing).is_file():
                errors.append(f"vault-template/{folder}: missing landing page {landing}")
        for top_level in ("Home.md", "Vault Self-Model.md"):
            if not (vault_root / top_level).is_file():
                errors.append(f"vault-template/{top_level}: missing operating map")

    for path in files:
        text = path.read_text(encoding="utf-8")
        active = note_type(text) in ACTIVE_TYPES
        try:
            display = path.relative_to(Path.cwd().resolve()).as_posix()
        except ValueError:
            display = str(path)
        for line_number, line in enumerate(text.splitlines(), 1):
            for match in WIKILINK.finditer(line):
                checked += 1
                content = match.group(1)
                target, separator, label = content.partition("|")
                if separator and label.strip().casefold() == "planned":
                    continue
                resolved = resolve_target(target, index)
                if not resolved:
                    errors.append(f"{display}:{line_number}: unresolved wikilink [[{content}]]")
                    continue
                if len(resolved) > 1:
                    candidates = ", ".join(sorted(str(item) for item in resolved))
                    errors.append(
                        f"{display}:{line_number}: ambiguous wikilink [[{content}]] -> {candidates}"
                    )
                    continue
                destination = next(iter(resolved))
                if vault_root and active:
                    try:
                        relative = destination.relative_to(vault_root)
                    except ValueError:
                        relative = None
                    if relative and relative.parts[0] == "Raw":
                        if not re.match(r"\s*provenance(?:\s+links?)?\s*:", line, flags=re.I):
                            errors.append(
                                f"{display}:{line_number}: active note links Raw outside a provenance field"
                            )
    return errors, len(files), checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path)
    args = parser.parse_args()
    missing = [str(path) for path in args.roots if not path.exists()]
    if missing:
        for path in missing:
            print(f"FAIL: missing input path: {path}")
        return 1
    errors, file_count, link_count = validate_links(args.roots)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"Wikilink verification failed with {len(errors)} error(s).")
        return 1
    print(f"PASS: {link_count} wikilink(s) resolve or are explicitly marked planned across {file_count} Markdown file(s)")
    print(f"PASS: all {len(MANDATORY_LANDINGS)} advertised vault layers have their required landing page")
    print("PASS: active seed-chain notes link Raw only through provenance fields")
    return 0


if __name__ == "__main__":
    sys.exit(main())
