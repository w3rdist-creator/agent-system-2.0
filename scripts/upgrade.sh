#!/bin/sh
set -eu

usage() {
    cat <<'EOF'
Usage: upgrade.sh --vault PATH [--hermes-home PATH] [--dry-run] [--force-unsupported]

Upgrades a manifest-owned Evidence First installation for Hermes v0.18.x.
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

hermes_home=$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$hermes_home")
vault=$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$vault")
manifest=$vault/.evidence-first/install-manifest.json
[ -f "$manifest" ] || { printf 'ERROR: install manifest not found; run install.sh before upgrade\n' >&2; exit 1; }

hermes_bin=${HERMES_BIN:-}
if [ -z "$hermes_bin" ]; then
    hermes_bin=$(command -v hermes 2>/dev/null || true)
fi
if [ -z "$hermes_bin" ]; then
    if [ "$force_unsupported" = false ]; then
        printf 'ERROR: Hermes version undetectable; install Hermes v0.18.x or use --force-unsupported at your own risk\n' >&2
        exit 1
    fi
    version_output='forced-undetectable-version'
else
    if ! version_output=$("$hermes_bin" --version 2>&1); then
        if [ "$force_unsupported" = false ]; then
            printf 'ERROR: Hermes version undetectable; version command failed before any write\n' >&2
            exit 1
        fi
        version_output='forced-undetectable-version'
    fi
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

printf 'COMPATIBLE: %s\n' "$version_output"
if [ "$dry_run" = true ]; then
    printf 'DRY RUN: no files, manifest, or Hermes configuration will be written\n'
    python3 "$script_dir/install_manifest.py" upgrade \
        --dry-run --root "$repo_root" --vault "$vault" --hermes-home "$hermes_home"
else
    python3 "$script_dir/install_manifest.py" upgrade \
        --root "$repo_root" --vault "$vault" --hermes-home "$hermes_home"
fi

external_path=$hermes_home/distributions/evidence-first/skills
if inspection=$(python3 "$script_dir/install_manifest.py" inspect-config --hermes-home "$hermes_home" --desired "$external_path"); then
    configured=$(printf '%s\n' "$inspection" | sed -n '2p')
    if [ "$configured" = true ]; then
        printf 'CONFIG: unchanged; the existing skills.external_dirs path remains valid, so no manual config step is required\n'
    else
        printf 'WARNING: config.yaml was unchanged, but the existing skills.external_dirs activation entry is missing; follow the original install.sh manual step\n'
    fi
else
    printf 'WARNING: config.yaml was unchanged, but skills.external_dirs could not be inspected\n'
fi
printf 'PLUGIN: files were upgraded preservation-first; if not already active, run hermes plugins enable evidence-first-enforcement and restart the Hermes gateway\n'
