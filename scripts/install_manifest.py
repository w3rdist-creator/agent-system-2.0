#!/usr/bin/env python3
"""Internal manifest engine for the POSIX installer entrypoints."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys


MANIFEST_RELATIVE = Path(".evidence-first/install-manifest.json")
MANIFEST_SCHEMA_VERSION = 2
SUPPORTED_MANIFEST_SCHEMAS = {1, MANIFEST_SCHEMA_VERSION}


class InstallError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def absolute(path: str) -> Path:
    return Path(path).expanduser().resolve()


def manifest_path(vault: Path) -> Path:
    return vault / MANIFEST_RELATIVE


def read_manifest(vault: Path) -> tuple[Path, dict[str, object]]:
    path = manifest_path(vault)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InstallError(f"install manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InstallError(f"invalid install manifest {path}: {exc}") from exc
    if (
        data.get("manifest_schema_version") not in SUPPORTED_MANIFEST_SCHEMAS
        or not isinstance(data.get("files"), list)
    ):
        raise InstallError(f"unsupported or malformed install manifest: {path}")
    return path, data


def write_manifest(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def unquote_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def external_dirs_from_config(path: Path) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise InstallError(f"cannot inspect Hermes config {path}: {exc}") from exc

    skills_indent = None
    external_line = None
    external_indent = None
    inline_value = ""
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if stripped == "skills:":
            skills_indent = indent
            continue
        if skills_indent is not None and indent <= skills_indent:
            skills_indent = None
        if skills_indent is not None and stripped.startswith("external_dirs:"):
            external_line = index
            external_indent = indent
            inline_value = stripped.split(":", 1)[1].strip()
            break

    if external_line is None or external_indent is None:
        return []
    if inline_value:
        if inline_value == "[]":
            return []
        if inline_value.startswith("[") and inline_value.endswith("]"):
            try:
                parsed = json.loads(inline_value.replace("'", '"'))
            except json.JSONDecodeError as exc:
                raise InstallError("skills.external_dirs inline list is not safely readable") from exc
            if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
                raise InstallError("skills.external_dirs must be a string list")
            return parsed
        return [unquote_yaml_scalar(inline_value)]

    entries: list[str] = []
    for line in lines[external_line + 1 :]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent <= external_indent:
            break
        if not stripped.startswith("- "):
            raise InstallError("skills.external_dirs contains a non-list value")
        entries.append(unquote_yaml_scalar(stripped[2:]))
    return entries


def normalize_config_path(value: str, hermes_home: Path) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(value))
    candidate = Path(expanded)
    if not candidate.is_absolute():
        candidate = hermes_home / candidate
    return candidate.resolve()


def inspect_config(args: argparse.Namespace) -> int:
    hermes_home = absolute(args.hermes_home)
    desired = absolute(args.desired)
    entries = external_dirs_from_config(hermes_home / "config.yaml")
    normalized = [normalize_config_path(entry, hermes_home) for entry in entries]
    if desired in normalized:
        print(normalized.index(desired))
        print("true")
    else:
        print(len(entries))
        print("false")
    return 0


def source_files(root: Path) -> list[tuple[Path, Path, str]]:
    result: list[tuple[Path, Path, str]] = []
    distribution_root = Path("__DISTRIBUTION__")
    for directory in ("agent", "enforcement", "skills", "templates"):
        source_root = root / directory
        for source in sorted(source_root.rglob("*")):
            if source.is_file() and "__pycache__" not in source.parts and source.suffix != ".pyc":
                result.append((source, distribution_root / directory / source.relative_to(source_root), "hermes-distribution"))
    result.append(
        (
            root / "packs" / "manifest.yaml",
            distribution_root / "packs" / "manifest.yaml",
            "hermes-distribution",
        )
    )
    for source in sorted((root / "packs").glob("*/PACK.md")):
        result.append(
            (
                source,
                distribution_root / "packs" / source.parent.name / "PACK.md",
                "hermes-distribution",
            )
        )
    vault_source = root / "vault-template"
    for source in sorted(vault_source.rglob("*")):
        if source.is_file():
            result.append((source, source.relative_to(vault_source), "vault-base"))
    return result


def destination_for(relative: Path, vault: Path, distribution: Path) -> Path:
    parts = relative.parts
    if parts and parts[0] == "__DISTRIBUTION__":
        return distribution.joinpath(*parts[1:])
    return vault / relative


def proposed_destination(target: Path) -> tuple[Path, str]:
    if not target.exists():
        return target, "absent"
    incoming = target.with_name(target.name + ".incoming")
    if incoming.exists():
        raise InstallError(f"conflict proposal already exists; refusing to overwrite: {incoming}")
    return incoming, "preexisting"


def copy_owned(source: Path, target: Path, component: str) -> dict[str, str]:
    actual, original_state = proposed_destination(target)
    actual.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, actual)
    return {
        "path": str(actual),
        "original_state": original_state,
        "sha256": sha256(actual),
        "component": component,
    }


def install_plan(args: argparse.Namespace) -> int:
    root = absolute(args.root)
    vault = absolute(args.vault)
    distribution = absolute(args.hermes_home) / "distributions" / "evidence-first"
    for source, relative, component in source_files(root):
        target = destination_for(relative, vault, distribution)
        actual, state = proposed_destination(target)
        print(f"PLAN {component}: {source.relative_to(root)} -> {actual} ({state})")
    print(f"PLAN manifest: {manifest_path(vault)}")
    return 0


def install(args: argparse.Namespace) -> int:
    root = absolute(args.root)
    vault = absolute(args.vault)
    hermes_home = absolute(args.hermes_home)
    distribution = hermes_home / "distributions" / "evidence-first"
    path = manifest_path(vault)
    if path.exists():
        raise InstallError(f"existing install manifest; refusing to overwrite: {path}")

    entries = []
    for source, relative, component in source_files(root):
        entries.append(copy_owned(source, destination_for(relative, vault, distribution), component))
    data: dict[str, object] = {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "strategy": "reference-first",
        "hermes_compatibility": "0.18.x",
        "hermes_home": str(hermes_home),
        "vault": str(vault),
        "external_dirs_index": args.external_index,
        "external_dirs_path": str(distribution / "skills"),
        "config_entry_added": args.config_entry_added == "true",
        "installed_packs": [],
        "files": entries,
    }
    write_manifest(path, data)
    print(f"INSTALLED: {len(entries)} owned files")
    print(f"MANIFEST: {path}")
    return 0


def logical_installed_path(entry: dict[str, object]) -> Path:
    path = Path(str(entry["path"]))
    if entry.get("original_state") == "preexisting" and path.name.endswith(".incoming"):
        return path.with_name(path.name[: -len(".incoming")])
    return path


def upgrade(args: argparse.Namespace) -> int:
    root = absolute(args.root)
    vault = absolute(args.vault)
    requested_home = absolute(args.hermes_home)
    manifest_file, data = read_manifest(vault)
    if data.get("hermes_home") != str(requested_home):
        raise InstallError("refusing upgrade: --hermes-home does not match the install manifest")

    distribution = requested_home / "distributions" / "evidence-first"
    files = data.get("files")
    if not isinstance(files, list):
        raise InstallError("install manifest files must be a list")

    managed: dict[Path, dict[str, object]] = {}
    pack_entries: list[dict[str, object]] = []
    for raw in files:
        if not isinstance(raw, dict) or not isinstance(raw.get("path"), str):
            raise InstallError("malformed manifest file entry; refusing partial upgrade")
        component = raw.get("component")
        if isinstance(component, str) and component.startswith("pack:"):
            pack_entries.append(raw)
            continue
        logical = logical_installed_path(raw)
        if logical in managed:
            raise InstallError(f"duplicate logical path in install manifest: {logical}")
        managed[logical] = raw

    actions: list[dict[str, object]] = []
    new_entries: list[dict[str, object]] = []
    matched: set[Path] = set()
    counts = {"replaced": 0, "preserved": 0, "added": 0, "retired": 0, "warnings": 0}

    for source, relative, component in source_files(root):
        target = destination_for(relative, vault, distribution)
        source_hash = sha256(source)
        old = managed.get(target)
        if old is None:
            actual, state = proposed_destination(target)
            entry = {
                "path": str(actual),
                "original_state": state,
                "sha256": source_hash,
                "component": component,
            }
            actions.append({"kind": "added", "source": source, "path": actual})
            new_entries.append(entry)
            counts["added"] += 1
            continue

        matched.add(target)
        installed = Path(str(old["path"]))
        if not (within(installed, vault) or within(installed, distribution)):
            raise InstallError(f"out-of-scope manifest path; refusing upgrade: {installed}")
        old_hash = old.get("sha256")
        marked_modified = "superseded_by_incoming" in old
        if installed.is_file() and sha256(installed) == old_hash and not marked_modified:
            if source_hash == old_hash:
                actions.append({"kind": "unchanged", "path": installed})
            else:
                actions.append({"kind": "replaced", "source": source, "path": installed})
                counts["replaced"] += 1
            entry = dict(old)
            entry["sha256"] = source_hash
            entry["component"] = component
            entry.pop("superseded_by_incoming", None)
            new_entries.append(entry)
            continue

        if installed.is_file():
            incoming = installed.with_name(installed.name + ".incoming")
            if incoming.exists():
                if not incoming.is_file() or sha256(incoming) != source_hash:
                    raise InstallError(
                        f"conflict proposal already exists; refusing to overwrite: {incoming}"
                    )
                write_incoming = False
            else:
                write_incoming = True
            current_hash = sha256(installed)
            entry = dict(old)
            entry["sha256"] = current_hash
            entry["component"] = component
            entry["superseded_by_incoming"] = str(incoming)
            actions.append(
                {
                    "kind": "preserved",
                    "source": source,
                    "path": installed,
                    "incoming": incoming,
                    "write": write_incoming,
                }
            )
            new_entries.append(entry)
            counts["preserved"] += 1
            continue

        actual, state = proposed_destination(target)
        entry = {
            "path": str(actual),
            "original_state": state,
            "sha256": source_hash,
            "component": component,
        }
        actions.append({"kind": "added", "source": source, "path": actual})
        new_entries.append(entry)
        counts["added"] += 1
        counts["warnings"] += 1
        actions.append({"kind": "warning", "message": f"previously installed file was absent: {installed}"})

    for logical, old in managed.items():
        if logical in matched:
            continue
        installed = Path(str(old["path"]))
        if not (within(installed, vault) or within(installed, distribution)):
            raise InstallError(f"out-of-scope retired manifest path; refusing upgrade: {installed}")
        if installed.is_file() and sha256(installed) == old.get("sha256") and "superseded_by_incoming" not in old:
            actions.append({"kind": "retired", "path": installed})
            counts["retired"] += 1
        elif installed.exists():
            actions.append(
                {
                    "kind": "warning",
                    "message": f"retired modified file preserved and no longer tracked: {installed}",
                }
            )
            counts["warnings"] += 1
        else:
            actions.append(
                {
                    "kind": "warning",
                    "message": f"retired file was already absent and is no longer tracked: {installed}",
                }
            )
            counts["warnings"] += 1

    if args.dry_run:
        for action in actions:
            kind = str(action["kind"])
            if kind == "preserved":
                print(f"PLAN preserved-with-incoming: {action['path']} -> {action['incoming']}")
            elif kind == "warning":
                print(f"PLAN warning: {action['message']}")
            else:
                print(f"PLAN {kind}: {action['path']}")
        print(f"PLAN manifest: {manifest_file} (schema {MANIFEST_SCHEMA_VERSION})")
    else:
        parents: set[Path] = set()
        for action in actions:
            kind = str(action["kind"])
            if kind in {"replaced", "added"}:
                destination = Path(str(action["path"]))
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(Path(str(action["source"])), destination)
                print(f"{kind.upper()}: {destination}")
            elif kind == "preserved":
                incoming = Path(str(action["incoming"]))
                if action["write"]:
                    incoming.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(Path(str(action["source"])), incoming)
                print(f"PRESERVED WITH INCOMING: {action['path']} -> {incoming}")
            elif kind == "retired":
                retired = Path(str(action["path"]))
                retired.unlink()
                parents.add(retired.parent)
                print(f"RETIRED: {retired}")
            elif kind == "warning":
                print(f"WARNING: {action['message']}")
        parents.update(remove_generated_bytecode(distribution))
        remove_empty_parents(parents, (vault, distribution))
        data["manifest_schema_version"] = MANIFEST_SCHEMA_VERSION
        data["files"] = new_entries + pack_entries
        write_manifest(manifest_file, data)

    print(
        "UPGRADE REPORT: "
        f"replaced={counts['replaced']} "
        f"preserved-with-incoming={counts['preserved']} "
        f"added={counts['added']} retired={counts['retired']} warnings={counts['warnings']}"
    )
    return 0


def load_pack_manifest(root: Path) -> dict[str, object]:
    path = root / "packs" / "manifest.yaml"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallError(f"cannot read pack manifest {path}: {exc}") from exc
    packs = data.get("packs")
    if not isinstance(packs, dict):
        raise InstallError("pack manifest has no packs mapping")
    return packs


def list_packs(args: argparse.Namespace) -> int:
    packs = load_pack_manifest(absolute(args.root))
    print("pack\tstatus\tactivation_trigger")
    for name, entry in packs.items():
        if not isinstance(entry, dict):
            raise InstallError(f"invalid pack entry: {name}")
        print(f"{name}\t{entry.get('status', 'unknown')}\t{entry.get('activation_trigger', '')}")
    return 0


def install_pack(args: argparse.Namespace) -> int:
    root = absolute(args.root)
    vault = absolute(args.vault)
    packs = load_pack_manifest(root)
    entry = packs.get(args.pack)
    if not isinstance(entry, dict):
        raise InstallError(f"unknown pack: {args.pack}")
    status = entry.get("status")
    trigger = entry.get("activation_trigger", "No activation trigger recorded.")
    if status != "shipped":
        raise InstallError(f"pack {args.pack} is inert; activation trigger: {trigger}")
    path, data = read_manifest(vault)
    installed = data.get("installed_packs")
    if not isinstance(installed, list):
        raise InstallError("install manifest has malformed installed_packs")
    if args.pack in installed:
        raise InstallError(f"pack already installed: {args.pack}")
    payload_value = entry.get("payload")
    if not isinstance(payload_value, str):
        raise InstallError(f"shipped pack has no payload: {args.pack}")
    payload = root / payload_value
    new_entries = []
    for source in sorted(payload.rglob("*")):
        if source.is_file():
            new_entries.append(copy_owned(source, vault / source.relative_to(payload), f"pack:{args.pack}"))
    data["files"].extend(new_entries)  # type: ignore[union-attr]
    installed.append(args.pack)
    write_manifest(path, data)
    print(f"INSTALLED PACK: {args.pack} ({len(new_entries)} files)")
    return 0


def verify(args: argparse.Namespace) -> int:
    vault = absolute(args.vault)
    _, data = read_manifest(vault)
    expected_home = absolute(args.hermes_home)
    if data.get("hermes_home") != str(expected_home):
        raise InstallError(
            f"manifest Hermes home is {data.get('hermes_home')!r}, not requested {str(expected_home)!r}"
        )
    preserve = {str(absolute(item)) for item in args.preserve}
    failures: list[str] = []
    files = data["files"]
    if not isinstance(files, list):
        raise InstallError("install manifest files must be a list")
    if args.expect_absent:
        for raw in files:
            if not isinstance(raw, dict) or not isinstance(raw.get("path"), str):
                failures.append("malformed manifest file entry")
                continue
            path = Path(raw["path"])
            if str(path.resolve()) in preserve:
                if not path.is_file():
                    failures.append(f"preserved path missing: {path}")
            elif path.exists():
                failures.append(f"owned file still present: {path}")
        for item in preserve:
            if not Path(item).is_file():
                failures.append(f"preserved path missing: {item}")
    else:
        for raw in files:
            if not isinstance(raw, dict) or not isinstance(raw.get("path"), str):
                failures.append("malformed manifest file entry")
                continue
            path = Path(raw["path"])
            if not path.is_file():
                failures.append(f"missing installed file: {path}")
            elif sha256(path) != raw.get("sha256"):
                failures.append(f"hash mismatch: {path}")
        if data.get("config_entry_added"):
            external_path = str(data.get("external_dirs_path"))
            entries = external_dirs_from_config(expected_home / "config.yaml")
            normalized = [normalize_config_path(entry, expected_home) for entry in entries]
            if normalize_config_path(external_path, expected_home) not in normalized:
                failures.append(
                    f"config entry missing: in {expected_home / 'config.yaml'}, add "
                    f"{external_path!r} as a new entry under skills.external_dirs; "
                    "the installer never edits config.yaml, so this manual step activates the install"
                )
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print(f"Install verification failed with {len(failures)} error(s).")
        return 1
    mode = "post-uninstall absence/preservation" if args.expect_absent else "installed files and hashes"
    print(f"PASS: {mode} verified across {len(files)} manifest file(s)")
    return 0


def within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def remove_empty_parents(parents: set[Path], roots: tuple[Path, ...]) -> int:
    candidates: set[Path] = set()
    for parent in parents:
        current = parent
        for root in roots:
            if within(current, root):
                while within(current, root):
                    candidates.add(current)
                    if current == root:
                        break
                    current = current.parent
                break
    removed = 0
    for directory in sorted(candidates, key=lambda item: len(item.parts), reverse=True):
        try:
            directory.rmdir()
        except (FileNotFoundError, OSError):
            continue
        removed += 1
    return removed


def remove_generated_bytecode(distribution: Path) -> set[Path]:
    """Remove interpreter caches strictly within the distribution-owned root."""
    parents: set[Path] = set()
    if not distribution.is_dir():
        return parents

    # Preservation-first protects user content; interpreter-generated bytecode is not user content.
    for current_value, directories, files in os.walk(distribution, followlinks=False):
        current = Path(current_value)
        if "__pycache__" in directories:
            cache = current / "__pycache__"
            directories.remove("__pycache__")
            try:
                shutil.rmtree(cache)
            except OSError as exc:
                raise InstallError(f"cannot remove generated bytecode cache {cache}: {exc}") from exc
            parents.add(current)
        for name in files:
            if not name.endswith(".pyc"):
                continue
            bytecode = current / name
            try:
                bytecode.unlink()
            except OSError as exc:
                raise InstallError(f"cannot remove generated bytecode file {bytecode}: {exc}") from exc
            parents.add(current)
    return parents


def uninstall(args: argparse.Namespace) -> int:
    vault = absolute(args.vault)
    requested_home = absolute(args.hermes_home)
    _, data = read_manifest(vault)
    if data.get("hermes_home") != str(requested_home):
        raise InstallError("refusing uninstall: --hermes-home does not match the install manifest")
    distribution = requested_home / "distributions" / "evidence-first"
    files = data["files"]
    if not isinstance(files, list):
        raise InstallError("install manifest files must be a list")
    removed = 0
    preserved = 0
    warned = 0
    parents: set[Path] = set()
    for raw in files:
        if not isinstance(raw, dict) or not isinstance(raw.get("path"), str):
            print("WARNING: malformed manifest entry preserved")
            warned += 1
            continue
        path = Path(raw["path"])
        if not (within(path, vault) or within(path, distribution)):
            print(f"WARNING: out-of-scope manifest path preserved: {path}")
            warned += 1
            preserved += 1
            continue
        if not path.exists():
            print(f"WARNED: already absent: {path}")
            warned += 1
            continue
        if (
            not path.is_file()
            or sha256(path) != raw.get("sha256")
            or "superseded_by_incoming" in raw
        ):
            print(f"WARNING: modified distribution-owned file preserved: {path}")
            warned += 1
            preserved += 1
            continue
        path.unlink()
        parents.add(path.parent)
        removed += 1
        print(f"REMOVED: {path}")
    parents.update(remove_generated_bytecode(distribution))
    directories = remove_empty_parents(parents, (vault, distribution))
    if data.get("config_entry_added"):
        index = data.get("external_dirs_index")
        external_path = data.get("external_dirs_path")
        print(
            "MANUAL CONFIG REMOVAL REQUIRED: "
            f"in {requested_home / 'config.yaml'}, remove only skills.external_dirs[{index}] "
            f"if its value is {external_path!r}; do not alter any other entry."
        )
    else:
        print("CONFIG: no removal required; the external directory entry predated this install.")
    print(
        f"UNINSTALL REPORT: removed={removed} preserved={preserved} warned={warned} "
        f"empty_directories_removed={directories}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect = subparsers.add_parser("inspect-config")
    inspect.add_argument("--hermes-home", required=True)
    inspect.add_argument("--desired", required=True)
    inspect.set_defaults(func=inspect_config)

    for name, func in (("plan", install_plan), ("install", install)):
        child = subparsers.add_parser(name)
        child.add_argument("--root", required=True)
        child.add_argument("--vault", required=True)
        child.add_argument("--hermes-home", required=True)
        if name == "install":
            child.add_argument("--external-index", required=True, type=int)
            child.add_argument("--config-entry-added", choices=("true", "false"), required=True)
        child.set_defaults(func=func)

    listing = subparsers.add_parser("list-packs")
    listing.add_argument("--root", required=True)
    listing.set_defaults(func=list_packs)

    pack = subparsers.add_parser("install-pack")
    pack.add_argument("pack")
    pack.add_argument("--root", required=True)
    pack.add_argument("--vault", required=True)
    pack.set_defaults(func=install_pack)

    migrate = subparsers.add_parser("upgrade")
    migrate.add_argument("--root", required=True)
    migrate.add_argument("--vault", required=True)
    migrate.add_argument("--hermes-home", required=True)
    migrate.add_argument("--dry-run", action="store_true")
    migrate.set_defaults(func=upgrade)

    check = subparsers.add_parser("verify")
    check.add_argument("--vault", required=True)
    check.add_argument("--hermes-home", default="~/.hermes")
    check.add_argument("--expect-absent", action="store_true")
    check.add_argument("--preserve", action="append", default=[])
    check.set_defaults(func=verify)

    remove = subparsers.add_parser("uninstall")
    remove.add_argument("--vault", required=True)
    remove.add_argument("--hermes-home", default="~/.hermes")
    remove.set_defaults(func=uninstall)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except InstallError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
