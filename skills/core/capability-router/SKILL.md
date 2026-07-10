---
{"name":"capability-router","description":"Route a request through the bounded Level-0 category index, one selected registry, and one narrow skill body. Use at startup, when a capability is ambiguous, or when an optional provider may be missing.","category":"governance","source_rows":["agent-intelligence-economy:skills/token-efficiency-router/SKILL.md","agent-intelligence-economy:docs/12-context-layering.md"],"license":"CC BY 4.0","triggers":["startup routing","capability selection","missing optional provider","explicit skill request"]}
---

# Capability Router

## Purpose

Select the smallest relevant capability surface without loading the full installed catalog. This skill is unconditional; the catalog bodies are not.

## Route through the three levels

1. Read Level 0 at `skills/level-0-categories.yaml` and compare the request with each category's `scope`.
2. Select one best-fit category. Use its `escalation` hint when the request is outside that scope or crosses an authority, safety, or ownership boundary.
3. Load only that category's Level 1 registry at `skills/categories/<category>/registry.yaml`.
4. Compare the registry's compact descriptions and select the narrowest skill that covers the task.
5. Load that skill's Level 2 body (`skills/library/<category>/<skill>/SKILL.md` or `skills/core/<skill>/SKILL.md`).

If the user names an installed skill, route directly to its Level 2 body after confirming the path; do not load unrelated registries to validate it.

## Task-shape core

Load `skills/core/evidence-first-operating-style/SKILL.md` when the work is ambiguous, investigative, strategic, diagnostic, consequential, or high-stakes. Skip only for pure formatting or a trivial lookup with a clear source; formatting a consequential claim is not pure formatting.

The other core skills are trigger-loaded:

- `source-grounding` for external claims, research, freshness, provenance, or source-authority questions;
- `knowledge-metabolism` for durable capture, belief revision, promotion, or demotion;
- `loop-governance` for recurring processes, queues, schedulers, admission, budgets, or kill decisions; and
- `vault-operations` for vault reads, writes, structure, links, merging, or deletion.

## Escalation rules

- If two categories are genuinely required, load the owning category first, then the second explicitly; never expand to all.
- If no category fits, report the missing route and use the category's escalation hint; never invent a skill or silently call an optional provider.
- A registry with `status: no-local-skills` is a valid terminal answer: report its `external_pointer` and continue without a local skill. Empty-by-design is deferred capability, not a fault.
- If a registry is absent, malformed, over limit, or points to a missing skill, stop that route and report the fault; unrelated work may continue through valid routes.
- If authority or safety is unclear, load the governance route or the applicable authority record before acting.
- If the request can be completed safely with a local or lower-cost capability, an unavailable optional provider is degradation, not a blocker: verify the recorded provider state from the provided status files, use the local capability, complete the task, and report `done`.

## Context discipline

Before selecting any capability path, read the provided provider, status, and config files; routing against unread recorded state is unrouted. Level 0 — the smallest provided index — is the only catalog surface permitted at startup. A route leaves an auditable chain — category, registry, skill — without retaining bodies no longer needed. Never read a full catalog or complete-inventory file (any file listing everything installed) unless the task's outcome requires its content; the small index plus targeted reads answer routing questions.
