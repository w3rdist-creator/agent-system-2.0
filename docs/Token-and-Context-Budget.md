# Token and Context Budget

Efficiency has four budgets. Saving tokens does not authorize removing provenance, verification, or decision quality.

| Budget | Release 1.0 numeric contract | Current measured state |
|---|---|---|
| Active context | Level 0 ≤400 approximate tokens; worst-case operational core ≤3,000; `SOUL.md` ≤900 words; ≤15 categories; ≤20 skills/category; registry descriptions target ≤350 characters | Level 0 394; operational core 2,964; `SOUL.md` 205 words; 11 categories; largest category 4 skills |
| Retrieval/source loading | Load one Level 1 registry and one Level 2 skill by default. A second registry requires a real routing boundary. Future corpus retrieval must declare numeric `max_items` and token budget before retrieval | Largest Level 1 registry 354 approximate tokens; no corpus payload ships |
| Reasoning, tools, delegation, retries | No universal task number is invented. Every bounded task/experiment packet must set numeric time, token, tool, and retry limits before execution; evaluation is fixed at 3 trials per arm | Evaluation harness enforces 3 treatment and 3 control trials; other limits remain task-specific and recorded in the packet |
| Downstream human review debt | Agent Ops unresolved queue ≤7 items and ≤45 review minutes/week; pause before item 8 or when estimated review exceeds 45 minutes | Seed Resolve Queue is within both limits |

## Operational-core calculation

The worst-case startup surface is:

```text
agent/SOUL.md                                      328
skills/core/capability-router/SKILL.md             959
skills/level-0-categories.yaml                     394
skills/core/evidence-first-operating-style/SKILL.md 1,283
                                                     -----
Operational core                                  2,964 / 3,000
```

The four other core skills are trigger-loaded and reported separately, not silently added to startup. Their current combined estimate is 3,304 approximate tokens.

## Approximation method

`scripts/audit_context_budget.py` uses:

```text
ceil(number of Unicode characters / 4)
```

This stable approximation is provider-neutral and intentionally does not claim equality with any provider tokenizer. The checked-in baseline fails when a measured item exceeds the greater of 5% or 20 approximate tokens above baseline; hard ceilings are never relaxed by that tolerance. Baseline changes require the explicit `--write-baseline` workflow after the hard limits pass.

Run the audit with:

```bash
python3 scripts/audit_context_budget.py --profile core
```
