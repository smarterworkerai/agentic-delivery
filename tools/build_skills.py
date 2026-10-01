#!/usr/bin/env python3
"""Build and validate generated Agent Skills package content."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
GUARDRAILS_START = "<!-- adw:guardrails:start -->"
GUARDRAILS_END = "<!-- adw:guardrails:end -->"
SKILLS_START = "<!-- skills:start -->"
SKILLS_END = "<!-- skills:end -->"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class Skill:
    path: Path
    name: str
    description: str
    compatibility: str
    metadata: dict[str, str]


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("frontmatter must start at byte 0")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("frontmatter closing delimiter missing")
    lines = text[4:end].splitlines()
    data: dict[str, object] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line or line.startswith(" ") or ":" not in line:
            raise ValueError(f"invalid top-level frontmatter line: {line!r}")
        key, raw = line.split(":", 1)
        raw = raw.strip()
        if key == "metadata":
            if raw:
                raise ValueError("metadata must be a mapping")
            metadata: dict[str, str] = {}
            index += 1
            while index < len(lines) and lines[index].startswith("  "):
                nested = lines[index]
                if nested.startswith("    ") or ":" not in nested:
                    raise ValueError("metadata must be a flat string map")
                meta_key, meta_raw = nested.strip().split(":", 1)
                meta_raw = meta_raw.strip()
                if not meta_raw or meta_raw[0] in "[{":
                    raise ValueError("metadata values must be strings")
                metadata[meta_key] = _unquote(meta_raw)
                index += 1
            data[key] = metadata
            continue
        if raw in {">", ">-", "|", "|-"}:
            folded: list[str] = []
            index += 1
            while index < len(lines) and lines[index].startswith("  "):
                folded.append(lines[index].strip())
                index += 1
            data[key] = " ".join(folded).strip()
            continue
        if not raw or raw[0] in "[{":
            raise ValueError(f"{key} must be a string")
        data[key] = _unquote(raw)
        index += 1
    return data, text[end + 5 :]


def discover_skills(root: Path) -> tuple[list[Skill], list[str]]:
    errors: list[str] = []
    skills: list[Skill] = []
    for path in sorted((root / "skills" / "adw").glob("*/SKILL.md")):
        relative = path.relative_to(root)
        try:
            data, _ = parse_frontmatter(path)
        except ValueError as exc:
            errors.append(f"{relative}: {exc}")
            continue
        metadata = data.get("metadata")
        if not isinstance(metadata, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in metadata.items()):
            errors.append(f"{relative}: metadata must be a flat string map")
            metadata = {}
        skills.append(
            Skill(
                path=path,
                name=str(data.get("name", "")),
                description=str(data.get("description", "")),
                compatibility=str(data.get("compatibility", "")),
                metadata=metadata,
            )
        )
    return skills, errors


def _replace_between(text: str, start: str, end: str, content: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    replacement = f"{start}\n{content.rstrip()}\n{end}"
    if not pattern.search(text):
        raise ValueError(f"missing generated markers {start} / {end}")
    return pattern.sub(lambda _: replacement, text, count=1)


def _with_version(text: str, version: str) -> str:
    frontmatter_end = text.find("\n---\n", 4)
    if frontmatter_end < 0:
        raise ValueError("frontmatter closing delimiter missing")
    frontmatter = text[:frontmatter_end]
    updated, count = re.subn(r'(?m)^  version: .*$', f'  version: "{version}"', frontmatter)
    if count != 1:
        raise ValueError("metadata.version must appear exactly once")
    return updated + text[frontmatter_end:]


def _yaml_version(text: str, version: str) -> str:
    updated, count = re.subn(r"(?m)^version: .*$", f"version: {version}", text, count=1)
    if count != 1:
        raise ValueError("plugin manifest version must appear exactly once")
    return updated


def _json_version(text: str, version: str) -> str:
    value = json.loads(text)
    value["version"] = version
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def _router_definitions(skills: list[Skill]) -> list[tuple[str, Skill, str]]:
    definitions: list[tuple[str, Skill, str]] = []
    for skill in skills:
        tokens = skill.metadata.get("router-tokens", "").split()
        presets = {}
        for item in skill.metadata.get("router-presets", "").split():
            token, separator, value = item.partition("=")
            if separator:
                presets[token] = f"type={value}"
        for token in tokens:
            definitions.append((token, skill, presets.get(token, "")))
    return definitions


def render_registry(skills: list[Skill]) -> str:
    definitions = _router_definitions(skills)
    rows = []
    for token, skill, preset in definitions:
        rows.append(
            "    WorkflowDefinition("
            + ", ".join(repr(value) for value in (token, skill.name, skill.path.parent.name, skill.description, preset))
            + "),"
        )
    return '''"""Generated workflow registry for the Hermes `/adw` command.

Run `python3 tools/build_skills.py`; do not edit this file directly.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowDefinition:
    token: str
    skill: str
    skill_dir: str
    description: str
    preset: str = ""


@dataclass(frozen=True)
class Route:
    workflow: str
    skill: str
    payload: str
    preset: str = ""


WORKFLOW_DEFINITIONS: tuple[WorkflowDefinition, ...] = (
''' + "\n".join(rows) + '''
)

WORKFLOWS: dict[str, str] = {definition.token: definition.skill for definition in WORKFLOW_DEFINITIONS}
_DEFINITION_BY_WORKFLOW = {definition.token: definition for definition in WORKFLOW_DEFINITIONS}
_SKILL_DIR_BY_NAME: dict[str, str] = {"adw-core": "adw-core"} | {
    definition.skill: definition.skill_dir for definition in WORKFLOW_DEFINITIONS
}


def normalize_token(token: str) -> str:
    return (token or "").strip().lower().replace("_", "-")


def canonical_workflow(token: str) -> str | None:
    workflow = normalize_token(token)
    return workflow if workflow in WORKFLOWS else None


def parse_route(raw_args: str) -> Route | None:
    args = (raw_args or "").strip()
    if not args:
        return None
    workflow_token, _, payload = args.partition(" ")
    workflow = canonical_workflow(workflow_token)
    if workflow is None:
        return None
    definition = _DEFINITION_BY_WORKFLOW[workflow]
    return Route(workflow=workflow, skill=definition.skill, payload=payload.strip(), preset=definition.preset)


def skill_dir_for_name(skill_name: str) -> str:
    return _SKILL_DIR_BY_NAME[skill_name]


def workflow_description(workflow: str) -> str:
    return _DEFINITION_BY_WORKFLOW[workflow].description
'''


def render_skill_table(skills: list[Skill]) -> str:
    ordered = sorted(skills, key=lambda skill: (skill.name != "adw-core", skill.name))
    lines = ["| Skill | Use it to | Human gate |", "|---|---|---|"]
    for skill in ordered:
        description = skill.description.replace("|", "\\|")
        gate = skill.metadata.get("human-gate", "—").replace("|", "\\|")
        lines.append(f"| `{skill.name}` | {description} | {gate} |")
    return "\n".join(lines)


def generated_outputs(root: Path, skills: list[Skill], version: str) -> dict[Path, str]:
    guardrails = (root / "skills" / "_shared" / "guardrails.md").read_text(encoding="utf-8").strip()
    outputs: dict[Path, str] = {}
    for skill in skills:
        text = _with_version(skill.path.read_text(encoding="utf-8"), version)
        text = _replace_between(text, GUARDRAILS_START, GUARDRAILS_END, guardrails)
        outputs[skill.path] = text

    for relative in ("plugin.yaml", "integrations/hermes/plugin.yaml"):
        path = root / relative
        outputs[path] = _yaml_version(path.read_text(encoding="utf-8"), version)
    claude_manifest = root / ".claude-plugin" / "plugin.json"
    if claude_manifest.exists():
        outputs[claude_manifest] = _json_version(claude_manifest.read_text(encoding="utf-8"), version)

    soul = root / "integrations" / "hermes" / "SOUL.md"
    outputs[soul] = _replace_between(soul.read_text(encoding="utf-8"), GUARDRAILS_START, GUARDRAILS_END, guardrails)
    registry = root / "integrations" / "hermes" / "adw_plugin" / "registry.py"
    outputs[registry] = render_registry(skills)
    readme = root / "README.md"
    outputs[readme] = _replace_between(readme.read_text(encoding="utf-8"), SKILLS_START, SKILLS_END, render_skill_table(skills))

    contract = root / "skills" / "adw" / "adw-core" / "assets" / "mise" / "v2" / "contract.md"
    contract_text, count = re.subn(r"The contract and schema version is `[^`]+`", f"The contract and schema version is `{version}`", contract.read_text(encoding="utf-8"), count=1)
    if count != 1:
        raise ValueError("contract.md package version line missing")
    outputs[contract] = contract_text

    snapshot = root / "skills" / "adw" / "adw-core" / "assets" / "mise" / "v2"
    contract_code = snapshot / "adw_contract.py"
    code_text = contract_code.read_text(encoding="utf-8")
    code_text, contract_count = re.subn(r'(?m)^CONTRACT_VERSION = "[^"]+"$', f'CONTRACT_VERSION = "{version}"', code_text)
    code_text, schema_count = re.subn(r'(?m)^SCHEMA_VERSION = "[^"]+"$', f'SCHEMA_VERSION = "{version}"', code_text)
    if contract_count != 1 or schema_count != 1:
        raise ValueError("adw_contract.py version constants missing")
    outputs[contract_code] = code_text

    template = snapshot / "templates" / "mise.toml"
    template_text, count = re.subn(r'(?m)^adw_contract_version = "[^"]+"$', f'adw_contract_version = "{version}"', template.read_text(encoding="utf-8"))
    if count != 1:
        raise ValueError("mise template contract version missing")
    outputs[template] = template_text

    for schema in sorted((snapshot / "schemas").glob("*.json")):
        schema_text = schema.read_text(encoding="utf-8")
        outputs[schema] = re.sub(r'("const": ")\d+\.\d+\.\d+("(?=,?\n))', rf'\g<1>{version}\2', schema_text)
    for fixture in sorted((snapshot / "fixtures").glob("*/.*/adw-task-manifest.json")):
        data = json.loads(fixture.read_text(encoding="utf-8"))
        data["schema_version"] = version
        data["contract"]["version"] = version
        outputs[fixture] = json.dumps(data, indent=2, sort_keys=True) + "\n"
    return outputs


def validate_skill(skill: Skill, version: str, root: Path) -> list[str]:
    relative = skill.path.relative_to(root)
    errors: list[str] = []
    try:
        data, body = parse_frontmatter(skill.path)
    except ValueError as exc:
        return [f"{relative}: {exc}"]
    if skill.name != skill.path.parent.name:
        errors.append(f"{relative}: name must match parent directory")
    if not NAME_PATTERN.fullmatch(skill.name) or len(skill.name) > 64:
        errors.append(f"{relative}: invalid skill name")
    if not 1 <= len(skill.description) <= 1024:
        errors.append(f"{relative}: description must contain 1-1024 characters")
    if skill.compatibility and len(skill.compatibility) > 500:
        errors.append(f"{relative}: compatibility exceeds 500 characters")
    if "version" in data or "author" in data:
        errors.append(f"{relative}: version and author belong under metadata")
    if skill.metadata.get("version") != version:
        errors.append(f"{relative}: metadata.version must equal VERSION")
    if skill.metadata.get("suite") != "agentic-delivery":
        errors.append(f"{relative}: metadata.suite must be agentic-delivery")
    if len(skill.path.read_text(encoding="utf-8").splitlines()) > 500:
        errors.append(f"{relative}: SKILL.md exceeds 500 lines")
    if not body.strip():
        errors.append(f"{relative}: skill body is empty")
    if GUARDRAILS_START not in body or GUARDRAILS_END not in body:
        errors.append(f"{relative}: generated guardrails block is missing")
    for reference in re.findall(r"\[[^]]*\]\(([^)]+)\)", body):
        reference = reference.split("#", 1)[0]
        if reference and "://" not in reference and not reference.startswith("#"):
            target = (skill.path.parent / reference).resolve()
            if skill.path.parent.resolve() not in (target, *target.parents) or not target.exists():
                errors.append(f"{relative}: unresolved or escaping relative reference {reference!r}")
    for reference in re.findall(r"`((?:\.\./|skills/adw/|adw-core/)[^`]*)`", body):
        errors.append(f"{relative}: cross-skill relative reference {reference!r}")
    for reference in re.findall(r"`(assets/[^`]+)`", body):
        if not (skill.path.parent / reference).exists():
            errors.append(f"{relative}: unresolved asset reference {reference!r}")
    return errors


def validate_all(root: Path) -> list[str]:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    skills, errors = discover_skills(root)
    if len(skills) != 13:
        errors.append(f"expected 13 skills, found {len(skills)}")
    if len({skill.name for skill in skills}) != len(skills):
        errors.append("skill names must be unique")
    tokens = [token for token, _, _ in _router_definitions(skills)]
    if len(tokens) != len(set(tokens)):
        errors.append("router tokens must be unique")
    for skill in skills:
        errors.extend(validate_skill(skill, version, root))
    changelog = root / "CHANGELOG.md"
    if not changelog.exists() or f"## [{version}]" not in changelog.read_text(encoding="utf-8"):
        errors.append(f"CHANGELOG.md must contain ## [{version}]")
    markdown_lines = sum(
        len(path.read_text(encoding="utf-8").splitlines())
        for path in (root / "skills" / "adw").rglob("*.md")
    )
    if markdown_lines > 2200:
        errors.append(f"shipped Markdown under skills/adw exceeds 2200 lines ({markdown_lines})")
    return errors


def build(root: Path, check: bool) -> list[str]:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    skills, errors = discover_skills(root)
    if errors:
        return errors
    try:
        outputs = generated_outputs(root, skills, version)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]
    stale: list[str] = []
    for path, expected in outputs.items():
        actual = path.read_text(encoding="utf-8")
        if actual == expected:
            continue
        if check:
            stale.append(f"generated content is stale: {path.relative_to(root)}")
        else:
            path.write_text(expected, encoding="utf-8")
    if check and stale:
        return stale
    return validate_all(root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args(argv)
    errors = build(args.root.resolve(), args.check)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Agent Skills package is current and spec-conformant")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
