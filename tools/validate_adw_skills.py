#!/usr/bin/env python3
"""Validate the ADW Hermes-compatible skill package."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "adw-core": "skills/adw/adw-core/SKILL.md",
    "adw-plan-feature": "skills/adw/plan-feature/SKILL.md",
    "adw-plan-bugfix": "skills/adw/plan-bugfix/SKILL.md",
    "adw-do-impl": "skills/adw/do-impl/SKILL.md",
    "adw-do-impl-delegate": "skills/adw/do-impl-delegate/SKILL.md",
    "adw-test-feature": "skills/adw/test-feature/SKILL.md",
    "adw-merge-feature": "skills/adw/merge-feature/SKILL.md",
    "adw-rollback-deployment": "skills/adw/rollback-deployment/SKILL.md",
    "adw-promote-release": "skills/adw/promote-release/SKILL.md",
    "adw-validate-regression": "skills/adw/validate-regression/SKILL.md",
    "adw-create-adr": "skills/adw/create-adr/SKILL.md",
    "adw-audit-dependencies": "skills/adw/audit-dependencies/SKILL.md",
    "adw-analyze-production": "skills/adw/analyze-production/SKILL.md",
}
CORE_SHARED = [
    "skills/adw/adw-core/references/playbooks/preview_deployments.md",
    "skills/adw/adw-core/references/playbooks/pr_reviewing.md",
    "skills/adw/adw-core/references/playbooks/release_promotion.md",
    "skills/adw/adw-core/references/playbooks/incident_response.md",
    "skills/adw/adw-core/references/playbooks/github_traceability.md",
    "skills/adw/adw-core/references/playbooks/deployment_gates.md",
    "skills/adw/adw-core/templates/implementation_plan.md",
    "skills/adw/adw-core/templates/bugfix_plan.md",
    "skills/adw/adw-core/templates/github_issue_feature.md",
    "skills/adw/adw-core/templates/github_issue_bugfix.md",
    "skills/adw/adw-core/templates/pull_request.md",
    "skills/adw/adw-core/templates/review_report.md",
    "skills/adw/adw-core/templates/validation_report.md",
    "skills/adw/adw-core/templates/deployment_report.md",
    "skills/adw/adw-core/templates/rollback_report.md",
    "skills/adw/adw-core/references/adr/0001-agentic-delivery-workflow.md",
    "skills/adw/adw-core/references/adr/0002-pr-as-delivery-unit.md",
    "skills/adw/adw-core/assets/diagrams/adw-complete-workflow.puml",
    "skills/adw/adw-core/assets/diagrams/adw-complete-workflow.svg",
]
REQUIRED_ROOT = [
    "SOUL.md",
    "skills/adw/README.md",
]
OBSOLETE_ROOT_SHARED_DIRS = [
    "playbooks",
    "templates",
    "adr",
    "docs/diagrams",
]


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("frontmatter must start at byte 0")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("frontmatter closing delimiter missing")
    raw = text[4:end]
    body = text[end + 5 :].strip()
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.startswith("  ") or line.startswith("    "):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data, body


def validate_skill(name: str, relpath: str) -> list[str]:
    path = ROOT / relpath
    errors: list[str] = []
    if not path.exists():
        return [f"missing {relpath}"]
    text = path.read_text(encoding="utf-8")
    try:
        meta, body = parse_frontmatter(text)
    except ValueError as exc:
        return [f"{relpath}: {exc}"]
    if meta.get("name") != name:
        errors.append(f"{relpath}: expected name {name!r}, got {meta.get('name')!r}")
    desc = meta.get("description", "")
    if not desc:
        errors.append(f"{relpath}: missing description")
    if len(desc) > 1024:
        errors.append(f"{relpath}: description exceeds 1024 characters")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name):
        errors.append(f"{relpath}: invalid skill name format")
    if not body:
        errors.append(f"{relpath}: empty body")
    for required in ["## Overview", "## When to Use", "## Common Pitfalls", "## Verification Checklist", "## ADW Shared Operating Contract"]:
        if required not in text:
            errors.append(f"{relpath}: missing {required}")
    if name != "adw-core":
        if "## Required Context" not in text:
            errors.append(f"{relpath}: missing ## Required Context")
        if "related_skills: [adw-core" not in text and "adw-core" not in text.split("---", 2)[1]:
            errors.append(f"{relpath}: missing adw-core in frontmatter related_skills")
        if "repo-root `playbooks/`, `templates/`, `adr/`, or `docs/`" not in text:
            errors.append(f"{relpath}: missing portable install warning")
    return errors


def main() -> int:
    errors: list[str] = []
    for name, relpath in EXPECTED.items():
        errors.extend(validate_skill(name, relpath))
    for relpath in REQUIRED_ROOT + CORE_SHARED:
        if not (ROOT / relpath).exists():
            errors.append(f"missing required artifact {relpath}")
    for relpath in OBSOLETE_ROOT_SHARED_DIRS:
        if (ROOT / relpath).exists():
            errors.append(f"obsolete root shared artifact directory still exists: {relpath}")
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    for token in [
        "adw-core",
        "Package Source of Truth",
        "skills/adw/adw-core/templates/",
        "Minimal Human Prompts",
        "Detailed Human Prompts",
    ]:
        if token not in readme_text:
            errors.append(f"README missing {token}")
    for obsolete in ["docs/diagrams/adw-complete-workflow", "playbooks/ —", "templates/ —", "adr/ —", "skills/agentic-delivery"]:
        if obsolete in readme_text:
            errors.append(f"README contains obsolete reference: {obsolete}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {len(EXPECTED)} ADW skills and {len(CORE_SHARED)} adw-core shared artifacts validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
