"""Workflow registry and parser for the ADW `/adw` command."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowDefinition:
    """A routable ADW workflow command."""

    token: str
    skill: str
    skill_dir: str
    description: str


@dataclass(frozen=True)
class Route:
    """Parsed `/adw` command route."""

    workflow: str
    skill: str
    payload: str


WORKFLOW_DEFINITIONS: tuple[WorkflowDefinition, ...] = (
    WorkflowDefinition("plan-feature", "adw-plan-feature", "plan-feature", "Plan a new feature: branch, implementation plan, GitHub issue, and acceptance criteria."),
    WorkflowDefinition("plan-bugfix", "adw-plan-bugfix", "plan-bugfix", "Plan a bugfix: symptom analysis, suspected root cause, branch, issue, and verification strategy."),
    WorkflowDefinition("do-impl", "adw-do-impl", "do-impl", "Implement the current approved plan directly, run checks, commit, and open a PR."),
    WorkflowDefinition("do-impl-delegate", "adw-do-impl-delegate", "do-impl-delegate", "Delegate implementation to the approved sandbox/remote agent flow, then inspect and review the returned PR."),
    WorkflowDefinition("test-feature", "adw-test-feature", "test-feature", "Review and validate a PR, including preview deployment and smoke/E2E checks when available."),
    WorkflowDefinition("merge-feature", "adw-merge-feature", "merge-feature", "Merge a validated PR into the destination branch and trigger/report the matching deployment."),
    WorkflowDefinition("rollback-deployment", "adw-rollback-deployment", "rollback-deployment", "Rollback a failed deployment to a known-good version and report impact/follow-up."),
    WorkflowDefinition("validate-regression", "adw-validate-regression", "validate-regression", "Run targeted regression checks against a PR, branch, deployment, or release candidate."),
    WorkflowDefinition("create-adr", "adw-create-adr", "create-adr", "Create an Architecture Decision Record for architectural or security-boundary changes."),
    WorkflowDefinition("audit-dependencies", "adw-audit-dependencies", "audit-dependencies", "Audit dependency changes for security, maintenance, and release risk."),
    WorkflowDefinition("analyze-production", "adw-analyze-production", "analyze-production", "Inspect production feedback, logs, metrics, or user reports and recommend continue/fix-forward/rollback."),
    WorkflowDefinition("chain", "adw-chain", "chain", "Coordinate a confirmed multi-stage ADW sequence such as plan, implement, test, merge, or deploy."),
    WorkflowDefinition("self-improve", "adw-self-improve", "self-improve", "Persist an explicitly requested ADW/context/project-adapter improvement through a confirm-first PR-based flow."),
)

WORKFLOWS: dict[str, str] = {definition.token: definition.skill for definition in WORKFLOW_DEFINITIONS}
_SKILL_DIR_BY_NAME: dict[str, str] = {"adw-core": "adw-core"} | {
    definition.skill: definition.skill_dir for definition in WORKFLOW_DEFINITIONS
}
_DESCRIPTION_BY_WORKFLOW: dict[str, str] = {
    definition.token: definition.description for definition in WORKFLOW_DEFINITIONS
}

def normalize_token(token: str) -> str:
    """Normalize a workflow token from a slash command."""

    return (token or "").strip().lower().replace("_", "-")


def canonical_workflow(token: str) -> str | None:
    """Resolve a workflow token to a canonical workflow."""

    workflow = normalize_token(token)
    if workflow not in WORKFLOWS:
        return None
    return workflow


def parse_route(raw_args: str) -> Route | None:
    """Parse raw `/adw` arguments into a workflow route."""

    args = (raw_args or "").strip()
    if not args:
        return None
    workflow_token, _, payload = args.partition(" ")
    workflow = canonical_workflow(workflow_token)
    if workflow is None:
        return None
    return Route(workflow=workflow, skill=WORKFLOWS[workflow], payload=payload.strip())


def skill_dir_for_name(skill_name: str) -> str:
    """Return the repository skill directory for an installed ADW skill name."""

    return _SKILL_DIR_BY_NAME[skill_name]


def workflow_description(workflow: str) -> str:
    """Return the short help text for a canonical workflow."""

    return _DESCRIPTION_BY_WORKFLOW[workflow]
