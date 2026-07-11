# Pre-tool-use enforcement

Release 1.1 applies the line **doctrine for judgment, code for rules**. The distribution ships a
small runner-agnostic guard for three machine-checkable boundaries: protected-path writes,
credential echo, and retrieval caps. Authority, relevance, evidence quality, and other judgment
calls remain doctrine-level responsibilities.

## Runner contract

A runner sends exactly one JSON object to `enforcement/pre_tool_use.py` on standard input before
each tool call:

```json
{"tool":"search_sources","args":{"query":"example","limit":25}}
```

It supplies the actual Hermes home and vault so policy placeholders can be resolved:

```sh
printf '%s\n' '{"tool":"search_sources","args":{"query":"example","limit":25}}' |
  python3 enforcement/pre_tool_use.py --hermes-home "$HOME/.hermes" --vault "$VAULT"
```

The command prints one verdict object:

```json
{"decision":"allow","reason":"no enforced rule matched","rule":null}
```

An allow exits 0. A policy denial exits 2. Malformed input, an unreadable policy, missing required
path context, or invalid policy/context returns a deny with rule `malformed-input` and exits 3.
The runner must execute the tool only after exit 0. It may pass `--declared-cap N` when a higher
retrieval cap has been explicitly approved for that envelope. The policy is JSON-form YAML and is
parsed with the Python standard library.

Write/edit/append/move/delete/copy-class tools are denied when a path-like argument lexically
normalizes into Hermes `config.yaml`, Hermes `bin/`, or the vault install-manifest area. Read-class
tools are not path-blocked. Any tool is denied when its serialized arguments match a named
credential pattern; the verdict identifies the rule but never repeats the matched value. Limit,
`max_results`, `result_limit`, and `top_k` arguments default to a maximum of 25.

Installed runners invoke the namespaced copy, for example:

```sh
python3 "$HOME/.hermes/distributions/evidence-first/enforcement/pre_tool_use.py" \
  --hermes-home "$HOME/.hermes" --vault "$VAULT"
```

The installer only places the manifest-tracked payload and prints this wiring advisory. It never
edits `config.yaml`; hook registration is runner-specific.

## Completion gate

The completion gate is the outbound partner to the pre-tool-use hook: the pre-tool-use hook checks
a proposed tool call on the way in, while `enforcement/completion_gate.py` checks a final answer on
the way out. A runner sends exactly one final-answer envelope on standard input:

```json
{"disposition":"watch","content":"Trigger: new evidence arrives. Review date: 2026-08-01."}
```

```sh
printf '%s\n' \
  '{"disposition":"watch","content":"Trigger: new evidence arrives. Review date: 2026-08-01."}' |
  python3 enforcement/completion_gate.py
```

The verdict shape and exit contract match `pre_tool_use.py`: allow exits 0, policy denial exits 2,
and malformed input or policy exits 3 with rule `malformed-input`. A runner should publish a final
answer only after exit 0. Canonical dispositions and the three legacy aliases mirror
`scripts/evaluation_lib.py`; they live in policy because the installed enforcement payload must be
self-contained. For alias-normalized `watch` and `no-action`, content must match both
`(?i)state.change|trigger` and `(?i)decay|review date`. Those policy patterns deliberately mirror
the assertions in evaluation scenarios 09 and 14. Other canonical dispositions have no outbound
surface requirement in this release.

## Evaluation harness

The shipped Codex and replay adapters keep both hooks off by default, so paired evaluations still
measure doctrine alone. Set `EVAL_ENFORCE=1` to evaluate every model tool call before execution or
replay stubbing and each completed answer after its disposition event. An inbound denial records a
`guard_denied` transcript event with the tool and rule. An outbound denial records a
`completion_denied` event after the disposition; the adapter does not retry or alter the answer.
The live adapter returns an inbound tool error naming that rule to the model without exposing
matched credential text. The option is applied identically to treatment and control arms.

## Honest limits

This hook is not a sandbox or a general permission system. A runner that does not call it receives
no enforcement. Lexical path checks do not resolve symlinks. Credential regexes can miss unfamiliar
formats or reject test-like values. Retrieval limits only cover the named limit-style arguments.
The completion regexes verify that parked-state record surfaces are present, not that their content
is specific, feasible, or high quality. Judgment-level doctrine remains advisory, and real
credentials should still be kept out of agent context.
