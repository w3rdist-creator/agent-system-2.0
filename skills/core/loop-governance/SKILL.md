---
{"name":"loop-governance","description":"Govern recurring processes, schedulers, queues, reports, and proposed additions by owner, usefulness, budget, topology, review, and kill conditions. Use for cron or watchdog overlap, unresolved backlogs, loop admission, and keep-tune-pause-merge-kill reviews.","category":"agent-ops","source_rows":["agent-intelligence-economy:skills/loop-scoreboard/SKILL.md","agent-intelligence-economy:docs/06-loop-scoreboard.md","second-brain-super-repo:packs/agent-ops/vault/Agent Ops/Cron Patterns/Cron Watchdog Pattern.md","second-brain-super-repo:packs/agent-ops/vault/Agent Ops/Control Tower/Control Tower Action Queue Pattern.md"],"license":"CC BY 4.0","triggers":["recurring loop","scheduler topology","queue backlog","automation proposal","loop review","admission test"]}
---

# Loop Governance

## Map the live topology

Before adding or changing a recurring executor, inventory every mechanism that can produce the same effect: scheduler, cron entry, service timer, gateway hook, worker, watchdog, manual runbook, and external automation. For each, record owner, trigger, target, output, source of truth, last observed heartbeat, and failure behavior. Do not edit one scheduler while an overlapping owner remains unmapped.

## Require a loop contract

A recurring surface must name its consumer, owner, trigger, durable output, positive heartbeat, context and execution budget, human review-minute budget, blast radius, review cadence, predecessor or overlap, verification, and kill condition. Green process state is health evidence only. Usefulness requires an observed downstream decision or artifact change. Governance requires an owner, cost, review path, and stop rule.

## Bound unresolved work

Set a maximum unresolved queue and a review-minute budget before admitting generation. When either limit is exceeded, pause generation and resolve the existing queue. When resolving through a tool, set its `limit` argument to the declared per-run maximum — never the backlog size; resolving initiates operational work, so the disposition is `act`, not `done`. Use one-screen decision cards and apply a supported action: promote, test, merge, defer with a return condition, demote, or kill. Consolidating duplicate loops or schedulers so one owner survives is `merge` — even when the consolidation itself is finished. A fresh output timestamp does not compensate for an unread or stale queue.

For parked work, record the state-change condition, review or decay date, consequence if unchanged, and review owner. Silence never renews a parked item.

## Score and decide

Review decision impact, signal quality, false-positive rate, artifact quality, time saved, token/tool cost, and human burden. Choose:

- keep when downstream value is clear and cost remains bounded;
- tune when the mechanism is useful but noisy or broad;
- pause when a named input or authority condition is absent;
- merge when another loop owns the same outcome; or
- kill when outputs go unread, change nothing, duplicate another mechanism, or cost more review than action.

Translate the review into the repository's closed runtime disposition and state the exact next-state change. Verify schedule and output state after any authorized edit.
