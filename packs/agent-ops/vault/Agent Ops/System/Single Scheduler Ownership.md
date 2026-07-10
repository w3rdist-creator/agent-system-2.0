---
license: CC BY 4.0
type: operating-rule
seed: true
source_rows:
  - second-brain-super-repo:packs/agent-ops/vault/Agent Ops/Cron Patterns/Cron Watchdog Pattern.md
  - second-brain-super-repo:packs/agent-ops/vault/Agent Ops/Control Tower/Control Tower Action Queue Pattern.md
  - agent-intelligence-economy:docs/06-loop-scoreboard.md
---

# Single Scheduler Ownership

One outcome has one scheduler owner. Before adding or editing recurring execution, inventory schedulers, cron entries, service timers, gateways, watchdogs, manual runbooks, and external automation that can produce the same effect.

For each candidate record owner, trigger, target, source of truth, durable output, positive heartbeat, timeout, retry behavior, deduplication key, queue destination, last verified execution, and kill path. If two mechanisms share target and outcome, pause the proposed addition until ownership is merged or the outcomes are proved distinct.

The generic double-scheduler failure class is duplicate execution followed by competing retries, alerts, or writes. A healthy heartbeat from either scheduler can hide ambiguous ownership; it cannot prove the topology is correct. Do not encode private hostnames, machine names, schedules, or live infrastructure in this pack.

Prefer deterministic script-only execution when reasoning is unnecessary. Use a stable queue ID and deduplicate standing failures. After an authorized scheduler change, verify both presence of the intended executor and absence of the retired overlap.
