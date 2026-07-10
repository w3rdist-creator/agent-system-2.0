# Hermes Ownership Spike

Read-only inspection date: 2026-07-10. No Hermes command that changes configuration or state was run.

## Verified

### Installed version

- **Verified:** `hermes --version` reported `Hermes Agent v0.18.2 (2026.7.7.2) · upstream 8727e672`.
- **Verified:** the same output reported a Git installation at `~/.hermes/hermes-agent` using Python 3.11.15 and OpenAI SDK 2.24.0.
- **Verified:** `command -v hermes` resolved inside the operator’s home-local binary directory. The absolute personal path is intentionally represented only as a home-relative location.

### Skill discovery and ownership

- **Verified:** `~/.hermes/skills/` exists. Upstream `hermes_constants.py:get_skills_dir()` defines this as the local skill directory under `HERMES_HOME`.
- **Verified:** `agent/skill_utils.py:get_all_skills_dirs()` returns the local skill directory first and then the result of `get_external_skills_dirs()`.
- **Verified:** `get_external_skills_dirs()` reads the exact config key `skills.external_dirs` from `~/.hermes/config.yaml`. It accepts a string or list, expands `~` and environment variables, resolves relative entries against `HERMES_HOME`, ignores missing directories, removes duplicates, and skips an entry resolving to the local skills directory.
- **Verified:** the live config contains `skills` as a mapping and `skills.external_dirs` as a list with one entry. Its value was not recorded because private-estate paths are outside this repository’s public evidence boundary.
- **Verified:** `agent/skill_commands.py` and gateway code rescan both `~/.hermes/skills/` and configured external directories for `SKILL.md` files.
- **Verified:** `agent/skill_utils.py:is_external_skill_path()` labels paths under `skills.external_dirs` as externally owned. Its docstring says Hermes may discover and view them while autonomous lifecycle maintenance must treat them as read-only.
- **Verified:** `~/.hermes/distributions/` did not exist at inspection time. No directory was created during the spike.

### Supported reference mechanism

- **Verified:** Hermes v0.18.2 has a supported mechanism capable of referencing `~/.hermes/distributions/evidence-first/skills/`: add that existing directory to `skills.external_dirs`.
- **Verified:** `hermes config set --help` supports a dotted key and value. The config implementation supports numeric list indices, updates only the requested nested value in the user config, and writes atomically. No mutating invocation was performed during this spike.
- **Corrected 2026-07-10:** the 2026-07-10 non-builder clean-room install disproved the append inference below by mutating a sandboxed Hermes home: `_set_nested` in `hermes_cli/config.py` performs `current[int(last)] = value`, so numeric list indices assign **in place only** and `skills.external_dirs.<len>` raises `IndexError: list assignment index out of range`. Because no supported append surface exists, the installer prints the one-line `skills.external_dirs` addition as a manual operator step (symmetric with uninstall) and `verify-install.sh` fails closed until the entry exists. This is exactly the class of error a read-only spike cannot catch; the correction stands as evidence for the non-builder gate.
- **Verified:** the supported mechanism is specific to skill discovery. This spike found no need to make Hermes own the other distribution artifacts; vault and distribution files remain managed by the distribution manifest.

## Inferred

- **Inferred:** for this pinned version, the safest Release 1.0 installer strategy is reference-first: install all owned state under `~/.hermes/distributions/evidence-first/`, place skill packages below its `skills/` directory, preserve existing external-directory entries, and propose adding the new path at the next list index.
- **Inferred:** the installer should show the exact proposed `hermes config set skills.external_dirs.<index> ~/.hermes/distributions/evidence-first/skills` command during `--dry-run`; it should execute it only in a later authorized install, after checking the version and detecting duplicates. It must never replace `config.yaml` wholesale.
- **Inferred:** because the live key already contains an entry, setting `skills.external_dirs` as a scalar or replacing the whole list would be unsafe. Index-aware append and exact rollback of only the added entry are required.
- **Inferred:** the namespace-copy fallback from plan §12 is not needed for v0.18.2. If a future supported version removes external directories, the fallback may copy uniquely prefixed skill directories into `~/.hermes/skills/`, record exact owned files and hashes, and preserve modified or user-authored files on uninstall.

## Unknown

- **Unknown:** whether later Hermes versions preserve the same key and ownership semantics. The installer must enforce an explicit compatibility range and fail before writing on unsupported versions.
- **Unknown:** the safest supported CLI operation for removing one list entry without changing later indices. Phase 6 must test uninstall against an isolated Hermes home; until then, config removal remains preview-only or manual.
- **Unknown:** whether every Hermes surface applies identical external-directory precedence in all edge cases. The inspected foreground, gateway, sync, and ownership code supports the mechanism, but the distribution has not yet run the Phase 6 integration suite.

## Resulting installer strategy

`reference-first`: use `skills.external_dirs` for the distribution-owned skill tree on Hermes v0.18.2. Never claim ownership of `~/.hermes/config.yaml`, `.env`, authentication, memory, sessions, state databases, or upstream-managed skills. Retain the unique namespace-copy strategy only as a compatibility fallback after a future spike proves the reference mechanism unavailable.

