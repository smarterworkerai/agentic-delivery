---
name: adw-merge-feature
description: >-
  Merges a validated pull request into an explicitly approved destination and deploys only when separately requested and gated. Use after review evidence is complete or when the user asks to merge or deliver an approved PR.
license: MIT
compatibility: Requires git and the GitHub CLI. Deterministic steps require mise and an ADW task manifest.
metadata:
  suite: agentic-delivery
  version: "2.2.0"
  author: smarterworkerai
  requires: adw-core
  router-tokens: "merge-feature"
  hermes-tags: "adw merge deployment release"
  hermes-related-skills: "adw-core adw-test-feature adw-validate-regression adw-analyze-production"
  human-gate: "Merge and any deployment target"
---
# ADW Merge Feature

## Overview

Use this skill to merge a validated PR and, when requested, deploy through the adapter-declared release strategy. The repository adapter and task manifest define any branch, artifact, and environment relationship; generic ADW treats environment names as opaque.

## When to Use

- A PR passed review and preview validation.
- The human explicitly requests the merge and approves the exact destination branch.
- When deployment is separately requested, its exact opaque target and consequences are known and approved.

## Required Context

Load `adw-core` first. Read the project adapter from `.adw/ADW.md`, or `.hermes/ADW.md` for an existing project, and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults. Shared playbooks are named from the `adw-core` skill; this skill's own templates are under `assets/`.

## Workflow

1. Inspect PR state, checks, review status, linked issue, and validation report using `references/deployment_gates.md` from the `adw-core` skill and `references/release_targets.md` from the `adw-core` skill.
2. Confirm the exact destination branch and, when deployment is requested, the exact opaque environment and deployment consequence with the human. A verified upfront chain authorization explicitly covering this exact branch/environment/operation satisfies this confirmation; do not request it again merely because a previous gate passed. If the scope or target changed, stop and renew authorization.
3. Stop if PR is rejected, checks are unresolved, or target is ambiguous.
4. Merge PR using the repository's merge policy.
5. Verify destination branch SHA. If deployment was not explicitly requested, report the merge result and stop. Otherwise resolve the environment through the repository adapter and manifest, then run `mise run adw:check` and `mise run adw:describe`; do not infer an environment name.
6. Run `mise run adw:deploy:config:pull <environment>` and `mise run adw:deploy:config:plan <environment>`. Inspect the plan and, after the external deployment approval gate (which an exact, still-valid upfront chain authorization may satisfy), apply it with `mise run adw:deploy:config:apply <environment>`. Stop on unexpected secret/config drift rather than treating the earlier authorization as a waiver.
7. Deploy with `mise run adw:deploy:apply <environment>` and inspect `mise run adw:deploy:status <environment>` evidence.
8. Verify artifact/revision identity and runtime behavior with `mise run adw:health <environment>`, `mise run adw:readiness <environment>`, and `mise run adw:validate-deployment <environment>` according to manifest support. Neither optional E2E suite is automatic; require explicit per-run authorization before executing either. Persistent services require write-path validation or an explicit blocker/waiver. Load `adw-validate-regression` for deeper coverage.
9. Close the linked issue only when repository policy and verified delivery state say its acceptance criteria are complete. Otherwise add an intermediate status comment. Link the merged PR, destination revision, validation/deployment evidence when applicable, final status, and follow-up or rollback note using `references/github_traceability.md` from the `adw-core` skill and file-backed Markdown.
10. Report final delivery status with `assets/deployment_report.md` when deployment ran; otherwise report the verified merge-only result.

## Merge Gate

Before merge, confirm:

- destination branch is correct; when deployment is requested, the adapter/manifest resolve the intended target environment
- PR is not rejected
- the PR-attached required quality/proof check passed for the exact current head and tested tree; pending, failed, skipped, stale, or unrelated checks block merge
- preview validation is complete when applicable
- when deployment is requested, deployment configuration parity is proven by `adw:deploy:config:pull` and `adw:deploy:config:plan` evidence for every affected target environment
- when deployment is requested, the approved plan is applied with `adw:deploy:config:apply` before deployment
- when deployment is requested, its consequences are understood
- when deployment is requested, target-environment smoke/E2E/regression requirements are known from the project adapter or explicitly documented as unavailable
- when deployment is requested for a persistent service, write-path validation requirements are known for databases, filesystem storage, mounted volumes, queues, or external side effects

## Output

- Merge result
- Destination branch
- Deployment target or `not requested`
- Deployment status or `not requested`
- Linked issue status
- Rollback path when deployment is requested, otherwise `not applicable`

## Common Pitfalls

1. Treating inferred destination branch as approval.
2. Merging without preview validation when the app supports preview.
3. Deploying without proving immutable source and artifact identity.
4. Closing issues while deployment is still unverified.
5. Treating a green deploy plus HTTP 200 as sufficient when persistent write paths were not exercised.
6. Posting closing/deployment comments with visible backslash-n escape sequences instead of file-backed Markdown.

## Verification Checklist

- [ ] Human explicitly approved the exact merge target and, when requested, the exact deployment target
- [ ] Review and preview gates satisfied
- [ ] When deployment is requested, the configuration plan covers all changed runtime configuration for relevant target environments
- [ ] When deployment is requested, configuration pull/plan/apply evidence is recorded for all relevant environments
- [ ] Merge completed and destination SHA is recorded
- [ ] When deployment is requested, status, endpoint semantics, artifact/revision parity, and target-environment smoke/E2E/regression are verified
- [ ] When deployment is requested for a persistent service, write-path validation or a blocker/waiver is recorded
- [ ] Linked issue closed only when acceptance criteria are complete under repository policy; otherwise updated with intermediate status
- [ ] GitHub issue/PR comments use readable Markdown with real line breaks
- [ ] When deployment is requested, the rollback path is documented

## Guardrails

<!-- adw:guardrails:start -->
- Never fake or upgrade results; `skipped` and `unsupported` are not `passed`.
- Run no deterministic operation without a valid manifest; report `blocked` and do not improvise commands.
- Require explicit human approval for merge, production-class deploy, rollback, secrets, destructive changes, and history rewrites.
- Inference is never approval.
- Resolve missing parameters through `adw-core`: repository → adapter → context → ask.
- Report status, completed work, risks/blockers, and the next action.
<!-- adw:guardrails:end -->
