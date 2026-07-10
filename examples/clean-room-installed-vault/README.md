# Clean-Room Installed Vault — reserved for the non-builder record

This directory is intentionally empty of vault content.

Plan §1 and §18 require a **non-builder** to complete a clean-room install and record the result. The builder cannot produce that evidence: a builder-generated "clean-room" record would be fabricated evidence, which the builder contract forbids. Builder-run install/uninstall transcripts exist separately in `docs/Effort-Ledger.md` (Phase 6 and Phase 7 gate output) and are labeled as builder-run.

When the non-builder clean-room install happens, this directory receives:

1. `install-transcript.md` — the verbatim command sequence and output, with date, installer identity role (non-builder), Hermes version, and OS.
2. `vault-tree.txt` — the resulting vault file listing (`find <vault> -type f | sort`).
3. `verify-output.txt` — the `verify-install.sh` output for that install.
4. `disposition.md` — blocker-free or the blockers found, using the closed disposition vocabulary.

Until those files exist, the clean-room gate is **open** and the supersession clock in the loop contract has not started.

## Record — 2026-07-10

The four files beside this README are the non-builder record: a fresh codex-cli agent session with no build context installed the distribution into a sandboxed Hermes-home fixture following only the repository documentation, performed the printed manual `skills.external_dirs` addition, and finished `blocker-free` / `done`. A production-Hermes install is deliberately left to the operator.

`attempt-1-blocked/` preserves the first attempt, which ended `blocked` after catching a real installer defect (Hermes v0.18.x `config set` cannot append to lists); the fix it forced is recorded in the effort ledger and CHANGELOG. The blocked record is retained as evidence that this gate does real work.
