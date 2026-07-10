#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(dirname "$script_dir")
cd "$repo_root"

git rev-parse --is-inside-work-tree >/dev/null
commit_count=$(git rev-list --all --count)
if [ "$commit_count" -ne 1 ]; then
    printf 'FAIL: publication repository must contain exactly one reachable commit; found %s\n' "$commit_count" >&2
    exit 1
fi

ref_list=$(git for-each-ref --format='%(refname)')
if [ "$ref_list" != 'refs/heads/main' ]; then
    printf 'FAIL: publication repository must contain only refs/heads/main; found: %s\n' "$ref_list" >&2
    exit 1
fi

if [ -n "$(git remote)" ]; then
    printf 'FAIL: sanitized export must be fresh and have no configured remote\n' >&2
    exit 1
fi
if [ -n "$(git status --porcelain)" ]; then
    printf 'FAIL: publication repository worktree must match its single commit\n' >&2
    exit 1
fi

python3 scripts/verify_private_markers.py .
git log --all -p | python3 scripts/verify_private_markers.py --stdin
printf 'PASS: publication gate verified one commit, main-only ref, no remote, clean checkout, and clean worktree/history scans\n'
