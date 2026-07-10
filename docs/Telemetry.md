# Telemetry

`python3 scripts/telemetry.py --vault PATH` collects usage evidence from named machine artifacts the system already produced. Supply one or more `--transcript-dir DIR` values and, when available, `--recert-log PATH` or `--metabolism-ledger PATH`. `--today YYYY-MM-DD` makes the ledger date deterministic, and `--dry-run` reports the proposed rows without writing them.

The collector counts emitted dispositions, tool calls, fixture reads before the first answer, and guard denials by rule in canonical evaluation transcript JSON files. It rolls up recert results and metabolism scream counts from their CSV ledgers. It reads only those explicitly named sources. It never reads or records user note content, scans the vault for behavior, or collects anything outside the named transcript directories and CSV paths.

Rows land in `Ledgers/Telemetry Ledger.csv` with the schema `date,source,metric,value`. The collector appends one row per key and skips an existing `date + source + metric` key on a same-day rerun, reporting written and skipped counts. Malformed transcripts are skipped with a warning. Missing or empty sources are reported; if no source yields evidence, the command exits successfully and writes nothing because absence of evidence is not an operational error. Invalid named CSV schemas fail closed.

Telemetry rows are usage evidence for governance decisions such as pack-demand triggers and kill conditions. They are not a surveillance layer and do not independently authorize a decision or state change.
