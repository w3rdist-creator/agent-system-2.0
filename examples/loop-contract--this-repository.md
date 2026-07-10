# Loop Contract — This Repository

## Owner

The repository maintainer named in `MAINTAINERS.md`; before publication this remains `w3rdist-creator`.

## Consumer

The first non-builder clean-room installer, then any public user who deliberately installs the distribution.

## Trigger

A tagged release, an upstream Hermes compatibility change, a verified user request, or a measured failure.

## Output

An installable release, verification report, disposition ledger, and compact changelog.

## Expected heartbeat

CI on every change; one clean-room install before publication; at least five recorded real uses during the 30-day supersession window; a 60-day demand review; and a 90-day keep, freeze, or archive decision.

## Budgets

The implementation budget is 15 builder sessions plus two operator review sessions. Phase 0 is one session. Release 1.0 ships two active packs and adds no recurring surface without replacing or retiring one. Context limits are fixed later by the Release 1.0 context-budget gate.

## Blast radius

Public history, the user Hermes home and vault, predecessor status, and maintainer attention.

## Review cadence

The advisor reviews each build phase. The operator performs the human gates and the 30-, 60-, and 90-day reviews after publication.

## Kill condition

Kill, freeze, or archive on no measurable downstream use, an unresolved privacy or licensing issue, an unsupported ownership contract, failure to meet the paired-evaluation threshold without a signed operator override, or maintenance load beyond the owner’s budget.

## Replacement or predecessor

The five pinned public repositories are conditionally superseded only after all supersession gates pass and the operator approves deprecation.

## Usefulness and demand populations

Operator self-use counts for usefulness and the 30-/90-day usefulness clocks. Only external users count toward demand triggers, including the 60-day external-install trigger and deferred-pack activation requests.

