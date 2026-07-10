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
