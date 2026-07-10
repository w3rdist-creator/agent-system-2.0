#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(dirname "$script_dir")
export_root=${EVIDENCE_FIRST_EXPORT_DIR:-$HOME/Code/evidence-first-hermes-distribution-public}

repo_root=$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$repo_root")
export_root=$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$export_root")

if [ "$repo_root" = "$export_root" ]; then
    printf 'FAIL: export directory must differ from the build repository\n' >&2
    exit 1
fi
if [ -n "$(git -C "$repo_root" remote)" ]; then
    printf 'FAIL: build repository must have no configured remote\n' >&2
    exit 1
fi
if [ -e "$export_root" ]; then
    printf 'FAIL: fresh export destination already exists: %s\n' "$export_root" >&2
    exit 1
fi

mkdir -p "$export_root"
rsync -a \
    --exclude=.git/ \
    --exclude=_build/ \
    --exclude=.DS_Store \
    --exclude=__pycache__/ \
    --exclude='*.pyc' \
    "$repo_root/" "$export_root/"

test ! -e "$export_root/.git"
test ! -e "$export_root/_build"

git -C "$export_root" init -b main
git -C "$export_root" add -A
git -C "$export_root" \
    -c user.name='Evidence First Contributors' \
    -c user.email='contributors' \
    commit -m 'Release 1.0 candidate'

bash "$export_root/scripts/publication-gate.sh"
printf 'EXPORT: %s\n' "$export_root"
