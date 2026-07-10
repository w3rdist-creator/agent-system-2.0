#!/bin/sh
set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(dirname "$script_dir")

if [ "$#" -lt 1 ]; then
    printf 'Usage: install-pack.sh PACK --vault PATH\n' >&2
    exit 2
fi
pack=$1
shift
exec python3 "$script_dir/install_manifest.py" install-pack "$pack" --root "$repo_root" "$@"
