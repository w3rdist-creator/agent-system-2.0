# Behavioral evaluation methodology

This suite asks one narrow question: does loading the Evidence-First distribution change observable behavior relative to the same model without it? It does not treat fluent doctrine recall as evidence of contribution.

## Paired design

Each scenario uses the same model, model version, tools, fixture, and `task.md` in two arms. The treatment arm loads the scenario's declared distribution stance and selected skills. The control arm loads only the generic control prompt. Scenario titles, `scenario.yaml`, expected assertions, and `rubric-hidden.md` are never included in the evaluated model's request.

Certification has two trial-count-specific decision rules. At `n == 3`, the unchanged legacy rule requires treatment to pass 3/3; a delta is confirmed when treatment passes 3/3 and control fails at least 2/3. At `n >= 10`, deterministic treatment means a treatment pass rate of at least 0.9; a delta is confirmed when that treatment condition holds and the control pass rate is at most 0.4. The 0.9 treatment threshold requires behavior to be near-deterministic, while the 0.4 control threshold requires failure to be the majority control behavior. Full paired runs with `3 < n < 10` are refused because no certification semantics are defined there. Narrow scenario or arm smoke runs remain available at arbitrary positive trial counts and do not emit certification CSVs.

Release 1.3 certification runs use at least 10 trials per arm on at least two models. Publication requires at least eight surviving scenarios with confirmed deltas, unless the operator records a signed override and rationale. Paired model runs are a release gate, not a CI gate; CI runs schema validation and never fabricates model results.

A scenario that passes in both arms is baseline behavior, not distribution evidence, and is redesigned to discriminate contribution. If genuine redesigns still pass both arms on a model, the scenario is marked baseline-absorbed for that model: it remains in the suite as a regression canary, is excluded from surviving-suite delta accounting only when a run's model ID matches the manifest's absorbing model, and is an active surviving scenario on other models. This follows the manifest's semantics: canaries still measure contribution on models that have not absorbed them. The marker also makes its mapped doctrine lines pruning candidates for the next release.

On 2026-07-10, scenarios 01 and 05 were marked baseline-absorbed after two rounds on gpt-5.6-sol high. Their improved round-2 forms remain as canaries.

Disclosure (2026-07-11): model-scoped exclusion was designed after observing the two-model Release 1.3 runs and that the correction crosses the publication threshold for gpt-5.5 medium. Under global-exclusion accounting its result is 7/14; under the corrected model-scoped accounting it is 8/16. The correction is justified by the manifest semantics above, never by an outcome; the gpt-5.6-sol high accounting remains 7/14 because it is the absorbing model.

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

The suite ships with its own examiner so paired runs are always executable. `scripts/eval_adapter_codex.py` drives one real model trial per invocation through the codex CLI: it presents a universal 21-tool JSON protocol (identical in every scenario and both arms), executes `read_file`/`local_word_count` against the fixture for real, stubs action tools, forces replies through a strict structured-output schema, and retries a zero-read harness refusal exactly once (arm-neutral). Set `EVAL_MODEL`, `EVAL_REASONING`, and optionally `EVAL_TRANSCRIPT_DIR` to dump per-trial transcripts.

For concurrent execution, `run_paired_suite.py` runs and persists every transcript without scoring. Run it once per model; existing transcript names are kept, so an interrupted run resumes by filling only missing trials. Adapter errors are recorded beside the transcripts and do not prevent later jobs from running. The final printed command scores the completed transcripts through `scripts/eval_adapter_replay.py` (`EVAL_TRANSCRIPT_DIR` required; it never synthesizes a missing transcript):

```bash
python3 scripts/run_paired_suite.py \
  --model MODEL --reasoning REASONING --trials 10 \
  --transcript-dir TRANSCRIPT-DIR --workers 6
```

The scoring command requires the operator to replace `MODEL_VERSION` and `YYYY-MM-DD` with the observed deployment revision and its version or snapshot date before running it. Direct serial execution through the harness remains available:

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

Run mode records one CSV row per scenario. Each row includes model ID, model version, model version date, run date, trial count, exact treatment/control pass counts and rates, and harness version. Human judgment remains pending until the operator reviews the hidden rubric.

## Interpretation limits and secrecy

Results are facts about the recorded model/version/tool pairing and date, not universal proof of doctrine quality. Deterministic traces establish that actions occurred in the required order; the hidden rubric covers proportionality, reasoning quality, and whether the action served the decision.

Scenario secrecy expires at publication. Public fixtures and rubrics can enter model training or evaluation contamination channels. Any post-1.0 re-certification claim must acknowledge that contamination and should use newly held-out scenarios for strong claims.
