---
{"name":"source-grounding","description":"Ground external claims in identified sources while bounding freshness, provenance, interpretation, and decision authority. Use for research, citations, drift-prone facts, source conflicts, datasets, dashboards, or cross-domain transfer.","category":"research","source_rows":["second-brain-os-powerpack:hermes/skills/source-grounding-loop/SKILL.md","second-brain-super-repo:docs/Source Grounding Rules.md","agent-intelligence-economy:docs/05-truth-seeking-engine.md","agent-intelligence-economy:templates/source-note.md"],"license":"CC BY 4.0","triggers":["external claim","research request","freshness check","source conflict","dataset interpretation","cross-domain analogy"]}
---

# Source Grounding

## Establish the claim boundary

State the claim, the decision it could affect, the required confidence, and what can drift. Treat inherited notes, citations, dashboards, search snippets, and model memory as leads until the relevant source is inspected. Do not perform an expensive live check when its expected decision value is lower than its cost; record that tradeoff and use the strongest proportionate evidence available.

## Build the source spine

1. Identify each source with a stable handle, date, author or owner, and access state.
2. Prefer the source with authority over the claim: primary records and official data before commentary, commentary before social leads.
3. Record whether the source is merely linked, preserved, read, synthesized, applied, superseded, or rejected.
4. Preserve the original claim separately from interpretation. A local snapshot proves what was captured, not that the captured claim is true.
5. Check freshness at the source of record for state likely to have changed.

For each material source, record:

- `source_fact`: what the source directly supports;
- `interpretation_allowed`: the inference its scope permits;
- `interpretation_forbidden`: the stronger conclusion it cannot decide;
- `next_evidence_required`: the observation that would resolve the remaining uncertainty; and
- `declared_decision_authority`: the state this measurement is allowed to change.

## Test evidence rather than count citations

Assess independence, proximity to the event, measurement method, incentives, missing population, and contradictory evidence. Multiple pages repeating one upstream claim remain one evidentiary line. For analogies, require independent evidence in both domains, an explicit causal mechanism, a falsifiable implication, and a non-applicability boundary. Record `no-edge` when resemblance does not survive those checks.

When sources conflict, preserve both observations with dates and scope. Resolve whether the conflict comes from freshness, definitions, populations, methods, or genuine disagreement. Do not silently rewrite the older record.

## Return a grounded decision surface

Separate verified facts, supported inferences, and unknowns. Cite the evidence handles used, name missing evidence, and state the supported disposition. Never convert a source score, coordinate, or dashboard status into permission for an action outside its declared authority.


## Disposition of a declined probe

The disposition labels the decision under test. Declining a costly or disproportionate probe is `no-action` for that decision even when adjacent authorized work proceeds; the answer must name the state-change condition or trigger that would justify running the probe later.
