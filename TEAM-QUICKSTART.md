# Team Quickstart — Agent System 2.0

This gets you from zero to a working agent-and-vault setup in about fifteen minutes, and tells you exactly where the edges are. It assumes nothing about your work domain: what you're installing is general infrastructure — an operating stance for your agent, a routed skill system, a governed vault, and templates — that you then build your own system on top of.

## What you actually get

- **An operating stance** (`agent/SOUL.md` + authority boundaries): a compact contract for how your agent decides, verifies, and reports — including a closed vocabulary of ten "disposition" labels every piece of work ends with (`act`, `done`, `blocked`, `needs-human`, ...). You'll see these constantly; there's a cheat sheet below.
- **A three-level skill router**: your agent loads one small index at startup, then only the category and skill it needs. This keeps context small and behavior auditable. Your own skills plug into the same system.
- **A 16-folder vault**: an Obsidian-compatible knowledge base with a deliberate layout (Sources, Decisions, Queues, Raw, System, ...) and one worked example chain showing how a source becomes a decision becomes a revisable belief.
- **Nine templates** for the recurring artifacts (source notes, decision packets, task/result packets, belief revisions, ...).
- **Two optional packs** (Research and Agent Ops) with working example content, plus eight declared-but-empty packs that activate only if you ever need them.
- **Lifecycle tools**: installer, verifier, uninstaller — all hash-verified, all reversible, none of them ever touch files you own.

Behavior claim, honestly stated: on the recorded eval pairing, loading this doctrine changed agent behavior on 10 of 16 adversarial scenarios versus the same model without it. It is a strong starting posture, not a guarantee — see "Known boundaries."

## Install (10 minutes)

Prerequisites: Hermes Agent v0.18.x, macOS or Linux, Python 3, git, rsync.

```bash
git clone https://github.com/w3rdist-creator/agent-system-2.0.git
cd agent-system-2.0

# 1. See what would happen (writes nothing):
bash scripts/install.sh --dry-run --vault "$HOME/Evidence-First-Vault"

# 2. Install for real:
bash scripts/install.sh --vault "$HOME/Evidence-First-Vault"
```

The installer will print **one manual step** — add one line to `~/.hermes/config.yaml` under `skills.external_dirs`, exactly as printed. This is deliberate: nothing in this system ever edits your Hermes config, in either direction. Make the edit, then:

```bash
# 3. Confirm the install is complete and active:
bash scripts/verify-install.sh \
  --vault "$HOME/Evidence-First-Vault" \
  --hermes-home "$HOME/.hermes"

# 4. Add the two working packs:
bash scripts/install-pack.sh research --vault "$HOME/Evidence-First-Vault"
bash scripts/install-pack.sh agent-ops --vault "$HOME/Evidence-First-Vault"
```

If `verify-install.sh` fails, it tells you the exact missing step. Open the vault folder in Obsidian (or any Markdown editor) and start from `Home.md`.

## Your first hour

1. **Read `Home.md` and `Vault Self-Model.md`** in the vault — five minutes; they explain what each folder is for and, importantly, what the vault refuses to become (a write-only note dump).
2. **Follow the seed chain.** Start at `Sources/` and follow the links: a real source note → a decision packet → a review → a belief that got revised when new evidence arrived. This chain is the whole operating model in miniature. Everything you build follows this shape.
3. **Run one real task through your agent.** Ask your Hermes agent to research something small and file it. Watch for two behaviors the doctrine installs: it should read its sources before concluding, and it should end with a disposition label and a short "decision surface" instead of a wall of text.
4. **Process the result into the vault** using `templates/source-note.md` and, if it led to a choice, `templates/decision-packet.md`.

## The disposition cheat sheet

Every unit of work ends with exactly one of these. They're how you scan agent output at a glance:

| Label | Means |
|---|---|
| `act` | a justified bounded action was taken or started; more remains |
| `done` | the requested outcome itself is verified complete |
| `blocked` | a dependency, approval, or missing evidence prevents progress |
| `needs-human` | a judgment or authority call is yours to make |
| `no-action` | evidence says deliberately leave things unchanged |
| `watch` | parked, with a named condition that reopens it |
| `defer` | moved out of scope, with a governed return condition |
| `merge` | duplicates were consolidated into one survivor |
| `kill` | a proposal or mechanism was rejected or retired |
| `no-edge` | investigated; no supported advantage or connection found |

## Building your own system on top

This is infrastructure — here's where your stuff goes:

- **Your own skills:** create a directory anywhere (e.g. `~/my-skills/`), add it as another `skills.external_dirs` entry, and write `SKILL.md` files following the format in `skills/library/` (frontmatter + focused body). Route them by adding one line to the matching registry under `skills/categories/`. Keep each skill narrow; the router rewards small surfaces.
- **Your own vault content:** anything you add is yours; the installer's manifest tracks only its own files, and the uninstaller will never touch yours. Follow the folder contracts in each folder's landing note, or consciously break them — they're conventions, not locks.
- **Your own templates:** copy an existing one and keep the frontmatter fields; `scripts/verify_templates.py` will validate structure.
- **Your own packs:** `packs/manifest.yaml` shows the contract. A pack is just a folder of vault content plus a `PACK.md` declaring what it's for and when it should die. The eight inert packs are worked examples of *declaring* capability without shipping filler.
- **Check your work:** `bash scripts/dev-gate.sh` runs the whole verification suite; individual verifiers under `scripts/` run standalone.

## Known boundaries (read before you judge it)

1. **Single-player.** One operator, one vault, one Hermes home. There is no shared-vault merge or team-sync story yet — coordinate across teammates manually.
2. **Doctrine is advisory, not enforced.** The stance measurably changes behavior, but nothing at runtime *blocks* an agent that ignores it. Treat authority boundaries as strong defaults, not a security layer, and keep real credentials out of anything an agent reads.
3. **No upgrade automation yet.** Install and uninstall are tested and safe; upgrading in place is not built. For now: uninstall (it preserves everything you modified), reinstall, re-add packs.
4. **The eval certificate is narrow.** One model, one date, simulated tools, single-turn scenarios — all checked in under `evaluations/results/`. Re-run it against your own model with `scripts/eval_adapter_codex.py` if you want current numbers.
5. **Windows is untested.** POSIX path only (WSL2 inferred compatible, not CI-tested).
6. **Empty registries are deliberate.** Four skill categories contain pointers instead of skills — that's declared deferred capability, not breakage.

## Uninstall (safe by design)

```bash
bash scripts/uninstall.sh --vault "$HOME/Evidence-First-Vault" --hermes-home "$HOME/.hermes"
```

Removes only unchanged files it installed, preserves everything you touched or created, never edits your Hermes config (it prints the one line to remove), and verifies its own work.

## Feedback

File friction as an issue using the improvement-proposal shape in `templates/improvement-proposal.md` — what you expected, what happened, what evidence would fix it. Real-use reports are literally the release currency of this project: they drive the 1.1 roadmap and the supersession clock for the predecessor repos.
