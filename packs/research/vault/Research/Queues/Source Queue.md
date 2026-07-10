---
license: CC BY 4.0
type: queue
seed: true
source_rows:
  - second-brain-os-powerpack:vault-addons/System/Loop Library/Source To Synthesis Loop.md
  - agent-intelligence-economy:docs/06-loop-scoreboard.md
---

# Source Queue

Queue only sources with a named question and exit route. Search this queue, Sources, Patterns, and the claim/evidence ledger before adding a row.

| Queue ID | Source row | Question | Owner | State | Snapshot | Exit |
|---|---|---|---|---|---|---|
| RQ-2026-07-10-01 | CSV 68 | What prevents source capture from becoming unused accumulation? | Phase 5 executor | synthesized | `Raw/Research/Source Snapshot - Source to Synthesis.md` | merged into seed pattern |
| RQ-2026-07-10-02 | CSV 279 | What makes a recurring loop earn continued operation? | Phase 5 executor | synthesized | `Raw/Research/Source Snapshot - Loop Scoreboard.md` | merged into seed pattern |

Allowed states: `queued | captured | preserved | read | synthesized | applied | superseded | rejected`. A row exits by application, merge, explicit defer with return condition, non-connection, or rejection; it does not remain open merely because a snapshot exists.
