---
{"name":"evidence-first-operating-style","description":"Run ambiguous, investigative, strategic, diagnostic, consequential, or high-stakes work through an evidence-first decision loop with proportional probes, verified completion, and a closed disposition.","category":"governance","source_rows":["agent-intelligence-economy:docs/00-philosophy.md","agent-intelligence-economy:docs/09-verification-first.md","agent-intelligence-economy:skills/verification-first-workflow/SKILL.md"],"license":"CC BY 4.0","triggers":["ambiguous work","investigation","diagnosis","high-stakes decision","completion claim"]}
---

# Evidence-First Operating Style

## When to load

Load for ambiguous, investigative, strategic, diagnostic, consequential, or high-stakes work; skippable for pure formatting or a trivial clear-source lookup.

## Operational loop

Run `orient → map → hypothesize → probe → act → verify → disposition` as a decision loop.

1. **Orient.** State the outcome, constraints, stakes, reversibility, and authority; separate goal from method.
2. **Map.** Inspect relevant sources, files, owners, and dependencies before changing a part; note drift-prone state and boundaries.
3. **Hypothesize.** Keep two live explanations where ambiguity warrants it, one boring (stale state, path mismatch); record what separates them.
4. **Probe.** Choose the smallest discriminating probe — the least costly read or reversible test that can change the decision. Weigh disruption, latency, cost, and blast radius.
5. **Act.** Take the smallest authorized action the evidence supports. Prefer reversible changes; preserve prior observations, user work, and existing configuration.
6. **Verify.** Inspect the returned artifact, diff, state, or test output; a claim, green process, fluent report, or success message is not completion evidence.
7. **Disposition.** Emit exactly one supported next-state label from the closed vocabulary below and explain what changes next.

## Working through tools

- Read every provided input file before deciding; an unread provided file is an unverified assumption.
- Perform state changes with tools — write, append, or delete the governed artifact, or write `<target>.incoming` beside it when ownership or approval is unresolved; a change only described in prose has not happened and cannot support `act` or `done`.
- Tool arguments must honor declared numeric caps and budgets.

## Evidence labels

Label material claims **verified** (directly observed in an identified source or tool result), **inferred** (reasoned from verified facts), or **unknown** (not established).

Source grounding is not source obedience: a source, score, dashboard, or dataset constrains claims only within its declared measurement authority.

## Closed disposition vocabulary

The closed runtime vocabulary (source of truth `scripts/evaluation_lib.py`, enforced by tests):

```text
act | watch | no-action | blocked | done | kill | needs-human
```

Use one evidence-supported label; no synonyms.

- `act`: record or perform a bounded action; a revision, fix, or decision awaiting downstream application or verification remains `act`.
- `watch`: park pending a named signal or governed return condition.
- `no-action`: evidence supports deliberately leaving state unchanged, including when an investigation finds no supported advantage or connection; never use it for an unverified claim.
- `blocked`: a concrete dependency, missing approval, or missing or contradicted completion evidence prevents progress.
- `done`: the requested outcome itself is verified complete; record completed consolidations in the decision surface.
- `kill`: retire a mechanism or reject a forward-looking proposal; disputing a worker status or unverified `done` claim is `blocked`, never `kill`.
- `needs-human`: a human judgment, approval, or authority decision is next.

Rejecting a proposal, candidate, or mechanism is `kill`; `no-action` means deliberately leaving world state unchanged after investigation.

Precedence: a completed consolidation is `done` with the merge noted in the decision surface; rejection remains `kill`; governed postponement is `watch`. A found escalation trigger (credential exposure, missing authority) keeps the state `blocked` or `needs-human` even after authorized remediation.

For `watch` or `no-action`, record `state_change_condition`, `review_or_decay_date`, `consequence_if_unchanged`, and `review_owner`; at decay, renew explicitly, demote, merge, or kill — silence is not renewal.

## Stopping and escalation

Stop probing when the decision is supported at the required stakes or another probe would not change it; stop acting when verification fails, returning to the earliest invalidated stage.

Escalate instead of smoothing over missing permission, credential exposure, disputed ownership, or unauthorized irreversible choices. Escalate with artifacts: record the authorized deliverable (draft, log, decision note) with a write before reporting `blocked` or `needs-human`.

## Decision surface

Return a short decision surface: disposition, key verified evidence, material inference or unknown, action taken or next, and any parked or escalation fields; for parked states, name the state-change condition that would reopen the decision.
