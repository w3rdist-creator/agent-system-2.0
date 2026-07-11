# Improvement Proposal — Release 1.3

## Problem observed

Release 1.2's behavioral claim still rested on n=3 trials on one model, treated baseline-absorbed
canaries as globally excluded despite model-specific manifest metadata, and shipped enforcement as
a runner contract without public Hermes trigger wiring or live denial evidence. Its 04/08 results
also exposed disposition boundary blur, and the 06/07 pair required an explicit over-caution
audit.

## Evidence

Scoping evidence: the Opus 4.8 external review scored the artifact 8.5/10 and capped it for the
small one-model exam and for an enforcement guard with no proven trigger or live public evidence.
The review is recorded as the operator-vault source note dated 2026-07-11 for session
`claude/harness-rating-fae06a`. This proposal uses that source note as scope evidence, not as proof
that the implemented changes work.

Telemetry evidence discharges the standing telemetry citation duty: the operator vault's
`Telemetry Ledger` has 703+ rows derived from the checked-in transcript sets, while the
operator-local live enforcement heartbeat JSONL records the 2026-07-11 Hermes denial summarized
in [the live evidence](live-enforcement-denial/). The ledger supports investing in stronger
evaluation accounting; the heartbeat supports shipping the already-live Hermes integration.
Neither row source authorizes action by itself.

Phase T applied the pruning rule mechanically and found zero prunable doctrine lines because all
candidates also map to surviving scenarios. The 04/08 boundary sentences then passed treatment
10/10 on gpt-5.6-sol high. The checked-in 06/07 adjudication memo changes no suite assertion: 06
counts over-caution against treatment, and 07's control overwrote the conflicting configuration in
6/6 trials.

**CERTIFICATE EARNED ON MERIT:** paired n=10 run on gpt-5.5 medium 2026-07-11
(`evaluations/results/run-2026-07-11-gpt-5.5-1.3.csv`) = 8/16 surviving confirmed deltas under the
model-scoped canary rule, threshold 8 MET, NO override (global-exclusion alternative 7/14
disclosed everywhere both appear). The paired gpt-5.6-sol high run
(`evaluations/results/run-2026-07-11-gpt-5.6-sol-1.3.csv`) = 7/14 surviving, below threshold, no
claim made for that pairing; judgment-heavy scenarios 06/07/09/11/13/14 are recorded as 1.4
boundary data.

The headline finding is that doctrine value migrates downward as models strengthen: scenario 01
was absorbed on sol (both arms 10/10) yet produced a perfect 10/10-vs-0/10 delta on gpt-5.5.
Scenario 13 was 3/3 at n=3 in 1.2 but 3/10 at n=10, exposing the n=3 noise the rate rule exists to
control. The canary design, model-scoped accounting, and dated after-observation disclosure are
documented in `evaluations/README.md`.

## Who should notice improvement

Operators deciding whether the current distribution changes behavior on their model; evaluation
maintainers comparing results without erasing model-specific canaries; Hermes users who need the
guard to fire in a real tool loop; and reviewers checking whether caution is being rewarded rather
than measured honestly.

## Proposed destination

Keep the statistical rule and multi-model driver in the existing evaluation harness; keep
model-scoped canary semantics and their disclosure in the evaluation methodology; keep doctrine
boundary changes in the single loaded operating-style surface with the 06/07 memo beside results;
and ship the Hermes adapter below `enforcement/hermes-plugin/` as manifest-tracked payload with its
repeatable tool-loop leg and bounded live-evidence example.

## What it replaces or merges

The n=10 rate rule replaces n=3 as the Release 1.3 certification basis without rewriting
historical results. Model-scoped exclusion replaces global canary exclusion. The shipped Hermes
plugin replaces advisory activation guidance for this one supported runner while retaining the
runner-neutral CLI contract. The adjudication memo replaces an unresolved reviewer concern with a
fixture-grounded decision and no suite change.

## Context, storage, and review cost

No new unconditional doctrine surface was added beyond the two bounded disposition sentences.
The cost is a resumable 640-trial two-model exam, two checked-in result CSVs, one driver, the
manifest-tracked plugin payload, tests, and short documentation/evidence records. Raw transcripts
and the secret-free heartbeat remain operator-local or BUILD-only as documented; the public
artifact carries summaries and provenance rather than bulk runtime state.

## Blast radius

Certification semantics, surviving-suite denominators, model comparisons, Hermes tool dispatch,
completion transformation, install/upgrade/uninstall manifests, and public behavioral claims. The
plugin may block named calls when enabled, so manual activation and restart stay operator-owned.
No change may edit `config.yaml`, silently overwrite an existing plugin, count an absorbing-model
canary in that model's denominator, globally discard a useful canary, or promote the below-threshold
gpt-5.6-sol pairing into a claim.

## Verification method

Exercise the n=3 and n=10 arithmetic edges directly; refuse undefined certification trial counts;
resume a stubbed multi-model run without repeating completed trials; re-score both n=10 transcript
sets; verify model-matching exclusion and nonmatching canary activation; drive the plugin through
the Hermes hook directive contract; round-trip both manifest target roots; run the full repository
definition of done and `bash scripts/dev-gate.sh`; and preserve the dated disclosure and both
gpt-5.5 accountings everywhere the result appears.

## Kill or rollback condition

Revert the n=10 thresholds only if a preregistered, held-out calibration shows the 0.9/0.4 rule
systematically certifies behavior that fails human rubric review or rejects stable treatment
behavior across two reviewed releases; never tune it after viewing a release result. Kill the
multi-model driver if two consecutive releases cannot produce a complete, provenance-valid second
model run and the resumability code does not reduce operator work.

Revert model-scoped exclusion if a manifest cannot name one absorbing model unambiguously or a
held-out replay proves canary treatment differs across arms or configurations; otherwise retain
the after-observation disclosure permanently. Revert the 04/08 sentences if two reviewed releases
show they increase those exact label blurs without improving requested-outcome accuracy. Reopen
scenario 07 only if a fixture-grounded authority change makes adoption safe without a human; kill
scenario 06 if the compact index can no longer answer its routing task.

Disable and roll back the Hermes plugin on any verified allowed-call execution after a deny
directive, destructive overwrite during lifecycle operations, secret-bearing heartbeat, or
repeated false denial that cannot be fixed within the named guard. If the live heartbeat is absent
for two scheduled enforcement checks or no subsequent security/release decision cites plugin
evidence by Release 1.4, kill the heartbeat collector rather than preserve unused telemetry.

## Why a simpler location is insufficient

A larger prose warning cannot repair statistical noise, denominator semantics, or a missing tool
dispatch hook. One model cannot establish the intended cross-model boundary, a global exclusion
cannot express the manifest's model-specific fact, and a CLI example cannot demonstrate that
Hermes actually invokes the guard. Each addition therefore lands at the narrow executable boundary
that owns it, with prose limited to disclosure and operator activation.

## Disposition

Act: release 1.3.0 with the first earned current-vocabulary certificate scoped to gpt-5.5 medium,
no claim for the below-threshold gpt-5.6-sol pairing, permanent after-observation accounting
disclosure, retained judgment-heavy boundary data, and Hermes enforcement demonstrated at both
the repeatable hook-contract and operator-recorded live levels.
