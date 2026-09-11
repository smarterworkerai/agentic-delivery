#!/usr/bin/env python3
"""Reference validator and evidence writer for ADW mise tasks."""
from __future__ import annotations

import argparse
from collections import namedtuple
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid
from typing import Any, Iterable


CONTRACT_NAME = "adw-mise-task-contract"
CONTRACT_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0.0"
EXIT_FAILED = 1
EXIT_BLOCKED = 20
EXIT_CONTRACT_ERROR = 21

STATUSES = {
    "passed",
    "failed",
    "skipped",
    "unsupported",
    "blocked",
    "contract-error",
}
SIDE_EFFECTS = {"read-only", "local-write", "remote-write", "destructive"}
SOURCE_LAYERS = {"generic", "context", "project"}
CANONICAL_TASKS = {
    "adw:describe",
    "adw:check",
    "adw:install",
    "adw:build",
    "adw:lint",
    "adw:static-analysis",
    "adw:test:unit",
    "adw:test:integration",
    "adw:verify:minimal",
    "adw:verify:full",
    "adw:deploy:config:pull",
    "adw:deploy:config:plan",
    "adw:deploy:config:apply",
    "adw:deploy:apply",
    "adw:deploy:status",
    "adw:health",
    "adw:readiness",
    "adw:e2e",
    "adw:validate-deployment",
    "adw:hotfix:apply",
    "adw:context:check",
    "adw:context:sync",
}
TASK_SIDE_EFFECTS = {
    "adw:describe": "read-only",
    "adw:check": "read-only",
    "adw:install": "local-write",
    "adw:build": "local-write",
    "adw:lint": "local-write",
    "adw:static-analysis": "local-write",
    "adw:test:unit": "local-write",
    "adw:test:integration": "local-write",
    "adw:verify:minimal": "local-write",
    "adw:verify:full": "local-write",
    "adw:deploy:config:pull": "local-write",
    "adw:deploy:config:plan": "read-only",
    "adw:deploy:config:apply": "remote-write",
    "adw:deploy:apply": "remote-write",
    "adw:deploy:status": "read-only",
    "adw:health": "read-only",
    "adw:readiness": "read-only",
    "adw:e2e": "remote-write",
    "adw:validate-deployment": "remote-write",
    "adw:hotfix:apply": "remote-write",
    "adw:context:check": "read-only",
    "adw:context:sync": "local-write",
}
ENVIRONMENT_TASKS = {
    "adw:deploy:config:pull",
    "adw:deploy:config:plan",
    "adw:deploy:config:apply",
    "adw:deploy:apply",
    "adw:deploy:status",
    "adw:health",
    "adw:readiness",
    "adw:e2e",
    "adw:validate-deployment",
    "adw:hotfix:apply",
}
CORE_TASKS = {"adw:describe", "adw:check"}
LOCAL_QUALITY_TASKS = {
    "adw:build",
    "adw:lint",
    "adw:static-analysis",
    "adw:test:unit",
    "adw:test:integration",
}
MINIMAL_SMOKE_TASKS = {"adw:build", "adw:test:unit", "adw:test:integration"}
SECRET_KEY_PATTERN = re.compile(r"(?:password|token|secret|credential|private[_-]?key)", re.I)
ALLOWED_SECRET_METADATA_KEYS = {"required_secret_env"}
CHECKSUM_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
GIT_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
COMPATIBILITY_PATTERN = re.compile(r"^>=(\d+)\.(\d+)\.(\d+),<(\d+)\.(\d+)\.(\d+)$")

Result = namedtuple("Result", "exit_code evidence payload")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _run_id(explicit: str | None) -> str:
    return explicit or os.environ.get("ADW_RUN_ID") or f"adw-{uuid.uuid4()}"


def _manifest_path(project_root: Path) -> Path:
    return project_root / ".hermes" / "adw-task-manifest.json"


def _load_manifest(project_root: Path) -> dict[str, Any]:
    path = _manifest_path(project_root)
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("manifest root must be an object")
    return value


def _source_revision(project_root: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return completed.stdout.strip() or None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _safe_task_filename(task: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", task).strip("_") or "task"


def _evidence_root(project_root: Path, manifest: dict[str, Any] | None) -> Path:
    configured = ".hermes/evidence"
    if manifest:
        evidence = manifest.get("evidence")
        if isinstance(evidence, dict) and isinstance(evidence.get("root"), str):
            configured = evidence["root"]
    root = (project_root / configured).resolve()
    project = project_root.resolve()
    if root != project and project not in root.parents:
        raise ValueError("evidence.root must remain inside the project")
    return root


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _finding(code: str, message: str, severity: str = "error") -> dict[str, str]:
    return {"code": code, "severity": severity, "message": message}


def _build_evidence(
    project_root: Path,
    manifest: dict[str, Any] | None,
    *,
    task: str,
    status: str,
    exit_code: int,
    run_id: str | None,
    findings: list[dict[str, str]] | None = None,
    arguments: dict[str, Any] | None = None,
    children: Iterable[str] | None = None,
    started_at: str | None = None,
) -> dict[str, Any]:
    if status not in STATUSES:
        raise ValueError(f"invalid evidence status: {status}")
    capability = {}
    if manifest and isinstance(manifest.get("capabilities"), dict):
        candidate = manifest["capabilities"].get(task)
        if isinstance(candidate, dict):
            capability = candidate
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "run_id": _run_id(run_id),
        "task": task,
        "status": status,
        "exit_code": exit_code,
        "started_at": started_at or _now(),
        "finished_at": _now(),
        "source_revision": _source_revision(project_root),
        "effective_source": capability.get("source"),
        "arguments": arguments or {},
        "findings": findings or [],
        "children": list(children or []),
    }


def _persist(project_root: Path, manifest: dict[str, Any] | None, evidence: dict[str, Any]) -> Path:
    try:
        root = _evidence_root(project_root, manifest)
    except ValueError:
        root = project_root.resolve() / ".hermes" / "evidence"
    directory = root / evidence["run_id"]
    path = directory / f"{_safe_task_filename(evidence['task'])}.json"
    _atomic_write_json(path, evidence)
    return path


def _result(
    project_root: Path,
    manifest: dict[str, Any] | None,
    *,
    task: str,
    status: str,
    exit_code: int,
    run_id: str | None,
    findings: list[dict[str, str]] | None = None,
    arguments: dict[str, Any] | None = None,
    children: Iterable[str] | None = None,
    payload: dict[str, Any] | None = None,
    started_at: str | None = None,
) -> Result:
    evidence = _build_evidence(
        project_root,
        manifest,
        task=task,
        status=status,
        exit_code=exit_code,
        run_id=run_id,
        findings=findings,
        arguments=arguments,
        children=children,
        started_at=started_at,
    )
    _persist(project_root, manifest, evidence)
    return Result(exit_code, evidence, payload or {})


def _validate_source(source: Any, location: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if not isinstance(source, dict):
        return [_finding("source.type", f"{location} must be an object")]
    layer = source.get("layer")
    if layer not in SOURCE_LAYERS:
        findings.append(_finding("source.layer", f"{location}.layer must be one of {sorted(SOURCE_LAYERS)}"))
    source_ref = source.get("ref")
    if not isinstance(source_ref, str) or not source_ref:
        findings.append(_finding("source.ref", f"{location}.ref must be a non-empty string"))
    elif layer in {"generic", "context"} and not GIT_COMMIT_PATTERN.fullmatch(source_ref):
        findings.append(_finding("source.ref", f"{location}.ref must be an immutable 40-character Git commit SHA for {layer} sources"))
    checksum = source.get("checksum")
    if not isinstance(checksum, str) or not CHECKSUM_PATTERN.fullmatch(checksum):
        findings.append(_finding("source.checksum", f"{location}.checksum must be sha256:<64 lowercase hex>"))
    source_path = source.get("path")
    if not isinstance(source_path, str) or not source_path:
        findings.append(_finding("source.path", f"{location}.path must be a non-empty project-relative path"))
    else:
        parsed_path = Path(source_path)
        if parsed_path.is_absolute() or ".." in parsed_path.parts:
            findings.append(_finding("source.path", f"{location}.path must be a non-escaping project-relative path"))
    return findings


def _find_secret_bearing_fields(value: Any, path: str = "$") -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if SECRET_KEY_PATTERN.search(str(key)) and key not in ALLOWED_SECRET_METADATA_KEYS:
                findings.append(_finding("secret.field", f"secret-bearing field is forbidden at {child_path}"))
                continue
            findings.extend(_find_secret_bearing_fields(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_find_secret_bearing_fields(child, f"{path}[{index}]"))
    return findings


def validate_manifest(manifest: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        findings.append(_finding("schema.version", f"schema_version must equal {SCHEMA_VERSION}"))
    contract = manifest.get("contract")
    if not isinstance(contract, dict):
        findings.append(_finding("contract.type", "contract must be an object"))
    else:
        if contract.get("name") != CONTRACT_NAME:
            findings.append(_finding("contract.name", f"contract.name must equal {CONTRACT_NAME}"))
        version = contract.get("version")
        if version != CONTRACT_VERSION:
            findings.append(_finding("contract.version", f"contract.version must equal consumed version {CONTRACT_VERSION}"))
        compatible = contract.get("compatible")
        match = COMPATIBILITY_PATTERN.fullmatch(compatible) if isinstance(compatible, str) else None
        if match is None:
            findings.append(_finding("contract.compatible", "contract.compatible must use >=x.y.z,<x.y.z syntax"))
        else:
            parts = tuple(int(value) for value in match.groups())
            lower, upper = parts[:3], parts[3:]
            current = tuple(int(value) for value in CONTRACT_VERSION.split("."))
            if not lower <= current < upper:
                findings.append(_finding("contract.compatible", f"contract.compatible does not accept {CONTRACT_VERSION}"))
    project = manifest.get("project")
    if not isinstance(project, dict) or not isinstance(project.get("id"), str) or not project["id"]:
        findings.append(_finding("project.id", "project.id must be a non-empty string"))
    evidence = manifest.get("evidence")
    if not isinstance(evidence, dict) or not isinstance(evidence.get("root"), str):
        findings.append(_finding("evidence.root", "evidence.root must be a string"))
    else:
        evidence_path = Path(evidence["root"])
        if evidence_path.is_absolute() or ".." in evidence_path.parts:
            findings.append(_finding("evidence.root", "evidence.root must be a project-relative non-escaping path"))
    environments = manifest.get("environments")
    if not isinstance(environments, list) or any(not isinstance(item, str) or not item for item in environments):
        findings.append(_finding("environments.type", "environments must be an array of non-empty strings"))
        environments_set: set[str] = set()
    else:
        environments_set = set(environments)
        if len(environments_set) != len(environments):
            findings.append(_finding("environments.unique", "environments must contain unique values"))
    sources = manifest.get("sources")
    registered_sources: set[str] = set()
    if not isinstance(sources, list) or not sources:
        findings.append(_finding("sources.type", "sources must be a non-empty array"))
    else:
        for index, source in enumerate(sources):
            findings.extend(_validate_source(source, f"sources[{index}]"))
            if isinstance(source, dict):
                registered_sources.add(json.dumps(source, sort_keys=True, separators=(",", ":")))
    capabilities = manifest.get("capabilities")
    if not isinstance(capabilities, dict):
        findings.append(_finding("capabilities.type", "capabilities must be an object"))
        capabilities = {}
    for core_task in sorted(CORE_TASKS):
        capability = capabilities.get(core_task)
        if not isinstance(capability, dict) or capability.get("status") != "supported":
            findings.append(_finding("capabilities.core", f"{core_task} must be declared supported"))
    for missing_task in sorted(CANONICAL_TASKS - set(capabilities)):
        findings.append(_finding("capabilities.missing", f"canonical capability must be declared supported or unsupported: {missing_task}"))
    for task, capability in capabilities.items():
        if task not in CANONICAL_TASKS:
            findings.append(_finding("capabilities.name", f"unknown canonical task {task}"))
        if not isinstance(capability, dict):
            findings.append(_finding("capabilities.type", f"capability {task} must be an object"))
            continue
        if capability.get("status") not in {"supported", "unsupported"}:
            findings.append(_finding("capabilities.status", f"{task}.status must be supported or unsupported"))
        side_effect = capability.get("side_effect")
        if side_effect not in SIDE_EFFECTS:
            findings.append(_finding("capabilities.side_effect", f"{task}.side_effect is invalid"))
        elif task in TASK_SIDE_EFFECTS and side_effect != TASK_SIDE_EFFECTS[task]:
            findings.append(
                _finding(
                    "capability.side_effect",
                    f"{task}.side_effect must be {TASK_SIDE_EFFECTS[task]}",
                )
            )
        task_environments = capability.get("environments")
        if not isinstance(task_environments, list):
            findings.append(_finding("capabilities.environments", f"{task}.environments must be an array"))
        else:
            unknown = sorted(set(task_environments) - environments_set)
            if unknown:
                findings.append(_finding("capabilities.environments", f"{task} references unknown environments: {', '.join(unknown)}"))
            if capability.get("status") == "supported" and task in ENVIRONMENT_TASKS and not task_environments:
                findings.append(
                    _finding("capabilities.environments", f"supported environment-aware task {task} requires an environment scope")
                )
        capability_source = capability.get("source")
        findings.extend(_validate_source(capability_source, f"capabilities.{task}.source"))
        if isinstance(capability_source, dict):
            source_key = json.dumps(capability_source, sort_keys=True, separators=(",", ":"))
            if source_key not in registered_sources:
                findings.append(
                    _finding("source.registry", f"capability source for {task} is missing from the sources registry")
                )
    verification = manifest.get("verification")
    if not isinstance(verification, dict):
        findings.append(_finding("verification.type", "verification must be an object"))
    else:
        for name in ("minimal", "full"):
            children = verification.get(name)
            if not isinstance(children, list) or not children:
                findings.append(_finding("verification.children", f"verification.{name} must be a non-empty array"))
                continue
            for child in children:
                capability = capabilities.get(child)
                if not isinstance(capability, dict):
                    findings.append(_finding("verification.capability", f"verification.{name} references undeclared task {child}"))
                elif capability.get("status") != "supported":
                    findings.append(_finding("verification.unsupported", f"verification.{name} references unsupported task {child}"))
        minimal_children = verification.get("minimal")
        if isinstance(minimal_children, list) and not (set(minimal_children) & MINIMAL_SMOKE_TASKS):
            findings.append(
                _finding("verification.minimal", "verification.minimal must include a supported build or test smoke capability")
            )
        full_children = verification.get("full")
        if isinstance(full_children, list):
            supported_quality = {
                task
                for task in LOCAL_QUALITY_TASKS
                if isinstance(capabilities.get(task), dict)
                and capabilities[task].get("status") == "supported"
            }
            missing_quality = sorted(supported_quality - set(full_children))
            if missing_quality:
                findings.append(
                    _finding(
                        "verification.full",
                        f"verification.full omits supported local quality tasks: {', '.join(missing_quality)}",
                    )
                )
    required_secret_env = manifest.get("required_secret_env", [])
    if not isinstance(required_secret_env, list) or any(
        not isinstance(item, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*", item)
        for item in required_secret_env
    ):
        findings.append(_finding("secret.names", "required_secret_env must contain environment-variable names only"))
    findings.extend(_find_secret_bearing_fields(manifest))
    return findings


def describe(project_root: Path | str, run_id: str | None = None) -> Result:
    root = Path(project_root)
    started = _now()
    try:
        manifest = _load_manifest(root)
    except FileNotFoundError:
        return _result(
            root,
            None,
            task="adw:describe",
            status="blocked",
            exit_code=EXIT_BLOCKED,
            run_id=run_id,
            findings=[_finding("manifest.missing", "ADW task manifest is missing")],
            started_at=started,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        return _result(
            root,
            None,
            task="adw:describe",
            status="contract-error",
            exit_code=EXIT_CONTRACT_ERROR,
            run_id=run_id,
            findings=[_finding("manifest.invalid", f"ADW task manifest is invalid: {exc}")],
            started_at=started,
        )
    findings = validate_manifest(manifest)
    if findings:
        return _result(
            root,
            manifest,
            task="adw:describe",
            status="contract-error",
            exit_code=EXIT_CONTRACT_ERROR,
            run_id=run_id,
            findings=findings,
            started_at=started,
        )
    payload = {
        "project": manifest["project"]["id"],
        "contract": manifest["contract"],
        "environments": manifest["environments"],
        "capabilities": manifest["capabilities"],
        "sources": manifest["sources"],
    }
    return _result(
        root,
        manifest,
        task="adw:describe",
        status="passed",
        exit_code=0,
        run_id=run_id,
        payload=payload,
        started_at=started,
    )


def _discover_mise_tasks(project_root: Path) -> tuple[set[str], dict[str, str], dict[str, str]]:
    completed = subprocess.run(
        ["mise", "tasks", "--json"],
        cwd=project_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    payload = json.loads(completed.stdout)
    names: set[str] = set()
    sources: dict[str, str] = {}
    usages: dict[str, str] = {}
    if isinstance(payload, dict):
        names = set(payload)
        items = ((name, item) for name, item in payload.items() if isinstance(item, dict))
    elif isinstance(payload, list):
        items = (
            (item["name"], item)
            for item in payload
            if isinstance(item, dict) and isinstance(item.get("name"), str)
        )
        names.update(item for item in payload if isinstance(item, str))
    else:
        raise ValueError("mise tasks --json returned an unsupported shape")
    for name, item in items:
        names.add(name)
        if isinstance(item.get("source"), str):
            sources[name] = item["source"]
        if isinstance(item.get("usage"), str):
            usages[name] = item["usage"]
    return names, sources, usages


def check(
    project_root: Path | str,
    task_names: Iterable[str] | None = None,
    task_sources: dict[str, str] | None = None,
    task_usages: dict[str, str] | None = None,
    run_id: str | None = None,
) -> Result:
    root = Path(project_root)
    started = _now()
    try:
        manifest = _load_manifest(root)
    except FileNotFoundError:
        return _result(
            root,
            None,
            task="adw:check",
            status="blocked",
            exit_code=EXIT_BLOCKED,
            run_id=run_id,
            findings=[_finding("manifest.missing", "ADW task manifest is missing")],
            started_at=started,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        return _result(
            root,
            None,
            task="adw:check",
            status="contract-error",
            exit_code=EXIT_CONTRACT_ERROR,
            run_id=run_id,
            findings=[_finding("manifest.invalid", f"ADW task manifest is invalid: {exc}")],
            started_at=started,
        )
    findings = validate_manifest(manifest)
    sources = dict(task_sources or {})
    usages = dict(task_usages or {})
    if task_names is None:
        try:
            names, sources, usages = _discover_mise_tasks(root)
        except (FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as exc:
            findings.append(_finding("mise.tasks", f"cannot inspect mise task catalog: {exc}"))
            names = set()
            sources = {}
            usages = {}
    else:
        names = set(task_names)
    capabilities = manifest.get("capabilities", {})
    if isinstance(capabilities, dict):
        for task in sorted(capabilities):
            if task not in names:
                findings.append(_finding("task.missing", f"declared canonical task is missing from mise catalog: {task}"))
                continue
            if task in ENVIRONMENT_TASKS and usages and "<environment>" not in usages.get(task, ""):
                findings.append(
                    _finding("task.signature", f"task {task} must declare a required <environment> input")
                )
            if sources:
                actual_source = sources.get(task)
                expected_source = capabilities[task].get("source", {}).get("path")
                if actual_source is None:
                    findings.append(_finding("task.source", f"mise catalog omits source metadata for {task}"))
                    continue
                actual_path = Path(actual_source)
                if actual_path.is_absolute():
                    try:
                        actual_source = actual_path.resolve().relative_to(root.resolve()).as_posix()
                    except ValueError:
                        actual_source = actual_path.resolve().as_posix()
                if actual_source != expected_source:
                    findings.append(
                        _finding(
                            "task.source",
                            f"task source mismatch for {task}: expected {expected_source!r}, got {actual_source!r}",
                        )
                    )
    if isinstance(capabilities, dict) and sources:
        checked_sources: set[tuple[str, str]] = set()
        for capability in capabilities.values():
            source = capability.get("source", {}) if isinstance(capability, dict) else {}
            source_path = source.get("path")
            checksum = source.get("checksum")
            if not isinstance(source_path, str) or not isinstance(checksum, str):
                continue
            source_key = (source_path, checksum)
            if source_key in checked_sources:
                continue
            checked_sources.add(source_key)
            candidate = root / source_path
            if not candidate.is_file():
                findings.append(_finding("source.missing", f"declared source file is missing: {source_path}"))
                continue
            actual_checksum = "sha256:" + hashlib.sha256(candidate.read_bytes()).hexdigest()
            if actual_checksum != checksum:
                findings.append(
                    _finding(
                        "source.checksum",
                        f"source checksum mismatch for {source_path}: expected {checksum}, got {actual_checksum}",
                    )
                )
    status = "contract-error" if findings else "passed"
    exit_code = EXIT_CONTRACT_ERROR if findings else 0
    return _result(
        root,
        manifest,
        task="adw:check",
        status=status,
        exit_code=exit_code,
        run_id=run_id,
        findings=findings,
        started_at=started,
    )


def unsupported(
    project_root: Path | str,
    task: str,
    run_id: str | None = None,
    environment: str | None = None,
) -> Result:
    root = Path(project_root)
    try:
        manifest = _load_manifest(root)
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        manifest = None
    return _result(
        root,
        manifest,
        task=task,
        status="unsupported",
        exit_code=0,
        run_id=run_id,
        findings=[_finding("capability.unsupported", f"{task} is unsupported by this project", "info")],
        arguments={"environment": environment} if environment else {},
    )


def require(
    project_root: Path | str,
    task: str,
    environment: str | None = None,
    run_id: str | None = None,
) -> Result:
    root = Path(project_root)
    try:
        manifest = _load_manifest(root)
    except FileNotFoundError:
        return _result(
            root,
            None,
            task=task,
            status="blocked",
            exit_code=EXIT_BLOCKED,
            run_id=run_id,
            findings=[_finding("manifest.missing", "ADW task manifest is missing")],
        )
    except (json.JSONDecodeError, ValueError) as exc:
        return _result(
            root,
            None,
            task=task,
            status="contract-error",
            exit_code=EXIT_CONTRACT_ERROR,
            run_id=run_id,
            findings=[_finding("manifest.invalid", f"ADW task manifest is invalid: {exc}")],
        )
    capability = manifest.get("capabilities", {}).get(task)
    if not isinstance(capability, dict) or capability.get("status") != "supported":
        return _result(
            root,
            manifest,
            task=task,
            status="blocked",
            exit_code=EXIT_BLOCKED,
            run_id=run_id,
            findings=[_finding("capability.required", f"required capability is unsupported: {task}")],
            arguments={"environment": environment} if environment else {},
        )
    if task in ENVIRONMENT_TASKS and environment is None:
        return _result(
            root,
            manifest,
            task=task,
            status="blocked",
            exit_code=EXIT_BLOCKED,
            run_id=run_id,
            findings=[_finding("environment.required", f"environment is required for {task}")],
        )
    supported_environments = capability.get("environments", [])
    if environment is not None and environment not in supported_environments:
        return _result(
            root,
            manifest,
            task=task,
            status="blocked",
            exit_code=EXIT_BLOCKED,
            run_id=run_id,
            findings=[_finding("environment.unsupported", f"environment {environment!r} is unsupported for {task}")],
            arguments={"environment": environment},
        )
    return _result(
        root,
        manifest,
        task=task,
        status="passed",
        exit_code=0,
        run_id=run_id,
        arguments={"environment": environment} if environment else {},
    )


def run_command(
    project_root: Path | str,
    task: str,
    command: list[str],
    environment: str | None = None,
    run_id: str | None = None,
    children: Iterable[str] | None = None,
) -> Result:
    root = Path(project_root)
    started = _now()
    manifest = _load_manifest(root)
    child_tasks = list(children or [])
    aggregate_tasks = {"adw:verify:minimal", "adw:verify:full", "adw:validate-deployment", "adw:hotfix:apply"}
    invalid_children = sorted(set(child_tasks) - CANONICAL_TASKS)
    child_error = None
    if child_tasks and task not in aggregate_tasks:
        child_error = f"{task} is not an aggregate task and cannot declare child evidence"
    elif task in child_tasks:
        child_error = f"{task} cannot declare itself as child evidence"
    elif len(set(child_tasks)) != len(child_tasks):
        child_error = "child evidence task names must be unique"
    elif invalid_children:
        child_error = f"unknown child evidence tasks: {', '.join(invalid_children)}"
    if child_error:
        return _result(
            root,
            manifest,
            task=task,
            status="contract-error",
            exit_code=EXIT_CONTRACT_ERROR,
            run_id=run_id,
            findings=[_finding("evidence.children", child_error)],
            arguments={"environment": environment} if environment else {},
            started_at=started,
        )
    preflight = require(root, task, environment=environment, run_id=run_id)
    if preflight.exit_code != 0:
        return preflight
    if not command:
        return _result(
            root,
            manifest,
            task=task,
            status="contract-error",
            exit_code=EXIT_CONTRACT_ERROR,
            run_id=run_id,
            findings=[_finding("command.missing", "project task command is missing")],
            arguments={"environment": environment} if environment else {},
            started_at=started,
        )
    try:
        completed = subprocess.run(command, cwd=root, check=False)
        child_exit = completed.returncode
    except FileNotFoundError:
        child_exit = 127
    exit_code = child_exit if child_exit >= 0 else 128 + abs(child_exit)
    status = "passed" if exit_code == 0 else "failed"
    severity = "info" if exit_code == 0 else "error"
    return _result(
        root,
        manifest,
        task=task,
        status=status,
        exit_code=exit_code,
        run_id=run_id,
        findings=[_finding("command.exit", f"project task command exited with code {exit_code}", severity)],
        arguments={"environment": environment} if environment else {},
        children=child_tasks,
        started_at=started,
    )


def _task_names_from_file(path: Path) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or any(not isinstance(item, str) for item in payload):
        raise ValueError("task names file must contain a JSON string array")
    return set(payload)


def _print_result(result: Result) -> None:
    print(f"{result.evidence['task']}: {result.evidence['status']}")
    for finding in result.evidence["findings"]:
        print(f"- {finding['severity']}: {finding['message']}")
    if result.payload:
        print(json.dumps(result.payload, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--run-id")
    subparsers = parser.add_subparsers(dest="command", required=True)
    describe_parser = subparsers.add_parser("describe")
    describe_parser.set_defaults(command_name="describe")
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--task-names-file", type=Path)
    unsupported_parser = subparsers.add_parser("unsupported")
    unsupported_parser.add_argument("--task", required=True)
    unsupported_parser.add_argument("--environment")
    require_parser = subparsers.add_parser("require")
    require_parser.add_argument("--task", required=True)
    require_parser.add_argument("--environment")
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--task", required=True)
    run_parser.add_argument("--environment")
    run_parser.add_argument("--child", action="append", choices=sorted(CANONICAL_TASKS), default=[])
    run_parser.add_argument("command_args", nargs=argparse.REMAINDER)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.project_root)
    if args.command == "describe":
        result = describe(root, run_id=args.run_id)
    elif args.command == "check":
        task_names = _task_names_from_file(args.task_names_file) if args.task_names_file else None
        result = check(root, task_names=task_names, run_id=args.run_id)
    elif args.command == "unsupported":
        result = unsupported(root, args.task, run_id=args.run_id, environment=args.environment)
    elif args.command == "require":
        result = require(root, args.task, environment=args.environment, run_id=args.run_id)
    else:
        command = args.command_args[1:] if args.command_args[:1] == ["--"] else args.command_args
        result = run_command(
            root,
            args.task,
            command,
            environment=args.environment,
            run_id=args.run_id,
            children=args.child,
        )
    _print_result(result)
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
