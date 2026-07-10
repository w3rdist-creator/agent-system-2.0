from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_adapter():
    spec = importlib.util.spec_from_file_location(
        "eval_adapter_codex", ROOT / "scripts" / "eval_adapter_codex.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AdapterFunctionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = load_adapter()

    def test_reply_schema_is_valid_strict_json(self):
        schema = json.loads(self.adapter.REPLY_SCHEMA)
        self.assertEqual(schema["type"], "object")
        self.assertEqual(
            set(schema["required"]), {"tool", "args", "answer", "disposition"}
        )
        self.assertFalse(schema["additionalProperties"])
        args = schema["properties"]["args"]
        self.assertFalse(args["additionalProperties"])
        self.assertEqual(set(args["required"]), set(args["properties"]))

    def test_extract_json_handles_fences_and_nesting(self):
        extract = self.adapter.extract_json
        self.assertEqual(extract('{"tool": "x", "args": {"a": "{b}"}}')["tool"], "x")
        self.assertEqual(extract('```json\n{"answer": "ok"}\n```')["answer"], "ok")
        self.assertIsNone(extract("no json here"))
        self.assertIsNone(extract('["a", "list"]'))

    def test_canonical_path_confines_reads_to_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "fixture"
            fixture.mkdir()
            (fixture / "a.json").write_text("{}", encoding="utf-8")
            label, resolved = self.adapter.canonical_path("fixture/a.json", fixture)
            self.assertEqual(label, "fixture/a.json")
            self.assertIsNotNone(resolved)
            label, resolved = self.adapter.canonical_path("a.json", fixture)
            self.assertEqual(label, "fixture/a.json")
            _, escaped = self.adapter.canonical_path("../../etc/passwd", fixture)
            self.assertIsNone(escaped)

    def test_execute_tool_strips_null_args_and_reads_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "fixture"
            fixture.mkdir()
            (fixture / "in.txt").write_text("three little words", encoding="utf-8")
            world = self.adapter.TrialWorld(fixture)
            event, result = self.adapter.execute_tool(
                "local_word_count", {"path": "fixture/in.txt", "content": None}, world
            )
            self.assertEqual(event["args"], {"path": "fixture/in.txt"})
            self.assertEqual(result["words"], 3)
            event, result = self.adapter.execute_tool(
                "optional_cloud", {"request": "count"}, world
            )
            self.assertIn("error", result)
            event, result = self.adapter.execute_tool(
                "write_file", {"path": "new.md", "content": "x"}, world
            )
            self.assertEqual(event["args"]["path"], "fixture/new.md")

    def test_writes_persist_within_a_trial_but_never_touch_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "fixture"
            fixture.mkdir()
            (fixture / "belief.md").write_text("original", encoding="utf-8")
            world = self.adapter.TrialWorld(fixture)
            self.adapter.execute_tool(
                "append_file", {"path": "fixture/belief.md", "content": " + revised"}, world
            )
            _, readback = self.adapter.execute_tool(
                "read_file", {"path": "fixture/belief.md"}, world
            )
            self.assertEqual(readback["content"], "original + revised")
            self.assertEqual((fixture / "belief.md").read_text(encoding="utf-8"), "original")
            self.adapter.execute_tool("delete_file", {"path": "fixture/belief.md"}, world)
            _, gone = self.adapter.execute_tool(
                "read_file", {"path": "fixture/belief.md"}, world
            )
            self.assertIn("error", gone)
            self.assertTrue((fixture / "belief.md").is_file())

    def test_zero_read_refusal_detection(self):
        refusal = self.adapter.is_zero_read_refusal(
            [{"type": "answer", "content": "The files were not readable here."}]
        )
        self.assertTrue(refusal)
        engaged = self.adapter.is_zero_read_refusal(
            [
                {"type": "tool_call", "tool": "read_file", "args": {"path": "fixture/a"}},
                {"type": "answer", "content": "The files were not readable here."},
            ]
        )
        self.assertFalse(engaged)


class ReplayAdapterTests(unittest.TestCase):
    def test_replay_roundtrip_and_missing_transcript_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            dump = Path(tmp)
            events = [{"type": "answer", "content": "ok"}]
            (dump / "01-x--treatment--t1.json").write_text(
                json.dumps({"request_loading": [], "events": events}), encoding="utf-8"
            )
            request = json.dumps(
                {"scenario_id": "01-x", "arm": "treatment", "trial": 1}
            )
            env = {**os.environ, "EVAL_TRANSCRIPT_DIR": str(dump)}
            done = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "eval_adapter_replay.py")],
                input=request, text=True, capture_output=True, env=env,
            )
            self.assertEqual(done.returncode, 0)
            self.assertEqual(json.loads(done.stdout), {"events": events})
            missing = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "eval_adapter_replay.py")],
                input=json.dumps({"scenario_id": "02-y", "arm": "control", "trial": 2}),
                text=True, capture_output=True, env=env,
            )
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("missing precomputed transcript", missing.stderr)


if __name__ == "__main__":
    unittest.main()
