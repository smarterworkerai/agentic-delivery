# Agentic Delivery Workflow Skillset Plan

## Goal

Define a complete, Hermes-compatible Agentic Delivery Workflow (ADW) skillset that lets an agent move software changes through a safe, traceable delivery lifecycle:

```text
Plan → Branch → Issue → Implementation → PR → Review → Preview → Validation → Merge → Deployment
```

The package must work when installed into a separate Hermes profile. Therefore shared operating material is packaged inside `adw-core`, not kept as loose repository-root artifacts.

## Package Architecture

### Identity

- `SOUL.md`
  - Agent identity and tone.
  - Hard delivery boundaries.
  - Assumption and ambiguity policy.
  - Intended to be copied or adopted as the profile-level `SOUL.md` for an ADW-specialized Hermes profile.

### Core Shared Context

- `skills/adw/adw-core/SKILL.md`
  - Must be loaded before any operational `adw-*` skill.
  - Provides the shared delivery contract, playbooks, templates, ADRs, and workflow diagram.
  - Is the package source of truth for installable shared artifacts.

Shared files live under `adw-core`:

```text
skills/adw/adw-core/
  SKILL.md
  references/
    playbooks/
      deployment_gates.md
      github_traceability.md
      incident_response.md
      pr_reviewing.md
      preview_deployments.md
      release_promotion.md
    adr/
      0001-agentic-delivery-workflow.md
      0002-pr-as-delivery-unit.md
  templates/
    implementation_plan.md
    bugfix_plan.md
    github_issue_feature.md
    github_issue_bugfix.md
    pull_request.md
    review_report.md
    validation_report.md
    deployment_report.md
    rollback_report.md
  assets/
    diagrams/
      adw-complete-workflow.puml
      adw-complete-workflow.svg
```

### Operational Skills

Each operational skill lives under `skills/adw/<skill-name>/SKILL.md`, includes `adw-core` in `metadata.hermes.related_skills`, and contains a `## Required Context` section instructing the agent to load `adw-core` first.

Required operational skills:

- `adw-plan-feature`
  - Create or confirm feature branch, implementation plan, GitHub issue, acceptance criteria, and traceability.
- `adw-plan-bugfix`
  - Analyze symptoms, suspected root cause, bugfix branch, bug issue, verification strategy, and acceptance criteria.
- `adw-do-impl`
  - Implement a planned change directly, keep scope tight, run checks, commit, and open a PR.
- `adw-do-impl-delegate`
  - Package context for sandbox/remote delegation, inspect returned PR, perform implicit review, and report acceptance/rejection.
- `adw-test-feature`
  - Check PR state, enforce review gate, deploy preview when supported, run smoke/E2E/manual validation, and report go/no-go.
- `adw-merge-feature`
  - Verify review/check/preview gates, merge a validated PR, deploy the destination branch, and report final delivery state.
- `adw-rollback-deployment`
  - Identify last known-good version, roll back safely, verify health, report impact, and create follow-up bug work if needed.
- `adw-promote-release`
  - Promote an already validated artifact across environments while preserving artifact identity and verification evidence.
- `adw-validate-regression`
  - Run targeted or broad regression checks against a PR, preview, branch, or deployment.
- `adw-create-adr`
  - Create workflow/project ADRs when architectural direction changes.
- `adw-audit-dependencies`
  - Audit dependency/build-tool/security risk before or during delivery.
- `adw-analyze-production`
  - Inspect production feedback after deployment and recommend continue, fix-forward, rollback, or incident response.

## Packaging Rules

1. `adw-core` is the source of truth for shared artifacts.
2. Do not create new repo-root `playbooks/`, `templates/`, `adr/`, or `docs/diagrams/` directories for ADW package content.
3. Root `README.md` must point to `adw-core` paths.
4. Operational skills must not duplicate shared artifacts.
5. Any new shared artifact must be placed under one of:
   - `skills/adw/adw-core/references/playbooks/`
   - `skills/adw/adw-core/templates/`
   - `skills/adw/adw-core/references/adr/`
   - `skills/adw/adw-core/assets/diagrams/`
6. If the PlantUML source changes, regenerate the matching SVG and commit both.

## Validation

The repository includes:

```text
tools/validate_adw_skills.py
```

The validator must check:

- all expected ADW skills exist;
- each `SKILL.md` has valid Hermes frontmatter;
- each skill has required sections;
- each operational skill references/requires `adw-core`;
- all packaged shared artifacts exist under `adw-core`;
- obsolete repo-root shared artifact directories are absent;
- README points to `adw-core` as package source of truth.

Run before commit:

```bash
python3 tools/validate_adw_skills.py
git diff --check
```

## Install / Profile Usage

When installing into a separate Hermes profile:

1. Install or copy the full `skills/adw/` tree into the target profile's `skills/` directory.
2. Adopt root `SOUL.md` as the profile-level ADW identity if the profile should behave as a dedicated delivery agent.
3. Load `adw-core` together with the operational skill for the current workflow stage.

Minimal prompt pattern:

```text
Use adw-core and adw-plan-feature for <feature>.
```

Detailed prompt pattern:

```text
Use adw-core and adw-plan-feature.
Repository: <owner>/<repo>
Base branch: main
Feature: <feature name>
Scope: <included scope>
Out of scope: <excluded scope>
Acceptance criteria:
- <criterion>
Create a feature branch and GitHub issue, then stop before implementation.
```

## Example Application: Invoice CSV Export

### 1. Plan

```text
Use adw-core and adw-plan-feature.
Repository: acme/invoicing
Base branch: main
Feature: invoice CSV export
Scope: add CSV export for invoice list using existing filters.
Out of scope: PDF export, invoice editing, permission model changes.
Acceptance criteria:
- Users can download filtered invoice lists as CSV.
- CSV columns are documented and stable.
- Existing invoice list behavior is unchanged.
- Tests cover export success and empty result behavior.
Create a feature branch and GitHub issue, then stop before implementation.
```

Expected artifacts:

- Branch: `feature/invoice-csv-export`
- Issue: GitHub issue labeled `enhancement`
- Plan: based on `adw-core/templates/implementation_plan.md`

### 2. Implement

```text
Use adw-core and adw-do-impl.
Implement only the linked invoice CSV export plan on the current feature branch.
Run relevant unit/integration checks.
Open a PR targeting main using the shared PR template from adw-core.
Do not merge or deploy.
```

Expected artifacts:

- Commit(s) on feature branch
- PR linked to issue
- Test/check evidence
- Remaining risks documented

### 3. Validate

```text
Use adw-core and adw-test-feature.
Validate the invoice CSV export PR.
Check review status, review if needed, deploy the feature branch to preview if supported, run smoke/E2E checks for CSV download, and report go/no-go.
```

Expected artifacts:

- Review status
- Preview URL if supported
- Validation report based on `adw-core/templates/validation_report.md`
- Go/no-go recommendation

### 4. Merge and Deploy

```text
Use adw-core and adw-merge-feature.
PR: <PR URL or number>
Destination branch: main
Deployment target: production
Only proceed if review is approved, checks pass, preview validation is complete, and I explicitly confirm the production deployment.
```

Expected artifacts:

- Merge result
- Destination branch
- Deployment status
- Deployment report based on `adw-core/templates/deployment_report.md`

### 5. Analyze or Roll Back if Needed

```text
Use adw-core and adw-analyze-production for the invoice CSV export production deployment.
```

If production validation fails:

```text
Use adw-core and adw-rollback-deployment.
Environment: production
Rollback target: last known-good release before invoice CSV export
Create a follow-up bug issue with the root-cause hypothesis and evidence.
```
