# Upgrade

Run an in-place release upgrade against the same vault and Hermes home used for installation:

```bash
bash scripts/upgrade.sh \
  --dry-run \
  --vault "$HOME/Evidence-First-Vault" \
  --hermes-home "$HOME/.hermes"

bash scripts/upgrade.sh \
  --vault "$HOME/Evidence-First-Vault" \
  --hermes-home "$HOME/.hermes"
```

The command supports Hermes v0.18.x and refuses other versions unless `--force-unsupported` is explicitly supplied. It also refuses when the vault has no install manifest and points back to `install.sh`. A dry run prints `PLAN` lines and writes nothing.

## Manifest migration semantics

| Installed state | Upgrade action |
|---|---|
| Hash still matches the old manifest; new payload differs | Replace the distribution-owned file and record its new hash. |
| Hash still matches and the new payload is identical | Leave the file unchanged. |
| Hash differs because the file was edited | Preserve it byte-for-byte, write the new payload beside it as `.incoming`, and track the preserved file's current hash with `superseded_by_incoming`. |
| New payload path was not in the old manifest | Add it; if the path already exists, preserve that content and install an `.incoming` proposal. |
| Old manifest path is retired and unmodified | Remove the retired distribution-owned file and drop its entry. |
| Old manifest path is retired and modified | Preserve it, stop tracking it, and print a warning. |

Every run ends with an honest `UPGRADE REPORT:` showing replaced, preserved-with-incoming, added, retired, and warning counts. The upgrader never edits `config.yaml`. The `skills.external_dirs` location is stable across releases, so a correctly activated prior install needs no new manual config step; the command verifies that condition and reports it.

## Review `.incoming` proposals

When a file is preserved with an incoming proposal, compare the two files and merge the desired distribution changes into your file deliberately. Remove or rename the `.incoming` proposal only after that review. If an unresolved proposal already exists with different content, upgrade refuses rather than overwriting it.

Installed packs are an intentional boundary. Once copied into the vault, pack payloads are user content: the upgrader carries their manifest records forward but does not replace, retire, or otherwise migrate pack files.

If manifest migration refuses because the installation is inconsistent, use the safe fallback: run `scripts/uninstall.sh`, review everything it preserves, reinstall the new release, perform the printed config step if needed, and re-add any packs deliberately.
