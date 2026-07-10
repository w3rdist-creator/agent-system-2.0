# Agent System 2.0

Agent System 2.0 is an evidence-first distribution for **Hermes Agent**, not a platform-neutral agent framework. (Its formal project and attribution name is the Evidence-First Hermes Distribution; the installed namespace remains `evidence-first`.) It installs a compact operating stance, a three-level routed skill catalog, a layered vault, governed templates, and two optional packs into a Hermes v0.18.x environment while keeping distribution-owned files separate from files Hermes owns.

**New user? Start with the [Team Quickstart](TEAM-QUICKSTART.md)** — install to first working session in fifteen minutes, plus the honest list of known boundaries.

The project is a bounded successor candidate to five earlier public repositories. It is justified by self-governance, selective loading, safe ownership, and measurable behavior—not by shipping more folders. The repository passed its own admission tests in the [1.0 improvement proposal](examples/improvement-proposal--this-repository.md), [1.1 improvement proposal](examples/improvement-proposal--release-1.1.md), and [loop contract](examples/loop-contract--this-repository.md).

## Install quickstart

Prerequisites:

- Hermes Agent v0.18.x already installed;
- macOS or Linux with POSIX shell, Python 3, Git, and rsync;
- WSL2 is inferred compatible through the POSIX path but is documented, not CI-tested;
- a vault destination you are willing to create or extend.

Review the dry run before authorizing writes:

```bash
git clone https://github.com/w3rdist-creator/agent-system-2.0.git
cd agent-system-2.0

bash scripts/install.sh --dry-run --vault "$HOME/Evidence-First-Vault"
bash scripts/install.sh --vault "$HOME/Evidence-First-Vault"

# The installer prints one manual step: add the printed path as a new entry
# under skills.external_dirs in ~/.hermes/config.yaml. Neither installer nor
# uninstaller ever edits config.yaml. Then confirm activation:
bash scripts/verify-install.sh \
  --vault "$HOME/Evidence-First-Vault" \
  --hermes-home "$HOME/.hermes"
```

The installer refuses unsupported Hermes versions before writing. It installs owned files under `~/.hermes/distributions/evidence-first/`, prints the exact one-line `skills.external_dirs` addition for you to make (Hermes v0.18.x `config set` cannot append to lists, and this distribution never edits `config.yaml` itself), writes vault conflicts as `.incoming` proposals, and records hashes in an install manifest. `verify-install.sh` fails closed until the config entry exists. Uninstall preserves modified distribution files and user files; it never edits `config.yaml` and prints the exact manual config-removal instruction, symmetric with install.

List or install the optional shipped packs:

```bash
bash scripts/list-packs.sh
bash scripts/install-pack.sh research --vault "$HOME/Evidence-First-Vault"
bash scripts/install-pack.sh agent-ops --vault "$HOME/Evidence-First-Vault"
```

## What ships

The 1.0 foundation includes:

- a posture-only `SOUL.md`, authority boundaries, and explicit loading model;
- one unconditional capability router, one task-shape-loaded operating skill, and four trigger-loaded core skills;
- 10 routed library skills across 11 category registries;
- a 16-layer base vault with one source-to-decision-to-belief-revision seed chain;
- nine governed templates with examples and structural validation;
- Research and Agent Ops as the only active packs;
- eight inert pack declarations with demand triggers and kill conditions;
- paired treatment/control evaluation harness, 16 scenarios, and deterministic trace assertions;
- reference-first installer, verifier, pack tools, safe uninstaller, scanners, budget auditor, and Linux/macOS CI.

Release 1.1 adds:

- pre-tool-use enforcement hooks for protected paths, credential echo, and retrieval caps;
- automated vault intake, exact-content deduplication, decay pressure, bounded resolve queues, and an honest metabolism ledger;
- a one-command live recert smoke examiner with append-only provenance;
- self-collected, idempotent telemetry from explicitly named machine artifacts;
- a team vault contract for shared/personal boundaries, attribution, promotion, and `.incoming` merge proposals;
- a consolidated seven-label runtime disposition vocabulary with compatibility aliases for historical evaluation records.

## Known limits

Machine-checkable rules are enforceable through the shipped hook, but only runners that wire and honor that hook receive enforcement; judgment-level doctrine remains advisory. Team use now has an explicit vault contract, but the release does not ship real-time sync, permissions enforcement, or CRDT merge tooling. The full Hermes platform layer, native Windows, backup/restore/upgrade automation, gateway and deployment integrations, MCP/plugin activation recipes, automated model grading, hosted UI, non-Hermes adapters, and corpus payloads remain deferred. Context Spine ships only as an architecture and bounded-retrieval contract; Deep Timeline remains its deferred temporal subcorpus. See [the roadmap](docs/Deferred-Capability-Roadmap.md).

## Evaluation status

The Release 1.1 paired 96-trial run used gpt-5.6-sol at high reasoning on 2026-07-10 and is checked in at `evaluations/results/run-2026-07-10-gpt-5.6-sol-1.1.csv`. It recorded **5 of 16 confirmed deltas**, below the fixed threshold of 8; the operator-directed release override is recorded in the CSV. Treatment passed all three trials on 8/16 scenarios. Scenarios 01 and 05 passed 3/3 in both arms on this model, so they do not demonstrate a treatment effect and are queued for redesign or removal under the methodology. One trial whose fixture was not mounted was re-administered. Scenario 12's write assertion was widened identically for both arms to accept the preservation-first `.incoming` proposal convention.

The earlier gpt-5.5 medium 10/16 certificate certifies Release 1.0's former ten-label vocabulary only; it is not the 1.1 certificate. The live recert log contains a passing gpt-5.6-sol high treatment-arm smoke for scenario 15 at `evaluations/results/recert-log.csv`, but a one-trial recert row is not paired delta evidence. The full development gate is green. Every result remains specific to its named model, reasoning setting, runner, date, and vocabulary rather than universal proof.

## Release status

Release 1.0 is published. Release 1.1.0 is the subsequent update described here; its below-threshold paired result is carried under the recorded operator-directed override, not represented as a threshold pass. Mechanical development and export gates do not push, tag, or supersede predecessors. Predecessors remain governed by the separate 30-day/five-use and operator-approval conditions.

For design and operating boundaries, read [Architecture](docs/Architecture.md), [Admission and Exclusion](docs/Admission-and-Exclusion-Policy.md), [Token and Context Budget](docs/Token-and-Context-Budget.md), and [Sanitization and Publication](docs/Sanitization-and-Publication.md).
