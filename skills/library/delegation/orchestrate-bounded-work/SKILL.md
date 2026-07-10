---
{"name":"orchestrate-bounded-work","description":"Coordinate direct tools, deterministic scripts, specialist workers, reviewers, and scheduled loops using the lightest adequate execution mode and verified artifact handoffs. Use for multi-part work with separable ownership or checks.","category":"delegation","source_rows":["agent-intelligence-economy:skills/orchestrator-operating-pattern/SKILL.md","agent-intelligence-economy:docs/10-orchestrator-pattern.md"],"license":"CC BY 4.0","triggers":["multi-part execution","worker coordination","task decomposition","parallel work","artifact integration"]}
---

# Orchestrate Bounded Work

## Select the lightest adequate mode

Start from the source of truth, then choose direct tools, a deterministic script, a specialist worker, a reviewer, or a governed recurring loop. Do not create a swarm when one bounded executor can finish the task. Parallelize only independent work with clear artifact boundaries.

## Define packets

Each task packet names the objective, inputs, allowed and forbidden surfaces, output schema, budget, dependencies, acceptance checks, and required evidence handles. Give a worker enough context to perform its bounded task without transferring unrelated secrets or authority.

Keep final integration with the orchestrator. Workers may investigate, draft, edit scoped artifacts, or run checks; they do not decide acceptance of their own side effects.

## Integrate from artifacts

Collect paths, diffs, test results, source coordinates, IDs, or explicit no-change reports. Inspect the returned artifacts and resolve overlaps before declaring completion. Re-run shared checks after integration because independently valid patches can conflict together.

Return accepted work, patched work, deferred dependencies, rejected outputs, and remaining unknowns. No-op and stop are valid outcomes when delegation adds more coordination cost than value.
