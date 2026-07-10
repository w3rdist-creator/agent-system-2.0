#!/usr/bin/env python3
"""Report governed loop-contract coverage across supplied paths."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


MARKERS = ("owner", "consumer", "kill condition")


def text_files(paths: list[Path]):
    for supplied in paths:
        if supplied.is_file():
            yield supplied
        elif supplied.is_dir():
            yield from (path for path in supplied.rglob("*") if path.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    missing = [str(path) for path in args.paths if not path.exists()]
    if missing:
        for path in missing:
            print(f"FAIL: missing scoring input: {path}")
        return 1
    scanned = 0
    governed = 0
    for path in text_files(args.paths):
        try:
            lowered = path.read_text(encoding="utf-8").casefold()
        except (OSError, UnicodeDecodeError):
            continue
        scanned += 1
        if all(marker in lowered for marker in MARKERS):
            governed += 1
    print(f"PASS: loop scoring inspected {scanned} text artifact(s); {governed} declare owner/consumer/kill-condition coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
