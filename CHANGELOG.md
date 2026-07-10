# Changelog

This changelog preserves the build narrative because the public export intentionally contains one sanitized initial commit.

## 1.1.0 — 2026-07-10

Release 1.1 adds the distribution's machine enforcement and operating metabolism without expanding its ownership boundary:

- **Enforcement layer:** ships a runner-agnostic pre-tool-use hook for protected-path writes, credential echo, and retrieval caps; enforcement is active only when a runner wires the hook.
- **Vault metabolism:** routes opted-in Inbox captures, archives exact duplicates, raises decay work into a bounded Resolve Queue, screams on queue-cap breaches, and writes an honest run ledger without deleting or overwriting content.
- **Live recertification:** adds a one-command, fail-closed treatment-arm smoke examiner with dated append-only results; a recert row is not a paired delta certificate.
- **Telemetry:** derives idempotent usage rows from explicitly named evaluation, recert, and metabolism artifacts; it inspects no note content and writes nothing when there is no evidence.
- **Team vault contract:** defines personal/shared topology, Inbox-only submission, durable attribution, promotion provenance, and `.incoming` merge proposals; this is a coordination contract, not sync, permissions, or CRDT tooling.
- **Disposition consolidation:** closes runtime outcomes to seven labels (`act`, `watch`, `no-action`, `blocked`, `done`, `kill`, `needs-human`); the evaluation library still accepts the retired `defer`, `no-edge`, and `merge` labels as compatibility aliases for historical 1.0 records.
- **Subsequent-release gate:** adds a clean-worktree, version-heading, update-range privacy, and development gate for multi-commit public updates while retaining the fresh single-commit publication gate for exports.

- **Evaluation status (2026-07-10):** the paired 96-trial gpt-5.6-sol run at high reasoning in `evaluations/results/run-2026-07-10-gpt-5.6-sol-1.1.csv` recorded 5/16 confirmed deltas, below the fixed threshold of 8, with the operator-directed release override recorded in that CSV. Treatment passed deterministically on 8/16 scenarios. Scenarios 01 and 05 passed 3/3 in both arms on this model and are queued for redesign or removal under the methodology. One unmounted-fixture trial was re-administered, and scenario 12's write assertion was widened arm-neutrally to accept the `.incoming` proposal convention. The gpt-5.5 medium 10/16 certificate remains a 1.0 result for the former ten-label vocabulary only. A live gpt-5.6-sol high scenario 15 recert smoke passed and is recorded in `evaluations/results/recert-log.csv`; it does not replace paired evidence. The full development gate was green.

## 1.0.0 — Release candidate — 2026-07-10

Public release name: **Agent System 2.0** (formal project name: Evidence-First Hermes Distribution; installed namespace `evidence-first`).

- **Phase 0 — govern the repository:** filed the repository's own improvement proposal and loop contract; froze 475 public file coordinates and 12 capability families; diagnosed the predecessor super-repo; verified the Hermes v0.18.2 ownership mechanism; chose Contract only for corpus payloads.
- **Phase 1 — evaluate before doctrine:** built paired treatment/control methodology, three-trial threshold, 16 scenarios, hidden human rubrics, deterministic trace assertions, result provenance schema, and no-runner honesty boundary.
- **Phase 2 — stance and routing:** added posture-only stance, authority boundaries, three-level loading model, two startup skills, line-to-scenario mapping, and hard context regression gates.
- **Phase 3 — catalog:** dispositioned all 475 public rows (`adapt` 9, `merge` 127, `supersede` 111, `external-pointer` 216, `reject` 12), routed 16 skills through 11 registries, and closed licensing checks without vendoring unverified third-party material.
- **Phase 4 — vault and templates:** shipped a 16-layer vault, immutable/append-only Raw boundary, one real source-derived seed chain, nine templates, examples, and wikilink/structure validation.
- **Phase 5 — bounded packs:** shipped Research and Agent Ops, retained eight declaration-only packs, completed all core and deferrable pack mechanisms within budget, and kept Context Spine payload-free.
- **Phase 6 — safe lifecycle:** added reference-first install, manifest verification, both pack install paths, conflict proposals, preservation-first uninstall, deterministic development gate, and publication gate.
- **Phase 7 — public handoff:** added public documentation, Linux/macOS CI, fresh sanitized export tooling, one-commit publication gate, operator command handoff, and final effort accounting.

- **Release gates (2026-07-10):** operator signed sanitization for all 136 accepted rows and 13 seed artifacts; confirmed the MIT/CC BY 4.0 split; paired model runs executed on gpt-5.5 and checked in (1/16 confirmed deltas — below the internal 8-delta bar; see the effort ledger for the operator decision record). The first non-builder clean-room install found a real blocker: Hermes v0.18.x `config set` cannot append to `skills.external_dirs`, so the installer's config write always failed against real Hermes while the permissive test stub passed. Fixed by making the config addition a printed manual operator step (symmetric with uninstall's manual removal), teaching `verify-install.sh` to fail closed until the entry exists, and correcting the test stub to refuse list appends exactly like the real CLI.

- **Performance round (2026-07-10, same day):** iterated doctrine and instrument to an earned eval pass — 10/16 confirmed deltas against the 8-scenario threshold (progression 1/16 → 2/16 → 6/16 → 10/16, all runs checked in). Shipped the reference eval runner (`scripts/eval_adapter_codex.py` + `scripts/eval_adapter_replay.py`) so the suite is always executable; fixed two instrument-faithfulness defects (per-trial write persistence; over-narrow assertion patterns); added the simulation-faithfulness contribution rule; sharpened disposition taxonomy boundaries and authority-boundary overwrite/credential clauses within the hard context budget. Public release name set to **Agent System 2.0**.

The candidate claims a measured behavioral delta only for the recorded pairing and date above. Publication and predecessor supersession remain explicit gates.
