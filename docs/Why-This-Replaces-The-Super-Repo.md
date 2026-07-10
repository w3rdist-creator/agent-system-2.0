# Why This Replaces the Super-Repo

This is a conditional replacement argument, not a claim that the new distribution has already superseded anything. Inspection was read-only at pinned commit `755e4a2018983317079999b4a975a81c8b4bddf4` on 2026-07-10.

## Verified

- The local source working copy was clean, its `HEAD` matched the pin, and `git ls-files` returned 197 tracked files.
- The tracked tree contains 109 files under `packs/`, 70 under `source-packages/`, 11 scripts, four documents, a README, an MIT license, and a `.gitignore`.
- Eight pack READMEs advertise Research, Deep Timeline, Markets, Product OS, Agent Ops, Personal OS, Learning OS, and Simulation Lab. The vendored starter and powerpack form two additional source-package layers.
- The README calls the repository a complete, sanitized Obsidian and Hermes command-center distribution intended to install the stack from one repository. It presents breadth across ten pack or source-package layers as the product.
- `scripts/install-super-repo.sh` installs starter, powerpack, and all eight packs with `rsync -a`, then writes a timestamped installation log. `scripts/install-pack.sh` also uses `rsync -a`. Neither script checks an ownership manifest or proposes conflicts as `.incoming` files before copying.
- The tree has no tracked `MAINTAINERS.md`, repository improvement-proposal template, repository loop-contract template, `evaluations/` directory, uninstall script, or 475-row source-disposition ledger.
- `docs/Architecture.md` names a generic artifact loop and allowed dispositions, but it does not name a loop owner, consumer, budget, review cadence, or kill condition.
- `scripts/verify-super-repo.sh` invokes only a wikilink verifier and a worktree private-marker scanner. The scanner checks a short fixed pattern list; the tree contains no paired behavioral evaluation harness or Git-history privacy gate.
- The source-grounding document distinguishes linked, clipped, preserved, read, synthesized, applied, and killed states and warns that harvesting is not reading. This useful mechanism remains source material for the successor.
- The clean local checkout is on `main` and has a GitHub `origin`. The README also contains a public clone instruction. The account coordinate is intentionally omitted here under this repository’s privacy rule.
- An attempt to inspect the public page during Phase 0 returned an external browser cache-miss error. Live star, fork, issue, archive, and visibility metadata were therefore not independently reverified by the executor.

## Inferred

- Installing every pack by default increases review surface before consumer demand is known. This may have made the distribution harder to evaluate and maintain, but repository contents alone cannot establish causation.
- Unconditional `rsync -a` without a distribution ownership manifest may overwrite same-path user content and cannot support the Release 1.0 uninstall contract. This is a risk inferred from the script semantics; no destructive incident was observed.
- A generic disposition vocabulary without a named owner, budget, heartbeat, or kill rule may preserve activity without proving downstream usefulness.
- The absence of paired controls, trace assertions, and recorded downstream use means the repository cannot attribute useful behavior to its doctrine from checked-in evidence.

## Unknown

- Actual private usage, clone behavior, reader completion, installed pack mix, and downstream decisions are unknown.
- Whether scope, discoverability, maintenance, installer safety, or another cause limited adoption is unknown.
- Maintainer intent beyond the checked-in documents is unknown.
- Current public-host metadata is unknown to this Phase 0 executor because the live fetch failed; no claim of zero stars, forks, or issues is made here.

## What is different now

The successor is not justified by more content. It is justified only if it delivers all of the following differences:

1. The repository files its own validated improvement proposal and loop contract before feature work.
2. Release 1.0 is bounded to Research and Agent Ops, with other packs inert or deferred behind demand.
3. Startup routing is selective and budgeted rather than proportional to the full catalog.
4. Behavioral claims use paired treatment/control trials, observable trace assertions, and a threshold fixed before results.
5. Public and private denominators are closed at 475 file rows and 12 capability-family rows.
6. Installation uses distribution-owned namespaced files, explicit conflicts, a manifest, and a real uninstall test that preserves user files.
7. Supersession requires a non-builder clean-room install, at least five recorded real uses during the 30-day window, operator approval, and explicit predecessor deprecation.

If those gates do not pass, this repository remains an experiment and does not replace the super-repo.

## Disposition

`act`: continue the bounded successor experiment. `watch`: park all predecessor deprecation until every supersession condition is positively satisfied.
