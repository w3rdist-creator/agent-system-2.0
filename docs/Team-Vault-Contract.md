# Team Vault Contract

This contract lets a team adopt the distribution with Git or any file-sync layer today. It defines ownership and merge conventions; it does not claim that the sync layer enforces them.

## Topology

Each member keeps a personal vault: their own installation and files. Personal vaults do not sync. The team adds exactly one shared vault, installed once by a designated vault owner. Only the shared vault is placed under the team's chosen Git or sync layer.

The vault owner owns installation, lifecycle decisions, `System/` rules, and scheduler coordination for the shared vault. Team membership does not make personal vault content shared by default.

## Write authority

All agent and member submissions enter the shared vault only through `Inbox/`. Every capture must include a `route:` frontmatter value naming an existing shipped top-level destination and `author:` with a stable team identity so its origin survives routing and review.

The designated scheduler owner runs `python3 scripts/metabolism.py --vault PATH`. Under the [Metabolism Rule](../vault-template/System/Metabolism%20Rule.md), that command is the single mechanical owner of Inbox routing, exact-content deduplication, and decay pressure. Follow the [operator-owned scheduling contract](Metabolism.md#operator-owned-scheduling): one shared vault has one scheduler owner and at most one scheduler for this outcome, with the metabolism ledger as its positive heartbeat.

Files outside `Inbox/` are canon. Direct canon edits happen only as an explicit human review or conflict-resolution action. Changes under `System/` additionally require the vault owner's authority. A sync client's ability to write a path is not permission to bypass these conventions.

## Attribution

Shared-vault notes use this frontmatter field:

```yaml
author: stable-team-identity
```

Use a durable handle the team can resolve to a person or accountable service. Preserve the field when metabolism routes a note, when a note is copied, and when a merge proposal is resolved. If several people materially author a note, use a YAML list rather than erasing earlier attribution.

## Merge conventions

Conflicts never overwrite either source. The installer's `.incoming` proposal pattern is the merge primitive: preserve the current path and place the competing version beside it as `<name>.incoming` (or the installer's collision-safe dated variant).

For every competing edit:

1. Preserve both source coordinates and bodies.
2. Create `YYYY-MM-DD Merge Proposal - <topic>.md` from `templates/merge-proposal.md`, recording the conflict, both sources, proposed survivor, evidence, and disposition.
3. Add an entry linking that proposal to `Queues/Resolve Queue.md`.
4. Let an authorized human resolve the queue item by selecting or composing the survivor. Move superseded material to an appropriate archive when useful; never delete it as part of consolidation.

The proposal is evidence for a decision, not authority to overwrite canon. Conflicts under `System/` remain for the vault owner to resolve.

## Crossing the personal/shared boundary

Personal-to-shared promotion is a copy, never a move. Add normal shared attribution and record provenance in the promoted copy:

```yaml
author: stable-team-identity
promoted-from: personal/stable-team-identity
```

Submit the copy through the shared `Inbox/` with a valid `route:`; do not write it directly into canon. The personal original remains untouched.

Shared-to-personal transfer is a plain copy, never a move. Preserve the shared note's attribution and provenance in the personal copy. Personal edits do not flow back implicitly; a proposed return to shared canon is a new attributed Inbox capture.

## Deliberately not built

Release 1.1 does not provide real-time sync, permissions enforcement, or CRDT merge. Git or another sync layer transports files; humans and the metabolism workflow apply this contract.

Tooling becomes eligible when one external team requests it **or** two maintainer production uses cannot be served cleanly by this contract. Activation still requires a named owner, preservation-first install and rollback behavior, testable authority boundaries, a review budget, and a kill condition. Until that evidence exists, manual coordination is the honest and smaller surface.
