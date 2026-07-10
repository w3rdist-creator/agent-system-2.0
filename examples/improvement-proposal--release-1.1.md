# Improvement Proposal — Release 1.1

## Problem observed

Release 1.0 states machine-checkable safety rules without a runner hook, relies on manual vault intake and decay, has no cheap live examiner or self-collected usage evidence, defines only a single-user vault, and exposes ten runtime disposition labels with overlapping meanings.

## Evidence

The Release 1.0 implementation and its checked-in evaluations provide the baseline. Operator direction dated 2026-07-10 admitted six bounded additions: enforcement, metabolism, recertification, telemetry, a team vault contract, and disposition consolidation. Each addition has a shipped deterministic implementation or contract, tests, and documentation; the Release 1.1 paired evaluation record remains the behavioral evidence rather than this proposal.

## Who should notice improvement

A runner integrator wiring pre-tool-use checks; a vault operator processing captures; a maintainer checking live model behavior and release evidence; a governance reviewer deciding from usage rows; a small team coordinating a shared vault; and any agent or operator interpreting a disposition.

## Proposed destination

Six namespaced additions inside the existing distribution: `enforcement/` and its runner contract; `scripts/metabolism.py` and governed vault queues/ledger; `scripts/recert.sh` and the recert log; `scripts/telemetry.py` and the telemetry ledger; `docs/Team-Vault-Contract.md` plus its merge-proposal template; and one canonical seven-label runtime vocabulary with evaluation-only legacy aliases.

## What it replaces or merges

Enforcement replaces reliance on prose for three machine-checkable rules when a runner opts in. Metabolism replaces ad hoc Inbox routing and silent aging. Recert replaces improvised one-off smoke commands. Telemetry replaces manual counting of existing machine artifacts. The team contract replaces an undefined shared-vault boundary, not a sync product. The seven labels merge `merge` into `done`, `defer` into `watch`, and `no-edge` into `no-action`, while retaining aliases only for historical evaluation compatibility.

## Context, storage, and review cost

The enforcement and disposition changes must stay inside the existing core context ceilings. Metabolism adds bounded queue and ledger rows; recert adds one row per attempted smoke trial; telemetry adds only new date/source/metric keys from named sources; the team contract adds no automatic shared payload. Scheduling remains operator-owned. Every recurring surface has an explicit owner, cap or idempotency key, and review boundary.

## Blast radius

Runner tool execution, protected-path safety, vault file movement, append-only evidence ledgers, model API cost, shared-vault ownership, evaluation comparability, and maintainer review attention. No addition may edit Hermes `config.yaml`, install a scheduler, overwrite conflicts, infer permission from telemetry, or reinterpret a Release 1.0 certificate as evidence for the consolidated vocabulary.

## Verification method

Run the unit suite and full development gate; test enforcement allows and denials through its CLI contract; exercise metabolism routing, deduplication, decay, caps, and no-data behavior; exercise recert pass/fail/error logging; verify telemetry extraction, idempotency, and no-data behavior; validate team merge proposals and vault links; validate canonical dispositions and legacy alias normalization. Run the fixed paired evaluation after vocabulary changes and retain its full provenance, failures, arm-neutral instrument repairs, and any operator override.

## Kill or rollback condition

Demote enforcement to evaluation-harness-internal if no non-evaluation runner wires the hook within the supersession window and the harness remains its only consumer. Turn the metabolism loop off after two consecutive silent weeks, or sooner if it cannot preserve conflicts and user content. Disable scheduled recert if two consecutive scheduled attempts produce no reviewed row or if its rows are presented as paired certification. Kill the telemetry collector if no governance decision cites a telemetry row by the next release. Keep team support contract-only, and withdraw any tooling proposal, if it cannot preserve personal/shared boundaries and a single merge authority. Remove legacy disposition aliases after the historical records that require them leave the supported evaluation path; revert the consolidation if canonicalization makes stored outcomes ambiguous rather than mechanically recoverable.

## Why a simpler location is insufficient

Chat instructions cannot enforce a runner boundary, provide a repeatable filesystem transform, retain dated examiner evidence, or normalize machine output. A standalone team tool would overbuild beyond observed demand. The smallest sufficient locations are deterministic namespaced code for stable rules and transforms, append-only vault evidence for observed operations, and one explicit contract for shared ownership.

## Disposition

Act: ship the six bounded Release 1.1 additions under their stated wiring, evidence, ownership, and kill conditions; do not claim scheduler installation, team tooling, or threshold-meeting paired evidence.
