---
{"name":"audit-quant-signals","description":"Audit a signal, indicator, model, or backtest for target definition, timestamp discipline, leakage, selection bias, costs, benchmark choice, robustness, capacity, and reproducibility before treating performance as evidence.","category":"markets","source_rows":["second-brain-os-powerpack:hermes/skills/quant-signal-auditor/SKILL.md","second-brain-os-powerpack:vault-addons/Knowledge/Market Research OS/Quant Signal Audit Loop.md","second-brain-os-powerpack:vault-addons/Knowledge/Market Research OS/Signal Audit Template.md","second-brain-os-powerpack:vault-addons/System/Rubrics/Evidence Quality Rubric.md"],"license":"CC BY 4.0","triggers":["backtest review","signal audit","alpha claim","indicator evaluation","model performance"]}
---

# Audit Quant Signals

## Reconstruct the test

Identify prediction target, forecast horizon, unit of observation, universe, rebalance rule, data vintage, benchmark, and exact information available at each decision timestamp. Require reproducible code or an explicit statement that reproduction is unavailable.

## Check validity

Inspect lookahead leakage, revised data, survivorship and delisting bias, selection after seeing results, overlapping labels, corporate actions, missing observations, universe drift, and train/test contamination. A clean chart does not repair an invalid data-generating process.

## Check economic realism

Apply transaction costs, spread, slippage, delay, turnover, borrow constraints, market impact, capacity, and liquidity. Compare against simple baselines and the right risk exposure. Separate gross statistical predictability from net deployable value.

## Test robustness

Use out-of-sample or walk-forward analysis where available; inspect parameter sensitivity, regime and subperiod stability, multiple-testing burden, concentration, drawdowns, and plausible failure modes. Prefer confidence intervals and distributions over one headline metric.

Return verified inputs, unverified assumptions, reproducibility status, net evidence, falsifiers, and a research disposition. Do not imply live execution or future performance.
