# Agent System 2.0

Agent System 2.0 is an evidence-first distribution for **Hermes Agent**, not a platform-neutral agent framework. (Its formal project and attribution name is the Evidence-First Hermes Distribution; the installed namespace remains `evidence-first`.) It installs a compact operating stance, a three-level routed skill catalog, a layered vault, governed templates, and two optional packs into a Hermes v0.18.x environment while keeping distribution-owned files separate from files Hermes owns.

**New user? Start with the [Team Quickstart](TEAM-QUICKSTART.md)** — install to first working session in fifteen minutes, plus the honest list of known boundaries.

The project is a bounded successor candidate to five earlier public repositories. It is justified by self-governance, selective loading, safe ownership, and measurable behavior—not by shipping more folders. The repository passed its own admission tests in the [1.0 improvement proposal](examples/improvement-proposal--this-repository.md), [1.1 improvement proposal](examples/improvement-proposal--release-1.1.md), [1.2 improvement proposal](examples/improvement-proposal--release-1.2.md), [1.3 improvement proposal](examples/improvement-proposal--release-1.3.md), and [loop contract](examples/loop-contract--this-repository.md).

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

# The installer prints a manual config step: add the printed path as a new entry
# under skills.external_dirs in ~/.hermes/config.yaml. Neither installer nor
# uninstaller ever edits config.yaml. Then confirm activation:
bash scripts/verify-install.sh \
  --vault "$HOME/Evidence-First-Vault" \
  --hermes-home "$HOME/.hermes"

# The installer also prints these operator-owned plugin activation steps:
hermes plugins enable evidence-first-enforcement
# Then restart the Hermes gateway.
```

The installer refuses unsupported Hermes versions before writing. It installs owned files under `~/.hermes/distributions/evidence-first/`, installs the manifest-tracked plugin below `~/.hermes/plugins/evidence-first-enforcement/`, prints the exact one-line `skills.external_dirs` addition for you to make (Hermes v0.18.x `config set` cannot append to lists, and this distribution never edits `config.yaml` itself), and prints but does not perform plugin enablement or gateway restart. Vault conflicts become `.incoming` proposals, and the install manifest records both target roots. `verify-install.sh` fails closed until the config entry exists. Uninstall preserves modified distribution files and user files; it never edits `config.yaml` and prints the exact manual config-removal instruction, symmetric with install.

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

Release 1.2 adds:

- an outbound completion gate that completes the enforcement pair by checking final parked-state surfaces after the pre-tool-use hook checks proposed actions;
- preservation-first manifest-to-manifest upgrades with schema migration and `.incoming` supersession for user-modified distribution files;
- baseline-absorbed handling for scenarios 01 and 05 after two redesign rounds, retaining them as regression canaries while excluding them from surviving delta accounting;
- a canonical boundary where rejecting a proposal, candidate, or mechanism is `kill`, while `no-action` deliberately leaves world state unchanged after investigation.

Release 1.3 adds:

- n=10 rate-based certification and a resumable multi-model paired-suite driver while preserving the historical n=3 rule;
- model-scoped canary accounting with a dated after-observation disclosure and both accounting alternatives reported;
- mechanically applied doctrine pruning (zero eligible lines), sharper 04/08 disposition boundaries, and a checked-in 06/07 adjudication memo;
- a manifest-tracked Hermes enforcement plugin, a development-gate tool-loop leg, and operator-recorded live denial evidence.

## Known limits

Machine-checkable enforcement is now demonstrated for Hermes through the shipped plugin: the development gate exercises its hook contract and the live example records an operator-observed denial. Other runners still receive only the inbound/outbound CLI contract and must wire and honor it; the plugin is not a sandbox, and completion regexes verify the presence, not the quality, of parked-state metadata, so judgment-level doctrine remains advisory. Team use now has an explicit vault contract, but the release does not ship real-time sync, permissions enforcement, or CRDT merge tooling. Upgrade automation now migrates manifest-tracked base-distribution files and the Hermes plugin, preserves user modifications with `.incoming` proposals, and leaves `config.yaml` untouched; installed packs and user content are not upgraded, and backup/restore automation remains deferred. The full Hermes platform layer, native Windows, gateway and deployment integrations beyond the shipped enforcement plugin, automated model grading, hosted UI, non-Hermes adapters, and corpus payloads remain deferred. Context Spine ships only as an architecture and bounded-retrieval contract; Deep Timeline remains its deferred temporal subcorpus. See [the roadmap](docs/Deferred-Capability-Roadmap.md).

## Evaluation status

**CERTIFICATE EARNED ON MERIT:** paired n=10 run on gpt-5.5 medium 2026-07-11 ([CSV](evaluations/results/run-2026-07-11-gpt-5.5-1.3.csv)) = 8/16 surviving confirmed deltas under the model-scoped canary rule, threshold 8 MET, NO override (global-exclusion alternative 7/14 disclosed everywhere both appear).

The paired gpt-5.6-sol high run ([CSV](evaluations/results/run-2026-07-11-gpt-5.6-sol-1.3.csv)) = 7/14 surviving, below threshold, no claim made for that pairing; judgment-heavy scenarios 06/07/09/11/13/14 are recorded as 1.4 boundary data. The headline finding is that doctrine value migrates downward as models strengthen: scenario 01 was absorbed on sol (both arms 10/10) yet produced a perfect 10/10-vs-0/10 delta on gpt-5.5. Scenario 13 was 3/3 at n=3 in 1.2 but 3/10 at n=10, demonstrating why the rate rule exists. The canary design, model-scoped accounting, and dated after-observation disclosure are documented in [the evaluation methodology](evaluations/README.md). Every result remains specific to its named model, reasoning setting, runner, date, and vocabulary rather than universal proof.

## Release status

Release 1.0 is published. Release 1.3.0 is the subsequent update described here and carries the first certificate earned on the current vocabulary without an override. Mechanical development and export gates do not push, tag, or supersede predecessors. Predecessors remain governed by the separate 30-day/five-use and operator-approval conditions.

For design and operating boundaries, read [Architecture](docs/Architecture.md), [Admission and Exclusion](docs/Admission-and-Exclusion-Policy.md), [Token and Context Budget](docs/Token-and-Context-Budget.md), and [Sanitization and Publication](docs/Sanitization-and-Publication.md).
