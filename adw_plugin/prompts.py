"""Prompt construction for ADW workflow invocations."""

from __future__ import annotations

import textwrap

from .registry import Route


def build_invocation_prompt(route: Route) -> str:
    """Build the normal agent prompt used by CLI injection and gateway rewrite."""

    payload = route.payload or "(none provided)"
    return textwrap.dedent(
        f"""
        ADW command invocation.

        Load the installed `adw-core` skill and then the installed `{route.skill}` skill before acting. Follow both skill contracts and apply the operational skill to the user payload below. If either skill is unavailable, stop and report the missing installation artifact.

        Keep the workflow PR-centric, traceable, reviewable, and deployment-safe. Resolve project-specific branch, release, deployment, validation, and administration facts through repository metadata, the machine-readable task manifest, `.hermes/ADW.md`, and any adapter-declared context layer. Do not bypass review, approval, manifest, or canonical task gates.

        Workflow: {route.workflow}
        Operational skill: {route.skill}
        User payload: {payload}

        Report current stage, completed work, risks/blockers, and next recommended action using the ADW communication contract.
        """
    ).strip()
