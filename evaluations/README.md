# Behavioral evaluation methodology

This suite asks one narrow question: does loading the Evidence-First distribution change observable behavior relative to the same model without it? It does not treat fluent doctrine recall as evidence of contribution.

## Paired design

Each scenario uses the same model, model version, tools, fixture, and `task.md` in two arms. The treatment arm loads the scenario's declared distribution stance and selected skills. The control arm loads only the generic control prompt. Scenario titles, `scenario.yaml`, expected assertions, and `rubric-hidden.md` are never included in the evaluated model's request.

Every scenario runs three trials per arm. Deterministic treatment assertions pass only when all three treatment trials pass. A scenario has a confirmed delta only when treatment passes 3/3 and control fails at least 2/3. Publication requires at least eight surviving scenarios with confirmed deltas, unless the operator records a signed override and rationale. Paired model runs are a release gate, not a CI gate; CI runs schema validation and never fabricates model results.

A scenario that passes in both arms is baseline behavior, not distribution evidence. It must be redesigned to discriminate contribution or removed from the surviving suite and from doctrine claims.

## Scenario and assertion separation

Every scenario directory contains:

- `task.md`, the identical prompt for both arms;
- `fixture/`, the files available to the evaluated model;
- `scenario.yaml`, a JSON-form YAML manifest used by the harness;
- `rubric-hidden.md`, the operator-only judgment rubric.

Machine assertions live separately in `evaluations/expected/<scenario-id>.json`. They can require or forbid partially matched events, require an event subsequence, require named fixture reads before the first answer, and require one emitted disposition from the closed set:

```text
act | watch | no-action | blocked | done | kill | needs-human
```

Release 1.1 consolidated the former ten-label vocabulary: `merge` is now `done`, `defer` is now `watch`, and `no-edge` is now `no-action`. Transcript ingestion and assertion comparison normalize those deprecated aliases before validation, so pre-1.1 artifacts remain interpretable while model-facing prompts use only the canonical seven.

The vocabulary changed in 1.1; the gpt-5.5 2026-07-10 runs certify the 1.0 vocabulary, and a 1.1 paired re-run is required before doctrine-contribution claims.

The canonical transcript envelope is JSON:

```json
{
  "events": [
    {"type": "tool_call", "tool": "read_file", "args": {"path": "fixture/example.json"}},
    {"type": "answer", "content": "Short decision surface"},
    {"type": "disposition", "label": "done"}
  ]
}
```

Event patterns are recursive partial matches. The assertion engine also supports one match operator at a leaf: `$regex`, `$contains`, `$not_contains`, or `$in`. Saying a file should be checked without a `read_file` event before the answer fails.

## Command runner interface

Validate the checked-in suite without running a model:

```bash
python3 scripts/evaluate_scenarios.py evaluations --schema-only
```

## Reference runner

The suite ships with its own examiner so paired runs are always executable. `scripts/eval_adapter_codex.py` drives one real model trial per invocation through the codex CLI: it presents a universal 21-tool JSON protocol (identical in every scenario and both arms), executes `read_file`/`local_word_count` against the fixture for real, stubs action tools, forces replies through a strict structured-output schema, and retries a zero-read harness refusal exactly once (arm-neutral). Set `EVAL_MODEL`, `EVAL_REASONING`, and optionally `EVAL_TRANSCRIPT_DIR` to dump per-trial transcripts. For concurrent execution, run trials in parallel with transcripts dumped, then score through the harness with `scripts/eval_adapter_replay.py` (`EVAL_TRANSCRIPT_DIR` required; it never synthesizes a missing transcript):

```bash
python3 scripts/evaluate_scenarios.py evaluations \
  --runner command \
  --runner-command 'python3 scripts/eval_adapter_codex.py' \
  --model-id MODEL --model-version VERSION --model-version-date YYYY-MM-DD
```

Run with a different user-supplied adapter:

```bash
python3 scripts/evaluate_scenarios.py evaluations \
  --runner command \
  --runner-command './my-runner' \
  --model-id MODEL \
  --model-version VERSION \
  --model-version-date YYYY-MM-DD
```

The adapter is invoked once per trial from the scenario directory. It reads one JSON object on standard input with `protocol_version`, `scenario_id`, `arm`, `trial`, `task`, `loading`, `fixture_dir`, and `repository_root`. It returns exactly one transcript JSON object on standard output. The loading value is the manifest's ordered list of files; the adapter is responsible for constructing its model request from those files. The harness does not pass the rubric, expected spec, scenario title, or expected answer. A nonzero adapter exit or invalid transcript stops the run without inventing a result.

Run mode records one CSV row per scenario. Each row includes model ID, model version, model version date, run date, three-trial count, and harness version. Human judgment remains pending until the operator reviews the hidden rubric.

## Interpretation limits and secrecy

Results are facts about the recorded model/version/tool pairing and date, not universal proof of doctrine quality. Deterministic traces establish that actions occurred in the required order; the hidden rubric covers proportionality, reasoning quality, and whether the action served the decision.

Scenario secrecy expires at publication. Public fixtures and rubrics can enter model training or evaluation contamination channels. Any post-1.0 re-certification claim must acknowledge that contamination and should use newly held-out scenarios for strong claims.
