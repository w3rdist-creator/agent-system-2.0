---
license: CC BY 4.0
type: operating-rule
---

# Health, Usefulness, and Governance Scorecard

Score each axis independently; health never substitutes for usefulness or governance.

| Axis | Required evidence | Pass condition | Failure disposition |
|---|---|---|---|
| Health | last verified execution, expected artifact, error state | observed execution and artifact match the declared contract | repair or pause |
| Usefulness | named consumer and downstream decision, artifact, or rule change | at least one verified change inside the review window | tune, done (record any merge), or kill |
| Governance | owner, source of truth, cost, review cadence, authority, rollback, kill rule | every field is current and one scheduler owns execution | pause until owned |

Record `pass | fail | unknown` per axis with an evidence handle and date. Overall state is `keep` only when all three pass. Unknown is not green. A healthy but unused loop is a kill candidate; a useful but unowned loop pauses until governance is restored.
