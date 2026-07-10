#!/bin/sh
set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(dirname "$script_dir")
exec python3 "$script_dir/install_manifest.py" list-packs --root "$repo_root" "$@"
