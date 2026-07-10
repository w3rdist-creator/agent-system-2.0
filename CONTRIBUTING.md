# Contributing

Contributions should reduce a demonstrated failure or serve a named consumer. Open an issue describing the evidence, destination, predecessor or overlap, cost, verification, and rollback/kill condition before proposing a new recurring surface, skill, template, or pack.

For changes:

1. Keep private data, credentials, session state, client material, and machine-specific topology out of every commit.
2. Preserve the Hermes ownership boundary: never overwrite or restore an upstream-owned file wholesale.
3. Add or update deterministic tests before changing installer, verifier, scanner, router, or evaluation behavior.
4. Run `bash scripts/dev-gate.sh` on macOS or Linux. WSL2 is documented but not CI-tested.
5. Explain any context-budget change and update the checked-in baseline only through the auditor's explicit baseline workflow.
6. Record source coordinates, licenses, attribution, routing, and lifecycle fields for accepted content.
7. Simulation faithfulness: any stub, fixture, or fake a gate depends on must be proven faithful to the real interface it stands in for — or deleted. When real behavior is verified (as with the Hermes v0.18.x `config set` list semantics on 2026-07-10), encode that behavior in the stub and cite the verification. A gate that passes against an idealized fake is not evidence.

Maintainer review is best-effort with no SLA; see [MAINTAINERS.md](MAINTAINERS.md). By contributing code you agree it is available under MIT; by contributing doctrine, skills, vault content, templates, examples, or documentation you agree it is available under CC BY 4.0. Do not submit material you cannot license on those terms.

