# Results schema

`evaluations/results/` is empty in source control except for this schema and `.gitkeep`. Configured model runs write CSV rows; schema-only runs never write results.

One row represents one scenario's paired run. Fields are ordered as follows:

| Field | Contract |
|---|---|
| `scenario_id` | Scenario directory and manifest identifier. |
| `model_id` | Provider/model identifier used identically in both arms. |
| `model_version` | Exact reported model version or deployment revision. |
| `model_version_date` | Version/snapshot date, not the run date. |
| `run_date` | Calendar date of the paired run. |
| `trial_count` | Exactly `3` per arm. |
| `harness_version` | Version from `scripts/evaluation_lib.py`. |
| `treatment_passes` | Count from 0 through 3. |
| `control_passes` | Count from 0 through 3. |
| `deterministic_treatment_pass` | True only for treatment 3/3. |
| `control_failures` | `3 - control_passes`. |
| `confirmed_delta` | True only for treatment 3/3 and control failure at least 2/3. |
| `treatment_dispositions` | JSON array of the three emitted labels. |
| `control_dispositions` | JSON array of the three emitted labels. |
| `human_judgment` | Operator rubric status or signed judgment. |
| `operator_override` | Boolean; does not alter the mechanical delta. |
| `operator_override_rationale` | Required by publication policy when an override is used. |

The authoritative field list and validator are `RESULT_FIELDS` and `validate_result_row` in `scripts/evaluation_lib.py`. Result claims must retain the provenance fields when copied elsewhere.

Rows recorded before Release 1.1 use the former ten-label disposition vocabulary. The evaluation library accepts `merge`, `defer`, and `no-edge` in those rows and transcripts as deprecated aliases for `done`, `watch`, and `no-action`, respectively.

## Recert log

`scripts/recert.sh` appends one row per attempted treatment-arm trial to `recert-log.csv`. Its ordered fields are `date`, `scenario`, `model`, `reasoning`, `arm`, `result`, and `failure_reason`. `result` is exactly `pass`, `fail`, or `error`: `fail` means the returned transcript failed one or more deterministic assertions, while `error` means the runner or harness did not produce an evaluable trial. The failure detail is empty only for a pass.

A recert row is a dated, single-arm smoke result for the named model, reasoning effort, and scenario. It is not a paired treatment/control delta and must not be presented as the paired three-trial certificate described above.
