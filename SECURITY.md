# Security Policy

## Supported surface

Release 1.0 supports the current candidate on Hermes v0.18.x through the macOS/Linux POSIX path. WSL2 compatibility is inferred, not CI-tested. Unsupported Hermes versions fail before installation unless a user explicitly accepts the unverified override.

## Reporting

GitHub Issues is the temporary security-contact placeholder. Do not place secrets, exploit payloads, private paths, client data, or credentials in a public issue. File a minimal issue requesting private coordination and include only the affected version and a non-sensitive impact summary.

Reports receive best-effort review with no SLA, consistent with [MAINTAINERS.md](MAINTAINERS.md). The maintainer may freeze or archive the distribution if a safe response exceeds the declared maintenance budget.

## Safety invariants

- No installer path may silently overwrite a user file.
- Distribution ownership never extends to Hermes config, authentication, memory, session, or state files.
- Uninstall removes only unchanged manifest-owned files and empty directories, non-recursively.
- Modified owned files and user-authored files are preserved and reported.
- No shipped command creates a remote, pushes, handles credentials, or configures recurring automation.

