# Your first hour with an Evidence-First Hermes agent

This is the guided path from no vault to one verified working session. Allow about 15 minutes of
attention. You need macOS or Linux, Python 3, Git, and Hermes v0.18.x already installed. Confirm
Hermes before going further:

```sh
hermes --version
python3 --version
git --version
```

Success includes a line like `Hermes Agent v0.18.2`; the Hermes line must contain `v0.18.`. If it
does not, stop at [the Hermes version refusal](docs/When-It-Refuses.md#hermes-version-refusal).

This is not a chatbot skin. It is a governed operating layer for an agent you already have.

The commands below use the default vault at `$HOME/Evidence-First-Vault` and the default Hermes
home at `$HOME/.hermes`. Run them exactly in order.

## 1. Clone the distribution

```sh
git clone https://github.com/w3rdist-creator/agent-system-2.0.git
cd agent-system-2.0
```

Success looks like:

```text
Cloning into 'agent-system-2.0'...
```

The `cd` command is silent on success. If cloning refuses, confirm that Git is installed and that
you can open the repository URL, then rerun these two commands. Nothing has been installed yet.

## 2. Read the dry-run plan

```sh
bash scripts/install.sh --dry-run --vault "$HOME/Evidence-First-Vault"
```

Success includes these real installer lines followed by `PLAN` lines:

```text
DRY RUN: no files or Hermes configuration will be written
PLAN config: MANUAL ADDITION REQUIRED after install — in ...
PLAN manual plugin step 1: hermes plugins enable evidence-first-enforcement
PLAN manual plugin step 2: restart the Hermes gateway after enabling the plugin
```

Read the destinations. They should be inside your chosen vault, `$HOME/.hermes/distributions/`,
and `$HOME/.hermes/plugins/`. A pre-existing destination becomes an `.incoming` proposal; it is
not overwritten. If the version check stops here, use [Hermes version refusal](docs/When-It-Refuses.md#hermes-version-refusal).

## 3. Install for real

```sh
bash scripts/install.sh --vault "$HOME/Evidence-First-Vault"
```

On a fresh Release 1.3.1 install, success includes:

```text
INSTALLED: 113 owned files
MANUAL CONFIG ADDITION REQUIRED: in ...
CONFIGURED: pending the manual skills.external_dirs addition above; run verify-install.sh to confirm activation
MANUAL PLUGIN ENABLE REQUIRED: hermes plugins enable evidence-first-enforcement
MANUAL GATEWAY RESTART REQUIRED: restart the Hermes gateway after enabling the plugin so hooks become active
```

The pending line is expected protection, not a failed install. Continue to the manual step. If
you see `.incoming`, read [Incoming files appeared](docs/When-It-Refuses.md#incoming-files-appeared)
before enabling anything.

## 4. Make the one manual Hermes configuration addition

Open the configuration file:

```sh
nano "$HOME/.hermes/config.yaml"
```

Add exactly this one list entry under `skills.external_dirs`:

```yaml
    - ~/.hermes/distributions/evidence-first/skills
```

For example, change this:

```yaml
skills:
  external_dirs:
    - /opt/shared/hermes-skills
```

to this, leaving the existing entry intact:

```yaml
skills:
  external_dirs:
    - /opt/shared/hermes-skills
    - ~/.hermes/distributions/evidence-first/skills
```

If your file has no `skills:` section, add this complete block at the left margin:

```yaml
skills:
  external_dirs:
    - ~/.hermes/distributions/evidence-first/skills
```

In nano, save with Control-O, Enter, then exit with Control-X. The installer refuses to make this
edit because `config.yaml` belongs to you and Hermes; preserving user configuration requires your
explicit review.

This edit is silent. The next verification command is the success test. If you skipped or
mis-indented the line, follow [Verify-install before manual config](docs/When-It-Refuses.md#verify-install-before-manual-config).

## 5. Verify every installed file and the activation path

```sh
bash scripts/verify-install.sh \
  --vault "$HOME/Evidence-First-Vault" \
  --hermes-home "$HOME/.hermes"
```

Success is exactly:

```text
PASS: installed files and hashes verified across 113 manifest file(s)
```

Anything beginning with `FAIL:` is actionable evidence. Do not enable the plugin until this step
passes; start with [When It Refuses](docs/When-It-Refuses.md).

## 6. Enable enforcement; restart only if you use the gateway

Enable the installed plugin:

```sh
hermes plugins enable evidence-first-enforcement
```

Then confirm its row is `enabled`:

```sh
hermes plugins list
```

Success looks like a row containing:

```text
evidence-first-enforcement   enabled
```

Only if you use Hermes through its messaging gateway, restart that gateway so its already-running
process loads the hook:

```sh
hermes gateway restart
```

A direct `hermes chat` user does not need a gateway restart. If enablement reports an `.incoming`
plugin conflict, reconcile it using [Incoming files appeared](docs/When-It-Refuses.md#incoming-files-appeared)
before retrying.

## 7. Give the agent one real, bounded task

```sh
hermes chat --query "Read $HOME/Evidence-First-Vault/Home.md and \"$HOME/Evidence-First-Vault/Vault Self-Model.md\". Explain in five bullets how a new note should enter and move through this vault. Cite the files you read, make no changes, and end with exactly one disposition plus a short decision surface."
```

A good answer proves it read both files, distinguishes Inbox capture from durable routing, and
ends in this shape:

```text
Disposition: done
Decision surface: Read both named vault files; the requested explanation is complete and no file was changed.
```

Exact prose may differ. `done` is correct because the requested explanation itself is verified
complete. A refusal to write a protected file or echo a credential is working protection; see
[Guard denial in a live session](docs/When-It-Refuses.md#guard-denial-in-a-live-session). A visible
parked-state note is explained under [Completion annotation](docs/When-It-Refuses.md#completion-annotation).

## 8. File the result as an Inbox capture with a route

```sh
cat > "$HOME/Evidence-First-Vault/Inbox/first-session.md" <<'EOF'
---
route: Reports
---

# First session

Hermes read Home.md and Vault Self-Model.md, then explained the Inbox-to-durable-note path.
Disposition: done.
EOF
sed -n '1,4p' "$HOME/Evidence-First-Vault/Inbox/first-session.md"
```

Success is the exact frontmatter you just filed:

```text
---
route: Reports
---
```

`route:` is an explicit opt-in. Without it, metabolism safely leaves the note in Inbox and reports
`SKIP`.

## 9. Run metabolism once and watch the route happen

```sh
python3 scripts/metabolism.py --vault "$HOME/Evidence-First-Vault"
```

In this fresh path, success ends with:

```text
METABOLISM: routed=1, deduped=0, decayed=0, skipped=0, screams=0, inbox=0, resolve_queue=0
HEALTHY: Inbox count 0; Resolve Queue entry count 0; cap 25
```

The earlier `ROUTE:` line shows `Inbox/first-session.md` moving to
`Reports/first-session.md`. Metabolism never overwrites or deletes content. If it exits 1 with
`SCREAM`, use [Metabolism queue scream](docs/When-It-Refuses.md#metabolism-queue-scream).

## Your three loops

Metabolism, live recertification, and telemetry are useful only with one clear owner each. Preview
a ready-to-paste 03:05 / 03:25 / 03:50 plan:

```sh
bash scripts/wire-loops.sh --vault "$HOME/Evidence-First-Vault"
```

The final line is:

```text
this tool prints; you paste — one scheduler, one owner, and it is you
```

The helper changes nothing. Read its wrappers and scheduler plan before you paste any part.

## Growing past day one

When another person joins, move to [Team Quickstart](TEAM-QUICKSTART.md) and the
[Team Vault Contract](docs/Team-Vault-Contract.md). For the mechanics behind today’s steps, read
[Enforcement](docs/Enforcement.md), [Metabolism](docs/Metabolism.md),
[Recert](docs/Recert.md), [Telemetry](docs/Telemetry.md), and
[When It Refuses](docs/When-It-Refuses.md).
