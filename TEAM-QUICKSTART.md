# Team Quickstart — Agent System 2.0

This gets you from zero to a working agent-and-vault setup in about fifteen minutes, and tells you exactly where the edges are. It assumes nothing about your work domain: what you're installing is general infrastructure — an operating stance for your agent, a routed skill system, a governed vault, and templates — that you then build your own system on top of.

Setting up alone for the first time? Start with [FIRST-HOUR.md](FIRST-HOUR.md).

## What you actually get

- **An operating stance** (`agent/SOUL.md` + authority boundaries): a compact contract for how your agent decides, verifies, and reports — including a closed vocabulary of seven "disposition" labels every piece of work ends with (`act`, `done`, `blocked`, `needs-human`, ...). You'll see these constantly; there's a cheat sheet below.
- **A three-level skill router**: your agent loads one small index at startup, then only the category and skill it needs. This keeps context small and behavior auditable. Your own skills plug into the same system.
- **A 17-folder vault**: an Obsidian-compatible knowledge base with a deliberate layout (Sources, Decisions, Queues, Raw, System, ...) and one worked example chain showing how a source becomes a decision becomes a revisable belief.
- **Ten templates** for the recurring artifacts (source notes, decision packets, task/result packets, belief revisions, merge proposals, ...).
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

When needed, the installer prints the manual `skills.external_dirs` addition. It also always prints two Hermes plugin activation steps: run `hermes plugins enable evidence-first-enforcement`, then restart the Hermes gateway. This is deliberate: the distribution never edits your Hermes config, enables a plugin, or restarts a service. Perform the printed steps, then:

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
4. **File the result through metabolism.** Have the agent write it only to `Inbox/` with a valid `route:` frontmatter destination, then run `python3 scripts/metabolism.py --vault "$HOME/Evidence-First-Vault"`. Use `templates/source-note.md` and, if it led to a choice, `templates/decision-packet.md` for the resulting durable artifacts.

## The disposition cheat sheet

Every unit of work ends with exactly one label. They're how you scan agent output at a glance.

### The four you'll see on day one

| Label | Means |
|---|---|
| `done` | the requested outcome itself is verified complete |
| `act` | an action or recorded revision awaits downstream application or verification |
| `blocked` | a dependency, approval, or disputed status or completion claim prevents progress |
| `needs-human` | a judgment or authority call is yours to make |

### The three that arrive with governance

| Label | Means |
|---|---|
| `watch` | parked, with a named condition that reopens it |
| `no-action` | after investigation, deliberately leave world state unchanged without rejecting a candidate |
| `kill` | reject a forward-looking proposal or retire a mechanism, never dispute a completion claim |

Boundary rules: verified completion is `done`, while a completed intermediate revision that still
needs application is `act`. A missing dependency or disputed completion claim is `blocked`; a
judgment or authority decision only a person can make is `needs-human`. `watch` must name its
return condition. `no-action` leaves state unchanged after investigation; it does not reject a
candidate. `kill` rejects a forward-looking proposal or retires a mechanism; it never disputes a
completion claim.

Deprecated aliases in old ledgers: `merge` means `done`, `defer` means `watch`, and `no-edge` means `no-action`.

## Building your own system on top

This is infrastructure — here's where your stuff goes:

- **Your own skills:** create a directory anywhere (e.g. `~/my-skills/`), add it as another `skills.external_dirs` entry, and write `SKILL.md` files following the format in `skills/library/` (frontmatter + focused body). Route them by adding one line to the matching registry under `skills/categories/`. Keep each skill narrow; the router rewards small surfaces.
- **Your own vault content:** anything you add is yours; the installer's manifest tracks only its own files, and the uninstaller will never touch yours. Follow the folder contracts in each folder's landing note, or consciously break them — they're conventions, not locks.
- **Your own templates:** copy an existing one and keep the frontmatter fields; `scripts/verify_templates.py` will validate structure.
- **Your own packs:** `packs/manifest.yaml` shows the contract. A pack is just a folder of vault content plus a `PACK.md` declaring what it's for and when it should die. The eight inert packs are worked examples of *declaring* capability without shipping filler.
- **Check your work:** `bash scripts/dev-gate.sh` runs the whole verification suite; individual verifiers under `scripts/` run standalone.

### Working as a team

Keep each member's installed vault personal and unsynced. Add one shared vault, installed once by a designated owner, and synchronize only that vault. Agents and members capture into its `Inbox/`; the owner's single scheduler runs metabolism to route captures into canon. Canon edits are human-only, and the vault owner governs `System/`. Promote personal notes by copying them with provenance, and copy shared notes back to personal vaults without moving them. The full write, merge, and attribution convention is in [Team Vault Contract](docs/Team-Vault-Contract.md).

## Known boundaries (read before you judge it)

1. **Team sync is contract-only.** The [shared-vault contract](docs/Team-Vault-Contract.md) defines topology, write authority, attribution, promotion, and conflict handling. Real-time sync, permissions enforcement, and automatic merge remain deliberately manual until one external team requests tooling or two maintainer production uses cannot be served cleanly by the contract.
2. **Hermes enforcement requires manual activation.** Hermes v0.18.2+ can use the shipped manifest-tracked plugin after you run the printed enable command and restart the gateway; this release's installer accepts the v0.18.x compatibility line. The dev gate proves the Hermes hook directive contract; the live example records one operator-observed real denial. Other runners must wire the inbound and outbound CLI contracts themselves. A runner that never calls the hooks gets no enforcement, and judgment-level doctrine remains advisory rather than a security layer. Keep real credentials out of anything an agent reads.
3. **Upgrade is manifest-scoped.** `scripts/upgrade.sh` safely migrates distribution-owned base files, preserving edits beside `.incoming` proposals. Packs already installed into the vault are user content and are not upgraded; use uninstall/reinstall if manifest migration cannot complete cleanly.
4. **The eval certificate is narrow.** One model, one date, simulated tools, single-turn scenarios — all checked in under `evaluations/results/`. Run `scripts/recert.sh` for a current single-arm smoke result; it does not replace the paired three-trial/two-arm delta certificate.
5. **Windows is untested.** POSIX path only (WSL2 inferred compatible, not CI-tested).
6. **Empty registries are deliberate.** Four skill categories contain pointers instead of skills — that's declared deferred capability, not breakage.

## Uninstall (safe by design)

```bash
bash scripts/uninstall.sh --vault "$HOME/Evidence-First-Vault" --hermes-home "$HOME/.hermes"
```

Removes only unchanged files it installed, preserves everything you touched or created, never edits your Hermes config (it prints the one line to remove), and verifies its own work.

## Feedback

File friction as an issue using the improvement-proposal shape in `templates/improvement-proposal.md` — what you expected, what happened, what evidence would fix it. Real-use reports are literally the release currency of this project: they drive the 1.1 roadmap and the supersession clock for the predecessor repos.
