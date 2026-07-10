# Maintainers

## Ownership

- Publishing owner and initial repository maintainer: `w3rdist-creator`
- Executor: builder agents implement artifacts and run mechanical gates; they do not publish or perform human review.
- Advisor: Fable 5 writes phase briefs, reviews phase gates, and performs the final coherence review.
- Operator: the project operator is the sole publisher and performs sanitization sign-off, the clean-room install, evaluation judgment when required, and publication approval.

Before publication, the operator replaces `w3rdist-creator` with the publishing GitHub account.

## Review independence

Release 1.0 human gates are operator-reviewed. The operator is independent of the builder agents, not independent of the project. Public materials must not call this an independent audit unless a genuine third party performs one.

## Response expectation

Contributor and compatibility reports receive best-effort review with no service-level agreement. If upstream Hermes breaks compatibility, the owner may mark the distribution unsupported, freeze releases, or archive it rather than promise an unbudgeted response.

## Publication authority

Only the operator may create the public repository, configure a remote, push, publish releases, or deprecate predecessors.

## Template ownership

`w3rdist-creator` owns all nine Release 1.0 templates and their structural contracts. Changes to a required field need a migration note for existing instances. A replacement may supersede or merge a template only when it preserves that template's consumer-facing evidence and decision boundary; the template header records the specific rationale.

## Pack ownership

`w3rdist-creator` owns the shipped Research and Agent Ops pack contracts, their seed-review cadence, and lifecycle dispositions. An inert pack has no active maintenance promise; the same account becomes owner only after its `PACK.md` activation trigger and required extra review pass. Context Spine remains Contract only until a separately reviewed corpus release satisfies its manifest, retrieval, ownership, and annotation-preservation contract.
