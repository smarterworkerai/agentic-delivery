#!/usr/bin/env python3
"""Validate the Agent Skills distribution and Hermes installer invariants."""
from __future__ import annotations

import ast
from pathlib import Path
import re
import sys

import build_skills


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "skills/adw/adw-core/assets/mise/v2/contract.md",
    "skills/adw/adw-core/assets/mise/v2/generation-guide.md",
    "skills/adw/adw-core/assets/mise/v2/adw_contract.py",
    "skills/adw/adw-core/assets/mise/v2/tasks.toml",
    "skills/adw/adw-core/assets/mise/v2/schemas/adw-task-manifest.schema.json",
    "skills/adw/adw-core/assets/mise/v2/schemas/adw-task-evidence.schema.json",
    "skills/adw/adw-core/assets/project_adw_adapter.md",
    "skills/adw/adw-core/references/deployment_gates.md",
    "skills/adw/adw-core/references/github_traceability.md",
    "skills/adw/adw-core/references/incident_response.md",
    "skills/adw/adw-core/references/pr_reviewing.md",
    "skills/adw/adw-core/references/preview_deployments.md",
    "skills/adw/adw-core/references/release_targets.md",
    "integrations/hermes/plugin.yaml",
    "integrations/hermes/__init__.py",
    "integrations/hermes/SOUL.md",
    "integrations/hermes/install_adw.sh",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    "docs/architecture.md",
    "docs/releasing.md",
    "README.md",
    "CHANGELOG.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
)


def extract_bash_array(text: str, name: str) -> list[str]:
    match = re.search(rf"^{name}=\(\n(?P<body>.*?)^\)", text, re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"missing bash array {name}")
    values = []
    for line in match.group("body").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            values.append(ast.literal_eval(line))
    return values


def validate_installer(skill_names: set[str]) -> list[str]:
    errors: list[str] = []
    installer = ROOT / "integrations/hermes/install_adw.sh"
    text = installer.read_text(encoding="utf-8")
    for invariant in (
        '[[ "${ADW_REF}" =~ ^[0-9a-f]{40}$ ]]',
        '[[ "${ADW_ARCHIVE_SHA256}" =~ ^[0-9a-f]{64}$ ]]',
        '[[ "${ACTUAL_ARCHIVE_SHA256}" == "${ADW_ARCHIVE_SHA256}" ]]',
        'OWNER_MARKER=".agentic-delivery-owner"',
        '[[ "${HERMES_HOME_DIR}" != "/" ]]',
        'plugins doctor "${SOURCE_DIR}" --ci',
        'plugins doctor "${STAGED_PLUGIN}" --ci',
        'plugins doctor "${PLUGIN_TARGET}" --ci',
        "rollback_activation",
        "LEGACY_INSTALLED_SKILL_NAMES",
        'POLICIES+=("owned-remove")',
    ):
        if invariant not in text:
            errors.append(f"integrations/hermes/install_adw.sh: missing safety invariant {invariant}")
    try:
        installed = set(extract_bash_array(text, "ADW_SKILLS"))
    except (ValueError, SyntaxError) as exc:
        return [f"integrations/hermes/install_adw.sh: {exc}"]
    if installed != skill_names:
        errors.append(f"installer skills mismatch: expected {sorted(skill_names)}, got {sorted(installed)}")
    if "skills/_shared" in text or '"_shared"' in text:
        errors.append("installer must exclude skills/_shared")
    return errors


def main() -> int:
    errors = build_skills.validate_all(ROOT)
    skills, discovery_errors = build_skills.discover_skills(ROOT)
    errors.extend(discovery_errors)
    names = {skill.name for skill in skills}
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required artifact {relative}")
    for obsolete in (
        "skills/adw/README.md",
        "skills/adw/adw-core/templates",
        "skills/adw/adw-core/assets/diagrams",
        "skills/adw/plan-feature",
        "skills/adw/plan-bugfix",
    ):
        if (ROOT / obsolete).exists():
            errors.append(f"obsolete artifact remains: {obsolete}")
    errors.extend(validate_installer(names))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {len(skills)} spec-conformant ADW skills and integration artifacts validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
