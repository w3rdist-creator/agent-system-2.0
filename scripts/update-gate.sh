#!/bin/sh
set -eu

usage() {
    printf 'Usage: %s --base REF --version X.Y.Z [--skip-dev-gate]\n' "$0"
}

base=
version=
skip_dev_gate=0

while [ "$#" -gt 0 ]; do
    case "$1" in
        --base)
            [ "$#" -ge 2 ] || { usage >&2; exit 2; }
            base=$2
            shift 2
            ;;
        --version)
            [ "$#" -ge 2 ] || { usage >&2; exit 2; }
            version=$2
            shift 2
            ;;
        --skip-dev-gate)
            skip_dev_gate=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            printf 'FAIL: unknown argument: %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if [ -z "$base" ] || [ -z "$version" ]; then
    printf 'FAIL: --base and --version are required\n' >&2
    usage >&2
    exit 2
fi

if ! printf '%s\n' "$version" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    printf 'FAIL: --version must have X.Y.Z numeric form; found %s\n' "$version" >&2
    exit 2
fi

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(dirname "$script_dir")
cd "$repo_root"

git rev-parse --is-inside-work-tree >/dev/null
if [ -n "$(git status --porcelain)" ]; then
    printf 'FAIL: update repository worktree must be clean\n' >&2
    exit 1
fi

if ! git rev-parse --verify "$base^{commit}" >/dev/null 2>&1; then
    printf 'FAIL: update base is not a commit: %s\n' "$base" >&2
    exit 1
fi
if ! git merge-base --is-ancestor "$base" HEAD; then
    printf 'FAIL: update base %s is not an ancestor of HEAD\n' "$base" >&2
    exit 1
fi
if [ "$(git rev-list --count "$base"..HEAD)" -eq 0 ]; then
    printf 'FAIL: update range %s..HEAD contains no commits\n' "$base" >&2
    exit 1
fi

version_pattern=$(printf '%s' "$version" | sed 's/[.]/\\./g')
if ! grep -Eq "^## ${version_pattern}([[:space:]]|$)" CHANGELOG.md; then
    printf 'FAIL: CHANGELOG.md has no ## %s release heading\n' "$version" >&2
    exit 1
fi

python3 scripts/verify_private_markers.py .
git log -p "$base"..HEAD | python3 scripts/verify_private_markers.py --stdin

if [ "$skip_dev_gate" -eq 0 ]; then
    bash scripts/dev-gate.sh
else
    printf 'TEST ONLY: skipped recursive development gate\n'
fi

printf 'PASS: update gate verified clean checkout, version %s, range %s..HEAD, privacy scans, and development gate policy\n' "$version" "$base"
