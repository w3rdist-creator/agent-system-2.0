# Update Gate

`scripts/publication-gate.sh` proves that a fresh first-publication export has one commit, one branch, no remote, and clean worktree and history scans. A subsequent release necessarily has more than one commit, so it uses the update gate in BUILD before a fresh export:

```sh
bash scripts/dev-gate.sh
sh scripts/update-gate.sh --base v1.0.0 --version 1.1.0
```

`--base REF` names the already-published ancestor of `HEAD`; `--version X.Y.Z` must match a `## X.Y.Z`-prefixed heading in `CHANGELOG.md`. The gate requires a clean worktree and a nonempty ancestral update range, scans the working tree, scans `git log -p REF..HEAD`, and runs the full development gate. It fails closed on any failed check.

`--skip-dev-gate` exists only so the unit smoke test can exercise the update gate without recursively invoking the development gate that launched it. It is not an operator release option.

## Full update flow

1. In BUILD, finish and commit the reviewed release bytes, then run `bash scripts/dev-gate.sh`.
2. Still in BUILD, run `sh scripts/update-gate.sh --base PREVIOUS-PUBLIC-REF --version X.Y.Z`.
3. Create a fresh temporary export with `EVIDENCE_FIRST_EXPORT_DIR=DESTINATION bash scripts/export-public.sh`; the exporter runs the first-publication gate against that sanitized one-commit export.
4. In the fresh export, substitute `w3rdist-creator` with the publishing account and rerun the development and publication gates after the substitution commit is amended.
5. Use `rsync` to copy the reviewed export tree into the existing public clone without copying the export's `.git/` directory. Review the public-clone diff and commit it as the release update.
6. Push the public-clone commit, wait for CI to report green, and only then create and push the release tag.

The BUILD executor may run steps 1–3 when its filesystem permits. Account substitution, writing into the existing public clone, committing or pushing there, judging remote CI, and creating or pushing a tag are operator-only actions. The update gate never configures a remote, pushes, tags, edits `config.yaml`, or changes user-owned content.
