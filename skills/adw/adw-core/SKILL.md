---
name: adw-core
description: Use before any Agentic Delivery Workflow skill. Provides the shared delivery contract, project/context resolution rules, playbooks, templates, ADRs, and workflow diagrams used by all adw-* skills.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, core, delivery-workflow, playbooks, templates]
    related_skills: [adw-plan-feature, adw-plan-bugfix, adw-do-impl, adw-test-feature, adw-merge-feature, adw-chain, adw-self-improve]
---

# ADW Core

## Overview

`adw-core` is the package source of truth for the Agentic Delivery Workflow shared operating material. Load it before using any specific `adw-*` workflow skill so the agent has the same gates, templates, playbooks, ADR context, and workflow diagram regardless of which Hermes profile installed the skills.

The workflow skills intentionally stay small and operational. This core skill carries the shared artifacts they depend on.

## When to Use

Use this skill whenever:

- starting any Agentic Delivery Workflow cycle;
- loading `adw-plan-feature`, `adw-plan-bugfix`, `adw-do-impl`, `adw-do-impl-delegate`, `adw-test-feature`, `adw-merge-feature`, or another `adw-*` skill;
- installing the ADW skillset into a separate Hermes profile;
- checking delivery gates, templates, playbooks, ADRs, or the workflow diagram;
- validating whether an ADW skill can be used without the full repository checked out.

Do not use this skill as a replacement for the workflow-specific skills. Use it as the shared context layer, then load the operational skill for the current stage.

## Packaged Shared Artifacts

This skill owns the shared artifacts for portable installs:

- `references/playbooks/deployment_gates.md` — review, preview, merge, and deployment gates.
- `references/playbooks/github_traceability.md` — branch, issue, PR, and status-linking rules.
- `references/playbooks/incident_response.md` — production incident response flow.
- `references/playbooks/pr_reviewing.md` — review expectations and rejection handling.
- `references/playbooks/preview_deployments.md` — preview deployment safety model.
- `references/playbooks/release_promotion.md` — artifact promotion across environments.
- `templates/implementation_plan.md` — feature implementation plan template.
- `templates/bugfix_plan.md` — bugfix plan template.
- `templates/github_issue_feature.md` — feature issue template.
- `templates/github_issue_bugfix.md` — bug issue template.
- `templates/pull_request.md` — PR body template.
- `templates/review_report.md` — review report template.
- `templates/validation_report.md` — validation report template.
- `templates/deployment_report.md` — deployment report template.
- `templates/rollback_report.md` — rollback report template.
- `templates/project_adw_adapter.md` — generic project `.hermes/ADW.md` adapter template.
- `references/project_contexts.md` — generic project adapter and context helper resolution contract.
- `references/adr/0001-agentic-delivery-workflow.md` — ADW architecture decision.
- `references/adr/0002-pr-as-delivery-unit.md` — PR-as-delivery-unit decision.
- `assets/diagrams/adw-complete-workflow.puml` — workflow diagram source.
- `assets/diagrams/adw-complete-workflow.svg` — pre-rendered local SVG for GitHub display.

The root `SOUL.md` remains the agent identity file for profiles that adopt ADW. The root README points to this skill for installable shared artifacts.

## Required Usage Pattern

1. Load `adw-core` first.
2. Read the playbook/template relevant to the current stage when needed.
3. Load exactly one operational `adw-*` skill for the next workflow step.
4. Keep generated delivery artifacts linked to branch, issue, PR, preview, merge, and deployment state.
5. Report status using the ADW status/final report format.
6. For short or context-specific human commands, resolve project/environment details through a repository adapter such as `.hermes/ADW.md` and any adapter-declared context helper. Do not hard-code organization or project defaults into generic ADW skills.

Example:

```text
Use adw-core and adw-plan-feature for invoice CSV export.
```

Then later:

```text
Use adw-core and adw-do-impl for the approved invoice CSV export issue.
```

## ADW Shared Operating Contract

All ADW workflow skills belong to one PR-centric pipeline:

```text
Plan → Branch → Issue → Implementation → PR → Review → Preview → Validation → Merge → Deployment
```

Shared artifacts are packaged here, not duplicated into individual workflow skills. When a workflow skill says to use a template or playbook, resolve it from this `adw-core` package.

Use the package paths below:

- Playbooks: `skills/adw/adw-core/references/playbooks/`
- Templates: `skills/adw/adw-core/templates/`
- ADRs: `skills/adw/adw-core/references/adr/`
- Diagrams: `skills/adw/adw-core/assets/diagrams/`
- Project/context resolution: `skills/adw/adw-core/references/project_contexts.md`

When installed into a Hermes profile, these files travel with the `adw-core` skill directory.

## Parameter Resolution

Human prompts may be minimal. Resolve missing parameters in this order:

1. Inspect current repository, branch, issue, PR, and deployment metadata.
2. Check `adw-core` playbooks, templates, ADRs, and the root `SOUL.md` if available.
3. Read the repository-local project adapter when present, for example `.hermes/ADW.md`.
4. Load or inspect any context helper declared by the adapter.
5. If exactly one safe candidate exists, state the inferred assumption and ask the human to confirm before proceeding.
6. If multiple candidates exist or the consequence is unsafe, ask for explicit human input.
7. Never treat inference as approval for merge, production deployment, rollback, secret handling, destructive infrastructure changes, or history rewrite.

## Common Pitfalls

1. Installing only a workflow skill such as `adw-plan-feature` and expecting repo-root `playbooks/` or `templates/` to be available. Install/load `adw-core` with the workflow skills.
2. Treating root-level repository layout as the runtime package contract. The portable package contract is this skill directory.
3. Duplicating templates into individual workflow skills. Update the central `adw-core` artifact instead.
4. Editing a `.puml` diagram without regenerating and committing the matching `.svg`.
5. Using an operational skill without first checking review, preview, merge, or deployment gates from the shared playbooks.
6. Putting project-specific defaults into generic ADW skills instead of a project adapter or context helper.

## Verification Checklist

- [ ] `adw-core` is installed in the target Hermes profile
- [ ] The operational `adw-*` skill lists or requires `adw-core`
- [ ] Required playbooks/templates exist under this skill directory
- [ ] Project adapter template and context-resolution reference exist under `adw-core`
- [ ] The workflow diagram source and rendered SVG both exist
- [ ] Root README points to `adw-core` as the package source of truth
- [ ] `tools/validate_adw_skills.py` passes
