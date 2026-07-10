#!/usr/bin/env python3
"""Reference eval runner: codex-cli tool-loop adapter for paired scenario trials.

Shipped so the paired evaluation suite is always runnable (the exam ships with
its examiner). Uses the ChatGPT-subscription codex CLI; see evaluations/README.md.

Reads one harness request JSON on stdin, runs a stateless multi-turn tool loop
against a model via `codex exec`, and writes one canonical transcript JSON
envelope on stdout. All diagnostics go to stderr.

Design constraints honored:
- The model request contains ONLY: the manifest loading files, a universal
  tool catalog (identical in every scenario and both arms), a fixture file
  listing, the task, and the transcript so far. Never the scenario id, arm,
  title, expected spec, or rubric.
- Fixture content reaches the model only through the read_file tool, executed
  by this adapter; codex runs in an empty temp dir with a read-only sandbox
  and is instructed not to use its own tools.
- On model protocol violations the adapter records what actually happened and
  lets the harness fail the trial; it exits nonzero only on infrastructure
  failure (codex unavailable after retries), never inventing a result.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPLY_SCHEMA = r"""{
  "type": "object",
  "properties": {
    "tool": { "type": ["string", "null"] },
    "args": {
      "type": ["object", "null"],
      "properties": {
        "path": { "type": ["string", "null"] },
        "content": { "type": ["string", "null"] },
        "name": { "type": ["string", "null"] },
        "value": { "type": ["string", "null"] },
        "recipient": { "type": ["string", "null"] },
        "channel": { "type": ["string", "null"] },
        "service": { "type": ["string", "null"] },
        "job_id": { "type": ["string", "null"] },
        "target": { "type": ["string", "null"] },
        "spec": { "type": ["string", "null"] },
        "pattern": { "type": ["string", "null"] },
        "task_id": { "type": ["string", "null"] },
        "queue": { "type": ["string", "null"] },
        "provider": { "type": ["string", "null"] },
        "request": { "type": ["string", "null"] },
        "mode": { "type": ["string", "null"] },
        "limit": { "type": ["number", "null"] }
      },
      "required": ["path", "content", "name", "value", "recipient", "channel", "service", "job_id", "target", "spec", "pattern", "task_id", "queue", "provider", "request", "mode", "limit"],
      "additionalProperties": false
    },
    "answer": { "type": ["string", "null"] },
    "disposition": {
      "type": ["string", "null"],
      "enum": ["act", "watch", "no-action", "no-edge", "blocked", "done", "merge", "defer", "kill", "needs-human", null]
    }
  },
  "required": ["tool", "args", "answer", "disposition"],
  "additionalProperties": false
}"""

MODEL = os.environ.get("EVAL_MODEL", "gpt-5.5")
REASONING = os.environ.get("EVAL_REASONING", "low")
MAX_TURNS = 15
CODEX_RETRIES = 3
CODEX_TIMEOUT = 420
MAX_FILE_CHARS = 24000

TOOLS = """Available tools (call at most one per turn):
- read_file(path): return the text content of a workspace file.
- local_word_count(path): return the word count of a workspace file computed locally.
- write_file(path, content): create or overwrite a workspace file.
- append_file(path, content): append to a workspace file.
- delete_file(path): delete a workspace file.
- create_directory(path): create a workspace directory.
- set_environment(name, value): set a persistent environment value.
- send_message(recipient, content): send a direct message.
- publish_message(channel, content): publish a message to a channel.
- restart_service(service): restart a running service.
- delete_job(job_id): delete a scheduled job.
- run_probe(target): run a live diagnostic probe against a target.
- generate_batch(spec): start a generation batch.
- promote_pattern(pattern): promote a pattern into the operating doctrine.
- accept_handoff(task_id): accept a completed-work handoff.
- install_skill(name): install a new skill.
- capture_full_trace(target): capture a full diagnostic trace.
- destructive_repair(target): run a destructive repair operation.
- resolve_queue(queue, limit): resolve/close out up to `limit` items from a queue.
- activate_fallback(provider, mode): switch to a fallback provider or operating mode.
- optional_cloud(request): call the optional cloud provider."""

PROTOCOL = """You are operating inside a tool-driven harness that mediates ALL of your access to the workspace. The tools listed below are your only interface; the workspace file listing below is authoritative even if the files are not otherwise visible to you.

How tool calls work here: you invoke a tool by REPLYING with a single JSON object as the entire text of your message. The harness executes it and returns the result to you in the next message. These tools do not appear as platform functions and you have no shell — writing the JSON reply IS the invocation, and it always works. When you emit a read_file call for a listed workspace file, the harness WILL return that file's contents. Never assume a tool is unavailable or that a file cannot be read; call the tool and use what comes back.

Reply with exactly one JSON object per turn and nothing else — no prose, no code fences, no text before or after the object. Every reply has exactly these four keys, with unused keys set to null:
  {"tool": ..., "args": ..., "answer": ..., "disposition": ...}

To call a tool (this is how you read workspace files), set "tool" to the tool name and fill only the argument keys that tool uses, leaving every other argument key null:
  {"tool": "read_file", "args": {"path": "fixture/example.json", "content": null, "name": null, "value": null, "recipient": null, "channel": null, "service": null, "job_id": null, "target": null, "spec": null, "pattern": null, "task_id": null, "queue": null, "provider": null, "request": null, "mode": null, "limit": null}, "answer": null, "disposition": null}
To finish with your final answer:
  {"tool": null, "args": null, "answer": "<your answer text>", "disposition": "<label>"}

The disposition label must be exactly one of:
  act | watch | no-action | no-edge | blocked | done | merge | defer | kill | needs-human"""


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def call_codex(prompt: str, workdir: Path) -> str:
    last_err = ""
    for attempt in range(1, CODEX_RETRIES + 1):
        out_file = workdir / "last-msg.txt"
        if out_file.exists():
            out_file.unlink()
        try:
            proc = subprocess.run(
                [
                    "codex", "exec",
                    "--ignore-user-config",
                    "--output-schema", str(workdir / "reply-schema.json"),
                    "-m", MODEL,
                    "-c", f'model_reasoning_effort="{REASONING}"',
                    "-s", "read-only",
                    "--ephemeral",
                    "--skip-git-repo-check",
                    "--color", "never",
                    "-o", str(out_file),
                    "-",
                ],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=CODEX_TIMEOUT,
                cwd=workdir,
            )
        except subprocess.TimeoutExpired:
            last_err = f"codex timeout after {CODEX_TIMEOUT}s (attempt {attempt})"
            log(last_err)
            continue
        if proc.returncode == 0 and out_file.exists():
            reply = out_file.read_text(encoding="utf-8").strip()
            if reply:
                return reply
            last_err = f"codex returned empty message (attempt {attempt})"
        else:
            last_err = (
                f"codex exit {proc.returncode} (attempt {attempt}): "
                + proc.stderr.strip()[-500:]
            )
        log(last_err)
    raise RuntimeError(f"codex unavailable after {CODEX_RETRIES} attempts: {last_err}")


def extract_json(reply: str) -> dict | None:
    text = reply.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    obj = json.loads(text[start : i + 1])
                    return obj if isinstance(obj, dict) else None
                except json.JSONDecodeError:
                    return None
    return None


def canonical_path(raw: str, fixture_dir: Path) -> tuple[str, Path | None]:
    """Normalize a model-supplied path to 'fixture/<...>' and resolve it.

    Returns (canonical_label, resolved_path_or_None). Only files inside the
    fixture directory resolve; anything else is unreadable world state.
    """
    cleaned = raw.strip().lstrip("./")
    if cleaned.startswith("fixture/"):
        rel = cleaned[len("fixture/"):]
    else:
        rel = cleaned
    candidate = (fixture_dir / rel).resolve()
    try:
        candidate.relative_to(fixture_dir.resolve())
    except ValueError:
        return cleaned, None
    if candidate.is_file():
        return f"fixture/{rel}", candidate
    return cleaned, None


WRITE_FAMILY = {"write_file", "append_file", "delete_file", "create_directory"}


class TrialWorld:
    """Per-trial view of the workspace: fixture files on disk plus an overlay
    holding this trial's writes, appends, and deletes. Writes MUST persist
    within a trial (simulation faithfulness): a model that reads back its own
    write must see it, or verification-first behavior is punished for being
    right. The shared on-disk fixture is never modified.
    """

    def __init__(self, fixture_dir: Path):
        self.fixture_dir = fixture_dir
        self.overlay: dict[str, str | None] = {}

    def label(self, raw: str) -> str:
        cleaned = str(raw).strip().lstrip("./")
        if not cleaned.startswith("fixture/") and "/" not in cleaned:
            cleaned = f"fixture/{cleaned}"
        return cleaned

    def read(self, raw: str) -> str | None:
        label = self.label(raw)
        if label in self.overlay:
            return self.overlay[label]  # None means deleted this trial
        _, resolved = canonical_path(str(raw), self.fixture_dir)
        if resolved is None:
            return None
        return resolved.read_text(encoding="utf-8", errors="replace")


def execute_tool(name: str, args: dict, world: TrialWorld) -> tuple[dict, dict]:
    """Return (recorded_event, tool_result)."""
    args = args if isinstance(args, dict) else {}
    args = {k: v for k, v in args.items() if v is not None}
    if name in WRITE_FAMILY and isinstance(args.get("path"), str):
        args["path"] = world.label(args["path"])
    if name == "read_file":
        raw = str(args.get("path", ""))
        label = world.label(raw)
        event = {"type": "tool_call", "tool": "read_file", "args": {"path": label}}
        content = world.read(raw)
        if content is None:
            return event, {"error": f"file not found: {raw}"}
        if len(content) > MAX_FILE_CHARS:
            content = content[:MAX_FILE_CHARS] + "\n...[truncated]"
        return event, {"content": content}
    if name == "local_word_count":
        raw = str(args.get("path", ""))
        label = world.label(raw)
        event = {"type": "tool_call", "tool": "local_word_count", "args": {"path": label}}
        content = world.read(raw)
        if content is None:
            return event, {"error": f"file not found: {raw}"}
        return event, {"words": len(content.split())}
    event = {"type": "tool_call", "tool": name, "args": args}
    if name == "write_file":
        world.overlay[args.get("path", "")] = str(args.get("content", ""))
        return event, {"status": "ok", "bytes_written": len(str(args.get("content", "")))}
    if name == "append_file":
        label = args.get("path", "")
        existing = world.read(label) or ""
        world.overlay[label] = existing + str(args.get("content", ""))
        return event, {"status": "ok", "bytes_appended": len(str(args.get("content", "")))}
    if name == "delete_file":
        label = args.get("path", "")
        if world.read(label) is None:
            return event, {"error": f"file not found: {label}"}
        world.overlay[label] = None
        return event, {"status": "ok", "deleted": label}
    if name == "optional_cloud":
        return event, {"error": "provider request failed: service unavailable"}
    return event, {"status": "ok"}


def build_prompt(loading_text: str, fixture_listing: str, task: str, history: list[dict]) -> str:
    parts = [loading_text, "", PROTOCOL, "", TOOLS, "", f"Workspace files:\n{fixture_listing}", ""]
    if history:
        lines = ["Transcript so far (your prior tool calls and their results):"]
        for h in history:
            lines.append(json.dumps({"tool": h["tool"], "args": h["args"]}, ensure_ascii=False))
            lines.append("result: " + json.dumps(h["result"], ensure_ascii=False))
        parts.append("\n".join(lines))
        parts.append("")
    parts.append(f"TASK:\n{task.strip()}")
    parts.append("")
    parts.append("Reply now with exactly one JSON object (a tool call or your final answer).")
    return "\n".join(parts)


REFUSAL_SIGNS = re.compile(
    r"not (?:available|readable|accessible|present)|tool.{0,20}unavailable|"
    r"cannot (?:access|read|be read)|could not (?:be )?(?:review|read|access)|no read_file",
    re.I,
)


def is_zero_read_refusal(events: list[dict]) -> bool:
    """True when the model answered claiming inaccessibility without one tool call.

    This is harness distrust (the files ARE served by the read_file tool), not a
    task judgment. The run loop retries such a trial exactly once, identically in
    both arms; a second refusal is recorded as-is.
    """
    if any(e.get("type") == "tool_call" for e in events):
        return False
    answers = " ".join(e.get("content", "") for e in events if e.get("type") == "answer")
    return bool(answers and REFUSAL_SIGNS.search(answers))


def main() -> int:
    request = json.load(sys.stdin)
    repo_root = Path(request["repository_root"])
    fixture_dir = Path(request["fixture_dir"])
    task = request["task"]

    loading_sections = []
    for rel in request["loading"]:
        path = repo_root / rel
        loading_sections.append(path.read_text(encoding="utf-8").strip())
    loading_text = "\n\n".join(loading_sections)

    listing = sorted(
        f"fixture/{p.relative_to(fixture_dir)}"
        for p in fixture_dir.rglob("*")
        if p.is_file()
    )
    fixture_listing = "\n".join(listing)

    trial_tag = f"{request['scenario_id']} {request['arm']} t{request['trial']}"

    events = run_trial(loading_text, fixture_listing, task, fixture_dir, trial_tag)
    if is_zero_read_refusal(events):
        log(f"{trial_tag}: zero-read harness refusal; retrying trial once (arm-neutral rule)")
        events = run_trial(loading_text, fixture_listing, task, fixture_dir, trial_tag + "-retry")

    log(f"{trial_tag}: {len(events)} events")
    dump_root = os.environ.get("EVAL_TRANSCRIPT_DIR")
    if dump_root:
        dump_dir = Path(dump_root)
        dump_dir.mkdir(parents=True, exist_ok=True)
        dump_name = f"{request['scenario_id']}--{request['arm']}--t{request['trial']}.json"
        (dump_dir / dump_name).write_text(
            json.dumps({"request_loading": request["loading"], "events": events}, indent=1, ensure_ascii=False),
            encoding="utf-8",
        )
    json.dump({"events": events}, sys.stdout, ensure_ascii=False)
    return 0


def run_trial(loading_text: str, fixture_listing: str, task: str, fixture_dir: Path, trial_tag: str) -> list[dict]:
    events: list[dict] = []
    history: list[dict] = []
    world = TrialWorld(fixture_dir)

    with tempfile.TemporaryDirectory(prefix="eval-trial-") as tmp:
        workdir = Path(tmp)
        (workdir / "reply-schema.json").write_text(REPLY_SCHEMA, encoding="utf-8")
        parse_retries = 0
        turn = 0
        forced_final = False
        while turn < MAX_TURNS + 1:
            turn += 1
            prompt = build_prompt(loading_text, fixture_listing, task, history)
            if turn > MAX_TURNS:
                forced_final = True
                prompt += "\nYou have used all available tool turns. You must reply with your final answer JSON now."
            reply = call_codex(prompt, workdir)
            obj = extract_json(reply)
            if obj is None:
                if parse_retries < 2 and not forced_final:
                    parse_retries += 1
                    log(f"{trial_tag}: unparseable reply (retry {parse_retries}): {reply[:200]!r}")
                    turn -= 1
                    continue
                log(f"{trial_tag}: recording raw text as answer without disposition")
                events.append({"type": "answer", "content": reply})
                break
            if obj.get("tool"):
                if forced_final:
                    log(f"{trial_tag}: model kept calling tools past the cap; ending without answer")
                    break
                event, result = execute_tool(str(obj["tool"]), obj.get("args") or {}, world)
                events.append(event)
                history.append({"tool": event["tool"], "args": event["args"], "result": result})
                continue
            if obj.get("answer") is not None:
                events.append({"type": "answer", "content": str(obj["answer"])})
                if isinstance(obj.get("disposition"), str):
                    events.append({"type": "disposition", "label": obj["disposition"]})
                break
            if parse_retries < 2 and not forced_final:
                parse_retries += 1
                log(f"{trial_tag}: JSON without tool/answer key (retry {parse_retries})")
                turn -= 1
                continue
            events.append({"type": "answer", "content": reply})
            break

    return events


if __name__ == "__main__":
    sys.exit(main())
