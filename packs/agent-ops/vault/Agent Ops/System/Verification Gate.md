---
license: CC BY 4.0
type: operating-rule
---

# Verification Gate

A worker or loop may report `done` only when the result packet identifies every artifact, runs an observable acceptance check, preserves exact outcome evidence, discloses deviations and blockers, and requests owner review. Process state, confident prose, or a fresh timestamp is not completion evidence.

Gate sequence:

1. match result to the originating task packet and its authority boundary;
2. inspect the returned artifact rather than the summary alone;
3. rerun proportionate acceptance checks from the source of truth;
4. classify each check `pass | fail | not-run` and preserve output;
5. compare changed paths with authorized write paths;
6. choose `accept | revise | defer | kill | escalate`.

Failed or unrun required checks block acceptance. Verification cannot grant authority forbidden by the task packet.
