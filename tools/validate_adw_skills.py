#!/usr/bin/env python3
"""Validate the ADW Hermes-compatible skill package."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
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
REQUIRED_SHARED = [
    "SOUL.md",
    "skills/adw/README.md",
    "playbooks/preview_deployments.md",
    "playbooks/pr_reviewing.md",
    "playbooks/release_promotion.md",
    "playbooks/incident_response.md",
    "playbooks/github_traceability.md",
    "playbooks/deployment_gates.md",
    "templates/implementation_plan.md",
    "templates/bugfix_plan.md",
    "templates/github_issue_feature.md",
    "templates/github_issue_bugfix.md",
    "templates/pull_request.md",
    "templates/review_report.md",
    "templates/validation_report.md",
    "templates/deployment_report.md",
    "templates/rollback_report.md",
    "adr/0001-agentic-delivery-workflow.md",
    "adr/0002-pr-as-delivery-unit.md",
    "docs/diagrams/adw-complete-workflow.puml",
    "docs/diagrams/adw-complete-workflow.svg",
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
    return errors


def main() -> int:
    errors: list[str] = []
    for name, relpath in EXPECTED.items():
        errors.extend(validate_skill(name, relpath))
    for relpath in REQUIRED_SHARED:
        if not (ROOT / relpath).exists():
            errors.append(f"missing shared artifact {relpath}")
    plan_text = (ROOT / "README.md").read_text(encoding="utf-8")
    for token in ["adw-plan-feature", "adw-do-impl", "Minimal Human Prompts", "Detailed Human Prompts"]:
        if token not in plan_text:
            errors.append(f"README missing {token}")
    if "skills/agentic-delivery" in plan_text:
        errors.append("README contains obsolete skills/agentic-delivery path")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {len(EXPECTED)} ADW skills and {len(REQUIRED_SHARED)} shared artifacts validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
