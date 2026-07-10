# Sanitization and Publication

Publication uses two repositories and two gates. The BUILD repository preserves advisor-reviewed phase history and is never pushed. The EXPORT repository is a fresh sanitized tree with exactly one commit and no remote until the operator publishes.

## Roles

- **Executor:** prepares documents, runs deterministic gates, creates the fresh one-commit export, and never configures a remote or pushes.
- **Advisor:** reviews and commits BUILD phases; the executor does not commit Phase 7 in BUILD.
- **Operator:** performs the human sanitization and license decisions, clean-room install, paired-evaluation judgment, GitHub creation, remote configuration, push, and any later predecessor deprecation.

Release 1.0 is described as operator-reviewed, not independently audited. Regex scanners are necessary but cannot decide whether a transformed example still exposes a real private engagement.

## Development gate (A5)

Run in BUILD and CI:

```bash
bash scripts/dev-gate.sh
```

It runs unit tests, all structural/content verifiers, the worktree privacy scan, schema-only evaluation, pack listing, dry-run/install/verify/both-pack/uninstall preservation cycle, and `git diff --check`. It does not scan Git history and does not run a model.

## Fresh sanitized export (A4)

The export script requires an absent destination and refuses a BUILD repository with a configured remote. It uses rsync while excluding `.git/`, `_build/`, editor/cache artifacts, initializes `main`, creates exactly one commit named `Release 1.0 candidate` with a non-personal command-scoped identity, and invokes the publication gate:

```bash
bash scripts/export-public.sh
```

Default output:

```text
~/Code/evidence-first-hermes-distribution-public/
```

No BUILD history is copied. `CHANGELOG.md` carries the public build narrative.

## Publication gate (A4/A5)

Run only inside EXPORT:

```bash
cd ~/Code/evidence-first-hermes-distribution-public
bash scripts/publication-gate.sh
```

The gate asserts:

- one reachable commit (`git rev-list --all --count == 1`);
- the only ref is `refs/heads/main`;
- no remote is configured;
- the export worktree matches its commit;
- the worktree private-marker scan passes;
- `git log --all -p` passes the full-history private-marker scan.

An external denylist may be supplied for a separate scanner run, but it must live outside the repository. A clean regex scan is not operator sanitization approval.

## Remaining human gates

Before the operator adds a remote:

1. inspect every accepted/adapted artifact and shipped seed for privacy and public suitability;
2. confirm or change the MIT/CC BY 4.0 split and record the decision in the effort ledger;
3. run paired model evaluations and review the hidden human-judgment rows, or sign the allowed threshold override with rationale;
4. perform and record a non-builder clean-room install;
5. replace the public account placeholder, amend the one candidate commit, and rerun both gates;
6. execute only the commands in [Publication Commands](Publication-Commands.md).

