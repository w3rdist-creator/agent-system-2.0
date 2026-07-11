# Live Hermes enforcement denial

This directory records sanitized facts from an operator-run Hermes Agent turn on 2026-07-11.
It is operator-recorded evidence, not CI-reproducible evidence. The contract-level fixture in
`tests/test_hermes_plugin.py` is the repeatable test; this example shows that the same hook fired
in a real Hermes tool-dispatch path.

No operator-local heartbeat, credentials, home path, or unsanitized session transcript is shipped.
See [transcript-facts.md](transcript-facts.md) for the bounded record.

This evidence directly answers the missing-live-trigger finding in the Opus 4.8 external review
(8.5/10, session `claude/harness-rating-fae06a`), recorded as an operator-vault source note on
2026-07-11. Together with the shipped plugin and development-gate tool-loop leg, it retires both
enforcement capping findings for the published artifact without claiming sandbox completeness.
