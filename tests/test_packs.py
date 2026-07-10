from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.verify_packs import validate_pattern_note, validate_packs


ROOT = Path(__file__).resolve().parents[1]


class PackContractTests(unittest.TestCase):
    def test_all_phase_5_pack_contracts_pass(self):
        errors, stats = validate_packs(ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(stats["packs"], 10)
        self.assertGreaterEqual(stats["seed_artifacts"], 10)
        self.assertEqual(stats["patterns"], 2)

    def test_pattern_validator_catches_missing_causal_mechanism(self):
        source = ROOT / "packs/research/vault/Research/Patterns/Pattern - Bounded Selection Pressure.md"
        text = source.read_text(encoding="utf-8")
        broken = text.replace("## Explicit causal mechanism", "## Removed mechanism")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "pattern.md"
            path.write_text(broken, encoding="utf-8")
            self.assertIn(
                "missing pattern field: Explicit causal mechanism",
                validate_pattern_note(path, template=False),
            )

    def test_pattern_validator_requires_independent_source_repositories(self):
        source = ROOT / "packs/research/vault/Research/Patterns/Pattern - Bounded Selection Pressure.md"
        text = source.read_text(encoding="utf-8")
        start = text.index("---\n") + 4
        end = text.index("\n---", start)
        metadata = json.loads(text[start:end])
        metadata["source_rows"] = [
            "one-repo:path/a.md",
            "one-repo:path/b.md",
        ]
        broken = text[:start] + json.dumps(metadata) + text[end:]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "pattern.md"
            path.write_text(broken, encoding="utf-8")
            self.assertIn(
                "pattern example must use two independently sourced repositories",
                validate_pattern_note(path, template=False),
            )


if __name__ == "__main__":
    unittest.main()
