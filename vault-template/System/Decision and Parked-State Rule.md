---
license: CC BY 4.0
type: operating-rule
---

# Decision and Parked-State Rule

Every investigation ends with `act | watch | no-action | no-edge | blocked | done | merge | defer | kill | needs-human` and a next-state consequence.

Every `watch`, `no-action`, or `defer` decision must record:

- state-change condition;
- review or decay date;
- consequence if nothing changes;
- owner of the next review.

At decay, renew explicitly with new evidence, demote, merge, or kill. Silence is not renewal. Use [[Decisions/Decisions Map]] for durable packets and [[Reviews/Reviews Map]] for their outcomes.
