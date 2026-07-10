# Loop Contract — Vault Link Verification

## Owner

`w3rdist-creator` owns the verification contract.

## Consumer

Maintainers changing vault, pack, or example Markdown.

## Trigger

Every development gate and any change to a wikilink-bearing note.

## Output

A deterministic pass or a path-and-target failure report.

## Expected heartbeat

The command reports the count of scanned Markdown files and checked links.

## Budgets

Read-only local execution, no network, no generated state, and less than one minute of reviewer attention on success.

## Blast radius

Only release gating; no content is mutated.

## Review cadence

Review when the vault folder contract or link syntax changes.

## Kill condition

Replace the loop if the supported vault engine provides an equally deterministic repository gate with Raw-boundary coverage.

## Replacement or predecessor

Replaces manual Phase 4 link spot-checks.

## Usefulness and demand populations

Operator gate runs satisfy usefulness; only an external maintainer request activates demand for additional link syntaxes.
