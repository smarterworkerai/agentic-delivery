---
name: adw-test-feature
description: >-
  Reviews and validates a pull request with local quality, preview deployment, smoke checks, and optional E2E evidence. Use before merge or when asked to test a feature branch, PR, or preview environment.
license: MIT
compatibility: Requires git and the GitHub CLI. Deterministic steps require mise and an ADW task manifest.
metadata:
  suite: agentic-delivery
  version: "2.2.0"
  author: smarterworkerai
  requires: adw-core
  router-tokens: "test-feature"
  hermes-tags: "adw review preview validation"
  hermes-related-skills: "adw-core adw-do-impl adw-merge-feature adw-validate-regression"
  human-gate: "Preview deployment and each E2E run"
---
# ADW Test Feature

## Overview

Use this skill after a PR exists and before merge. It enforces review and preview gates.

## When to Use

- A feature or bugfix PR needs validation.
- Preview deployment is required before merge.
- The PR review status is unknown.

## Required Context

Load `adw-core` first. Read the project adapter from `.adw/ADW.md`, or `.hermes/ADW.md` for an existing project, and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults. Shared playbooks are named from the `adw-core` skill; this skill's own templates are under `assets/`.

## Workflow

1. Inspect PR state, branch, target branch, linked issue, and checks.
2. Check whether a review already exists.
3. Review the PR if needed using `references/pr_reviewing.md` from the `adw-core` skill, then apply `references/deployment_gates.md` from the `adw-core` skill and `references/preview_deployments.md` from the `adw-core` skill to any preview work.
4. Stop if rejected.
5. Resolve the preview environment from the manifest, then run `mise run adw:check` and `mise run adw:describe`. Stop if the required deployment capabilities are unsupported or the environment is not in their declared scope.
6. When deployment configuration changes, run `mise run adw:deploy:config:pull <environment>` and `mise run adw:deploy:config:plan <environment>`. Inspect the plan; after the external ADW approval gate is satisfied, apply it with `mise run adw:deploy:config:apply <environment>`.
7. Deploy with `mise run adw:deploy:apply <environment>` and inspect `mise run adw:deploy:status <environment>` evidence.
8. Validate with `mise run adw:health <environment>`, `mise run adw:readiness <environment>`, and `mise run adw:validate-deployment <environment>` according to the manifest. The fast/full E2E suites are separate optional remote-write runs requiring per-run approval; non-execution needs no waiver. Invoke `adw-validate-regression` for deeper coverage. Persistent services require a write-path smoke or a documented blocker/waiver.
9. Write validation report using `assets/validation_report.md` and the Markdown/newline hygiene rules from `references/github_traceability.md` from the `adw-core` skill.
10. Report go/no-go recommendation.

## Review Gate

Do not deploy or merge a rejected PR. Missing required review must be resolved before preview validation proceeds.

## Preview Gate

Disposable preview deployments are for validation only. Do not use preview evidence as production approval.

## Output

- PR review status
- Preview URL or reason preview is not applicable
- Artifact identity and runtime revision/digest parity when preview is deployed
- Test result
- Write-path smoke result for persistent services, or documented blocker/waiver
- Manual QA notes if applicable
- Go/no-go recommendation

## Common Pitfalls

1. Treating green CI as a human/code review.
2. Deploying rejected work to preview.
3. Reporting HTTP 200 as success without validating response semantics.
4. Skipping manual QA notes for user-visible changes.
5. Posting structured PR comments with visible backslash-n escape sequences instead of real Markdown line breaks.

## Verification Checklist

- [ ] PR state and checks inspected
- [ ] Review status known
- [ ] Rejection blocks further workflow
- [ ] Preview URL and deployment status recorded when applicable
- [ ] Artifact identity and runtime revision/digest parity recorded when applicable
- [ ] Smoke/manual validation result documented; optional E2E only if explicitly run, including write-path checks for persistent services
- [ ] Validation report/comment follows GitHub traceability Markdown hygiene

## Guardrails

<!-- adw:guardrails:start -->
- Never fake or upgrade results; `skipped` and `unsupported` are not `passed`.
- Run no deterministic operation without a valid manifest; report `blocked` and do not improvise commands.
- Require explicit human approval for merge, production-class deploy, rollback, secrets, destructive changes, and history rewrites.
- Inference is never approval.
- Resolve missing parameters through `adw-core`: repository → adapter → context → ask.
- Report status, completed work, risks/blockers, and the next action.
<!-- adw:guardrails:end -->
