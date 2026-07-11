#!/bin/sh
set -eu

# This helper is print-only. It never writes, installs, or registers anything.

usage() {
    cat <<'EOF'
Usage: wire-loops.sh --vault PATH [--clone PATH] [--hermes-home PATH]

Print a ready-to-paste plan for the metabolism, recert, and telemetry loops.
The clone defaults to the repository containing this script; Hermes home
defaults to ~/.hermes. This command never writes, installs, or registers.
EOF
}

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(dirname "$script_dir")
vault=
clone=$repo_root
hermes_home=${HOME}/.hermes

while [ "$#" -gt 0 ]; do
    case "$1" in
        --vault) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; vault=$2; shift 2 ;;
        --clone) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; clone=$2; shift 2 ;;
        --hermes-home) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; hermes_home=$2; shift 2 ;;
        --help|-h) usage; exit 0 ;;
        *) printf 'ERROR: unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
done

[ -n "$vault" ] || { printf 'ERROR: --vault is required\n' >&2; usage >&2; exit 2; }

absolute() {
    python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$1"
}

shell_quote() {
    escaped=$(printf '%s' "$1" | sed "s/'/'\\\\''/g")
    printf "'%s'" "$escaped"
}

vault=$(absolute "$vault")
clone=$(absolute "$clone")
hermes_home=$(absolute "$hermes_home")
wrapper_dir=$hermes_home/scripts
state_dir=$hermes_home/state/evidence-first
transcript_dir=$state_dir/transcripts
recert_log=$clone/evaluations/results/recert-log.csv
metabolism_ledger=$vault/Ledgers/Metabolism\ Ledger.csv

metabolism_wrapper=$wrapper_dir/evidence-first-metabolism.sh
recert_wrapper=$wrapper_dir/evidence-first-recert.sh
telemetry_wrapper=$wrapper_dir/evidence-first-telemetry.sh

q_vault=$(shell_quote "$vault")
q_clone=$(shell_quote "$clone")
q_metabolism_command=$(shell_quote "$clone/scripts/metabolism.py")
q_recert_command=$(shell_quote "$clone/scripts/recert.sh")
q_telemetry_command=$(shell_quote "$clone/scripts/telemetry.py")
q_state=$(shell_quote "$state_dir")
q_transcripts=$(shell_quote "$transcript_dir")
q_recert_log=$(shell_quote "$recert_log")
q_metabolism_ledger=$(shell_quote "$metabolism_ledger")
q_metabolism_wrapper=$(shell_quote "$metabolism_wrapper")
q_recert_wrapper=$(shell_quote "$recert_wrapper")
q_telemetry_wrapper=$(shell_quote "$telemetry_wrapper")
q_hermes_home=$(shell_quote "$hermes_home")

cat <<EOF
EVIDENCE-FIRST LOOP WIRING PLAN (PRINT-ONLY)
This helper has written nothing and registered nothing.
Single-scheduler doctrine: inventory first, then give each outcome one scheduler and one owner.

Create these three wrapper files yourself under $wrapper_dir and make them executable.

--- $metabolism_wrapper ---
#!/bin/sh
set -eu
mkdir -p $q_state
cd $q_clone
exec python3 $q_metabolism_command --vault $q_vault
--- end ---

--- $recert_wrapper ---
#!/bin/sh
set -eu
mkdir -p $q_transcripts
export EVAL_TRANSCRIPT_DIR=$q_transcripts
cd $q_clone
exec $q_recert_command
--- end ---

--- $telemetry_wrapper ---
#!/bin/sh
set -eu
mkdir -p $q_state
cd $q_clone
exec python3 $q_telemetry_command \\
  --vault $q_vault \\
  --transcript-dir $q_transcripts \\
  --recert-log $q_recert_log \\
  --metabolism-ledger $q_metabolism_ledger
--- end ---

After saving them:
mkdir -p $q_state
chmod 700 $q_metabolism_wrapper $q_recert_wrapper $q_telemetry_wrapper
EOF

scheduler=none
# Do not execute a candidate scheduler during detection: even some help paths
# initialize user state. The supported Hermes line exposes `hermes cron`.
if command -v hermes >/dev/null 2>&1; then
    scheduler=hermes
elif command -v crontab >/dev/null 2>&1; then
    scheduler=cron
elif [ "$(uname -s 2>/dev/null || true)" = Darwin ] && command -v launchctl >/dev/null 2>&1; then
    scheduler=launchd
fi

case "$scheduler" in
    hermes)
        cat <<EOF

BEST AVAILABLE SCHEDULER: Hermes cron
Paste these only after saving the wrappers. The explicit HERMES_HOME keeps the jobs with this Hermes profile.

HERMES_HOME=$q_hermes_home hermes cron create '5 3 * * *' --name evidence-first-metabolism --script $q_metabolism_wrapper --no-agent
HERMES_HOME=$q_hermes_home hermes cron create '25 3 * * *' --name evidence-first-recert --script $q_recert_wrapper --no-agent
HERMES_HOME=$q_hermes_home hermes cron create '50 3 * * *' --name evidence-first-telemetry --script $q_telemetry_wrapper --no-agent
EOF
        ;;
    cron)
        cat <<EOF

BEST AVAILABLE SCHEDULER: crontab
Paste these three lines into the single crontab you own with: crontab -e

5 3 * * * $q_metabolism_wrapper >> $q_state/metabolism.log 2>&1
25 3 * * * $q_recert_wrapper >> $q_state/recert.log 2>&1
50 3 * * * $q_telemetry_wrapper >> $q_state/telemetry.log 2>&1
EOF
        ;;
    launchd)
        launch_agents=${HOME}/Library/LaunchAgents
        cat <<EOF

BEST AVAILABLE SCHEDULER: launchd
Save each complete block at its named path under $launch_agents, then bootstrap exactly those three user agents.

--- $launch_agents/org.evidence-first.metabolism.plist ---
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>org.evidence-first.metabolism</string>
<key>ProgramArguments</key><array><string>$metabolism_wrapper</string></array>
<key>StartCalendarInterval</key><dict><key>Hour</key><integer>3</integer><key>Minute</key><integer>5</integer></dict>
<key>StandardOutPath</key><string>$state_dir/metabolism.log</string>
<key>StandardErrorPath</key><string>$state_dir/metabolism.log</string>
</dict></plist>
--- end ---

--- $launch_agents/org.evidence-first.recert.plist ---
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>org.evidence-first.recert</string>
<key>ProgramArguments</key><array><string>$recert_wrapper</string></array>
<key>StartCalendarInterval</key><dict><key>Hour</key><integer>3</integer><key>Minute</key><integer>25</integer></dict>
<key>StandardOutPath</key><string>$state_dir/recert.log</string>
<key>StandardErrorPath</key><string>$state_dir/recert.log</string>
</dict></plist>
--- end ---

--- $launch_agents/org.evidence-first.telemetry.plist ---
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>org.evidence-first.telemetry</string>
<key>ProgramArguments</key><array><string>$telemetry_wrapper</string></array>
<key>StartCalendarInterval</key><dict><key>Hour</key><integer>3</integer><key>Minute</key><integer>50</integer></dict>
<key>StandardOutPath</key><string>$state_dir/telemetry.log</string>
<key>StandardErrorPath</key><string>$state_dir/telemetry.log</string>
</dict></plist>
--- end ---

launchctl bootstrap gui/\$(id -u) '$launch_agents/org.evidence-first.metabolism.plist'
launchctl bootstrap gui/\$(id -u) '$launch_agents/org.evidence-first.recert.plist'
launchctl bootstrap gui/\$(id -u) '$launch_agents/org.evidence-first.telemetry.plist'
EOF
        ;;
    *)
        cat <<'EOF'

BEST AVAILABLE SCHEDULER: none detected
Keep the wrapper files and run them manually at 03:05, 03:25, and 03:50, or install one scheduler and rerun this helper.
EOF
        ;;
esac

cat <<'EOF'

Review the plan before doing anything. No scheduler state was inspected beyond capability detection.
this tool prints; you paste — one scheduler, one owner, and it is you
EOF
