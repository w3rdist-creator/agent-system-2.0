# Improvement Proposal — Release 1.2

## Problem observed

Release 1.1 enforces machine-checkable rules before tool use but not at completion, has no safe in-place release upgrade, retains two scenarios that no longer discriminate on a strong model, and leaves rejection of a candidate ambiguous between `kill` and `no-action`.

## Evidence

The completion gate was scoped from the 1.1 paired-run disposition-surface failures. Telemetry citation to discharge the 1.1 kill condition: the completion gate was scoped from the 1.1 paired-run disposition-surface failures; the vault Telemetry Ledger built from the checked-in 1.1 and 1.2 transcript sets contains 703 rows including 30 disposition.watch/disposition.no-action rows — cite this as the governance decision that consumed telemetry. This governance citation discharges the 1.1 kill condition that required a governance decision to cite a telemetry row by the next release.

The 1.1 release created the first real upgrade need, activating the roadmap trigger for upgrade tooling. Scenarios 01 and 05: two live-probed redesign rounds passed both arms; both marked Baseline absorbed (gpt-5.6-sol high, 2026-07-10), retained as regression canaries, excluded from surviving delta accounting; tuning record at evaluations/results/tuning-2026-07-10-gpt-5.6-sol-scenarios-01-05.md; their SOUL lines are annotated pruning candidates for 1.3. The scenario 03 result exposed the missing semantic boundary between rejecting a candidate and deliberately leaving world state unchanged.

Paired 96-trial run on gpt-5.6-sol reasoning high, 2026-07-10, checked in at evaluations/results/run-2026-07-10-gpt-5.6-sol-1.2.csv: 6/14 surviving confirmed deltas (below the fixed threshold of 8; operator-directed release override recorded per-row), treatment 3/3 on 9/16; the kill/no-action boundary rule converted scenarios 03, 10, and 13 into confirmed deltas; scenarios 04 and 08 each lost one trial to blocked-vs-kill and act-vs-done label blurs, recorded as 1.3 boundary data.

## Who should notice improvement

A runner integrator enforcing both proposed actions and final-answer surfaces; an operator moving from an older installed release without losing modifications; an evaluation maintainer distinguishing doctrine contribution from absorbed baseline behavior; and any agent or reviewer assigning `kill` or `no-action`.

## Proposed destination

Four bounded additions inside existing surfaces: `enforcement/completion.py` and `enforcement/completion_gate.py`; `scripts/upgrade.sh` plus schema-2 manifest migration; redesigned scenario 01 and 05 fixtures retained under their existing evaluation paths with baseline-absorbed metadata; and one canonical kill/no-action sentence in the loaded disposition doctrine with aligned scenario 03 expectations and quickstart guidance.

## What it replaces or merges

The completion gate closes the enforcement pair: pre-tool-use on the way in and completion on the way out. Manifest migration replaces uninstall-and-reinstall as the normal base-distribution update path without replacing the safe fallback. Baseline-absorbed metadata replaces repeated trap redesign for behaviors already supplied by the model. The boundary rule replaces label ambiguity: rejecting a proposal, candidate, or mechanism is `kill`; `no-action` leaves world state deliberately unchanged after investigation.

## Context, storage, and review cost

The completion rule stays in the existing policy payload and core budget. Upgrade adds one script, schema metadata, and only conflict-driven `.incoming` proposals; it does not copy packs or user content. The redesigned scenarios retain the fixed three-trial arms and checked-in tuning record but no longer count toward the surviving-delta denominator. The boundary costs one load-bearing doctrine sentence and aligned evaluation metadata.

## Blast radius

Runner publication of final answers, manifest-owned distribution files, user-modified owned files, evaluation denominators, historical comparison, and disposition reporting. No addition may edit `config.yaml`, overwrite a user modification or existing `.incoming` conflict, upgrade installed packs or user content, count baseline-absorbed canaries as surviving deltas, or treat lexical completion checks as proof of answer quality.

## Verification method

Run the unit suite and full development gate, including the outbound gate cases and the new same-version upgrade leg. Verify schema-1 manifests migrate to schema 2, user-modified files remain byte-identical, new distribution payload arrives as `.incoming`, `config.yaml` remains byte-identical, and installed packs remain untouched. Keep scenario schemas and deterministic assertions green, retain both redesign rounds, exclude baseline-absorbed scenarios from surviving accounting, and run the fixed paired evaluation with per-row provenance and any operator override.

## Kill or rollback condition

Remove the completion gate if two reviewed releases show its regex surface admits missing parked-state meaning or blocks valid parked states often enough that a bounded policy-pattern correction cannot fix it; it must never be represented as semantic grading. Revert upgrade automation to the documented uninstall/reinstall fallback on any verified overwrite of user content, `config.yaml` edit, pack mutation, unrecoverable partial migration, or manifest downgrade. Remove scenarios 01 and 05 from the active canary set if their retained fixtures stop detecting a regression across two reviewed releases; do not redesign them merely to manufacture control failures. Revert the kill/no-action sentence if reviewed artifacts remain mechanically ambiguous after the artifact-under-judgment is named; otherwise treat recurring `blocked`/`kill` and `act`/`done` blurs as 1.3 boundary data rather than silently moving assertions.

## Why a simpler location is insufficient

Prompt reminders cannot fail closed at the runner boundary or preserve files according to old-manifest hashes. Deleting baseline scenarios would lose useful regression coverage, while continuing to count them would distort the behavioral denominator. A local scenario-only label repair would leave the same disposition ambiguity everywhere else, so the rule belongs in the single loaded vocabulary surface.

## Disposition

Act: ship the four bounded Release 1.2 additions with the completion and upgrade boundaries explicit, scenarios 01 and 05 retained only as regression canaries, the telemetry kill condition discharged by this governance citation, and the paired result reported without promoting the operator override to a threshold pass.
