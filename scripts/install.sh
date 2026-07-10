#!/bin/sh
set -eu

usage() {
    cat <<'EOF'
Usage: install.sh --vault PATH [--hermes-home PATH] [--dry-run] [--force-unsupported]

Installs the reference-first Evidence First distribution for Hermes v0.18.x.
--force-unsupported bypasses the version refusal at your own risk; compatibility is unverified.
EOF
}

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(dirname "$script_dir")
vault=
hermes_home=${HOME}/.hermes
dry_run=false
force_unsupported=false

while [ "$#" -gt 0 ]; do
    case "$1" in
        --vault) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; vault=$2; shift 2 ;;
        --hermes-home) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; hermes_home=$2; shift 2 ;;
        --dry-run) dry_run=true; shift ;;
        --force-unsupported) force_unsupported=true; shift ;;
        --help|-h) usage; exit 0 ;;
        *) printf 'ERROR: unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
done

[ -n "$vault" ] || { printf 'ERROR: --vault is required\n' >&2; usage >&2; exit 2; }

hermes_bin=${HERMES_BIN:-}
if [ -z "$hermes_bin" ]; then
    hermes_bin=$(command -v hermes 2>/dev/null || true)
fi
if [ -z "$hermes_bin" ]; then
    if [ "$force_unsupported" = false ]; then
        printf 'ERROR: Hermes version undetectable; install Hermes v0.18.x or use --force-unsupported at your own risk\n' >&2
        exit 1
    fi
    printf 'WARNING: Hermes command not found; forced install cannot configure skill discovery\n' >&2
    exit 1
fi

if ! version_output=$("$hermes_bin" --version 2>&1); then
    if [ "$force_unsupported" = false ]; then
        printf 'ERROR: Hermes version undetectable; version command failed before any write\n' >&2
        exit 1
    fi
    version_output='forced-undetectable-version'
fi

case "$version_output" in
    *v0.18.*) ;;
    *)
        if [ "$force_unsupported" = false ]; then
            printf 'ERROR: unsupported Hermes version; expected v0.18.x, detected: %s\n' "$version_output" >&2
            exit 1
        fi
        printf 'WARNING: forcing unsupported Hermes version at your own risk: %s\n' "$version_output" >&2
        ;;
esac

hermes_home=$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$hermes_home")
vault=$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$vault")
external_path=$hermes_home/distributions/evidence-first/skills

if ! inspection=$(python3 "$script_dir/install_manifest.py" inspect-config --hermes-home "$hermes_home" --desired "$external_path"); then
    printf 'ERROR: Hermes skills.external_dirs semantics could not be verified before installation\n' >&2
    exit 1
fi
external_index=$(printf '%s\n' "$inspection" | sed -n '1p')
duplicate=$(printf '%s\n' "$inspection" | sed -n '2p')

printf 'COMPATIBLE: %s\n' "$version_output"
printf 'STRATEGY: reference-first via skills.external_dirs[%s]\n' "$external_index"

if [ "$dry_run" = true ]; then
    printf 'DRY RUN: no files or Hermes configuration will be written\n'
    python3 "$script_dir/install_manifest.py" plan --root "$repo_root" --vault "$vault" --hermes-home "$hermes_home"
    if [ "$duplicate" = false ]; then
        printf 'PLAN config: MANUAL ADDITION REQUIRED after install — in %s/config.yaml, add %s as a new entry under skills.external_dirs; the installer never edits config.yaml\n' "$hermes_home" "$external_path"
    else
        printf 'PLAN config: existing exact external directory entry retained\n'
    fi
    exit 0
fi

python3 "$script_dir/install_manifest.py" install \
    --root "$repo_root" \
    --vault "$vault" \
    --hermes-home "$hermes_home" \
    --external-index "$external_index" \
    --config-entry-added "$(if [ "$duplicate" = false ]; then printf true; else printf false; fi)"

# Hermes v0.18.x `config set` assigns list indices in place and cannot append
# (`skills.external_dirs.N` for N == len raises IndexError), so the reference
# addition is a manual operator step, symmetric with uninstall's manual removal.
# verify-install.sh fails closed until the entry exists.
if [ "$duplicate" = false ]; then
    printf 'MANUAL CONFIG ADDITION REQUIRED: in %s/config.yaml, add %s as a new entry under skills.external_dirs; do not alter any other entry. The installer never edits config.yaml (symmetric with uninstall).\n' "$hermes_home" "$external_path"
    printf 'CONFIGURED: pending the manual skills.external_dirs addition above; run verify-install.sh to confirm activation\n'
else
    printf 'CONFIGURED: exact reference already present; config unchanged\n'
fi
