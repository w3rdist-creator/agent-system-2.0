# Clean-room install transcript
> Paths under the operator's home directory are redacted to `~redacted~` for publication; the underlying record is otherwise verbatim.

Date: 2026-07-10
Installer identity: non-builder: fresh codex-cli agent session with no build context, supervised by the operator
Hermes version detected: Hermes Agent v0.18.2 (2026.7.7.2) · upstream 8727e672
OS: macOS, Darwin 25.5.0
Target note: sandboxed Hermes-home fixture; production install deferred to operator

Repository documentation was read first from `README.md`. The verbatim execution sequence and output follow.

## Command 1

```console
$ sed -n '1,240p' README.md
# Evidence-First Hermes Distribution

This is an evidence-first distribution for **Hermes Agent**, not a platform-neutral agent framework. It installs a compact operating stance, a three-level routed skill catalog, a layered vault, governed templates, and two optional packs into a Hermes v0.18.x environment while keeping distribution-owned files separate from files Hermes owns.

The project is a bounded successor candidate to five earlier public repositories. It is justified by self-governance, selective loading, safe ownership, and measurable behavior—not by shipping more folders. The repository passed its own admission test in [the improvement proposal](examples/improvement-proposal--this-repository.md) and [loop contract](examples/loop-contract--this-repository.md).

## Install quickstart

Prerequisites:

- Hermes Agent v0.18.x already installed;
- macOS or Linux with POSIX shell, Python 3, Git, and rsync;
- WSL2 is inferred compatible through the POSIX path but is documented, not CI-tested;
- a vault destination you are willing to create or extend.

Review the dry run before authorizing writes:

```bash
git clone https://github.com/w3rdist-creator/evidence-first-hermes-distribution.git
cd evidence-first-hermes-distribution

bash scripts/install.sh --dry-run --vault "$HOME/Evidence-First-Vault"
bash scripts/install.sh --vault "$HOME/Evidence-First-Vault"
bash scripts/verify-install.sh \
  --vault "$HOME/Evidence-First-Vault" \
  --hermes-home "$HOME/.hermes"
```

The installer refuses unsupported Hermes versions before writing. It installs owned files under `~/.hermes/distributions/evidence-first/`, adds the skill directory through Hermes's supported `config set` interface, writes vault conflicts as `.incoming` proposals, and records hashes in an install manifest. Uninstall preserves modified distribution files and user files; it never edits `config.yaml` and prints the exact manual config-removal instruction.

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

The harness and all 16 deterministic scenario schemas ship and pass schema validation. No paired model result is checked in, and this repository does not claim a measured behavioral improvement yet. Before publication, a runner must execute three trials per arm on the same recorded model/version/tool pairing. At least eight surviving scenarios must show treatment 3/3 with control failing at least 2/3, unless the operator records a signed override with rationale. Results are recorded only when actually run.

## Release-candidate status

Mechanical development and sanitized-export gates may pass while human release gates remain open. Operator sanitization sign-off, split-license confirmation, paired-model review, a non-builder clean-room install, and publication approval are required before public release. Predecessors are not superseded until the additional 30-day/five-use conditions pass.

For design and operating boundaries, read [Architecture](docs/Architecture.md), [Admission and Exclusion](docs/Admission-and-Exclusion-Policy.md), [Token and Context Budget](docs/Token-and-Context-Budget.md), and [Sanitization and Publication](docs/Sanitization-and-Publication.md).
```

## Command 2

```console
$ bash scripts/install.sh --dry-run --vault /private/tmp/efhd-clean-room/vault --hermes-home /private/tmp/efhd-clean-room/hermes-home
COMPATIBLE: Hermes Agent v0.18.2 (2026.7.7.2) · upstream 8727e672
Install directory: ~redacted~/.hermes/hermes-agent
Install method: git
Python: 3.11.15
OpenAI SDK: 2.24.0
Update available: 1 commit behind — run 'hermes update'
STRATEGY: reference-first via skills.external_dirs[1]
DRY RUN: no files or Hermes configuration will be written
PLAN hermes-distribution: agent/AUTHORITY_BOUNDARIES.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/agent/AUTHORITY_BOUNDARIES.md (absent)
PLAN hermes-distribution: agent/LOADING_MODEL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/agent/LOADING_MODEL.md (absent)
PLAN hermes-distribution: agent/SOUL-scenario-map.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/agent/SOUL-scenario-map.yaml (absent)
PLAN hermes-distribution: agent/SOUL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/agent/SOUL.md (absent)
PLAN hermes-distribution: agent/USER_PROFILE_TEMPLATE.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/agent/USER_PROFILE_TEMPLATE.md (absent)
PLAN hermes-distribution: skills/categories/agent-ops/registry.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/categories/agent-ops/registry.yaml (absent)
PLAN hermes-distribution: skills/categories/delegation/registry.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/categories/delegation/registry.yaml (absent)
PLAN hermes-distribution: skills/categories/deployment/registry.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/categories/deployment/registry.yaml (absent)
PLAN hermes-distribution: skills/categories/documents-media/registry.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/categories/documents-media/registry.yaml (absent)
PLAN hermes-distribution: skills/categories/governance/registry.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/categories/governance/registry.yaml (absent)
PLAN hermes-distribution: skills/categories/integrations/registry.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/categories/integrations/registry.yaml (absent)
PLAN hermes-distribution: skills/categories/knowledge/registry.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/categories/knowledge/registry.yaml (absent)
PLAN hermes-distribution: skills/categories/markets/registry.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/categories/markets/registry.yaml (absent)
PLAN hermes-distribution: skills/categories/research/registry.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/categories/research/registry.yaml (absent)
PLAN hermes-distribution: skills/categories/software/registry.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/categories/software/registry.yaml (absent)
PLAN hermes-distribution: skills/categories/vault-ops/registry.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/categories/vault-ops/registry.yaml (absent)
PLAN hermes-distribution: skills/core/capability-router/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/core/capability-router/SKILL.md (absent)
PLAN hermes-distribution: skills/core/evidence-first-operating-style/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/core/evidence-first-operating-style/SKILL.md (absent)
PLAN hermes-distribution: skills/core/knowledge-metabolism/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/core/knowledge-metabolism/SKILL.md (absent)
PLAN hermes-distribution: skills/core/knowledge-metabolism/agents/openai.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/core/knowledge-metabolism/agents/openai.yaml (absent)
PLAN hermes-distribution: skills/core/loop-governance/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/core/loop-governance/SKILL.md (absent)
PLAN hermes-distribution: skills/core/loop-governance/agents/openai.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/core/loop-governance/agents/openai.yaml (absent)
PLAN hermes-distribution: skills/core/source-grounding/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/core/source-grounding/SKILL.md (absent)
PLAN hermes-distribution: skills/core/source-grounding/agents/openai.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/core/source-grounding/agents/openai.yaml (absent)
PLAN hermes-distribution: skills/core/vault-operations/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/core/vault-operations/SKILL.md (absent)
PLAN hermes-distribution: skills/core/vault-operations/agents/openai.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/core/vault-operations/agents/openai.yaml (absent)
PLAN hermes-distribution: skills/level-0-categories.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/level-0-categories.yaml (absent)
PLAN hermes-distribution: skills/library/delegation/execute-action-packets/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/delegation/execute-action-packets/SKILL.md (absent)
PLAN hermes-distribution: skills/library/delegation/execute-action-packets/agents/openai.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/delegation/execute-action-packets/agents/openai.yaml (absent)
PLAN hermes-distribution: skills/library/delegation/orchestrate-bounded-work/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/delegation/orchestrate-bounded-work/SKILL.md (absent)
PLAN hermes-distribution: skills/library/delegation/orchestrate-bounded-work/agents/openai.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/delegation/orchestrate-bounded-work/agents/openai.yaml (absent)
PLAN hermes-distribution: skills/library/governance/run-bounded-agent-labs/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/governance/run-bounded-agent-labs/SKILL.md (absent)
PLAN hermes-distribution: skills/library/governance/run-bounded-agent-labs/agents/openai.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/governance/run-bounded-agent-labs/agents/openai.yaml (absent)
PLAN hermes-distribution: skills/library/knowledge/optimize-skills-from-evidence/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/knowledge/optimize-skills-from-evidence/SKILL.md (absent)
PLAN hermes-distribution: skills/library/knowledge/optimize-skills-from-evidence/agents/openai.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/knowledge/optimize-skills-from-evidence/agents/openai.yaml (absent)
PLAN hermes-distribution: skills/library/markets/audit-quant-signals/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/markets/audit-quant-signals/SKILL.md (absent)
PLAN hermes-distribution: skills/library/markets/audit-quant-signals/agents/openai.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/markets/audit-quant-signals/agents/openai.yaml (absent)
PLAN hermes-distribution: skills/library/markets/calibrate-market-theses/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/markets/calibrate-market-theses/SKILL.md (absent)
PLAN hermes-distribution: skills/library/markets/calibrate-market-theses/agents/openai.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/markets/calibrate-market-theses/agents/openai.yaml (absent)
PLAN hermes-distribution: skills/library/markets/research-crypto-protocols/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/markets/research-crypto-protocols/SKILL.md (absent)
PLAN hermes-distribution: skills/library/markets/research-crypto-protocols/agents/openai.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/markets/research-crypto-protocols/agents/openai.yaml (absent)
PLAN hermes-distribution: skills/library/markets/research-public-companies/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/markets/research-public-companies/SKILL.md (absent)
PLAN hermes-distribution: skills/library/markets/research-public-companies/agents/openai.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/markets/research-public-companies/agents/openai.yaml (absent)
PLAN hermes-distribution: skills/library/research/analyze-cross-domain-mechanisms/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/research/analyze-cross-domain-mechanisms/SKILL.md (absent)
PLAN hermes-distribution: skills/library/research/analyze-cross-domain-mechanisms/agents/openai.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/research/analyze-cross-domain-mechanisms/agents/openai.yaml (absent)
PLAN hermes-distribution: skills/library/research/harvest-clippings-into-skills/SKILL.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/research/harvest-clippings-into-skills/SKILL.md (absent)
PLAN hermes-distribution: skills/library/research/harvest-clippings-into-skills/agents/openai.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills/library/research/harvest-clippings-into-skills/agents/openai.yaml (absent)
PLAN hermes-distribution: templates/belief-revision.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/templates/belief-revision.md (absent)
PLAN hermes-distribution: templates/decision-packet.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/templates/decision-packet.md (absent)
PLAN hermes-distribution: templates/improvement-proposal.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/templates/improvement-proposal.md (absent)
PLAN hermes-distribution: templates/loop-contract.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/templates/loop-contract.md (absent)
PLAN hermes-distribution: templates/project-handoff.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/templates/project-handoff.md (absent)
PLAN hermes-distribution: templates/result-packet.json -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/templates/result-packet.json (absent)
PLAN hermes-distribution: templates/source-note.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/templates/source-note.md (absent)
PLAN hermes-distribution: templates/task-packet.json -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/templates/task-packet.json (absent)
PLAN hermes-distribution: templates/two-layer-report.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/templates/two-layer-report.md (absent)
PLAN hermes-distribution: packs/manifest.yaml -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/packs/manifest.yaml (absent)
PLAN hermes-distribution: packs/agent-ops/PACK.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/packs/agent-ops/PACK.md (absent)
PLAN hermes-distribution: packs/context-spine/PACK.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/packs/context-spine/PACK.md (absent)
PLAN hermes-distribution: packs/deep-timeline/PACK.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/packs/deep-timeline/PACK.md (absent)
PLAN hermes-distribution: packs/learning-os/PACK.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/packs/learning-os/PACK.md (absent)
PLAN hermes-distribution: packs/markets-research-only/PACK.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/packs/markets-research-only/PACK.md (absent)
PLAN hermes-distribution: packs/personal-os/PACK.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/packs/personal-os/PACK.md (absent)
PLAN hermes-distribution: packs/product-os/PACK.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/packs/product-os/PACK.md (absent)
PLAN hermes-distribution: packs/research/PACK.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/packs/research/PACK.md (absent)
PLAN hermes-distribution: packs/simulation-lab/PACK.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/packs/simulation-lab/PACK.md (absent)
PLAN hermes-distribution: packs/software-delivery/PACK.md -> /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/packs/software-delivery/PACK.md (absent)
PLAN vault-base: vault-template/Archive/Archive Map.md -> /private/tmp/efhd-clean-room/vault/Archive/Archive Map.md (absent)
PLAN vault-base: vault-template/Areas/Areas Map.md -> /private/tmp/efhd-clean-room/vault/Areas/Areas Map.md (absent)
PLAN vault-base: vault-template/Clippings/Clippings Map.md -> /private/tmp/efhd-clean-room/vault/Clippings/Clippings Map.md (absent)
PLAN vault-base: vault-template/Daily/Daily Map.md -> /private/tmp/efhd-clean-room/vault/Daily/Daily Map.md (absent)
PLAN vault-base: vault-template/Dashboards/Dashboards Map.md -> /private/tmp/efhd-clean-room/vault/Dashboards/Dashboards Map.md (absent)
PLAN vault-base: vault-template/Decisions/Decision - One Real Chain Not Broad Seeding.md -> /private/tmp/efhd-clean-room/vault/Decisions/Decision - One Real Chain Not Broad Seeding.md (absent)
PLAN vault-base: vault-template/Decisions/Decisions Map.md -> /private/tmp/efhd-clean-room/vault/Decisions/Decisions Map.md (absent)
PLAN vault-base: vault-template/Experiments/Experiments Map.md -> /private/tmp/efhd-clean-room/vault/Experiments/Experiments Map.md (absent)
PLAN vault-base: vault-template/Home.md -> /private/tmp/efhd-clean-room/vault/Home.md (absent)
PLAN vault-base: vault-template/Inbox/Capture - Truth-Seeking Engine.md -> /private/tmp/efhd-clean-room/vault/Inbox/Capture - Truth-Seeking Engine.md (absent)
PLAN vault-base: vault-template/Inbox/Inbox Map.md -> /private/tmp/efhd-clean-room/vault/Inbox/Inbox Map.md (absent)
PLAN vault-base: vault-template/Knowledge/Belief Revision - Useful Maps Beat Filler.md -> /private/tmp/efhd-clean-room/vault/Knowledge/Belief Revision - Useful Maps Beat Filler.md (absent)
PLAN vault-base: vault-template/Knowledge/Claim - Judgment Needs a Visible Revision Trail.md -> /private/tmp/efhd-clean-room/vault/Knowledge/Claim - Judgment Needs a Visible Revision Trail.md (absent)
PLAN vault-base: vault-template/Knowledge/Knowledge Map.md -> /private/tmp/efhd-clean-room/vault/Knowledge/Knowledge Map.md (absent)
PLAN vault-base: vault-template/Knowledge/Mechanism - Append Before Canon.md -> /private/tmp/efhd-clean-room/vault/Knowledge/Mechanism - Append Before Canon.md (absent)
PLAN vault-base: vault-template/Ledgers/Ledgers Map.md -> /private/tmp/efhd-clean-room/vault/Ledgers/Ledgers Map.md (absent)
PLAN vault-base: vault-template/Projects/Project - Phase 4 Base Vault.md -> /private/tmp/efhd-clean-room/vault/Projects/Project - Phase 4 Base Vault.md (absent)
PLAN vault-base: vault-template/Projects/Projects Map.md -> /private/tmp/efhd-clean-room/vault/Projects/Projects Map.md (absent)
PLAN vault-base: vault-template/Raw/Raw Map.md -> /private/tmp/efhd-clean-room/vault/Raw/Raw Map.md (absent)
PLAN vault-base: vault-template/Raw/Truth-Seeking Engine Snapshot.md -> /private/tmp/efhd-clean-room/vault/Raw/Truth-Seeking Engine Snapshot.md (absent)
PLAN vault-base: vault-template/Reports/Reports Map.md -> /private/tmp/efhd-clean-room/vault/Reports/Reports Map.md (absent)
PLAN vault-base: vault-template/Reviews/Review - Phase 4 Seed Scope.md -> /private/tmp/efhd-clean-room/vault/Reviews/Review - Phase 4 Seed Scope.md (absent)
PLAN vault-base: vault-template/Reviews/Reviews Map.md -> /private/tmp/efhd-clean-room/vault/Reviews/Reviews Map.md (absent)
PLAN vault-base: vault-template/Sources/Source Note - Truth-Seeking Engine.md -> /private/tmp/efhd-clean-room/vault/Sources/Source Note - Truth-Seeking Engine.md (absent)
PLAN vault-base: vault-template/Sources/Sources Map.md -> /private/tmp/efhd-clean-room/vault/Sources/Sources Map.md (absent)
PLAN vault-base: vault-template/System/Belief Revision Rule.md -> /private/tmp/efhd-clean-room/vault/System/Belief Revision Rule.md (absent)
PLAN vault-base: vault-template/System/Decision and Parked-State Rule.md -> /private/tmp/efhd-clean-room/vault/System/Decision and Parked-State Rule.md (absent)
PLAN vault-base: vault-template/System/Measurement Authority Rule.md -> /private/tmp/efhd-clean-room/vault/System/Measurement Authority Rule.md (absent)
PLAN vault-base: vault-template/System/Operating States and Promotion.md -> /private/tmp/efhd-clean-room/vault/System/Operating States and Promotion.md (absent)
PLAN vault-base: vault-template/System/Resolve Queue Rule.md -> /private/tmp/efhd-clean-room/vault/System/Resolve Queue Rule.md (absent)
PLAN vault-base: vault-template/System/System Rules.md -> /private/tmp/efhd-clean-room/vault/System/System Rules.md (absent)
PLAN vault-base: vault-template/Vault Self-Model.md -> /private/tmp/efhd-clean-room/vault/Vault Self-Model.md (absent)
PLAN manifest: /private/tmp/efhd-clean-room/vault/.evidence-first/install-manifest.json
PLAN config: HERMES_HOME=/private/tmp/efhd-clean-room/hermes-home ~redacted~/.local/bin/hermes config set skills.external_dirs.1 /private/tmp/efhd-clean-room/hermes-home/distributions/evidence-first/skills
```

Exit status: 0

## Command 3

```console
$ bash scripts/install.sh --vault /private/tmp/efhd-clean-room/vault --hermes-home /private/tmp/efhd-clean-room/hermes-home
COMPATIBLE: Hermes Agent v0.18.2 (2026.7.7.2) · upstream 8727e672
Install directory: ~redacted~/.hermes/hermes-agent
Install method: git
Python: 3.11.15
OpenAI SDK: 2.24.0
Update available: 1 commit behind — run 'hermes update'
STRATEGY: reference-first via skills.external_dirs[1]
INSTALLED: 99 owned files
MANIFEST: /private/tmp/efhd-clean-room/vault/.evidence-first/install-manifest.json
Traceback (most recent call last):
  File "~redacted~/.hermes/hermes-agent/venv/bin/hermes", line 10, in <module>
    sys.exit(main())
             ^^^^^^
  File "~redacted~/.hermes/hermes-agent/hermes_cli/main.py", line 14709, in main
    args.func(args)
  File "~redacted~/.hermes/hermes-agent/hermes_cli/main.py", line 4346, in cmd_config
    config_command(args)
  File "~redacted~/.hermes/hermes-agent/hermes_cli/config.py", line 8218, in config_command
    set_config_value(key, value)
  File "~redacted~/.hermes/hermes-agent/hermes_cli/config.py", line 8159, in set_config_value
    _set_nested(user_config, key, value)
  File "~redacted~/.hermes/hermes-agent/hermes_cli/config.py", line 4541, in _set_nested
    current[int(last)] = value
    ~~~~~~~^^^^^^^^^^^
IndexError: list assignment index out of range
```

Exit status: 1

## Command 4

```console
$ bash scripts/verify-install.sh --vault /private/tmp/efhd-clean-room/vault --hermes-home /private/tmp/efhd-clean-room/hermes-home
PASS: installed files and hashes verified across 99 manifest file(s)
```

Exit status: 0

## Command 5

```console
$ bash scripts/list-packs.sh
pack	status	activation_trigger
research	shipped	Explicit operator installation for a source-grounded research workflow.
agent-ops	shipped	Explicit operator installation for governed agent operations.
context-spine	inert	One external user request or two production uses not cleanly served by shipped surfaces, plus a separately passing corpus review.
deep-timeline	inert	One external user request or two production uses not cleanly served by shipped surfaces, after Context Spine activation.
markets-research-only	inert	One external user request or two production uses not cleanly served by shipped surfaces, plus separate liability and freshness review.
product-os	inert	One external user request or two production uses not cleanly served by shipped surfaces.
personal-os	inert	One external user request or two production uses not cleanly served by shipped surfaces, plus separate universal-doctrine and privacy review.
learning-os	inert	One external user request or two production uses not cleanly served by shipped surfaces, plus separate maintenance review.
software-delivery	inert	One external user request or two production uses not cleanly served by shipped surfaces.
simulation-lab	inert	One external user request or two production uses not cleanly served by shipped surfaces.
```

Exit status: 0

## Command 6

```console
$ bash scripts/install-pack.sh research --vault /private/tmp/efhd-clean-room/vault
INSTALLED PACK: research (16 files)
```

Exit status: 0

## Command 7

```console
$ bash scripts/install-pack.sh agent-ops --vault /private/tmp/efhd-clean-room/vault
INSTALLED PACK: agent-ops (14 files)
```

Exit status: 0

## Command 8

```console
$ find /private/tmp/efhd-clean-room/vault -type f | sort
/private/tmp/efhd-clean-room/vault/.evidence-first/install-manifest.json
/private/tmp/efhd-clean-room/vault/Agent Ops/Agent Ops Map.md
/private/tmp/efhd-clean-room/vault/Agent Ops/Ledgers/Loop Scoreboard.csv
/private/tmp/efhd-clean-room/vault/Agent Ops/Ledgers/Operator Correction Ledger.csv
/private/tmp/efhd-clean-room/vault/Agent Ops/Ledgers/Prediction Calibration Ledger.csv
/private/tmp/efhd-clean-room/vault/Agent Ops/Packets/Result Packet - Scheduler Review.json
/private/tmp/efhd-clean-room/vault/Agent Ops/Packets/Task Packet - Scheduler Review.json
/private/tmp/efhd-clean-room/vault/Agent Ops/Queues/Resolve Queue.md
/private/tmp/efhd-clean-room/vault/Agent Ops/Reports/Two-Layer Report - Scheduler Review.md
/private/tmp/efhd-clean-room/vault/Agent Ops/Reviews/Failure Review Template.md
/private/tmp/efhd-clean-room/vault/Agent Ops/Reviews/Review - Single Scheduler Seed.md
/private/tmp/efhd-clean-room/vault/Agent Ops/System/Health Usefulness Governance Scorecard.md
/private/tmp/efhd-clean-room/vault/Agent Ops/System/Operator Correction Rule.md
/private/tmp/efhd-clean-room/vault/Agent Ops/System/Single Scheduler Ownership.md
/private/tmp/efhd-clean-room/vault/Agent Ops/System/Verification Gate.md
/private/tmp/efhd-clean-room/vault/Archive/Archive Map.md
/private/tmp/efhd-clean-room/vault/Areas/Areas Map.md
/private/tmp/efhd-clean-room/vault/Clippings/Clippings Map.md
/private/tmp/efhd-clean-room/vault/Daily/Daily Map.md
/private/tmp/efhd-clean-room/vault/Dashboards/Dashboards Map.md
/private/tmp/efhd-clean-room/vault/Decisions/Decision - One Real Chain Not Broad Seeding.md
/private/tmp/efhd-clean-room/vault/Decisions/Decisions Map.md
/private/tmp/efhd-clean-room/vault/Experiments/Experiments Map.md
/private/tmp/efhd-clean-room/vault/Home.md
/private/tmp/efhd-clean-room/vault/Inbox/Capture - Truth-Seeking Engine.md
/private/tmp/efhd-clean-room/vault/Inbox/Inbox Map.md
/private/tmp/efhd-clean-room/vault/Knowledge/Belief Revision - Useful Maps Beat Filler.md
/private/tmp/efhd-clean-room/vault/Knowledge/Claim - Judgment Needs a Visible Revision Trail.md
/private/tmp/efhd-clean-room/vault/Knowledge/Knowledge Map.md
/private/tmp/efhd-clean-room/vault/Knowledge/Mechanism - Append Before Canon.md
/private/tmp/efhd-clean-room/vault/Ledgers/Ledgers Map.md
/private/tmp/efhd-clean-room/vault/Projects/Project - Phase 4 Base Vault.md
/private/tmp/efhd-clean-room/vault/Projects/Projects Map.md
/private/tmp/efhd-clean-room/vault/Raw/Raw Map.md
/private/tmp/efhd-clean-room/vault/Raw/Research/Source Snapshot - Loop Scoreboard.md
/private/tmp/efhd-clean-room/vault/Raw/Research/Source Snapshot - Source to Synthesis.md
/private/tmp/efhd-clean-room/vault/Raw/Truth-Seeking Engine Snapshot.md
/private/tmp/efhd-clean-room/vault/Reports/Reports Map.md
/private/tmp/efhd-clean-room/vault/Research/Ledgers/Citation Use Log.csv
/private/tmp/efhd-clean-room/vault/Research/Ledgers/Claim Evidence Ledger.csv
/private/tmp/efhd-clean-room/vault/Research/Methods/Strategic Interaction and Goodhart Check.md
/private/tmp/efhd-clean-room/vault/Research/Patterns/Pattern - Bounded Selection Pressure.md
/private/tmp/efhd-clean-room/vault/Research/Patterns/Pattern Note Template.md
/private/tmp/efhd-clean-room/vault/Research/Queues/Source Queue.md
/private/tmp/efhd-clean-room/vault/Research/Research Map.md
/private/tmp/efhd-clean-room/vault/Research/Reviews/Constructive Counterweight Template.md
/private/tmp/efhd-clean-room/vault/Research/Reviews/Review - Bounded Selection Pressure.md
/private/tmp/efhd-clean-room/vault/Research/Sources/Source Note - Loop Scoreboard.md
/private/tmp/efhd-clean-room/vault/Research/Sources/Source Note - Source to Synthesis.md
/private/tmp/efhd-clean-room/vault/Research/System/Citation Use and Demotion Rule.md
/private/tmp/efhd-clean-room/vault/Research/System/Creative-to-Empirical Firewall.md
/private/tmp/efhd-clean-room/vault/Research/System/Search Merge and Non-Connection Rule.md
/private/tmp/efhd-clean-room/vault/Reviews/Review - Phase 4 Seed Scope.md
/private/tmp/efhd-clean-room/vault/Reviews/Reviews Map.md
/private/tmp/efhd-clean-room/vault/Sources/Source Note - Truth-Seeking Engine.md
/private/tmp/efhd-clean-room/vault/Sources/Sources Map.md
/private/tmp/efhd-clean-room/vault/System/Belief Revision Rule.md
/private/tmp/efhd-clean-room/vault/System/Decision and Parked-State Rule.md
/private/tmp/efhd-clean-room/vault/System/Measurement Authority Rule.md
/private/tmp/efhd-clean-room/vault/System/Operating States and Promotion.md
/private/tmp/efhd-clean-room/vault/System/Resolve Queue Rule.md
/private/tmp/efhd-clean-room/vault/System/System Rules.md
/private/tmp/efhd-clean-room/vault/Vault Self-Model.md
```

Exit status: 0
