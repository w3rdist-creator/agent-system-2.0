---
license: CC BY 4.0
type: queue
seed: true
source_rows:
  - second-brain-super-repo:packs/agent-ops/vault/Agent Ops/Control Tower/Control Tower Action Queue Pattern.md
  - agent-intelligence-economy:docs/06-loop-scoreboard.md
---

# Resolve Queue

- **Maximum unresolved backlog:** 7 cards
- **Weekly human review-minute budget:** 45 minutes
- **Generation-pause threshold:** pause every contributing generator before it creates item 8, or as soon as estimated unresolved review work exceeds 45 minutes; resume only when both measures are within budget
- **Owner:** `w3rdist-creator`
- **Review cadence:** weekly while any card is unresolved

Each one-screen card records stable ID, first/last seen, owner, severity, evidence, minutes estimated, decision needed, `promote | test | done | watch | demote | kill`, return condition, and state change. `done` records a verified merge. Adding reviewers or capacity is not a resolution.

## Seed card — resolved

- **ID:** AO-RQ-2026-07-10-001
- **First/last seen:** 2026-07-10
- **Decision:** should a second recurring executor ship for the same deterministic watchdog outcome?
- **Evidence:** CSV rows 81, 82, and 279; task/result packet pair
- **Review estimate / actual:** 10 / 8 minutes
- **Disposition:** `kill`
- **State change:** Release 1.0 retains one scheduler owner and no second executor
- **Return condition:** a distinct target, owner, source of truth, and failure behavior that cannot be served by the existing scheduler
- **Status:** resolved; does not consume unresolved capacity
