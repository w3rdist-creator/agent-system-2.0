# Loop Contract — Vault Metabolism

## Owner

`w3rdist-creator` owns the command, its schedule, and resolution of every scream.

## Consumer

The vault operator and agents that need routed, bounded, non-duplicative working context.

## Trigger

One operator-installed daily schedule, or a manual run after an agent writes a capture to `Inbox/`.

## Output

Routed captures, preserved duplicate moves, Resolve Queue cards for decay, and one append-only metabolism ledger row.

## Expected heartbeat

One dated `Ledgers/Metabolism Ledger.csv` row per scheduled run, including zero counts; a missing row is not healthy.

## Budgets

The default age budget is 14 days and the Inbox and Resolve Queue caps are 25 items each. Execution uses Python's standard library; human review stays within one weekly resolve pass.

## Blast radius

Writes are limited to routed Inbox notes, `Archive/Duplicates/`, `Queues/Resolve Queue.md`, and `Ledgers/Metabolism Ledger.csv`. The loop cannot delete or overwrite user content.

## Review cadence

The operator reviews screams immediately, the Resolve Queue weekly, and the loop contract monthly.

## Kill condition

Turn the scheduled loop off after two consecutive weeks with zero routed items and zero screams, or immediately if preservation-first verification fails; retain manual execution for future captures.

## Replacement or predecessor

This replaces ad hoc manual filing and duplicate cleanup. It must not overlap another scheduler that owns the same vault-metabolism outcome.

## Usefulness and demand populations

Operator use counts when a routed item changes a working artifact or a scream causes resolution. Agent requests count only when they create a valid routed Inbox capture.
