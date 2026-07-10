# Corpus Disposition

Inspection target: `agent-intelligence-context-pack` at pinned commit `7acf6bac45d49f748efca85052ca96f5e89a5949`. Inspection was read-only on 2026-07-10.

## Closed count

The repository has 96 tracked files. They partition mechanically into:

| Partition | Files |
|---|---:|
| Non-market artifacts under `vault/` | 76 |
| Artifacts under `vault/Market Research/` | 13 |
| Repository support files outside `vault/` | 7 |
| **Total** | **96** |

The 76 inspected non-market artifacts contain 2,814 lines and partition as 14 AI Evolution files, 16 Cross-Disciplinary files, 42 Deep Timeline files, and four vault-wide dashboard, database-log, source-guardrail, and source-registry files.

## Evidence

### Mechanical-import evidence

- A read-only pattern scan found no absolute home paths, Hermes-home paths, credential assignments, or email-shaped strings in the 76-file set.
- The source repository is MIT-licensed and already public at the pin.
- Files already use a coherent `vault/` namespace and source-oriented front matter.

### Adaptation-heavy evidence

- 53 of 76 files declare `status: seeded-source-note` and `evidence_quality: orientation-secondary`.
- 52 files explicitly instruct a future reviewer to add or fetch a source summary, replace an orientation source with a primary or scholarly source, add counterexamples, or create bridge notes only after review. These are review queues, not publication-ready knowledge.
- Zero of the 76 files contains a `freshness`, `last_verified`, or `as_of` metadata field.
- Six event notes use open-ended `present` date ranges, including contemporary AI, foundation-model, smartphone, social-media, and software-abstraction topics. Importing them under the Release 1.0 freshness contract requires claim-level review and dating.
- Although the 13-file Market Research directory was excluded, 28 of the 76 files contain market-, finance-, price-, capital-, dollar-, stock-, or bitcoin-related language. Examples include a markets bridge note and several finance-history timeline events. Separating the optional non-market corpus from research-only market interpretation is therefore not a pure path move.
- The event notes frequently use a single orientation-secondary source and model-authored mechanism suggestions. Release 1.0 requires source authority, interpretation limits, provenance, falsifiers, non-applicability, and operator review before these claims can become a shipped seed.

## Assessment

Namespace changes, a manifest, and content hashes are mechanical. The evidence above shows that source upgrading, freshness metadata, market-boundary adjudication, and claim-level sanitization/authority review are not. Import would therefore be adaptation-heavy even though the obvious privacy risk is low.

## Disposition

**Contract only.** Release 1.0 may ship the corpus architecture, manifest and retrieval interface contract, and inert `packs/context-spine/PACK.md`; all payloads defer to 1.1 or a separately reviewed corpus release. The full private Deep Timeline, additional critic cards, market corpus, and corpus automation remain deferred regardless.

What would change the decision: a bounded subset with primary or approved secondary sources, explicit freshness/caution fields, no mixed market authority, license/provenance checks, operator sanitization review, bounded retrieval tests, and an installation/uninstall budget separate from the core release.

