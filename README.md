# agentic-delivery

Agentic Delivery Workflow (ADW) defines a Hermes-compatible skillset for moving software changes safely from intent to production.

```text
Plan → Branch → Issue → Implementation → PR → Review → Preview → Validation → Merge → Deployment
```

The PR is the central delivery artifact. The workflow prioritizes traceability, reviewability, deployment safety, clear operational communication, and small reliable iterations.

Chat/status updates may be localized separately. Repository artifacts are written in English.

## Repository Layout

- `SOUL.md` — ADW agent identity, tone, boundaries, and assumption policy for profiles that adopt ADW.
- `skills/adw/adw-core/SKILL.md` — package source of truth for shared ADW context.
- `skills/adw/adw-core/references/playbooks/` — shared operational procedures referenced by workflow skills.
- `skills/adw/adw-core/templates/` — shared issue, PR, plan, report, and deployment templates.
- `skills/adw/adw-core/references/adr/` — workflow architecture decisions.
- `skills/adw/adw-core/assets/diagrams/` — PlantUML source and pre-rendered SVG diagrams.
- `skills/adw/*/SKILL.md` — Hermes-compatible operational workflow skills.
- `tools/validate_adw_skills.py` — local validation for skill frontmatter, required `adw-core` links, and expected packaged artifacts.

## Package Source of Truth

`adw-core` owns all installable shared artifacts. Do not add new shared playbooks, templates, ADRs, or diagrams at repository root. Put them under `skills/adw/adw-core/` so installing the skillset into a separate Hermes profile keeps the shared context available.

Operational skills must:

- include `adw-core` in `metadata.hermes.related_skills`;
- contain a `## Required Context` section that tells the agent to load `adw-core` first;
- resolve templates/playbooks from `adw-core`, not from repo-root directories.

## Installation

This repository is both a Hermes skill source and a Hermes plugin package.

### One-line bootstrap

After this branch is merged to the default branch:

```bash
curl -fsSL https://raw.githubusercontent.com/smarterworkerai/agentic-delivery/main/scripts/install_adw.sh | bash
```

For branch testing before merge:

```bash
curl -fsSL https://raw.githubusercontent.com/smarterworkerai/agentic-delivery/feature/initial-skills/scripts/install_adw.sh | bash
```

The installer prompts for the target Hermes profile, removes older ADW-owned skills/plugin copies, installs the current skillset and plugin, verifies the result, and prints the gateway restart command. It does not request or print secrets.

### Manual skill installation

```bash
hermes skills tap add smarterworkerai/agentic-delivery
hermes skills install smarterworkerai/agentic-delivery/skills/adw/adw-core
hermes skills install smarterworkerai/agentic-delivery/skills/adw/plan-feature
hermes skills install smarterworkerai/agentic-delivery/skills/adw/plan-bugfix
hermes skills install smarterworkerai/agentic-delivery/skills/adw/do-impl
hermes skills install smarterworkerai/agentic-delivery/skills/adw/do-impl-delegate
hermes skills install smarterworkerai/agentic-delivery/skills/adw/test-feature
hermes skills install smarterworkerai/agentic-delivery/skills/adw/merge-feature
hermes skills install smarterworkerai/agentic-delivery/skills/adw/promote-release
hermes skills install smarterworkerai/agentic-delivery/skills/adw/rollback-deployment
hermes skills install smarterworkerai/agentic-delivery/skills/adw/validate-regression
hermes skills install smarterworkerai/agentic-delivery/skills/adw/create-adr
hermes skills install smarterworkerai/agentic-delivery/skills/adw/audit-dependencies
hermes skills install smarterworkerai/agentic-delivery/skills/adw/analyze-production
```

For a named profile, insert `--profile <profile>` after `hermes`, for example:

```bash
hermes --profile delivery skills list
```

### Manual plugin installation

```bash
hermes plugins install smarterworkerai/agentic-delivery --enable
hermes gateway restart
```

For a named profile:

```bash
hermes --profile delivery plugins install smarterworkerai/agentic-delivery --enable
hermes --profile delivery gateway restart
```

The plugin is intentionally thin. It only routes `/adw <workflow> <payload>` into the ADW skills; workflow policy remains in `skills/adw/*`.

### `/adw` usage

Send `/adw` without arguments to list supported workflow arguments and aliases with short explanations.

Examples:

```text
/adw plan-feature invoice CSV export
/adw do-impl issue #42
/adw test-feature PR #42
/adw merge-feature main PR #42
```

If plugin installation is unavailable, use the skill-only fallback:

```text
Use adw-core and adw-plan-feature for invoice CSV export.
```

## Hermes-Compatible Skill Usage

Load `adw-core` together with the operational ADW skill for the current delivery stage:

- `adw-core` — shared gates, playbooks, templates, ADRs, and diagrams.
- `adw-plan-feature`
- `adw-plan-bugfix`
- `adw-do-impl`
- `adw-do-impl-delegate`
- `adw-test-feature`
- `adw-merge-feature`
- `adw-rollback-deployment`
- `adw-promote-release`
- `adw-validate-regression`
- `adw-create-adr`
- `adw-audit-dependencies`
- `adw-analyze-production`

Example:

```text
Use adw-core and adw-plan-feature for invoice CSV export.
```

When installing into a separate Hermes profile, install/copy the complete `skills/adw/` tree or at minimum install `adw-core` plus the operational skills you want to use. Installing only `adw-plan-feature` or another individual workflow skill is not enough because the shared artifacts live in `adw-core`.

## Complete Workflow Diagram

PlantUML source: [`skills/adw/adw-core/assets/diagrams/adw-complete-workflow.puml`](skills/adw/adw-core/assets/diagrams/adw-complete-workflow.puml)

![ADW complete workflow](skills/adw/adw-core/assets/diagrams/adw-complete-workflow.svg)

If the `.puml` file changes, regenerate and commit the matching `.svg`:

```bash
docker run --rm -v "$PWD":/work -w /work plantuml/plantuml -tsvg skills/adw/adw-core/assets/diagrams/adw-complete-workflow.puml
```

## Example Application: Invoice CSV Export

This example shows how a human can guide an ADW agent from plan to production using either minimal prompts or detailed prompts.

### Minimal Human Prompts

Use these when repository context is clear and the agent can infer safe candidates. The agent must confirm inferred assumptions before side effects.

1. Plan the feature:

```text
Use adw-core and adw-plan-feature for invoice CSV export.
```

2. Implement the approved plan:

```text
Use adw-core and adw-do-impl for the CSV export issue.
```

3. Validate PR and preview:

```text
Use adw-core and adw-test-feature on the CSV export PR.
```

4. Merge and deploy after validation:

```text
Use adw-core and adw-merge-feature for the validated CSV export PR.
```

5. Optional promotion when environments are separated by artifact promotion:

```text
Use adw-core and adw-promote-release to promote the validated CSV export artifact from demo to production.
```

6. Optional production analysis after deployment:

```text
Use adw-core and adw-analyze-production for the CSV export production deployment.
```

7. Emergency rollback if validation or production feedback fails:

```text
Use adw-core and adw-rollback-deployment for the CSV export production deployment.
```

### Detailed Human Prompts

Use these when you want to reduce inference and make the delivery path explicit.

1. Plan:

```text
Use adw-core and adw-plan-feature.
Repository: <owner>/<repo>
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

2. Optional architecture decision:

```text
Use adw-core and adw-create-adr if CSV export introduces a new cross-service export pattern or external storage decision. Otherwise state why ADR is not needed.
```

3. Optional dependency/security audit:

```text
Use adw-core and adw-audit-dependencies for any new CSV/export dependency before implementation. Prefer no new dependency if the platform standard library is sufficient.
```

4. Implementation:

```text
Use adw-core and adw-do-impl.
Implement only the linked invoice CSV export plan on the current feature branch.
Run relevant unit/integration checks.
Open a PR targeting main using the shared PR template from adw-core.
Do not merge or deploy.
```

5. Delegated implementation alternative:

```text
Use adw-core and adw-do-impl-delegate.
Delegate the linked invoice CSV export plan to the approved sandbox flow.
Require the worker to return a PR URL, commit SHA, changed-file summary, and test output.
Review the returned PR before reporting acceptance.
```

6. Validation:

```text
Use adw-core and adw-test-feature.
Validate the invoice CSV export PR.
Check review status, review if needed, deploy the feature branch to preview if supported, run smoke/E2E checks for CSV download, and report go/no-go.
```

7. Extra regression validation:

```text
Use adw-core and adw-validate-regression.
Target: invoice CSV export PR and preview URL.
Checks: existing invoice list behavior, filtered exports, empty exports, and unauthorized access behavior.
Attach evidence to the validation report.
```

8. Merge and production deployment:

```text
Use adw-core and adw-merge-feature.
PR: <PR URL or number>
Destination branch: main
Deployment target: production
Only proceed if review is approved, checks pass, preview validation is complete, and I explicitly confirm the production deployment.
```

9. Release promotion alternative:

```text
Use adw-core and adw-promote-release.
Promote the exact validated invoice CSV export artifact from demo to production.
Preserve artifact identity and verify production after deployment.
```

10. Production analysis:

```text
Use adw-core and adw-analyze-production.
Inspect production feedback for the invoice CSV export deployment.
Check the deployment artifact, logs, endpoint behavior, and user-visible CSV download path.
Recommend continue, fix-forward, or rollback.
```

11. Rollback:

```text
Use adw-core and adw-rollback-deployment.
Environment: production
Rollback target: last known-good release before invoice CSV export
Create a follow-up bug issue with the root-cause hypothesis and evidence.
```

## Parameter Resolution Policy

Minimal prompts are allowed. The agent may infer safe values from current repository context, branch, issue, PR, deployment metadata, and ADW artifacts, but must ask for confirmation before acting on inferred assumptions.

The agent must ask for explicit human input when ambiguity affects production, data, security, destructive actions, merge targets, rollback targets, or secret handling.

## Validation

Run:

```bash
python3 tools/validate_adw_skills.py
python3 tools/validate_adw_plugin_package.py
bash -n scripts/install_adw.sh
git diff --check
```
