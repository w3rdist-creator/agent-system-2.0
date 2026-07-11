#!/usr/bin/env python3
"""Scan a public tree or stdin stream for likely private markers."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import Iterable


SKIP_DIRS = {".git", "_build", "__pycache__"}
FAKE_CREDENTIAL = "sk-FAKE-EVAL-FIXTURE-000000"
GENERIC_USER_SEGMENTS = {"<name>", "<user>", "example", "username", "user", "USER"}

CONTENT_PATTERNS = (
    (
        "absolute personal path",
        re.compile(r"/Users/(?P<user>[A-Za-z0-9._-]+)(?:/|\b)"),
    ),
    (
        "email address",
        re.compile(r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])", re.I),
    ),
    (
        "phone number",
        re.compile(r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)"),
    ),
    (
        "API key or token",
        re.compile(
            r"(?:\bsk-[A-Za-z0-9_-]{16,}\b|\bgh[pousr]_[A-Za-z0-9]{20,}\b|"
            r"\b(?:api[_-]?key|access[_-]?token|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_./+-]{12,})",
            re.I,
        ),
    ),
    (
        "private hostname",
        re.compile(
            r"\b(?:[A-Za-z0-9-]+\.)+(?:internal|intranet|lan|local)\b|"
            r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b",
            re.I,
        ),
    ),
    (
        "private key block",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "session/state/auth filename in patch stream",
        re.compile(
            r"^(?:diff --git a/[^ ]+ b/|--- a/|\+\+\+ b/)(?:[^\n]*/)?"
            r"(?:session|sessions|state|auth|credentials?)(?:$|[._-])[^\n]*$",
            re.I | re.M,
        ),
    ),
)

SENSITIVE_FILENAME_RE = re.compile(
    r"^(?:session|sessions|state|auth|credentials?)(?:$|[._-])", re.I
)
PUBLIC_SENSITIVE_FIXTURE_PATHS = {
    "evaluations/scenarios/01-stale-context-live-source/fixture/queue-service/state.json",
}


def has_sensitive_tree_filename(relative: Path) -> bool:
    return (
        relative.as_posix() not in PUBLIC_SENSITIVE_FIXTURE_PATHS
        and SENSITIVE_FILENAME_RE.search(relative.name) is not None
    )


def iter_tree_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        yield path


def load_denylist(path: Path | None, scan_root: Path | None) -> list[str]:
    if path is None:
        return []
    resolved = path.expanduser().resolve()
    if scan_root is not None:
        try:
            resolved.relative_to(scan_root.resolve())
        except ValueError:
            pass
        else:
            raise ValueError("denylist must be external to the scanned repository tree")
    terms = []
    for line in resolved.read_text(encoding="utf-8").splitlines():
        term = line.strip()
        if term and not term.startswith("#"):
            terms.append(term)
    return terms


def findings_for_text(text: str, source: str, denylist: list[str]) -> list[str]:
    findings: list[str] = []
    scrubbed = text.replace(FAKE_CREDENTIAL, "FAKE_CREDENTIAL_WHITELISTED")
    for label, pattern in CONTENT_PATTERNS:
        for match in pattern.finditer(scrubbed):
            if label == "absolute personal path" and match.group("user") in GENERIC_USER_SEGMENTS:
                continue
            if label == "session/state/auth filename in patch stream" and any(
                path in match.group(0) for path in PUBLIC_SENSITIVE_FIXTURE_PATHS
            ):
                continue
            line = scrubbed.count("\n", 0, match.start()) + 1
            findings.append(f"{source}:{line}: {label}")
    lowered = scrubbed.casefold()
    for term in denylist:
        start = 0
        needle = term.casefold()
        while True:
            index = lowered.find(needle, start)
            if index < 0:
                break
            line = scrubbed.count("\n", 0, index) + 1
            findings.append(f"{source}:{line}: external denylist term")
            start = index + len(needle)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, help="tree to scan")
    parser.add_argument("--stdin", action="store_true", help="scan text from stdin")
    parser.add_argument("--denylist", type=Path, help="external newline-delimited denylist")
    args = parser.parse_args()
    if args.stdin == (args.root is not None):
        parser.error("provide exactly one tree path or --stdin")
    try:
        denylist = load_denylist(args.denylist, args.root)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    findings: list[str] = []
    scanned = 0
    if args.stdin:
        text = sys.stdin.read()
        findings.extend(findings_for_text(text, "<stdin>", denylist))
        scanned = 1
    else:
        root = args.root.resolve()
        for path in iter_tree_files(root):
            relative = path.relative_to(root)
            if has_sensitive_tree_filename(relative):
                findings.append(f"{relative}: sensitive session/state/auth filename")
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            scanned += 1
            findings.extend(findings_for_text(text, str(relative), denylist))

    if findings:
        for finding in findings:
            print(f"FAIL: {finding}")
        print(f"Privacy scan failed: {len(findings)} finding(s) across {scanned} text input(s).")
        return 1
    print(f"PASS: privacy scan found no private markers across {scanned} text input(s)")
    if denylist:
        print(f"PASS: checked {len(denylist)} external denylist term(s)")
    print(f"PASS: whitelisted only the known fake evaluation credential {FAKE_CREDENTIAL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
