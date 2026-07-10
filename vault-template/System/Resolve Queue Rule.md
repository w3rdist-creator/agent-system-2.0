---
license: CC BY 4.0
type: operating-rule
---

# Resolve Queue Rule

Every recurring generator, intake lane, or candidate queue declares a maximum unresolved count and a weekly review-minute budget. When either limit is exceeded, generation pauses.

A bounded resolve pass applies `promote | test | watch | kill | done | demote` until the queue is back within both budgets; `done` records a verified merge. The owner records the disposition and next-state consequence; adding capacity without resolving existing debt is not a pass.

Unrouted captures begin at [[Inbox/Inbox Map]]; review outcomes belong in [[Reviews/Reviews Map]].
