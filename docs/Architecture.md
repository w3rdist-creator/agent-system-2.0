# Architecture

The distribution adds evidence-first operating material to Hermes without becoming a replacement platform. Hermes remains responsible for its config, authentication, memory, sessions, model/tool integration, and runtime. Distribution-owned artifacts live in a namespaced directory and a user-selected vault.

## Three-level capability router

| Level | Loaded when | Surface | Bound |
|---|---|---|---:|
| 0 | Startup | `skills/level-0-categories.yaml` plus the unconditional capability router | 15 categories and 400 approximate tokens |
| 1 | After category selection | One `skills/categories/<category>/registry.yaml` | 20 skills/category; descriptions target 350 characters |
| 2 | After skill selection | One full `SKILL.md` body | Selected only for the task |

`evidence-first-operating-style` joins the startup surface only for ambiguous, investigative, strategic, diagnostic, consequential, or high-stakes work. `source-grounding`, `knowledge-metabolism`, `loop-governance`, and `vault-operations` are installed but trigger-loaded. An empty registry with `status: no-local-skills` is a truthful terminal route to an external pointer, not a reason to fabricate a local skill.

## Ownership and installation

The reference-first installer supports Hermes v0.18.x and writes distribution artifacts below `~/.hermes/distributions/evidence-first/`. It never edits `config.yaml`: Hermes v0.18.x `config set` assigns list indices in place and cannot append to `skills.external_dirs` (verified against the real CLI during the 2026-07-10 non-builder clean-room install), so the installer prints the exact one-line addition as an operator step and `verify-install.sh` fails closed until that entry exists. Vault files are installed relative to an explicit `--vault` path. The manifest records schema version, path, component, original state, and installed hash.

Conflicts become `.incoming` files. Uninstall removes only unchanged owned files and then empty directories, non-recursively. Modified owned files, user files, and upstream Hermes files remain. The config entry is a printed manual removal because safe list-entry deletion was not proven for the supported upstream surface; install and uninstall are now symmetric on this point.

## Packs

`packs/manifest.yaml` is the lifecycle index. Research and Agent Ops are shipped, explicit-install payloads. The other eight entries are inert `PACK.md` declarations containing purpose, sources, missing consumer evidence, trigger, owner-if-activated, review cost, seed requirement, and kill condition. Inert packs contain no active payload.

Pack installation extends the same ownership manifest as the base install. Research supplies source-grounding and cross-domain pattern workflow. Agent Ops supplies bounded queue, verification, scheduling-ownership, reporting, and loop-governance surfaces.

## Vault layers

The vault is a graph with five architectural layers:

1. operating maps and system rules;
2. domain or pack landing pages;
3. nearest local section maps;
4. content, project, decision, experiment, and review artifacts;
5. immutable or append-only Raw snapshots.

The physical 16-layer layout is `Home.md`, `Vault Self-Model.md`, Raw, Inbox, Clippings, Sources, Knowledge, Areas, Projects, Decisions, Experiments, Ledgers, Reports, Reviews, Daily, Dashboards, Archive, and System. Raw and Archive remain provenance/retrieval surfaces but do not dominate active routing. Promotion from capture to canonical knowledge requires provenance, objections, caveats/falsifiers, observed application, a decision delta, and a demotion/rollback path.

## Corpus contract

Context Spine is Contract only in 1.0. It is a future off-by-default retrieval substrate; Deep Timeline is its temporal subcorpus and Adversarial Canon is its challenge layer. No corpus payload or wholesale startup injection ships.

A future request must declare purpose, namespaces, query, numeric `max_items`, token/context budget, minimum authority, freshness need, and adversarial-challenge need. Each returned item must carry source provenance, caution, as-of/freshness data, license, retrieval reason, and content hash. Distribution content and user annotations occupy separate ownership namespaces. Hashes verify bytes, not claims.

