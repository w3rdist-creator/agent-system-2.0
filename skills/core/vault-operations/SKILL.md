---
{"name":"vault-operations","description":"Read, write, restructure, link, merge, and prune a filesystem-first knowledge vault while preserving raw provenance and user content. Use whenever work touches vault paths, inboxes, source notes, indexes, Git-backed notes, or graph hygiene.","category":"vault-ops","source_rows":["second-brain-os-starter:hermes/skills/obsidian-operating-system/SKILL.md","second-brain-os-starter:hermes/skills/second-brain-os/SKILL.md","second-brain-os-starter:hermes/skills/git-backed-vault/SKILL.md","second-brain-os-starter:vault-template/System/Operating Principles.md"],"license":"CC BY 4.0","triggers":["vault read","vault write","inbox processing","wikilink update","note merge","vault Git check"]}
---

# Vault Operations

## Resolve the vault and ownership boundary

Confirm the vault root and requested scope before writing. Inspect the nearest local map, index, or system rule rather than assuming one universal folder layout. Treat chat and capture channels as working inputs; durable state belongs in the authorized vault. Never copy credentials, session state, private keys, or unrelated personal material into it.

## Read before creating

Search for existing notes, aliases, and nearby maps. Classify the input as raw capture, source, concept, mechanism, question, project state, decision, experiment, review, or archive candidate. Prefer updating or merging an owning artifact over creating a parallel note. Preserve raw snapshots and prior claims when synthesis changes.

Use links for real navigation, hierarchy, provenance, disagreement, or semantic relationships. Do not manufacture link density. Before merging similar notes, classify the relationship as duplicate, expected hierarchy, bridge, disagreement, reconciliation candidate, or noise.

## Make bounded changes

1. Preserve raw input with date and source context when provenance matters.
2. Apply small anchored edits to the owning note.
3. Update the nearest relevant map or index when navigation changes.
4. Record meaningful structural changes in the vault's designated log when one exists.
5. Keep derived sidecars rebuildable and separate from source truth.
6. Do not create automation, remotes, or schedules unless explicitly authorized.

For inbox processing, assign a disposition to every touched item: route to an owning artifact, preserve as source work, use `done` after a verified merge, use `watch` for a deferral with a return condition, archive, or reject. To consolidate duplicate artifacts: read every copy, write the surviving artifact with the merged content, delete the redundant copy, and emit `done` with the merge noted in the decision surface. A write-only vault with growing unread notes should be reduced or pruned before more organization is added.

## Verify and report

Check that touched paths exist, formats remain parseable, links resolve as far as the available checker permits, and no secret-like material was added. If the vault is Git-backed, inspect status and diffs, stage only when authorized, and never claim a push or backup without verifying the remote result. Return exact changed paths, checks actually run, unresolved conflicts, and whether durable state changed.
