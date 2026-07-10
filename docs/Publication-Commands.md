# Operator-Only Publication Commands

These commands are documentation, not executor authorization. Only the operator runs them. Run them from the sanitized EXPORT repository, never from BUILD.

## 1. Close human release gates before any remote exists

Set the publishing account and review the remaining placeholders:

```bash
cd "$HOME/Code/evidence-first-hermes-distribution-public"
export ACCOUNT='YOUR-GITHUB-ACCOUNT'

git grep -n 'w3rdist-creator'
git grep -n 'operator-confirmation: pending' docs/Effort-Ledger.md
```

The operator must complete and record sanitization sign-off, the split-license decision, paired-model results/judgment, and a non-builder clean-room install. Replace the account placeholder only after those decisions:

```bash
git grep -l 'w3rdist-creator' | while IFS= read -r file; do
  ACCOUNT="$ACCOUNT" perl -pi -e 's/w3rdist-creator/$ENV{ACCOUNT}/g' "$file"
done

# Edit docs/Effort-Ledger.md to record the actual human-gate evidence.
${EDITOR:-vi} docs/Effort-Ledger.md

git add -A
git diff --cached --check
git -c user.name='Evidence First Contributors' \
    -c user.email='contributors' \
    commit --amend --no-edit

bash scripts/dev-gate.sh
bash scripts/publication-gate.sh
test -z "$(git remote)"
test "$(git rev-list --all --count)" -eq 1
test "$(git for-each-ref --format='%(refname)')" = 'refs/heads/main'
```

Do not proceed on a failed command. The amend retains one commit; the rerun ensures the reviewed bytes, worktree, and history are the bytes about to publish.

## 2. Recheck frozen predecessor metadata

Phase 0 froze source content and recorded public metadata on 2026-07-10; the build environment did not perform a later live recheck. Before publication, use the GitHub API and retain the output with the handoff record:

```bash
export PREDECESSOR_OWNER="$ACCOUNT"
for repo in \
  second-brain-os-starter \
  second-brain-os-powerpack \
  second-brain-super-repo \
  agent-intelligence-economy \
  agent-intelligence-context-pack
do
  gh api "repos/$PREDECESSOR_OWNER/$repo" \
    --jq '{full_name,visibility,archived,stargazers_count,forks_count,open_issues_count,pushed_at,default_branch}'
done
```

If the repositories are owned elsewhere, set `PREDECESSOR_OWNER` to that account. Record any divergence; do not rewrite the frozen file denominator without a separately reviewed source update.

## 3. Create the GitHub repository, add the first remote, and push

This is the first point at which any remote may be configured:

```bash
gh repo create "$ACCOUNT/agent-system-2.0" \
  --public \
  --description 'Agent System 2.0 — evidence-first Hermes distribution with routed skills, governed vaults, and safe lifecycle tools'

git remote add origin "https://github.com/$ACCOUNT/agent-system-2.0.git"
git remote -v
git push -u origin main
```

After the push, enable branch protection and required checks in GitHub settings. Do not claim a tagged 1.0 release until the pushed `verify` workflow is green.

## 4. Predecessor deprecation — DO NOT RUN YET

**DO NOT RUN until all release gates pass, the non-builder clean-room install is recorded, at least five real uses occur during the blocker-free 30-day window, and the operator separately approves supersession.** Publication of the successor alone does not satisfy these conditions.

When and only when those conditions pass, use fresh predecessor clones so no remote is added to BUILD or EXPORT:

```bash
export PUBLIC_URL="https://github.com/$ACCOUNT/agent-system-2.0"
export DEPRECATION_WORK="$HOME/Code/evidence-first-predecessor-deprecation"
mkdir -p "$DEPRECATION_WORK"

for repo in \
  second-brain-os-starter \
  second-brain-os-powerpack \
  second-brain-super-repo \
  agent-intelligence-economy \
  agent-intelligence-context-pack
do
  gh repo clone "$PREDECESSOR_OWNER/$repo" "$DEPRECATION_WORK/$repo"
  (
    cd "$DEPRECATION_WORK/$repo"
    python3 - "$PUBLIC_URL" <<'PY'
from pathlib import Path
import sys

readme = Path("README.md")
old = readme.read_text(encoding="utf-8")
notice = (
    "> **Read-only / superseded.** This repository is preserved for provenance. "
    f"Its conditionally verified successor is [{sys.argv[1]}]({sys.argv[1]}).\n\n"
)
if old.startswith(notice):
    raise SystemExit("deprecation notice already present")
readme.write_text(notice + old, encoding="utf-8")
PY
    git diff --check
    git add README.md
    git commit -m 'mark repository read-only and superseded'
    git push origin HEAD
  )
done
```

Verify all five public README pages after pushing. Archiving the predecessor repositories is a separate operator decision; README deprecation is mandatory under the supersession contract.

## 5. Updates after first publication

The one-commit publication gate remains correct for each fresh sanitized export, but the existing public clone gains commits after its first release. For the BUILD gate, fresh-export step, account substitution, `rsync` update, public commit and push, CI check, and tag sequence, follow [Update Gate](Update-Gate.md). Remote writes, public-clone commits, pushes, CI judgment, and tagging remain operator-only.
