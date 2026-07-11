# When It Refuses

A refusal is a safe stop with evidence. Match what you see below, use the stated exit, then rerun
the command that stopped. Do not bypass a refusal until you understand the protected boundary.

## Verify-install before manual config

What you will see (the paths reflect the development fixture; yours will reflect your home):

```text
FAIL: config entry missing: in /private/tmp/evidence-first-test-hermes/config.yaml, add '/private/tmp/evidence-first-test-hermes/distributions/evidence-first/skills' as a new entry under skills.external_dirs; the installer never edits config.yaml, so this manual step activates the install
Install verification failed with 1 error(s).
```

Why: verification refuses to call an installed skill tree active until Hermes has an explicit
reference to it.

Resolve: open the `config.yaml` named in your message, add the quoted path as one new list item
under `skills.external_dirs`, preserve every existing item, save, then rerun `verify-install.sh`.
The before/after form is in [FIRST-HOUR step 4](../FIRST-HOUR.md#4-make-the-one-manual-hermes-configuration-addition).

## Hermes version refusal

What you will see when a different version answers:

```text
ERROR: unsupported Hermes version; expected v0.18.x, detected: Hermes Agent v0.19.0
```

Or, when Hermes cannot be found:

```text
ERROR: Hermes version undetectable; install Hermes v0.18.x or use --force-unsupported at your own risk
```

Why: the distribution has verified compatibility only with the v0.18.x line and refuses before
writing when that contract cannot be established.

Resolve: install or select Hermes v0.18.x, make sure `hermes --version` works in this shell, and
rerun the installer. `--force-unsupported` exists for an operator who deliberately accepts
unverified compatibility; it is not the first-timer exit.

## Guard denial in a live session

What you will see for the three machine-enforced boundaries:

```text
[evidence-first] blocked by protected-path-write: write-class tool targets a protected path
[evidence-first] blocked by credential-echo:openai-api-key: arguments match credential rule openai-api-key
[evidence-first] blocked by retrieval-cap: requested limit 26 exceeds approved cap 25
```

Why: the plugin prevents writes to protected distribution/configuration paths, prevents recognized
credentials from entering tool arguments, and bounds an unapproved retrieval request.

Resolve:

- Protected path: have the agent write ordinary content under the vault, but never under
  `$HOME/.hermes/config.yaml`, `$HOME/.hermes/bin/`, or the vault's `.evidence-first/` manifest
  area. Make user-owned configuration changes yourself after review.
- Credential echo: remove the secret from the prompt/tool arguments, rotate it if it was exposed,
  and use the provider's secret store or environment mechanism outside agent context.
- Retrieval cap: retry at 25 or fewer results. A non-Hermes runner may pass an explicitly approved
  higher `--declared-cap`; do not increase a cap merely to silence the refusal.

## Completion annotation

What you will see appended to a bare `watch` or `no-action` answer:

```text
[evidence-first] parked-state surface missing: include both state_change_condition/trigger and review_or_decay_date.
```

Why: a parked decision without a return condition and a review/decay surface can disappear
silently while looking complete.

Resolve: ask the agent to restate the answer with both fields, for example `Trigger: the source
changes.` and `Review date: 2026-08-01.` The annotation checks that the surfaces exist; you still
judge whether they are specific and useful.

## Metabolism queue scream

What you will see when both budgets are over the default cap (the counts reflect the run):

```text
SCREAM: Inbox count 26 (cap 25); Resolve Queue entry count 26 (cap 25)
```

Why: an over-cap Inbox or Resolve Queue means intake is outrunning review, so a quiet success would
hide operational debt; metabolism records the run and exits 1.

Resolve: read the `SKIP` and `DECAY` lines, then route valid Inbox notes, correct missing/invalid
`route:` values, and resolve cards in `Queues/Resolve Queue.md` by recording the resulting state
change. Rerun `python3 scripts/metabolism.py --vault PATH`. Do not simply raise `--queue-cap`
unless you have deliberately changed the queue budget and ownership capacity.

## Upgrade without a prior install

What you will see:

```text
ERROR: install manifest not found; run install.sh before upgrade
```

Why: upgrade cannot distinguish distribution-owned files from your content without the prior
install manifest.

Resolve: use `scripts/install.sh` for the first installation. If you expected an existing install,
confirm you passed the same `--vault` used originally and that
`<vault>/.evidence-first/install-manifest.json` still exists before retrying.

## Incoming files appeared

What you may see during upgrade (your paths will differ):

```text
PRESERVED WITH INCOMING: /private/tmp/evidence-first-test-hermes/distributions/evidence-first/agent/SOUL.md -> /private/tmp/evidence-first-test-hermes/distributions/evidence-first/agent/SOUL.md.incoming
```

Or a safe stop when an unresolved proposal already exists:

```text
ERROR: conflict proposal already exists; refusing to overwrite: /path/to/file.incoming
```

Why: `.incoming` is the preservation-first conflict proposal containing the distribution's new
payload beside an existing or modified file; your file was not overwritten.

Resolve: compare the original and `.incoming` files, decide which incoming changes belong in the
original, merge those changes deliberately, verify the result, then remove or archive the
`.incoming` proposal. Retain `vault-path.txt` when reconciling the plugin. Rerun verify or upgrade
only after every relevant proposal is resolved.
