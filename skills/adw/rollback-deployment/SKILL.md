---
name: adw-rollback-deployment
description: Use when restoring a failed deployment through policy.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, rollback, incident, deployment, recovery]
    related_skills: [adw-core, adw-analyze-production, adw-plan-bugfix, adw-merge-feature]
---

# ADW Rollback Deployment

## Overview

Restore a failed deployment to an explicitly approved last-known-good state. The repository adapter owns the rollback strategy; generic ADW does not assume branch restoration, artifact format, provider, or environment name.

## When to Use

- A deployment or post-deployment validation fails severely.
- Monitoring shows a regression that cannot safely wait for fix-forward.
- The human explicitly requests rollback.
- `adw-analyze-production` recommends rollback.

## Required Context

Load `adw-core` before using this skill. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories. Read repository-local `.hermes/ADW.md`, any adapter-declared context helper, `adw-core/references/playbooks/release_targets.md`, and `adw-core/references/playbooks/deployment_gates.md` before changing source, configuration, or runtime state.

## Workflow

1. Identify the failed environment, failed source revision, deployment identity, and last-known-good candidate from live evidence.
2. Ask for explicit approval of the exact environment, restore identity, and adapter-declared rollback strategy. Stop if any target is ambiguous.
3. Preserve the failed state before mutation:
   - source revision and PR/branch when applicable;
   - deployment and immutable artifact identity when applicable;
   - canonical status/health/readiness/E2E evidence;
   - non-sensitive logs and stateful-risk notes.
4. Create or link a bug issue and fix-forward path without assuming a branch naming convention.
5. Assess migrations, data changes, persistent storage, external services, credentials, and configuration compatibility. Stop for a separate decision when recovery crosses a stateful or destructive boundary.
6. Prepare the approved last-known-good state using the adapter-declared strategy. This may be an auditable Git revert/restore, immutable artifact selection, configuration restoration, or a documented combination. Never rewrite history without separate approval.
7. Run `mise run adw:check` and `mise run adw:describe`. Stop on manifest, provenance, or capability errors.
8. Run `mise run adw:deploy:config:pull <environment>` and `mise run adw:deploy:config:plan <environment>`. Inspect the plan, then invoke `mise run adw:deploy:config:apply <environment>` only under the approved rollback/deployment gate.
9. Deploy with `mise run adw:deploy:apply <environment>` and inspect `mise run adw:deploy:status <environment>` evidence.
10. Verify the intended restored identity and runtime behavior with manifest-supported `adw:health`, `adw:readiness`, `adw:e2e`, and `adw:validate-deployment` tasks.
11. Update the bug issue and `adw-core/templates/rollback_report.md` with failed/restored identities, stateful-risk decisions, canonical evidence, impact, and fix-forward work.

## Safety Boundary

Rollback is high-impact. Approval must identify the exact target environment and restore state. A previously approved target does not authorize a different environment, revision, artifact, configuration, history rewrite, or destructive data action.

Do not:

- infer an environment, branch, artifact, or provider operation;
- bypass the manifest-declared configuration and deployment tasks;
- expose secrets or private infrastructure details in evidence;
- discard the failed state before preserving a fix-forward path;
- equate command completion with restored runtime identity;
- claim success before source, configuration, deployment status, and runtime validation agree.

## Output

- Target environment and non-secret deployment reference
- Failed source/deployment/artifact identity
- Approved last-known-good identity and restore strategy
- Bug issue and fix-forward path
- Configuration plan/apply evidence
- Deployment status and restored runtime identity
- Health/readiness/E2E/deployment-validation result
- User impact, stateful risks, and remaining blockers

## Common Pitfalls

1. Assuming every project rolls back by moving a release branch.
2. Reusing a mutable artifact name without proving immutable identity.
3. Restoring code while leaving failed deployment configuration active.
4. Treating liveness as full recovery for a persistent service.
5. Skipping migration or data compatibility analysis.
6. Losing failed-state evidence needed for root-cause analysis.

## Verification Checklist

- [ ] Exact rollback environment, restore identity, and strategy explicitly approved
- [ ] Failed state preserved with non-sensitive evidence
- [ ] Bug issue and fix-forward path linked
- [ ] Stateful and destructive risks resolved explicitly
- [ ] `adw:check` and `adw:describe` passed for the restored source state
- [ ] Configuration pull/plan/apply evidence matches the approved restore state
- [ ] Deployment status proves the intended restored identity
- [ ] Health, readiness, E2E, and deployment validation completed as supported
- [ ] Rollback report records impact, evidence, blockers, and follow-up

## ADW Shared Operating Contract

All ADW skills belong to one PR-centric pipeline. Planning, implementation, review, approval, and rollback decisions remain agentic workflow policy. Deterministic project operations use the manifest-declared canonical `adw:*` task ABI packaged by `adw-core`.

Load `adw-core` before executing this skill. Do not copy shared playbooks/templates into individual workflow skills; update the central `adw-core` artifact instead.

## Parameter Resolution

1. Inspect repository, issue, PR, manifest, adapter, and live deployment metadata.
2. Load any adapter-declared context helper.
3. Ask for the exact rollback target and restore identity even when one candidate appears likely.
4. Never infer approval for rollback, production deployment, secret handling, destructive infrastructure changes, data mutation, or history rewrite.

## Standard Status Report

```markdown
### Status
<current rollback stage>

### Completed
- <verified artifact/result>

### Risks / Blockers
- <risk or "None">

### Next
- <recommended approved action>
```
