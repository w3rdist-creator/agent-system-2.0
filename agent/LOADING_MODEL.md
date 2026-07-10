# Loading Model

The distribution uses three routing levels so the complete installed library does not become the startup context.

## Level 0 — startup category index

Load `skills/level-0-categories.yaml` with the unconditional `skills/core/capability-router/SKILL.md`. Level 0 contains only category names, one-sentence scopes, and escalation hints. It is capped at 15 categories and 400 approximate tokens.

## Level 1 — selected category registry

After choosing one category, load only `skills/categories/<category>/registry.yaml`. A registry exposes the skill names and compact descriptions in that category, with no more than 20 skills and descriptions targeting at most 350 characters. If the request crosses a real routing boundary, a second category may be loaded deliberately; do not load every registry for convenience.

## Level 2 — selected skill body

After choosing a skill, load only its full `SKILL.md`, normally from `skills/library/<category>/<skill>/SKILL.md` or `skills/core/<skill>/SKILL.md`. Explicit user requests for a named skill may route directly to Level 2 after confirming the path exists.

## Core loading policy

- `capability-router` is unconditional and always loaded.
- `evidence-first-operating-style` is task-shape-loaded for ambiguous, investigative, strategic, diagnostic, consequential, or high-stakes work. Pure formatting and trivial lookup may skip it.
- `source-grounding`, `knowledge-metabolism`, `loop-governance`, and `vault-operations` are installed core capabilities but trigger-loaded only when claims/research, durable knowledge revision, recurring-loop governance, or vault contact respectively makes them relevant.

The worst-case operational core is `SOUL.md` plus the capability router, Level 0, and the evidence-first operating skill. `scripts/audit_context_budget.py --profile core` enforces a 3,000-token approximate ceiling and compares that surface with the checked-in baseline.
