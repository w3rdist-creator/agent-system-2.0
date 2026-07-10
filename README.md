# Agent System 2.0

Agent System 2.0 is an evidence-first distribution for **Hermes Agent**, not a platform-neutral agent framework. (Its formal project and attribution name is the Evidence-First Hermes Distribution; the installed namespace remains `evidence-first`.) It installs a compact operating stance, a three-level routed skill catalog, a layered vault, governed templates, and two optional packs into a Hermes v0.18.x environment while keeping distribution-owned files separate from files Hermes owns.

**New user? Start with the [Team Quickstart](TEAM-QUICKSTART.md)** — install to first working session in fifteen minutes, plus the honest list of known boundaries.

The project is a bounded successor candidate to five earlier public repositories. It is justified by self-governance, selective loading, safe ownership, and measurable behavior—not by shipping more folders. The repository passed its own admission test in [the improvement proposal](examples/improvement-proposal--this-repository.md) and [loop contract](examples/loop-contract--this-repository.md).

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

## What ships in 1.0

- a posture-only `SOUL.md`, authority boundaries, and explicit loading model;
- one unconditional capability router, one task-shape-loaded operating skill, and four trigger-loaded core skills;
- 10 routed library skills across 11 category registries;
- a 16-layer base vault with one source-to-decision-to-belief-revision seed chain;
- nine governed templates with examples and structural validation;
- Research and Agent Ops as the only active packs;
- eight inert pack declarations with demand triggers and kill conditions;
- paired treatment/control evaluation harness, 16 scenarios, and deterministic trace assertions;
- reference-first installer, verifier, pack tools, safe uninstaller, scanners, budget auditor, and Linux/macOS CI.

The full Hermes platform layer, native Windows, backup/restore/upgrade automation, gateway and deployment recipes, MCP/plugin activation recipes, automated model grading, hosted UI, non-Hermes adapters, and corpus payloads are deferred. Context Spine ships only as an architecture and bounded-retrieval contract; Deep Timeline remains its deferred temporal subcorpus. See [the roadmap](docs/Deferred-Capability-Roadmap.md).

## Evaluation status

The harness, all 16 deterministic scenario schemas, and a shipped reference runner (`scripts/eval_adapter_codex.py`) pass validation, and paired model results are checked in under `evaluations/results/`. On the recorded pairing (gpt-5.5 via codex-cli 0.144.1, reasoning medium, 2026-07-10), the final run shows **10 of 16 scenarios with confirmed deltas** — treatment 3/3 with control failing at least 2/3 — meeting the 8-scenario publication threshold without an override. Earlier same-day runs (1/16, then 2/16, then 6/16) are retained: the gap was closed by doctrine sharpening and two instrument-faithfulness fixes, and the full progression is part of the record. These results are facts about that model/version/tool pairing and date, not universal proof; scenario secrecy expired at publication, so post-1.0 re-certification claims need held-out scenarios.

## Release-candidate status

Mechanical development and sanitized-export gates may pass while human release gates remain open. Operator sanitization sign-off, split-license confirmation, paired-model review, a non-builder clean-room install, and publication approval are required before public release. Predecessors are not superseded until the additional 30-day/five-use conditions pass.

For design and operating boundaries, read [Architecture](docs/Architecture.md), [Admission and Exclusion](docs/Admission-and-Exclusion-Policy.md), [Token and Context Budget](docs/Token-and-Context-Budget.md), and [Sanitization and Publication](docs/Sanitization-and-Publication.md).

