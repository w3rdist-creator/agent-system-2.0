#!/usr/bin/env python3
"""Repository-level structural verifier for the Release 1.0 candidate."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import re
import sys

from verify_skills import validate_catalog
from verify_packs import validate_packs


PUBLIC_FILE_DISPOSITIONS = frozenset(
    {"copy", "adapt", "merge", "supersede", "external-pointer", "reject"}
)
FAMILY_DISPOSITIONS = frozenset(
    {"adapt", "merge", "defer", "external-pointer", "reject"}
)
REQUIRED_PATHS = (
    ".gitignore",
    "LICENSE",
    "MAINTAINERS.md",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".github/workflows/verify.yml",
    "docs/Effort-Ledger.md",
    "docs/Architecture.md",
    "docs/Why-This-Replaces-The-Super-Repo.md",
    "docs/Admission-and-Exclusion-Policy.md",
    "docs/Token-and-Context-Budget.md",
    "docs/Source-Consolidation.md",
    "docs/Sanitization-and-Publication.md",
    "docs/Deferred-Capability-Roadmap.md",
    "docs/Opus-Review-Disposition.md",
    "docs/Publication-Commands.md",
    "docs/Update-Gate.md",
    "docs/Enforcement.md",
    "docs/Recert.md",
    "docs/Telemetry.md",
    "docs/Team-Vault-Contract.md",
    "docs/Upgrade.md",
    "evaluations/README.md",
    "evaluations/controls/README.md",
    "evaluations/results/RESULTS-SCHEMA.md",
    "scripts/evaluate_scenarios.py",
    "scripts/evaluation_lib.py",
    "scripts/run_paired_suite.py",
    "scripts/recert.py",
    "scripts/recert.sh",
    "scripts/telemetry.py",
    "scripts/audit_context_budget.py",
    "scripts/verify_private_markers.py",
    "scripts/verify_skills.py",
    "scripts/verify_licenses.py",
    "tests/test_evaluations.py",
    "tests/test_run_paired_suite.py",
    "tests/test_dispositions.py",
    "tests/test_router.py",
    "tests/test_licenses.py",
    "tests/test_templates.py",
    "tests/test_enforcement.py",
    "tests/test_hermes_plugin.py",
    "tests/test_completion_gate.py",
    "tests/test_recert.py",
    "tests/test_telemetry.py",
    "agent/SOUL.md",
    "agent/SOUL-scenario-map.yaml",
    "agent/AUTHORITY_BOUNDARIES.md",
    "agent/USER_PROFILE_TEMPLATE.md",
    "agent/LOADING_MODEL.md",
    "enforcement/__init__.py",
    "enforcement/policy.yaml",
    "enforcement/guards.py",
    "enforcement/pre_tool_use.py",
    "enforcement/completion.py",
    "enforcement/completion_gate.py",
    "enforcement/hermes-plugin/__init__.py",
    "enforcement/hermes-plugin/plugin.yaml",
    "skills/level-0-categories.yaml",
    "skills/core/capability-router/SKILL.md",
    "skills/core/evidence-first-operating-style/SKILL.md",
    "skills/core/source-grounding/SKILL.md",
    "skills/core/knowledge-metabolism/SKILL.md",
    "skills/core/loop-governance/SKILL.md",
    "skills/core/vault-operations/SKILL.md",
    "evaluations/context-budget-baseline.json",
    "source-packages/public-file-dispositions.csv",
    "source-packages/capability-family-dispositions.csv",
    "packs/.gitkeep",
    "packs/manifest.yaml",
    "packs/research/PACK.md",
    "packs/agent-ops/PACK.md",
    "packs/context-spine/PACK.md",
    "packs/deep-timeline/PACK.md",
    "packs/markets-research-only/PACK.md",
    "packs/product-os/PACK.md",
    "packs/personal-os/PACK.md",
    "packs/learning-os/PACK.md",
    "packs/software-delivery/PACK.md",
    "packs/simulation-lab/PACK.md",
    "templates/source-note.md",
    "templates/decision-packet.md",
    "templates/task-packet.json",
    "templates/result-packet.json",
    "templates/belief-revision.md",
    "templates/two-layer-report.md",
    "templates/project-handoff.md",
    "templates/merge-proposal.md",
    "examples/merge-proposal/example.md",
    "examples/live-enforcement-denial/README.md",
    "examples/live-enforcement-denial/transcript-facts.md",
    "scripts/verify_wikilinks.py",
    "scripts/verify_packs.py",
    "scripts/install.sh",
    "scripts/upgrade.sh",
    "scripts/uninstall.sh",
    "scripts/install-pack.sh",
    "scripts/list-packs.sh",
    "scripts/verify-install.sh",
    "scripts/install_manifest.py",
    "scripts/score_loops.py",
    "scripts/dev-gate.sh",
    "scripts/publication-gate.sh",
    "scripts/update-gate.sh",
    "scripts/export-public.sh",
    "tests/test_packs.py",
    "tests/test_installer.py",
    "tests/test_upgrade.py",
    "tests/test_uninstaller.py",
    "tests/test_privacy.py",
    "tests/test_update_gate.py",
    "tests/fixtures/hermes-home/README.md",
    "tests/fixtures/hermes-home/config.yaml",
    "tests/fixtures/hermes-home/bin/hermes",
    "vault-template/Home.md",
    "vault-template/Vault Self-Model.md",
    "vault-template/Ledgers/Telemetry Ledger.csv",
    "vault-template/System/System Rules.md",
)
SKIP_DIRS = {".git", "_build", "__pycache__"}
PLACEHOLDER_RE = re.compile(r"\bOPERATOR-[A-Z0-9][A-Z0-9-]*\b")
ALLOWED_PLACEHOLDER = "w3rdist-creator"


def text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        try:
            path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        yield path


def validate_csv(path: Path, allowed: frozenset[str], expected_rows: int | None = None) -> list[str]:
    errors: list[str] = []
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        return [f"cannot read {path}: {exc}"]
    if expected_rows is not None and len(rows) != expected_rows:
        errors.append(f"{path}: expected {expected_rows} rows, found {len(rows)}")
    for line, row in enumerate(rows, 2):
        disposition = row.get("disposition", "")
        if disposition not in allowed:
            errors.append(f"{path}:{line}: invalid disposition {disposition!r}")
    return errors


def script_use_errors(root: Path) -> list[str]:
    errors: list[str] = []
    consumers = [root / "scripts" / "dev-gate.sh", root / "scripts" / "publication-gate.sh"]
    consumers.extend(sorted((root / "tests").glob("test_*.py")))
    workflow_root = root / ".github" / "workflows"
    if workflow_root.is_dir():
        consumers.extend(path for path in workflow_root.rglob("*") if path.is_file())
    usage = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in consumers
        if path.is_file()
    )
    entrypoints = {"dev-gate.sh", "publication-gate.sh"}
    for path in sorted((root / "scripts").iterdir()):
        if not path.is_file() or path.name == "__init__.py" or path.name in entrypoints:
            continue
        module_reference = f"scripts.{path.stem}"
        if path.name not in usage and module_reference not in usage:
            errors.append(f"unused shipped script: scripts/{path.name}")
    return errors


def shell_safety_errors(root: Path) -> list[str]:
    errors: list[str] = []
    forbidden = "rm " + "-rf"
    for path in sorted((root / "scripts").glob("*.sh")):
        text = path.read_text(encoding="utf-8")
        if forbidden in text:
            errors.append(f"forbidden recursive removal form in scripts/{path.name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")
    scenarios = root / "evaluations" / "scenarios"
    expected = root / "evaluations" / "expected"
    if not scenarios.is_dir():
        errors.append("missing required directory: evaluations/scenarios")
    if not expected.is_dir():
        errors.append("missing required directory: evaluations/expected")

    errors.extend(
        validate_csv(
            root / "source-packages" / "public-file-dispositions.csv",
            PUBLIC_FILE_DISPOSITIONS,
            expected_rows=475,
        )
    )

    pack_errors, _ = validate_packs(root)
    errors.extend(f"pack contract: {error}" for error in pack_errors)

    skill_errors, _ = validate_catalog(root)
    errors.extend(f"skill catalog: {error}" for error in skill_errors)
    errors.extend(
        validate_csv(
            root / "source-packages" / "capability-family-dispositions.csv",
            FAMILY_DISPOSITIONS,
            expected_rows=12,
        )
    )

    for path in text_files(root):
        text = path.read_text(encoding="utf-8")
        for match in PLACEHOLDER_RE.finditer(text):
            if match.group(0) != ALLOWED_PLACEHOLDER:
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{path.relative_to(root)}:{line}: unresolved operator placeholder")

    errors.extend(script_use_errors(root))
    errors.extend(shell_safety_errors(root))

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"Repository verification failed with {len(errors)} error(s).")
        return 1
    print("PASS: required Release 1.0 repository structure and public document set are present")
    print("PASS: public file disposition CSV has 475 final rows, zero pending, and a closed vocabulary")
    print("PASS: capability family CSV has 12 rows and a closed vocabulary")
    print("PASS: every accepted skill has exactly one registry route")
    print("PASS: two shipped and eight inert pack contracts pass with source-mapped seeds")
    print("PASS: no unresolved OPERATOR-* placeholders beyond w3rdist-creator")
    print("PASS: every shipped script is exercised by a gate, workflow, or test")
    print("PASS: shell scripts contain no forbidden recursive removal form")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
