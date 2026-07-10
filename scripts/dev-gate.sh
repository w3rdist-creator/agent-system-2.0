#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(dirname "$script_dir")
vault=/tmp/evidence-first-test-vault
hermes_home=/tmp/evidence-first-test-hermes
uninstall_output=/tmp/evidence-first-uninstall-output.txt
dry_run_output=/tmp/evidence-first-dry-run-output.txt

cd "$repo_root"

python3 -m unittest discover -s tests -v
python3 scripts/verify_repo.py .
python3 scripts/verify_private_markers.py .
python3 scripts/verify_licenses.py source-packages skills templates packs
python3 scripts/verify_wikilinks.py vault-template packs examples
python3 scripts/verify_skills.py agent skills
python3 scripts/audit_context_budget.py --profile core
python3 scripts/evaluate_scenarios.py evaluations --schema-only
python3 scripts/score_loops.py vault-template/System templates examples
bash scripts/list-packs.sh
python3 scripts/install_manifest.py --help >/dev/null
bash -n scripts/publication-gate.sh
bash -n scripts/export-public.sh

python3 - "$vault" "$hermes_home" "$uninstall_output" "$dry_run_output" <<'PY'
from pathlib import Path
import shutil
import sys

for raw in sys.argv[1:]:
    path = Path(raw)
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
PY

cp -R tests/fixtures/hermes-home "$hermes_home"
chmod +x "$hermes_home/bin/hermes"
export PATH="$hermes_home/bin:$PATH"

bash scripts/install.sh \
  --dry-run \
  --vault "$vault" \
  --hermes-home "$hermes_home" > "$dry_run_output"

test ! -e "$vault"
test ! -e "$hermes_home/distributions"
grep -F "DRY RUN: no files or Hermes configuration will be written" "$dry_run_output" >/dev/null
grep -F "PLAN config:" "$dry_run_output" >/dev/null
dry_run_operations=$(grep -c '^PLAN ' "$dry_run_output")
printf 'PASS: dry run wrote nothing and listed %s planned operation(s)\n' "$dry_run_operations"

install_output=/tmp/evidence-first-install-output.txt
bash scripts/install.sh \
  --vault "$vault" \
  --hermes-home "$hermes_home" | tee "$install_output"
grep -F "MANUAL CONFIG ADDITION REQUIRED" "$install_output" >/dev/null

# Fail-closed check: verify must refuse activation before the manual step.
if bash scripts/verify-install.sh --vault "$vault" --hermes-home "$hermes_home" >/dev/null 2>&1; then
  printf 'FAIL: verify-install passed without the manual config addition\n' >&2
  exit 1
fi
printf 'PASS: verify-install fails closed until the manual config addition\n'

# Simulate the operator performing the documented manual addition.
python3 - "$hermes_home/config.yaml" "$hermes_home/distributions/evidence-first/skills" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()
anchor = next(i for i, line in enumerate(lines) if line.strip() == "external_dirs:")
lines.insert(anchor + 1, f"    - {sys.argv[2]}")
path.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

bash scripts/verify-install.sh \
  --vault "$vault" \
  --hermes-home "$hermes_home"

bash scripts/install-pack.sh research --vault "$vault"
bash scripts/install-pack.sh agent-ops --vault "$vault"

bash scripts/verify-install.sh \
  --vault "$vault" \
  --hermes-home "$hermes_home"

modified_file=$(python3 - "$hermes_home/distributions/evidence-first/agent/SOUL.md" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).resolve())
PY
)
printf '\nuser modification retained by uninstall gate\n' >> "$modified_file"

mkdir -p "$vault/Sources"
user_file="$vault/Sources/user-owned.md"
printf 'user content\n' > "$user_file"

config_hash_before=$(python3 - "$hermes_home/config.yaml" <<'PY'
from hashlib import sha256
from pathlib import Path
import sys
print(sha256(Path(sys.argv[1]).read_bytes()).hexdigest())
PY
)

bash scripts/uninstall.sh \
  --vault "$vault" \
  --hermes-home "$hermes_home" > "$uninstall_output"

config_hash_after=$(python3 - "$hermes_home/config.yaml" <<'PY'
from hashlib import sha256
from pathlib import Path
import sys
print(sha256(Path(sys.argv[1]).read_bytes()).hexdigest())
PY
)

test "$config_hash_before" = "$config_hash_after"
grep -F "WARNING: modified distribution-owned file preserved: $modified_file" "$uninstall_output" >/dev/null
grep -F "MANUAL CONFIG REMOVAL REQUIRED" "$uninstall_output" >/dev/null
grep -F "WARNING: modified distribution-owned file preserved: $modified_file" "$uninstall_output"
grep -F "MANUAL CONFIG REMOVAL REQUIRED" "$uninstall_output"
grep -F "UNINSTALL REPORT:" "$uninstall_output"
test -f "$hermes_home/bin/hermes"
test -f "$hermes_home/config.yaml"

bash scripts/verify-install.sh \
  --expect-absent \
  --preserve "$user_file" \
  --preserve "$modified_file" \
  --vault "$vault" \
  --hermes-home "$hermes_home"

git diff --check
printf 'PASS: Phase 6 dev gate completed end to end with fixtures %s and %s\n' "$vault" "$hermes_home"
