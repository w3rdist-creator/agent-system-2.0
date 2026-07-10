---
author: alex
proposal-date: 2026-07-10
---

# Merge Proposal — Source Review Cadence

## What conflicts

On 2026-07-10, `System/Source Review Cadence.md` and `System/Source Review Cadence.incoming` propose different review intervals. Resolve Queue entry `merge-source-review-cadence-2026-07-10` tracks the decision.

## Source A

`System/Source Review Cadence.md`, authored by alex on 2026-07-01, requires a 30-day review for every source.

## Source B

`System/Source Review Cadence.incoming`, authored by sam on 2026-07-09, proposes 14 days for volatile sources and 90 days for stable references.

## Proposed survivor

Keep `System/Source Review Cadence.md` as the canonical path, preserving Source B's volatility tiers and Source A's requirement that every source has a dated review.

## Evidence

The source-note contract already distinguishes freshness and caveats, which supports risk-based intervals. No measured team review cost is available yet; the strongest objection is that tiering adds judgment and may produce inconsistent labels.

## Disposition

needs-human — the vault owner must approve a `System/` rule change before the proposal can be merged.
