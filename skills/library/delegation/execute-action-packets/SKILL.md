---
{"name":"execute-action-packets","description":"Turn an approved recommendation list or handoff into bounded artifact changes with explicit scope, authority, dependencies, acceptance checks, and per-item dispositions. Use when asked to execute a report, checklist, or numbered action packet.","category":"delegation","source_rows":["agent-intelligence-economy:skills/action-packet-executor/SKILL.md","agent-intelligence-economy:templates/task-packet.json","agent-intelligence-economy:templates/result-packet.json","agent-intelligence-economy:examples/two-layer-report/example.md"],"license":"CC BY 4.0","triggers":["execute recommendations","make it so","action packet","numbered implementation list","report handoff"]}
---

# Execute Action Packets

## Reconstruct the contract

Translate every requested item into an outcome, target artifact or system, allowed mutations, forbidden surfaces, dependencies, acceptance evidence, and owner for unresolved decisions. Resolve contradictions and shared targets before editing. A recommendation is not authority to perform external, destructive, or unrelated actions.

## Execute by target

Group items that touch the same artifact so overlapping changes are integrated once. Preserve user work, use the smallest reversible change, and maintain a live item table with `pending`, `in progress`, and final disposition. When an item is blocked, continue independent authorized items and record the exact dependency.

If a worker performs an item, send the bounded contract and require returned handles: paths, diffs, test output, URLs, IDs, or an explicit no-change result. Verify side-effect claims against the actual artifact; a worker's completion statement is not acceptance evidence.

## Verify and close

Run the item-specific check after each risky mutation, then the integrated checks after all changes. Inspect output, not just exit status. Return a compact decision surface mapping every original item to changed handles, verification, remaining unknowns, and one supported disposition. Do not replace executed work with another plan.
