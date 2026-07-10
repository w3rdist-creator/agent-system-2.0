---
license: CC BY 4.0
---

# Context Spine Pack Declaration

- **Purpose:** provide an off-by-default retrieval substrate for bounded public context, with Deep Timeline as its temporal subcorpus and an adversarial challenge layer
- **Source paths and pinned commits:** `agent-intelligence-context-pack:vault/` at `7acf6bac45d49f748efca85052ca96f5e89a5949`; architecture review in `docs/Corpus-Disposition.md`
- **Known useful mechanisms:** source registry, namespaced context, temporal retrieval, critic routing, provenance, caution, and freshness boundaries
- **Missing consumer evidence:** no clean-room user has shown which corpus artifacts are actually retrieved; 53/76 candidate public notes remain seeded-source-note quality and zero had freshness metadata at inspection
- **Activation trigger:** implement only when one external user requests it or the maintainer records two production uses not cleanly served by Research, Agent Ops, the base vault, or routed skills, followed by the separate corpus gates
- **Owner if activated:** `w3rdist-creator`
- **Expected review cost:** at least one bounded import session plus artifact-level license, sanitization, freshness, retrieval, install, and uninstall review; stop and rescope on overrun
- **Seed-content source requirement:** only pinned public artifacts with content hashes, accepted licenses, artifact-level `sanitization_reviewed_by`, freshness/caution metadata, and a demonstrated retrieval scenario
- **Kill condition:** remain inert, or remove only unchanged distribution payloads, if bounded retrieval, provenance, caution/freshness, privacy, licensing, or user-annotation preservation fails

## Corpus architecture

**Context Spine ⊃ Deep Timeline; Adversarial Canon is the challenge layer.** Context Spine owns the retrieval namespace and small index. Deep Timeline is a temporal subcorpus, not a second top-level knowledge system. Adversarial Canon supplies bounded critic perspectives against promoted claims and high-stakes decisions; it does not load as always-on doctrine.

## Future corpus manifest contract

A future manifest must record `artifact_id`, namespace, relative path, SHA-256, public source coordinate and pin, license, attribution, `sanitization_reviewed_by`, content kind, caution class, `as_of`, `last_verified`, freshness state, annotation namespace, and install ownership. Distribution payload and user annotations occupy separate namespaces and separate ownership records.

The manifest is an index of available artifacts, not permission to inject them. Content hashes verify captured bytes; they do not validate claims.

## Retrieval interface contract

Every request declares purpose, allowed namespaces, query, `max_items`, context/token budget, minimum source authority, freshness need, and whether adversarial challenge is required. The retriever returns only a bounded set and, for every item, returns artifact ID, source provenance, caution, freshness/as-of metadata, license, retrieval reason, and content hash.

Callers must distinguish source fact from analogy, require local context and non-applicability for historical transfer, and expose stale or unknown freshness rather than silently filtering it. User annotations may be retrieved alongside, never overwritten by, distribution content.

There is **no wholesale startup load**. Startup may load only a small versioned index; corpus notes are trigger-retrieved within the declared bound.

## Release disposition

`Contract only`, as decided in `docs/Corpus-Disposition.md` and confirmed by the advisor. No `corpus/` payload ships in Release 1.0. All payloads, the three corpus evaluation scenarios, expanded critic cards, market corpus, and automation defer to 1.1 or a separately reviewed corpus release.
