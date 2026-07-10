# Minimal Hermes home fixture

Phase 6 integration tests copy this directory to an isolated temporary or `/tmp` Hermes home.

The fixture contains:

- `config.yaml`: a `skills.external_dirs` list with one preexisting entry, proving the installer appends at index `1` without replacing index `0`;
- `bin/hermes`: a local, no-network Hermes CLI stand-in reporting v0.18.2 and implementing only the tested `config set skills.external_dirs.<index> VALUE` operation;
- no distribution directory initially, so the version/config compatibility checks necessarily happen before the installer creates owned state.

The fake command honors `HERMES_HOME` and `FAKE_HERMES_VERSION`. It is test infrastructure, not a Hermes compatibility implementation.
