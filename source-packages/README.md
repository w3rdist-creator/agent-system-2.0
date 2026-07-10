# Source Packages

This directory records the frozen source denominator and dispositions. It does not vendor the five repositories.

## Pinned manifest

| Source repository | Pinned commit | Tracked files |
|---|---|---:|
| `second-brain-os-starter` | `9a2508ae0bab1e50da70f6b757aab9ba8d9c7208` | 36 |
| `second-brain-os-powerpack` | `a3d474323c961eaca2e15b444659d18b011a3aca` | 34 |
| `second-brain-super-repo` | `755e4a2018983317079999b4a975a81c8b4bddf4` | 197 |
| `agent-intelligence-economy` | `166e370850502c1878195ba122ab2ec82b2138d5` | 112 |
| `agent-intelligence-context-pack` | `7acf6bac45d49f748efca85052ca96f5e89a5949` | 96 |
| **Total** | | **475** |

## Denominator statement

The public file denominator is exactly the tracked files returned by `git ls-files` in each clean local source working copy after its `HEAD` is verified against the pinned commit above. At Phase 0 this produces 475 file rows. It excludes untracked files, Git internals, and the separately closed 12-row private/local capability-family denominator. It does not use “relevant file” or “logical artifact” as an expandable category.

## Regeneration command

Run from this repository. The command fails before writing rows if any source `HEAD` differs from its pin.

```bash
output=source-packages/public-file-dispositions.csv
printf '%s\n' 'source_repo,source_commit,source_path,license,attribution,private_risk,sanitization_reviewed_by,disposition,new_path,rationale' > "$output"

while IFS='|' read -r repo directory commit; do
  actual=$(git -C "$HOME/Code/$directory" rev-parse HEAD)
  test "$actual" = "$commit" || {
    printf 'SHA mismatch: %s expected %s got %s\n' "$repo" "$commit" "$actual" >&2
    exit 1
  }
  git -C "$HOME/Code/$directory" ls-files | while IFS= read -r source_path; do
    printf '%s,%s,%s,pending,pending,pending,pending,pending,,Phase 3 review pending\n' \
      "$repo" "$commit" "$source_path" >> "$output"
  done
done <<'SOURCES'
second-brain-os-starter|Second-Brain-OS-Starter|9a2508ae0bab1e50da70f6b757aab9ba8d9c7208
second-brain-os-powerpack|Second-Brain-OS-Powerpack|a3d474323c961eaca2e15b444659d18b011a3aca
second-brain-super-repo|second-brain-super-repo|755e4a2018983317079999b4a975a81c8b4bddf4
agent-intelligence-economy|agent-intelligence-economy|166e370850502c1878195ba122ab2ec82b2138d5
agent-intelligence-context-pack|agent-intelligence-context-pack|7acf6bac45d49f748efca85052ca96f5e89a5949
SOURCES
```

Phase 0 deliberately uses `pending` for file-level license, attribution, privacy, sanitization, disposition, and rationale review. Phase 3 must replace those placeholders with closed dispositions and evidence before Release 1.0 can satisfy the complete-disposition gate.

