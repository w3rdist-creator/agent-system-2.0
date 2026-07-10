---
{"name":"run-bounded-agent-labs","description":"Design and run controlled agent experiments with one mutation surface, fixed budget, independent evaluator, objective score or explicit rubric, and keep-discard-revert rules. Use for autonomous optimization or sandbox trials.","category":"governance","source_rows":["agent-intelligence-economy:skills/bounded-agent-lab/SKILL.md","agent-intelligence-economy:docs/07-bounded-agent-labs.md","agent-intelligence-economy:templates/program-contract.md","agent-intelligence-economy:examples/bounded-agent-lab-run/example.md"],"license":"CC BY 4.0","triggers":["agent experiment","autonomous optimization","sandbox trial","bounded mutation","evaluation harness"]}
---

# Run Bounded Agent Labs

## Write the program contract

Before execution, state the objective, baseline, allowed mutation surface, forbidden surfaces, evaluator, budget, score or human rubric, stop condition, and keep/discard/revert rule. Use one mutation surface per run so the result remains attributable.

The optimizing agent must not edit its evaluator, test fixtures, scoring rule, or safety boundary. Place experiments in a sandbox or isolated branch and block production credentials and irreversible external actions unless separately authorized.

## Run against a baseline

Capture the pre-run artifact and score. Execute within fixed time, token, retry, and tool budgets. Record attempted mutation, observations, failures, and actual consumption. Crash, null result, discard, and early stop are valid results.

## Evaluate independently

Run the fixed evaluator on baseline and candidate. Check for reward hacking, test contamination, hidden cost, safety regression, complexity growth, and performance that depends on leaked evaluation context. Prefer a simpler candidate when the measured gain does not justify maintenance.

Keep only a candidate that meets the predeclared threshold and all safety checks. Otherwise revert or discard it while preserving the run record. Return the evidence handles, measured delta, caveats, and supported disposition; never promote a lab result silently into production or canon.
