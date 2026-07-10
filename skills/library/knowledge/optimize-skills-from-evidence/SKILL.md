---
{"name":"optimize-skills-from-evidence","description":"Improve an existing skill or runbook through recurring run evidence, a localized candidate patch, duplicate and safety checks, validation, and a durable rejection record. Use after repeated failures, useful source harvests, or stale behavior.","category":"knowledge","source_rows":["agent-intelligence-economy:skills/bounded-skill-optimization/SKILL.md","agent-intelligence-economy:templates/skill-patch-candidate.md","agent-intelligence-economy:examples/rejected-skill-patch/example.md","agent-intelligence-economy:scripts/skill_patch_candidate_extractor.py"],"license":"CC BY 4.0","triggers":["skill failure","runbook improvement","repeated agent mistake","skill patch","stale procedure"]}
---

# Optimize Skills From Evidence

## Establish recurring evidence

Collect raw run artifacts: prompts, tool traces, outputs, diffs, test failures, and user corrections. Distinguish a recurring procedure failure from a one-off task fact, model variance, missing input, or external outage. Do not patch from a single surprising event unless its impact is severe and mechanism is clear.

## Locate the owning artifact

Search existing skills, runbooks, system rules, scripts, and references. Confirm the proposed behavior belongs in the selected skill and does not duplicate another route. Prefer removing ambiguity or narrowing a trigger over adding broad doctrine.

## Draft the smallest candidate

Record the observed problem, evidence handles, target section, minimal patch, expected future behavior change, scope, safety/privacy effect, and validation gate. Preserve source facts in references rather than embedding drift-prone details in the procedure.

## Validate without leakage

Run structural validation and a representative task or fixture. For complex behavior, use an independent forward test that receives the skill and task but not the suspected defect or intended answer. Compare against the prior version when practical and inspect for regressions outside the target behavior.

Accept only evidence-backed, reusable changes whose maintenance cost is smaller than the failure prevented. Otherwise reject, mark the candidate `watch` with a return condition, or mark a verified merge `done`; record why and what evidence would reopen it.
