from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.verify_templates import (
    MARKDOWN_SCHEMAS,
    json_packet_errors,
    markdown_instance_errors,
    validate_all,
)
from scripts.verify_wikilinks import validate_links


ROOT = Path(__file__).resolve().parents[1]


class TemplateContractTests(unittest.TestCase):
    def test_all_templates_and_examples_pass(self):
        failures = [
            (path, errors)
            for path, errors in validate_all(ROOT / "examples", ROOT)
            if errors
        ]
        self.assertEqual(failures, [])

    def test_validator_catches_missing_markdown_field(self):
        schema = MARKDOWN_SCHEMAS["source-note"]
        text = (ROOT / "examples" / "source-note" / "example.md").read_text(encoding="utf-8")
        broken = text.replace("## Declared decision authority", "## Removed authority field")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "example.md"
            path.write_text(broken, encoding="utf-8")
            self.assertIn(
                "missing field: Declared decision authority",
                markdown_instance_errors(path, schema),
            )

    def test_validator_catches_empty_markdown_field(self):
        schema = MARKDOWN_SCHEMAS["belief-revision"]
        text = (ROOT / "examples" / "belief-revision" / "example.md").read_text(encoding="utf-8")
        start = text.index("## Decision delta")
        end = text.index("## Standing-doctrine update rule")
        broken = text[:start] + "## Decision delta\n\n<!-- empty -->\n\n" + text[end:]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "example.md"
            path.write_text(broken, encoding="utf-8")
            self.assertIn("empty field: Decision delta", markdown_instance_errors(path, schema))

    def test_merge_proposal_requires_attribution(self):
        schema = MARKDOWN_SCHEMAS["merge-proposal"]
        text = (ROOT / "examples" / "merge-proposal" / "example.md").read_text(
            encoding="utf-8"
        )
        broken = text.replace("author: alex\n", "")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "example.md"
            path.write_text(broken, encoding="utf-8")
            self.assertIn(
                "missing frontmatter field: author",
                markdown_instance_errors(path, schema),
            )

    def test_packet_json_round_trips(self):
        for packet_type in ("task-packet", "result-packet"):
            path = ROOT / "examples" / packet_type / "example.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            round_tripped = json.loads(json.dumps(data, sort_keys=True))
            self.assertEqual(round_tripped, data)
            self.assertEqual(json_packet_errors(path, packet_type, template=False), [])

    def test_packet_validator_catches_missing_field(self):
        data = json.loads(
            (ROOT / "examples" / "task-packet" / "example.json").read_text(encoding="utf-8")
        )
        del data["acceptance_checks"]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "example.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertIn(
                "missing field: acceptance_checks",
                json_packet_errors(path, "task-packet", template=False),
            )


class WikilinkContractTests(unittest.TestCase):
    def test_repository_links_and_layers_pass(self):
        errors, files, links = validate_links(
            [ROOT / "vault-template", ROOT / "packs", ROOT / "examples"]
        )
        self.assertEqual(errors, [])
        self.assertGreater(files, 0)
        self.assertGreater(links, 0)

    def test_missing_link_fails_and_planned_link_passes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "note.md").write_text(
                "# Note\n\n[[Missing]]\n\n[[Future|planned]]\n", encoding="utf-8"
            )
            errors, _, _ = validate_links([root])
            self.assertEqual(len(errors), 1)
            self.assertIn("unresolved wikilink [[Missing]]", errors[0])

    def test_active_raw_link_requires_provenance_field(self):
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault-template"
            (vault / "Raw").mkdir(parents=True)
            (vault / "Raw" / "Evidence.md").write_text("# Evidence\n", encoding="utf-8")
            (vault / "Claim.md").write_text(
                "---\ntype: grounded-claim\n---\n# Claim\n\nSee [[Raw/Evidence]].\n",
                encoding="utf-8",
            )
            errors, _, _ = validate_links([vault])
            self.assertTrue(any("outside a provenance field" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
