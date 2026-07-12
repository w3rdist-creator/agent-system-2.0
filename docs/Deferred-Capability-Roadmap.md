# Deferred Capability Roadmap

Deferred means named and trigger-gated, not silently discarded. External-user requests satisfy demand triggers; operator use can satisfy the stated two-production-use path but does not count as external demand.

## Released from deferral in 1.1

These operator-directed additions were admitted on 2026-07-10 and shipped in Release 1.1. They are recorded here so activation history is not mistaken for untriggered scope growth.

| Capability | 1.1 status | Activation trigger recorded | Remaining boundary |
|---|---|---|---|
| Pre-tool-use enforcement hooks | Shipped | Operator direction, 2026-07-10 | Runner wiring is required; the hook is not a sandbox. |
| Vault intake and metabolism | Shipped | Operator direction, 2026-07-10 | The distribution supplies the command and recipe, not a scheduler. |
| Live recert examiner | Shipped | Operator direction, 2026-07-10 | Single-arm smoke evidence does not certify a paired delta. |
| Self-collected telemetry | Shipped | Operator direction, 2026-07-10 | Only named machine artifacts are read; rows do not authorize action. |
| Team vault contract | Contract shipped | Operator direction, 2026-07-10 | Sync, permissions, CRDT merge, and other team tooling remain deferred. |

## Released from deferral in 1.3

The Hermes enforcement activation recipe was admitted on 2026-07-11 after the operator-recorded
live denial and the repeatable hook-contract test supplied the trigger and evidence the external
review found missing. Other plugin and MCP integrations remain trigger-gated in the table below.

| Capability | 1.3 status | Activation trigger recorded | Remaining boundary |
|---|---|---|---|
| Hermes enforcement plugin | Shipped as manifest-tracked payload | Operator live denial plus hook-contract test, 2026-07-11 | Manual enable and gateway restart remain operator actions; the plugin is not a sandbox. |

| Capability | Earliest release | Activation trigger | Blocking question |
|---|---:|---|---|
| Full Hermes config/profile/toolset layer | 1.1 | One external clean-room user succeeds | Can all touched capabilities remain namespaced without owning upstream files? |
| Context Spine payload | 1.1 or separate corpus release | One external request or two production uses plus corpus review | Which public artifacts are actually retrieved, fresh, licensed, and useful? |
| Deep Timeline payload | 1.1 | Context Spine active plus default demand trigger | Can it avoid bulk filler and analogy overreach? |
| Software Delivery pack | 1.1 | Default demand trigger | Does the routed library already serve the need? |
| Simulation Lab split vault | 1.1 | Default demand trigger | Is hard isolation worth lifecycle and false-realism cost? |
| Product OS | 1.1 | Default demand trigger | Is there a named consumer and changed product decision? |
| Learning OS | 1.1 | Default trigger plus maintenance review | Can it avoid universal learning doctrine and stale curricula? |
| Personal OS | 1.1+ | Explicit external request or two production uses plus privacy/universal-doctrine review | Can user-owned personal context stay private and non-prescriptive? |
| Markets research-only | 1.1+ | Explicit demand plus liability/freshness review | Can research-only/no-action boundaries remain enforceable? |
| Native Windows | 1.1+ | One real Windows user or contributor | Is a second installer/CI surface maintainable? |
| Gateway/messaging/voice/mobile | 1.1+ | One user needs it | Are upstream pointers better than version-stale recipes? |
| MCP/plugin activation recipes | Hermes enforcement plugin shipped in 1.3; other integrations remain deferred | Operator live denial plus hook-contract test, 2026-07-11 | Hermes activation is documented and tested; which other integration has verified demand and testable version, secret, and authority boundaries? |
| Cron/watchdog/control tower | 1.1+ | Repeated scheduling need beyond the shipped operator recipes | Still deferred: 1.1 documents cron recipes for metabolism and recert but installs no scheduler. Is there one scheduler owner, positive heartbeat, and usefulness evidence? |
| Team vault sync/permissions/merge tooling | 1.2+ | One external team request or two maintainer production uses not served by the 1.1 contract | Can tooling enforce the contract without owning user content or inventing a second merge authority? |
| Backup/restore/upgrade tooling | Upgrade shipped in 1.2; backup/restore remains deferred | Trigger fired by the 1.1 release's first real upgrade need | Upgrade now uses manifest migration without owning upstream, pack, or user state; what evidence should trigger backup/restore? |
| VPS/local-LLM/hybrid/satellite | 1.1+ | Real deployment request | Is the topology available for repeatable tests? |
| Hosted UI | Separate project | Explicit product decision | Why should it enter the core distribution? |
| Non-Hermes compatibility | Later | Maintainer plus user demand | Can platform-neutrality become a tested claim? |
| Automated model grading | 1.1+ | Repeated evaluation operations and held-out data | Can it preserve provenance and human-judgment limits? |

## Candidates recorded 2026-07-12 (operator production incidents, gated for 1.4)

Eight patterns emerged from one operator production weekend (2026-07-11/12). Per admission policy,
each is recorded with its evidence status and stays out of doctrine until its gate fires. Three
carry multiple dated incidents already; five carry one incident or zero time-in-service.

| Capability | Earliest release | Evidence status / activation trigger | Blocking question |
|---|---:|---|---|
| Prose-contract registry + executable checkers ("a promise without a check is a future incident") | 1.4 | THREE dated incidents 2026-07-10..12: a brief's prompt rewrite silently evicted an integration for 3 days; a scheduler reported ok while the delivery plane dropped the message; a spec sentence ("missing line = alarm") was unenforceable until scripted. First live checker run caught its own motivating incident. | Can evaluation scenarios test checker-firing without shipping a scheduler? |
| False-green verification taxonomy (job-ran ≠ delivered; kill-rc-0 ≠ dead, verify new PID; hand-run ≠ timer-run; self-test-passed ≠ real-formats-handled) | 1.4 | Each rule carries a distinct dated operator incident (2026-07-08..12), incl. one committed by the orchestrating agent itself. | Which rules become doctrine lines vs. scenario expected-results? |
| Prompt-as-code versioning (extract scheduled-job prompts to git; diff + drift callouts on change) | 1.4 | One incident class (the eviction above); mechanism live in production since 2026-07-12 (93 prompts under version control). | Is one incident class plus production service enough, or wait for a second drift catch? |
| Tiered auto-fixer (mechanical playbook w/ cooldown caps → diagnose-only escalation → failure ledger; every action confesses) | 1.4+ | Deployed 2026-07-12; ZERO live saves on record. Trigger: first real save, or a second motivating incident. | Can cooldown/never-disable boundaries be certified without a live scheduler in the exam? |
| Scoped-allowlist agent dispatch (builder agents run under narrow file/tool allowlists with the deliverable's own dangerous commands denied during build — guardrails, never approvals-off) | 1.4 | Three clean production builds 2026-07-12; review caught one real-world-format bug and one dropped output-contract each time. Two-production-use path arguably satisfied. | How does an allowlist recipe stay runner-portable? |
| Amortized token audit (per-run cost × scheduled frequency from agent logs; interactive-session replay measured as the dominant class) | 1.4+ | One audit run 2026-07-12 (found 65% of spend outside cron fleet); verification rerun scheduled 2026-07-19. Trigger: projection confirmed or honestly refuted by the rerun. | Does the method generalize beyond one gateway's log format? |
| Operator-execution feedback + program kill-criterion (ledger records real fills vs printed levels; the automation carries its own invalidation and tracks "week N of M") | 1.4+ | Wired 2026-07-12, zero graded cycles. Trigger: first weekly replay grading real fills. | Can "unused system is a finding" be scored without operator-privacy leakage? |
| Advisor red-team ritual (adversarial review by a second model family before load-bearing commits) | 1.4+ | Declared 2026-07-12 after an orchestrator false-positive; never yet exercised. Trigger: first exercised review with findings addressed on the record. | Does it earn scenarios, or remain a team-contract line? |

## Pack-level triggers

The default inert-pack trigger is one external user request **or** two maintainer production uses that cannot be served cleanly by Research, Agent Ops, the base vault, or the routed library. Each pack adds narrower gates:

- **Context Spine:** separate provenance, licensing, freshness, bounded-retrieval, privacy, install/uninstall, and annotation-preservation review.
- **Deep Timeline:** Context Spine first; historical local-context, falsifier, and non-applicability review.
- **Markets:** separate research-only authority, liability, freshness, and no-edge review.
- **Personal OS:** separate privacy, retention, and universal-doctrine review.
- **Learning OS:** outcome measurement and ongoing curriculum-maintenance review.
- **Product OS, Software Delivery, Simulation Lab:** named decision delta and proof that existing shipped surfaces do not already own the workflow.

Every activated pack needs a source-derived seed, operator sanitization review, an owner, review budget, install/uninstall verification, and a kill condition.

## Corpus deferrals

Release 1.0 ships no Context Spine or Deep Timeline payload. The inspected 76 public non-market artifacts required source upgrading, as-of/freshness work, market-boundary adjudication, and claim-level review; that was adaptation-heavy, so Contract only was mandatory. The full 242-file private timeline, additional critic cards, market corpus, corpus automation, and three corpus-specific model scenarios all defer.

A future corpus release must use separate namespaces for immutable distribution payload and user annotations, a manifest with content hashes and public source coordinates, a small index, numeric retrieval bounds, caution/freshness fields, and preservation-first uninstall. It may not turn an index or hash into claim authority.
