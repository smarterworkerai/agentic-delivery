"""Project-local ADW command router spike for Hermes.

This plugin intentionally stays thin: it parses `/adw <workflow> <payload>`
and injects the existing ADW skill content into the active Hermes turn. The
workflow rules remain in `skills/adw/*`, not in plugin code.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import textwrap
from typing import Any


WORKFLOWS: dict[str, str] = {
    "plan-feature": "adw-plan-feature",
    "plan-bugfix": "adw-plan-bugfix",
    "do-impl": "adw-do-impl",
    "do-impl-delegate": "adw-do-impl-delegate",
    "test-feature": "adw-test-feature",
    "merge-feature": "adw-merge-feature",
    "promote-release": "adw-promote-release",
    "rollback-deployment": "adw-rollback-deployment",
    "validate-regression": "adw-validate-regression",
    "create-adr": "adw-create-adr",
    "audit-dependencies": "adw-audit-dependencies",
    "analyze-production": "adw-analyze-production",
}

ALIASES: dict[str, str] = {
    "plan": "plan-feature",
    "feature": "plan-feature",
    "bug": "plan-bugfix",
    "bugfix": "plan-bugfix",
    "fix": "plan-bugfix",
    "impl": "do-impl",
    "implement": "do-impl",
    "delegate": "do-impl-delegate",
    "test": "test-feature",
    "validate": "test-feature",
    "merge": "merge-feature",
    "promote": "promote-release",
    "rollback": "rollback-deployment",
    "regress": "validate-regression",
    "regression": "validate-regression",
    "adr": "create-adr",
    "deps": "audit-dependencies",
    "dependencies": "audit-dependencies",
    "prod": "analyze-production",
    "production": "analyze-production",
}

_SKILL_DIR_BY_NAME: dict[str, str] = {
    "adw-core": "adw-core",
    "adw-plan-feature": "plan-feature",
    "adw-plan-bugfix": "plan-bugfix",
    "adw-do-impl": "do-impl",
    "adw-do-impl-delegate": "do-impl-delegate",
    "adw-test-feature": "test-feature",
    "adw-merge-feature": "merge-feature",
    "adw-promote-release": "promote-release",
    "adw-rollback-deployment": "rollback-deployment",
    "adw-validate-regression": "validate-regression",
    "adw-create-adr": "create-adr",
    "adw-audit-dependencies": "audit-dependencies",
    "adw-analyze-production": "analyze-production",
}


@dataclass(frozen=True)
class Route:
    workflow: str
    skill: str
    payload: str


def register(ctx: Any) -> None:
    """Register the `/adw` CLI command and gateway rewrite hook."""

    def handle_adw(raw_args: str) -> str:
        route = parse_route(raw_args)
        if route is None:
            return usage()
        prompt = build_invocation_prompt(route)
        injected = False
        try:
            injected = bool(ctx.inject_message(prompt, role="user"))
        except Exception:
            injected = False
        if injected:
            return f"Queued ADW workflow `{route.workflow}` with skill `{route.skill}`."
        return (
            "ADW workflow parsed, but this surface did not support direct "
            "message injection. Send the generated prompt as a normal message "
            "or use a gateway platform with the ADW rewrite hook enabled.\n\n"
            f"{prompt}"
        )

    ctx.register_command(
        "adw",
        handle_adw,
        description="Run an Agentic Delivery Workflow",
        args_hint="<workflow> <payload>",
    )
    ctx.register_hook("pre_gateway_dispatch", gateway_rewrite_hook)


def gateway_rewrite_hook(event: Any, **_: Any) -> dict[str, str] | None:
    """Rewrite valid `/adw ...` gateway commands into a normal agent prompt.

    Invalid or incomplete `/adw` commands are left for the registered plugin
    command handler so users get a direct usage/error response instead of an
    agent turn containing usage text.
    """

    args = extract_adw_args(event)
    if args is None:
        return None
    route = parse_route(args)
    if route is None:
        return None
    return {"action": "rewrite", "text": build_invocation_prompt(route)}


def extract_adw_args(event: Any) -> str | None:
    """Return raw ADW args from a gateway event, or None if it is not `/adw`."""

    try:
        command = event.get_command()
    except Exception:
        command = None
    if isinstance(command, str):
        normalized = command.lower().lstrip("/").split("@", 1)[0].replace("_", "-")
        if normalized == "adw":
            try:
                return event.get_command_args().strip()
            except Exception:
                return ""
        return None

    text = str(getattr(event, "text", "") or "").strip()
    match = re.match(r"^/adw(?:@[A-Za-z0-9_]+)?(?:\s+(.*))?$", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return (match.group(1) or "").strip()


def parse_route(raw_args: str) -> Route | None:
    args = (raw_args or "").strip()
    if not args:
        return None
    workflow_token, _, payload = args.partition(" ")
    workflow_key = workflow_token.strip().lower().replace("_", "-")
    workflow = ALIASES.get(workflow_key, workflow_key)
    skill = WORKFLOWS.get(workflow)
    if skill is None:
        return None
    return Route(workflow=workflow, skill=skill, payload=payload.strip())


def build_invocation_prompt(route: Route) -> str:
    core = read_skill("adw-core")
    workflow_skill = read_skill(route.skill)
    payload = route.payload or "(none provided)"
    return textwrap.dedent(
        f"""
        ADW command invocation.

        Execute the selected Agentic Delivery Workflow using the embedded ADW skills below.
        Keep the workflow PR-centric, traceable, reviewable, and deployment-safe.
        Do not bypass ADW gates. If a required artifact or safety decision is missing, stop and report the blocker.

        Workflow: {route.workflow}
        Operational skill: {route.skill}
        User payload: {payload}

        ## Embedded ADW Core Skill (`adw-core`)

        ```markdown
        {core}
        ```

        ## Embedded Operational Skill (`{route.skill}`)

        ```markdown
        {workflow_skill}
        ```

        ## Task

        Apply the operational skill to the user payload. Report current stage, completed work, risks/blockers, and next recommended action using the ADW communication contract.
        """
    ).strip()


def read_skill(skill_name: str) -> str:
    skill_dir = _SKILL_DIR_BY_NAME[skill_name]
    skill_path = repo_root() / "skills" / "adw" / skill_dir / "SKILL.md"
    try:
        return skill_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        return f"# {skill_name}\n\nERROR: could not read {skill_path}: {exc}"


def repo_root() -> Path:
    # __file__ = <repo>/.hermes/plugins/adw/__init__.py
    return Path(__file__).resolve().parents[3]


def usage() -> str:
    workflows = ", ".join(sorted(WORKFLOWS))
    aliases = ", ".join(f"{alias}->{target}" for alias, target in sorted(ALIASES.items()))
    return (
        "Usage: `/adw <workflow> <payload>`\n"
        f"Workflows: {workflows}\n"
        f"Aliases: {aliases}"
    )
