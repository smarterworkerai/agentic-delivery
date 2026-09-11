---
name: adw-rollback-deployment
description: Use when restoring a failed ADW environment branch to the last known-good Git state, preserving a bugfix path for the failed state, redeploying through the normal branch-to-environment flow, and reporting impact.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, rollback, incident, deployment, branch-restore]
    related_skills: [adw-core, adw-analyze-production, adw-plan-bugfix, adw-merge-feature]
---

# ADW Rollback Deployment

## Overview

Use this skill when a deployment fails or post-deploy validation identifies a critical regression that must be restored to a last known-good state.

Rollback is a branch restore workflow, not only a runtime redeploy. The environment must continue to reflect the owning Git branch declared by the repository adapter. Restore that branch to the last known-good tree, preserve a bugfix path for the failed state, then redeploy through the normal deployment gates.

## When to Use

- Production, demo, or preview deployment fails.
- Post-deploy validation fails severely.
- Monitoring indicates a severe regression.
- The user requests rollback.
- `adw-analyze-production` recommends rollback instead of continue or fix-forward.

## Required Context

Load `adw-core` before using this skill. It contains the shared delivery gates, templates, playbooks, ADRs, and workflow diagram. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories. If the current repository contains `.hermes/ADW.md`, read it before acting and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults.

Also read `adw-core/references/playbooks/branch_environment_releases.md` and `adw-core/references/playbooks/deployment_gates.md` before changing a release branch or deployment target.

## Workflow

1. Confirm rollback target, owning branch, environment, and last known-good candidate with the human. Never infer approval for rollback.
2. Capture the failed state before changing it:
   - environment and owning branch;
   - failed branch head SHA;
   - failed deployment ID/status and image/revision identity;
   - non-sensitive logs, endpoint evidence, failed smoke/E2E/regression evidence;
   - stateful risk notes.
3. If a bug issue and bugfix branch do not already exist, create them from the failed owning branch state:
   - branch from the failed branch head, for example `bugfix/<short-failure-name>`;
   - open or update a bug issue with symptoms, failed SHA/deployment, validation evidence, and rollback plan;
   - link the bug issue and bugfix branch before restoring the environment branch.
4. Assess stateful risks: migrations, data changes, persistent volumes, external services, credentials, compose topology, and runtime env contract. Stop for explicit decision if rollback crosses a stateful boundary.
5. Restore the owning environment branch to the last known-good state. Default to a normal restore commit whose tree matches the selected good SHA; do not force-push long-lived branches unless the human explicitly confirms history rewrite. For release branches, a tree-restore commit is preferred because it is auditable and triggers the normal CI/image/deploy flow.
6. Push the restored branch and wait for the branch's CI/image publication. Verify mutable environment tags and immutable `sha-<short-sha>` tags point to the restore commit.
7. Run `mise run adw:check` and `mise run adw:describe`, then re-apply restored deployment configuration with `mise run adw:deploy:config:pull <environment>`, `mise run adw:deploy:config:plan <environment>`, and—after explicit rollback/deployment approval—`mise run adw:deploy:config:apply <environment>`.
8. Deploy the restored branch with `mise run adw:deploy:apply <environment>` and inspect `mise run adw:deploy:status <environment>` evidence.
9. Verify artifact/revision parity and runtime behavior using `mise run adw:health <environment>`, `mise run adw:readiness <environment>`, `mise run adw:e2e <environment>`, and `mise run adw:validate-deployment <environment>` according to manifest support.
10. Update the bug issue and rollback report with failed state, restored state, restore commit, deployment evidence, stateful risk decisions, and next fix-forward steps.
11. Report impact and current status using `adw-core/templates/rollback_report.md`.

## Restore Commit Pattern

Prefer a tree-restore commit for adapter-declared long-lived environment branches:

```bash
git fetch origin
git switch -C <environment-branch> origin/<environment-branch>
git read-tree --reset -u <last-known-good-sha>
git status --short
git commit -m "revert: restore <environment> to <last-known-good-sha>"
git diff --quiet HEAD <last-known-good-sha>
git push origin <environment-branch>
```

Adjust the exact command sequence for repository policy. The invariant is that the restored branch tree matches the selected good state while history records the rollback action.

## Safety Boundary

Rollback is destructive or high-impact. Always ask for explicit confirmation of environment, owning branch, and rollback target before changing branches or deployments.

Do not:

- force-push an adapter-declared long-lived environment branch without separate explicit approval;
- bypass the manifest-declared configuration tasks or expose secret values in evidence;
- discard the failed state before preserving a bug issue/branch path;
- claim rollback success before branch, image, deployment, endpoint, and revision parity are verified.

## Output

- Rolled-back environment and owning branch
- Failed branch head / artifact / deployment identity
- Last known-good SHA and restore commit SHA
- Bug issue and bugfix branch for the failed state
- Deployment target and status
- Verification result, including target smoke/E2E/regression evidence
- User impact and stateful risk notes
- Follow-up fix-forward path

## Common Pitfalls

1. Rolling back runtime tags without restoring the branch that owns the environment.
2. Restoring code without creating a bug issue/branch from the failed state first.
3. Assuming a code restore also updates provider-owned deployment configuration instead of running the canonical config pull/plan/apply tasks.
4. Force-pushing long-lived release branches when an auditable restore commit would work.
5. Rolling back code without checking data, migration, volume, or external-service compatibility.
6. Losing evidence needed for root-cause analysis.
7. Not creating follow-up work after emergency recovery.

## Verification Checklist

- [ ] Explicit rollback approval recorded for environment, branch, and target SHA
- [ ] Failed state captured with non-sensitive evidence
- [ ] Bug issue and bugfix branch exist for the failed state, or an existing equivalent is linked
- [ ] Last known-good SHA identified and stateful risks checked
- [ ] Environment branch restored with an auditable commit unless history rewrite was explicitly approved
- [ ] CI/image publication for the restore commit completed
- [ ] Deployment configuration pull/plan/apply evidence proves restored configuration without exposing secrets
- [ ] Deployment verified through status, endpoint semantics, logs or compensated evidence, and revision parity
- [ ] Target smoke/E2E/regression checks completed or blocker documented
- [ ] Bug issue and rollback report updated with failed/restored SHAs and deployment evidence

## ADW Shared Operating Contract

All ADW skills belong to one pipeline and share installable supporting material through `adw-core`.

Shared artifacts are package-owned by `adw-core`:

- Root `SOUL.md` — identity, tone, hard boundaries, and assumption policy for profiles that adopt ADW.
- `adw-core/references/playbooks/` — reusable operational procedures.
- `adw-core/templates/` — canonical issue, PR, report, and plan formats.
- `adw-core/references/adr/` — architecture decisions for the workflow itself.
- `adw-core/assets/diagrams/` — PlantUML sources and pre-rendered local SVGs.

Load `adw-core` before executing this skill. Do not copy shared playbooks/templates into individual workflow skills; update the central `adw-core` artifact instead.

## Parameter Resolution

Human prompts may be minimal. Resolve missing parameters in this order:

1. Inspect current repository, branch, issue, PR, and deployment metadata.
2. Check `adw-core` artifacts, playbooks, templates, ADRs, and the root `SOUL.md` if available.
3. If exactly one safe candidate exists, state the inferred assumption and ask the human to confirm before proceeding.
4. If multiple candidates exist or the consequence is unsafe, ask for explicit human input.
5. Never treat inference as approval for merge, production deployment, rollback, secret handling, destructive infrastructure changes, or history rewrite.

## Standard Status Report

```markdown
### Status
<current stage>

### Completed
- <artifact/result>

### Risks / Blockers
- <risk or "None">

### Next
- <recommended next action>
```
