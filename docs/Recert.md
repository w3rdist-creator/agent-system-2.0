# Live recertification

Run `scripts/recert.sh` for a cheap live check that the current doctrine still moves one model through one scenario. The default selects one of the 16 scenarios by day of year, runs the treatment arm once through `scripts/eval_adapter_codex.py`, and appends the evaluated outcome to `evaluations/results/recert-log.csv`:

```sh
scripts/recert.sh
scripts/recert.sh --scenario 01-stale-context-live-source
scripts/recert.sh --model MODEL --reasoning medium
scripts/recert.sh --full
```

The model defaults to the operator's top-level `model` in `$CODEX_HOME/config.toml` (normally `~/.codex/config.toml`). `--model` overrides `EVAL_MODEL`, which overrides that configured default. Reasoning follows the same flag-then-`EVAL_REASONING` precedence and otherwise uses the Codex default or `low`. The command exits zero only when every attempted trial passed and always ends an attempted run with `RECERT: <n>/<m> passed (<model>, <date>)`.

Each row certifies only that the named live model, on that date and reasoning effort, passed or failed the deterministic rubric for that one treatment-arm trial. An `error` row says the runner or harness did not return an evaluable result; the command never converts a crash into a pass or fail. Recert is a smoke check, not evidence of a treatment effect. The paired two-arm suite with three trials per arm remains the only delta certificate.

The recert log is an optional machine-produced source for the collector documented in [Telemetry](Telemetry.md); telemetry rolls up its result counts without changing what a recert row certifies.

## Operator-owned nightly schedule

Preview the command manually, then install exactly one operator-owned scheduler for this outcome. For example, an operator may add this cron entry with `crontab -e`:

```cron
30 2 * * * cd "$HOME/agent-system-2.0" && ./scripts/recert.sh >> "$HOME/.local/state/evidence-first-recert.log" 2>&1
```

Scheduling remains operator territory; this distribution makes no cron or launchd changes. Apply the Agent Ops `Single Scheduler Ownership` doctrine cited by vault metabolism: inventory recurring jobs first, assign one owner to this outcome, and require a positive heartbeat. The dated recert row supplies that heartbeat, so a missing row exposes failure. Select machine-appropriate paths and retention, and keep cron, launchd, gateways, and watchdogs from duplicating this recert job. `--full` runs one treatment trial for all 16 scenarios and is suitable for a more expensive weekly smoke check, but it is still not paired evidence.

## When smoke recertification is insufficient

Run the full paired three-trial/two-arm suite after any change under `agent/`, `skills/`, or `templates/`, or after any change to the disposition vocabulary. Those surfaces alter the treatment or its measured output contract, so a single-arm smoke row cannot establish the delta. Use the paired command documented in `evaluations/README.md`, retain its complete model provenance, and treat recert rows only as supplementary current-health evidence.
