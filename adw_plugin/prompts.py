"""Prompt construction for ADW workflow invocations."""

from __future__ import annotations

from pathlib import Path
import textwrap

from .registry import Route, skill_dir_for_name


def build_invocation_prompt(route: Route) -> str:
    """Build the normal agent prompt used by CLI injection and gateway rewrite.

    The plugin remains a router. It embeds local skill content when available so
    an installed root plugin package can route without relying on slash-command
    chaining. If skill files are unavailable, the prompt still names the required
    installed skills and tells the agent to load them.
    """

    core = read_skill("adw-core")
    workflow_skill = read_skill(route.skill)
    payload = route.payload or "(none provided)"
    return textwrap.dedent(
        f"""
        ADW command invocation.

        Execute the selected Agentic Delivery Workflow using the ADW skills below.
        Keep the workflow PR-centric, traceable, reviewable, and deployment-safe.
        Do not bypass ADW gates. If a required artifact or safety decision is missing, stop and report the blocker.

        Workflow: {route.workflow}
        Operational skill: {route.skill}
        User payload: {payload}

        ## Required ADW Skills

        - adw-core
        - {route.skill}

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
    """Read packaged skill content for prompt embedding, with a safe fallback."""

    skill_dir = skill_dir_for_name(skill_name)
    skill_path = repo_root() / "skills" / "adw" / skill_dir / "SKILL.md"
    try:
        return skill_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        return textwrap.dedent(
            f"""
            # {skill_name}

            Packaged skill content could not be read from `{skill_path}`: {exc}

            Fallback instruction: load installed skills `adw-core` and `{skill_name}` before acting. If either skill is unavailable, stop and report the missing installation artifact.
            """
        ).strip()


def repo_root() -> Path:
    """Return the root of the installed combined ADW repository/plugin package."""

    return Path(__file__).resolve().parents[1]
