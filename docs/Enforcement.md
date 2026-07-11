# Enforcement

Release 1.3 ships a Hermes plugin requiring Hermes Agent v0.18.2 or newer, where the hook engine
supports the required `pre_tool_call` directive contract. The release installer retains its
v0.18.x compatibility gate. The plugin connects the
distribution's runner-agnostic inbound and outbound policy evaluators to Hermes tool dispatch and
answer transformation. Authority, relevance, evidence quality, and other judgment calls remain
doctrine-level responsibilities.

## Install and activate on Hermes

`scripts/install.sh` places the manifest-tracked plugin at
`<hermes-home>/plugins/evidence-first-enforcement/`. It writes the normalized `--vault` value to
`vault-path.txt` beside the plugin and prints, but never performs, these two operator actions:

```sh
hermes plugins enable evidence-first-enforcement
# Then restart the Hermes gateway.
```

The existing manual `skills.external_dirs` configuration step is still required when that path is
not already present. The installer never edits `config.yaml`, enables plugins, or restarts Hermes.
Run `scripts/verify-install.sh` after the manual config addition to verify the distribution and
plugin payloads.

At runtime the plugin resolves the Hermes home through Hermes' profile-aware helper, with
`HERMES_HOME` and then `~/.hermes` as standalone fallbacks. It resolves the vault in this order:

1. `EVIDENCE_FIRST_VAULT` environment variable;
2. the installed `vault-path.txt`;
3. loud disable with a warning when neither provides a usable path.

An unreadable policy or vault setting disables the plugin conspicuously rather than bricking every
agent tool call. A policy denial still acts. The secret-free heartbeat stays operator-local at
`enforcement-log.jsonl` beside the installed plugin; it is not part of the distribution payload or
manifest.

If a plugin directory already exists, preservation rules apply normally: existing files stay
untouched and shipped replacements are written as `.incoming` proposals. Reconcile the proposals
manually, retain the installed `vault-path.txt`, then enable/restart as above. Upgrade similarly
replaces only unchanged manifest-owned files and preserves changed files beside `.incoming`
proposals. Uninstall removes only unchanged manifest-owned plugin files.

## What the Hermes plugin enforces

Before each tool call, Hermes invokes `pre_tool_call`. A denial returns the hook-engine directive:

```json
{"action":"block","message":"[evidence-first] blocked by protected-path-write: ..."}
```

Hermes treats that message as the tool result and does not execute the tool. The adapter maps
Hermes `patch` and mutating `terminal` calls into the existing guard envelope. It enforces three
machine-checkable boundaries: protected-path writes, credential echo, and retrieval caps. Vault
content writes remain allowed; the vault's `.evidence-first` manifest area remains protected.

The `transform_llm_output` hook is the outbound partner. When a `watch` or `no-action` answer lacks
both a state-change/trigger surface and a decay/review-date surface, it appends a visible
annotation. These regexes verify presence, not specificity, feasibility, or quality.

## Evidence boundary

`tests/test_hermes_plugin.py`, run explicitly by `scripts/dev-gate.sh`, imports the shipped module,
registers its hooks in a fixture tool loop, and follows Hermes' block-directive semantics. It
proves at the contract level that a protected-path write and credential-bearing arguments are
blocked, an ordinary vault write proceeds, and a bare parked answer is annotated. CI cannot run a
real Hermes gateway.

The [live enforcement denial](../examples/live-enforcement-denial/README.md) records a sanitized
2026-07-11 operator turn where a real Hermes agent attempted a protected write, reported the block,
and left the proposed file absent. That is live, operator-recorded evidence, not a CI-reproducible
test and not a claim that the plugin is a complete sandbox.

## Other runners: CLI contract

Non-Hermes runners can invoke the runner-agnostic inbound evaluator before each tool call:

```sh
printf '%s\n' '{"tool":"search_sources","args":{"query":"example","limit":25}}' |
  python3 enforcement/pre_tool_use.py --hermes-home "$HOME/.hermes" --vault "$VAULT"
```

It emits one verdict object. Allow exits 0, a policy denial exits 2, and malformed input or broken
policy/context exits 3 with `malformed-input`. A runner must execute the tool only after exit 0.
It may pass `--declared-cap N` when a higher retrieval cap was explicitly approved.

The outbound CLI accepts a final-answer envelope:

```sh
printf '%s\n' \
  '{"disposition":"watch","content":"Trigger: evidence changes. Review date: 2026-08-01."}' |
  python3 enforcement/completion_gate.py
```

Its exit contract matches the inbound evaluator. The Codex and replay evaluation adapters keep
both hooks off by default so paired evaluations measure doctrine alone; `EVAL_ENFORCE=1` enables
the policy identically for treatment and control arms.

## Honest limits

The plugin is not a sandbox or general permission system. It protects only runners and tool paths
that invoke and honor the hooks. Lexical path checks do not resolve symlinks. Credential patterns
can miss unfamiliar formats or reject test-like values. Retrieval limits cover only named
limit-style arguments. Keep real credentials out of agent context.
