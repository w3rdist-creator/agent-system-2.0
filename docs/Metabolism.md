# Vault Metabolism

`python3 scripts/metabolism.py --vault PATH` is the single mechanical owner of Inbox routing, exact-body deduplication, decay pressure, and queue-cap alarms. Agents write automatically only to `Inbox/`; a capture opts into routing with a `route:` frontmatter value naming an existing shipped destination folder. Use `--dry-run` to print `PLAN ...` operations without writing, `--today YYYY-MM-DD` for a deterministic examination, and `--max-age-days` or `--queue-cap` to change the default 14-day and 25-item budgets.

The command never deletes or overwrites content. It moves routed notes out of Inbox, sends exact duplicates to `Archive/Duplicates/` with a dated suffix, and uses the installer's `.incoming` proposal convention when a route destination already exists. Outside Inbox it may write only those duplicate archives, `Queues/Resolve Queue.md`, and `Ledgers/Metabolism Ledger.csv`. Missing or invalid routes stay in Inbox and are reported. Decayed notes also stay in Inbox; their stable queue IDs make repeated runs idempotent.

After processing, the command exits 1 and prints `SCREAM` when either the remaining Inbox count or Resolve Queue entry count exceeds the configured cap. A healthy run exits 0. Operational errors exit 2. Every non-dry run that finds Inbox data appends an honest count row to the ledger; a run with no Markdown Inbox data says so and writes nothing.

The metabolism ledger is an optional machine-produced source for the collector documented in [Telemetry](Telemetry.md); telemetry rolls up its scream counts and does not inspect Inbox or note content.

## Operator-owned scheduling

Preview first, then install exactly one scheduler for this outcome. For example, an operator may add this cron entry with `crontab -e`:

```cron
15 7 * * * cd "$HOME/agent-system-2.0" && /usr/bin/python3 scripts/metabolism.py --vault "$HOME/Evidence-First-Vault" >> "$HOME/.local/state/evidence-first-metabolism.log" 2>&1
```

The distribution does not install, edit, or own cron or launchd configuration. The Agent Ops `Single Scheduler Ownership` doctrine requires one owner per outcome, an inventory before adding recurring execution, and a positive heartbeat. Here the dated ledger row is that heartbeat; absence is visible failure. Choose paths and log retention appropriate to the operator's machine, and do not add a second cron, launchd, gateway, or watchdog for the same vault.
