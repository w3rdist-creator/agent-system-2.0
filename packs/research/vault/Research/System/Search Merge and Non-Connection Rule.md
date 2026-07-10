---
license: CC BY 4.0
type: operating-rule
---

# Search, Merge, and Non-Connection Rule

Before creating a source note, claim, or pattern, search titles, stable source coordinates, aliases, claim text, and mechanism text across the queue, Sources, Patterns, and ledgers.

Classify the nearest result before writing:

- `duplicate`: merge into the existing artifact and preserve both provenance paths;
- `expected hierarchy`: link to the local map without cloning content;
- `bridge`: create only after two sourced domains and a causal mechanism exist;
- `disagreement`: preserve both claims until evidence resolves scope or method;
- `reconciliation candidate`: record the test that could align them;
- `noise`: reject without a durable synthesis note.

Merge before duplicating. Append the new evidence, keep the earlier state, and record the merge in the claim ledger.

When a bridge fails, route a compact `non_connection` result containing the attempted domains, missing causal link, counterexample or boundary, evidence checked, and return condition. A null result may remain in the ledger to prevent repeated work; it must not be softened into a pattern merely to justify capture.
