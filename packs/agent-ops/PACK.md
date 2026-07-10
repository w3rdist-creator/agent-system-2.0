---
license: CC BY 4.0
---

# Agent Ops Pack

- **Status:** shipped
- **Consumer:** the operator's repeated health, verification, reporting, and bounded worker-packet workflows
- **Owner:** `w3rdist-creator`
- **Activation trigger:** explicit installation for governed agent operations
- **Kill condition:** uninstall or demote when operations artifacts produce no verified decision or state change in two reviews, duplicate an owned control surface, or exceed the declared review budget
- **Vault payload:** `vault/`, copied relative to a target vault root

## Core contract

The pack ships a health/usefulness/governance scorecard, manual Resolve Queue with a cap and review budget, verification gate, Phase 4-compatible task/result packet examples, single-scheduler ownership rule, two-layer report, loop scoreboard with a real kill decision, and a reviewed seed chain.

## Seed source rows

- CSV row 81: `second-brain-super-repo:packs/agent-ops/vault/Agent Ops/Control Tower/Control Tower Action Queue Pattern.md`
- CSV row 82: `second-brain-super-repo:packs/agent-ops/vault/Agent Ops/Cron Patterns/Cron Watchdog Pattern.md`
- CSV row 279: `agent-intelligence-economy:docs/06-loop-scoreboard.md`
- CSV row 365: `agent-intelligence-economy:templates/loop-scoreboard.csv`

The seed is a real Release 1.0 design review of a second-scheduler proposal. It does not claim a private incident or live topology. Operator confirmation remains pending as recorded in `examples/use-evidence--agent-ops.md`.

## Version 1.1 trigger list

Empty after Phase 5 implementation. All three A2 deferrables shipped as bounded, domain-neutral contracts:

- prediction/calibration ledger — dated resolver, source of record, base rate or confidence, falsifier, outcome, score, and rule update;
- operator correction ledger — append-preserving events, with one event updating a hypothesis and standing doctrine changing only after repeated evidence or an explicit strong instruction;
- failure review — evidence, cause, corrective action, verification, and rollback template.

Future additions require a named operator decision, a source row, and a bounded review budget. Deferrable source basis: CSV rows 370, 373, and 84 respectively.
