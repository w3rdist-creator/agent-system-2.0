# Clean-room install transcript
> Paths under the operator's home directory are redacted to `~redacted~` for publication; the underlying record is otherwise verbatim.

- Date: 2026-07-10
- Installer identity: non-builder: fresh codex-cli agent session with no build context, supervised by the operator
- Hermes version detected: Hermes Agent v0.18.2 (2026.7.7.2) · upstream 8727e672
- OS: macOS, Darwin 25.5.0
- Target note: sandboxed Hermes-home fixture; production install deferred to operator

The command sequence below records the clean-room installation actions in execution order. The pre-install README inspection and post-run record-authoring operations are not installation actions.

## Dry run

```console
$ bash scripts/install.sh --dry-run --vault /private/tmp/efhd-clean-room-2/vault --hermes-home /private/tmp/efhd-clean-room-2/hermes-home
COMPATIBLE: Hermes Agent v0.18.2 (2026.7.7.2) · upstream 8727e672
Install directory: ~redacted~/.hermes/hermes-agent
Install method: git
Python: 3.11.15
OpenAI SDK: 2.24.0
Update available: 1 commit behind — run 'hermes update'
STRATEGY: reference-first via skills.external_dirs[1]
DRY RUN: no files or Hermes configuration will be written
PLAN hermes-distribution: agent/AUTHORITY_BOUNDARIES.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/agent/AUTHORITY_BOUNDARIES.md.incoming (preexisting)
PLAN hermes-distribution: agent/LOADING_MODEL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/agent/LOADING_MODEL.md.incoming (preexisting)
PLAN hermes-distribution: agent/SOUL-scenario-map.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/agent/SOUL-scenario-map.yaml.incoming (preexisting)
PLAN hermes-distribution: agent/SOUL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/agent/SOUL.md.incoming (preexisting)
PLAN hermes-distribution: agent/USER_PROFILE_TEMPLATE.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/agent/USER_PROFILE_TEMPLATE.md.incoming (preexisting)
PLAN hermes-distribution: skills/categories/agent-ops/registry.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/categories/agent-ops/registry.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/categories/delegation/registry.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/categories/delegation/registry.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/categories/deployment/registry.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/categories/deployment/registry.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/categories/documents-media/registry.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/categories/documents-media/registry.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/categories/governance/registry.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/categories/governance/registry.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/categories/integrations/registry.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/categories/integrations/registry.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/categories/knowledge/registry.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/categories/knowledge/registry.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/categories/markets/registry.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/categories/markets/registry.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/categories/research/registry.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/categories/research/registry.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/categories/software/registry.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/categories/software/registry.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/categories/vault-ops/registry.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/categories/vault-ops/registry.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/core/capability-router/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/core/capability-router/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/core/evidence-first-operating-style/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/core/evidence-first-operating-style/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/core/knowledge-metabolism/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/core/knowledge-metabolism/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/core/knowledge-metabolism/agents/openai.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/core/knowledge-metabolism/agents/openai.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/core/loop-governance/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/core/loop-governance/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/core/loop-governance/agents/openai.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/core/loop-governance/agents/openai.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/core/source-grounding/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/core/source-grounding/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/core/source-grounding/agents/openai.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/core/source-grounding/agents/openai.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/core/vault-operations/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/core/vault-operations/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/core/vault-operations/agents/openai.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/core/vault-operations/agents/openai.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/level-0-categories.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/level-0-categories.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/library/delegation/execute-action-packets/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/delegation/execute-action-packets/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/library/delegation/execute-action-packets/agents/openai.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/delegation/execute-action-packets/agents/openai.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/library/delegation/orchestrate-bounded-work/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/delegation/orchestrate-bounded-work/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/library/delegation/orchestrate-bounded-work/agents/openai.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/delegation/orchestrate-bounded-work/agents/openai.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/library/governance/run-bounded-agent-labs/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/governance/run-bounded-agent-labs/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/library/governance/run-bounded-agent-labs/agents/openai.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/governance/run-bounded-agent-labs/agents/openai.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/library/knowledge/optimize-skills-from-evidence/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/knowledge/optimize-skills-from-evidence/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/library/knowledge/optimize-skills-from-evidence/agents/openai.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/knowledge/optimize-skills-from-evidence/agents/openai.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/library/markets/audit-quant-signals/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/markets/audit-quant-signals/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/library/markets/audit-quant-signals/agents/openai.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/markets/audit-quant-signals/agents/openai.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/library/markets/calibrate-market-theses/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/markets/calibrate-market-theses/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/library/markets/calibrate-market-theses/agents/openai.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/markets/calibrate-market-theses/agents/openai.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/library/markets/research-crypto-protocols/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/markets/research-crypto-protocols/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/library/markets/research-crypto-protocols/agents/openai.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/markets/research-crypto-protocols/agents/openai.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/library/markets/research-public-companies/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/markets/research-public-companies/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/library/markets/research-public-companies/agents/openai.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/markets/research-public-companies/agents/openai.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/library/research/analyze-cross-domain-mechanisms/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/research/analyze-cross-domain-mechanisms/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/library/research/analyze-cross-domain-mechanisms/agents/openai.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/research/analyze-cross-domain-mechanisms/agents/openai.yaml.incoming (preexisting)
PLAN hermes-distribution: skills/library/research/harvest-clippings-into-skills/SKILL.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/research/harvest-clippings-into-skills/SKILL.md.incoming (preexisting)
PLAN hermes-distribution: skills/library/research/harvest-clippings-into-skills/agents/openai.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills/library/research/harvest-clippings-into-skills/agents/openai.yaml.incoming (preexisting)
PLAN hermes-distribution: templates/belief-revision.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/templates/belief-revision.md.incoming (preexisting)
PLAN hermes-distribution: templates/decision-packet.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/templates/decision-packet.md.incoming (preexisting)
PLAN hermes-distribution: templates/improvement-proposal.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/templates/improvement-proposal.md.incoming (preexisting)
PLAN hermes-distribution: templates/loop-contract.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/templates/loop-contract.md.incoming (preexisting)
PLAN hermes-distribution: templates/project-handoff.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/templates/project-handoff.md.incoming (preexisting)
PLAN hermes-distribution: templates/result-packet.json -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/templates/result-packet.json.incoming (preexisting)
PLAN hermes-distribution: templates/source-note.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/templates/source-note.md.incoming (preexisting)
PLAN hermes-distribution: templates/task-packet.json -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/templates/task-packet.json.incoming (preexisting)
PLAN hermes-distribution: templates/two-layer-report.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/templates/two-layer-report.md.incoming (preexisting)
PLAN hermes-distribution: packs/manifest.yaml -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/packs/manifest.yaml.incoming (preexisting)
PLAN hermes-distribution: packs/agent-ops/PACK.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/packs/agent-ops/PACK.md.incoming (preexisting)
PLAN hermes-distribution: packs/context-spine/PACK.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/packs/context-spine/PACK.md.incoming (preexisting)
PLAN hermes-distribution: packs/deep-timeline/PACK.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/packs/deep-timeline/PACK.md.incoming (preexisting)
PLAN hermes-distribution: packs/learning-os/PACK.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/packs/learning-os/PACK.md.incoming (preexisting)
PLAN hermes-distribution: packs/markets-research-only/PACK.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/packs/markets-research-only/PACK.md.incoming (preexisting)
PLAN hermes-distribution: packs/personal-os/PACK.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/packs/personal-os/PACK.md.incoming (preexisting)
PLAN hermes-distribution: packs/product-os/PACK.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/packs/product-os/PACK.md.incoming (preexisting)
PLAN hermes-distribution: packs/research/PACK.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/packs/research/PACK.md.incoming (preexisting)
PLAN hermes-distribution: packs/simulation-lab/PACK.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/packs/simulation-lab/PACK.md.incoming (preexisting)
PLAN hermes-distribution: packs/software-delivery/PACK.md -> /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/packs/software-delivery/PACK.md.incoming (preexisting)
PLAN vault-base: vault-template/Archive/Archive Map.md -> /private/tmp/efhd-clean-room-2/vault/Archive/Archive Map.md.incoming (preexisting)
PLAN vault-base: vault-template/Areas/Areas Map.md -> /private/tmp/efhd-clean-room-2/vault/Areas/Areas Map.md.incoming (preexisting)
PLAN vault-base: vault-template/Clippings/Clippings Map.md -> /private/tmp/efhd-clean-room-2/vault/Clippings/Clippings Map.md.incoming (preexisting)
PLAN vault-base: vault-template/Daily/Daily Map.md -> /private/tmp/efhd-clean-room-2/vault/Daily/Daily Map.md.incoming (preexisting)
PLAN vault-base: vault-template/Dashboards/Dashboards Map.md -> /private/tmp/efhd-clean-room-2/vault/Dashboards/Dashboards Map.md.incoming (preexisting)
PLAN vault-base: vault-template/Decisions/Decision - One Real Chain Not Broad Seeding.md -> /private/tmp/efhd-clean-room-2/vault/Decisions/Decision - One Real Chain Not Broad Seeding.md.incoming (preexisting)
PLAN vault-base: vault-template/Decisions/Decisions Map.md -> /private/tmp/efhd-clean-room-2/vault/Decisions/Decisions Map.md.incoming (preexisting)
PLAN vault-base: vault-template/Experiments/Experiments Map.md -> /private/tmp/efhd-clean-room-2/vault/Experiments/Experiments Map.md.incoming (preexisting)
PLAN vault-base: vault-template/Home.md -> /private/tmp/efhd-clean-room-2/vault/Home.md.incoming (preexisting)
PLAN vault-base: vault-template/Inbox/Capture - Truth-Seeking Engine.md -> /private/tmp/efhd-clean-room-2/vault/Inbox/Capture - Truth-Seeking Engine.md.incoming (preexisting)
PLAN vault-base: vault-template/Inbox/Inbox Map.md -> /private/tmp/efhd-clean-room-2/vault/Inbox/Inbox Map.md.incoming (preexisting)
PLAN vault-base: vault-template/Knowledge/Belief Revision - Useful Maps Beat Filler.md -> /private/tmp/efhd-clean-room-2/vault/Knowledge/Belief Revision - Useful Maps Beat Filler.md.incoming (preexisting)
PLAN vault-base: vault-template/Knowledge/Claim - Judgment Needs a Visible Revision Trail.md -> /private/tmp/efhd-clean-room-2/vault/Knowledge/Claim - Judgment Needs a Visible Revision Trail.md.incoming (preexisting)
PLAN vault-base: vault-template/Knowledge/Knowledge Map.md -> /private/tmp/efhd-clean-room-2/vault/Knowledge/Knowledge Map.md.incoming (preexisting)
PLAN vault-base: vault-template/Knowledge/Mechanism - Append Before Canon.md -> /private/tmp/efhd-clean-room-2/vault/Knowledge/Mechanism - Append Before Canon.md.incoming (preexisting)
PLAN vault-base: vault-template/Ledgers/Ledgers Map.md -> /private/tmp/efhd-clean-room-2/vault/Ledgers/Ledgers Map.md.incoming (preexisting)
PLAN vault-base: vault-template/Projects/Project - Phase 4 Base Vault.md -> /private/tmp/efhd-clean-room-2/vault/Projects/Project - Phase 4 Base Vault.md.incoming (preexisting)
PLAN vault-base: vault-template/Projects/Projects Map.md -> /private/tmp/efhd-clean-room-2/vault/Projects/Projects Map.md.incoming (preexisting)
PLAN vault-base: vault-template/Raw/Raw Map.md -> /private/tmp/efhd-clean-room-2/vault/Raw/Raw Map.md.incoming (preexisting)
PLAN vault-base: vault-template/Raw/Truth-Seeking Engine Snapshot.md -> /private/tmp/efhd-clean-room-2/vault/Raw/Truth-Seeking Engine Snapshot.md.incoming (preexisting)
PLAN vault-base: vault-template/Reports/Reports Map.md -> /private/tmp/efhd-clean-room-2/vault/Reports/Reports Map.md.incoming (preexisting)
PLAN vault-base: vault-template/Reviews/Review - Phase 4 Seed Scope.md -> /private/tmp/efhd-clean-room-2/vault/Reviews/Review - Phase 4 Seed Scope.md.incoming (preexisting)
PLAN vault-base: vault-template/Reviews/Reviews Map.md -> /private/tmp/efhd-clean-room-2/vault/Reviews/Reviews Map.md.incoming (preexisting)
PLAN vault-base: vault-template/Sources/Source Note - Truth-Seeking Engine.md -> /private/tmp/efhd-clean-room-2/vault/Sources/Source Note - Truth-Seeking Engine.md.incoming (preexisting)
PLAN vault-base: vault-template/Sources/Sources Map.md -> /private/tmp/efhd-clean-room-2/vault/Sources/Sources Map.md.incoming (preexisting)
PLAN vault-base: vault-template/System/Belief Revision Rule.md -> /private/tmp/efhd-clean-room-2/vault/System/Belief Revision Rule.md.incoming (preexisting)
PLAN vault-base: vault-template/System/Decision and Parked-State Rule.md -> /private/tmp/efhd-clean-room-2/vault/System/Decision and Parked-State Rule.md.incoming (preexisting)
PLAN vault-base: vault-template/System/Measurement Authority Rule.md -> /private/tmp/efhd-clean-room-2/vault/System/Measurement Authority Rule.md.incoming (preexisting)
PLAN vault-base: vault-template/System/Operating States and Promotion.md -> /private/tmp/efhd-clean-room-2/vault/System/Operating States and Promotion.md.incoming (preexisting)
PLAN vault-base: vault-template/System/Resolve Queue Rule.md -> /private/tmp/efhd-clean-room-2/vault/System/Resolve Queue Rule.md.incoming (preexisting)
PLAN vault-base: vault-template/System/System Rules.md -> /private/tmp/efhd-clean-room-2/vault/System/System Rules.md.incoming (preexisting)
PLAN vault-base: vault-template/Vault Self-Model.md -> /private/tmp/efhd-clean-room-2/vault/Vault Self-Model.md.incoming (preexisting)
PLAN manifest: /private/tmp/efhd-clean-room-2/vault/.evidence-first/install-manifest.json
PLAN config: existing exact external directory entry retained
```

## Real install

```console
$ bash scripts/install.sh --vault /private/tmp/efhd-clean-room-2/vault --hermes-home /private/tmp/efhd-clean-room-2/hermes-home
COMPATIBLE: Hermes Agent v0.18.2 (2026.7.7.2) · upstream 8727e672
Install directory: ~redacted~/.hermes/hermes-agent
Install method: git
Python: 3.11.15
OpenAI SDK: 2.24.0
Update available: 1 commit behind — run 'hermes update'
STRATEGY: reference-first via skills.external_dirs[1]
INSTALLED: 99 owned files
MANIFEST: /private/tmp/efhd-clean-room-2/vault/.evidence-first/install-manifest.json
MANUAL CONFIG ADDITION REQUIRED: in /private/tmp/efhd-clean-room-2/hermes-home/config.yaml, add /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills as a new entry under skills.external_dirs; do not alter any other entry. The installer never edits config.yaml (symmetric with uninstall).
CONFIGURED: pending the manual skills.external_dirs addition above; run verify-install.sh to confirm activation
```

## Manual config addition required by installer

```diff
 skills:
   external_dirs:
     - /opt/shared/hermes-skills
+    - /private/tmp/efhd-clean-room-2/hermes-home/distributions/evidence-first/skills
```

Output: none.

## Verification

```console
$ bash scripts/verify-install.sh --vault /private/tmp/efhd-clean-room-2/vault --hermes-home /private/tmp/efhd-clean-room-2/hermes-home
PASS: installed files and hashes verified across 99 manifest file(s)
```

## Pack listing

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

## Active pack installs

```console
$ bash scripts/install-pack.sh research --vault /private/tmp/efhd-clean-room-2/vault
INSTALLED PACK: research (16 files)
```

```console
$ bash scripts/install-pack.sh agent-ops --vault /private/tmp/efhd-clean-room-2/vault
INSTALLED PACK: agent-ops (14 files)
```

## Vault inventory capture

```console
$ find /private/tmp/efhd-clean-room-2/vault -type f | sort
/private/tmp/efhd-clean-room-2/vault/.evidence-first/install-manifest.json
/private/tmp/efhd-clean-room-2/vault/Agent Ops/Agent Ops Map.md
/private/tmp/efhd-clean-room-2/vault/Agent Ops/Ledgers/Loop Scoreboard.csv
/private/tmp/efhd-clean-room-2/vault/Agent Ops/Ledgers/Operator Correction Ledger.csv
/private/tmp/efhd-clean-room-2/vault/Agent Ops/Ledgers/Prediction Calibration Ledger.csv
/private/tmp/efhd-clean-room-2/vault/Agent Ops/Packets/Result Packet - Scheduler Review.json
/private/tmp/efhd-clean-room-2/vault/Agent Ops/Packets/Task Packet - Scheduler Review.json
/private/tmp/efhd-clean-room-2/vault/Agent Ops/Queues/Resolve Queue.md
/private/tmp/efhd-clean-room-2/vault/Agent Ops/Reports/Two-Layer Report - Scheduler Review.md
/private/tmp/efhd-clean-room-2/vault/Agent Ops/Reviews/Failure Review Template.md
/private/tmp/efhd-clean-room-2/vault/Agent Ops/Reviews/Review - Single Scheduler Seed.md
/private/tmp/efhd-clean-room-2/vault/Agent Ops/System/Health Usefulness Governance Scorecard.md
/private/tmp/efhd-clean-room-2/vault/Agent Ops/System/Operator Correction Rule.md
/private/tmp/efhd-clean-room-2/vault/Agent Ops/System/Single Scheduler Ownership.md
/private/tmp/efhd-clean-room-2/vault/Agent Ops/System/Verification Gate.md
/private/tmp/efhd-clean-room-2/vault/Archive/Archive Map.md
/private/tmp/efhd-clean-room-2/vault/Areas/Areas Map.md
/private/tmp/efhd-clean-room-2/vault/Clippings/Clippings Map.md
/private/tmp/efhd-clean-room-2/vault/Daily/Daily Map.md
/private/tmp/efhd-clean-room-2/vault/Dashboards/Dashboards Map.md
/private/tmp/efhd-clean-room-2/vault/Decisions/Decision - One Real Chain Not Broad Seeding.md
/private/tmp/efhd-clean-room-2/vault/Decisions/Decisions Map.md
/private/tmp/efhd-clean-room-2/vault/Experiments/Experiments Map.md
/private/tmp/efhd-clean-room-2/vault/Home.md
/private/tmp/efhd-clean-room-2/vault/Inbox/Capture - Truth-Seeking Engine.md
/private/tmp/efhd-clean-room-2/vault/Inbox/Inbox Map.md
/private/tmp/efhd-clean-room-2/vault/Knowledge/Belief Revision - Useful Maps Beat Filler.md
/private/tmp/efhd-clean-room-2/vault/Knowledge/Claim - Judgment Needs a Visible Revision Trail.md
/private/tmp/efhd-clean-room-2/vault/Knowledge/Knowledge Map.md
/private/tmp/efhd-clean-room-2/vault/Knowledge/Mechanism - Append Before Canon.md
/private/tmp/efhd-clean-room-2/vault/Ledgers/Ledgers Map.md
/private/tmp/efhd-clean-room-2/vault/Projects/Project - Phase 4 Base Vault.md
/private/tmp/efhd-clean-room-2/vault/Projects/Projects Map.md
/private/tmp/efhd-clean-room-2/vault/Raw/Raw Map.md
/private/tmp/efhd-clean-room-2/vault/Raw/Research/Source Snapshot - Loop Scoreboard.md
/private/tmp/efhd-clean-room-2/vault/Raw/Research/Source Snapshot - Source to Synthesis.md
/private/tmp/efhd-clean-room-2/vault/Raw/Truth-Seeking Engine Snapshot.md
/private/tmp/efhd-clean-room-2/vault/Reports/Reports Map.md
/private/tmp/efhd-clean-room-2/vault/Research/Ledgers/Citation Use Log.csv
/private/tmp/efhd-clean-room-2/vault/Research/Ledgers/Claim Evidence Ledger.csv
/private/tmp/efhd-clean-room-2/vault/Research/Methods/Strategic Interaction and Goodhart Check.md
/private/tmp/efhd-clean-room-2/vault/Research/Patterns/Pattern - Bounded Selection Pressure.md
/private/tmp/efhd-clean-room-2/vault/Research/Patterns/Pattern Note Template.md
/private/tmp/efhd-clean-room-2/vault/Research/Queues/Source Queue.md
/private/tmp/efhd-clean-room-2/vault/Research/Research Map.md
/private/tmp/efhd-clean-room-2/vault/Research/Reviews/Constructive Counterweight Template.md
/private/tmp/efhd-clean-room-2/vault/Research/Reviews/Review - Bounded Selection Pressure.md
/private/tmp/efhd-clean-room-2/vault/Research/Sources/Source Note - Loop Scoreboard.md
/private/tmp/efhd-clean-room-2/vault/Research/Sources/Source Note - Source to Synthesis.md
/private/tmp/efhd-clean-room-2/vault/Research/System/Citation Use and Demotion Rule.md
/private/tmp/efhd-clean-room-2/vault/Research/System/Creative-to-Empirical Firewall.md
/private/tmp/efhd-clean-room-2/vault/Research/System/Search Merge and Non-Connection Rule.md
/private/tmp/efhd-clean-room-2/vault/Reviews/Review - Phase 4 Seed Scope.md
/private/tmp/efhd-clean-room-2/vault/Reviews/Reviews Map.md
/private/tmp/efhd-clean-room-2/vault/Sources/Source Note - Truth-Seeking Engine.md
/private/tmp/efhd-clean-room-2/vault/Sources/Sources Map.md
/private/tmp/efhd-clean-room-2/vault/System/Belief Revision Rule.md
/private/tmp/efhd-clean-room-2/vault/System/Decision and Parked-State Rule.md
/private/tmp/efhd-clean-room-2/vault/System/Measurement Authority Rule.md
/private/tmp/efhd-clean-room-2/vault/System/Operating States and Promotion.md
/private/tmp/efhd-clean-room-2/vault/System/Resolve Queue Rule.md
/private/tmp/efhd-clean-room-2/vault/System/System Rules.md
/private/tmp/efhd-clean-room-2/vault/Vault Self-Model.md
```
