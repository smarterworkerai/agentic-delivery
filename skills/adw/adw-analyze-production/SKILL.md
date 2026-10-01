---
name: adw-analyze-production
description: >-
  Triages production feedback, logs, metrics, and incidents into continue, fix-forward, or rollback recommendations. Use when a deployment misbehaves, users report a live defect, or runtime evidence needs structured analysis.
license: MIT
compatibility: Requires git and the GitHub CLI. Deterministic steps require mise and an ADW task manifest.
metadata:
  suite: agentic-delivery
  version: "2.2.0"
  author: smarterworkerai
  requires: adw-core
  router-tokens: "analyze-production"
  hermes-tags: "adw production incident analysis"
  hermes-related-skills: "adw-core adw-rollback-deployment adw-plan"
  human-gate: "Rollback or other remote mutation"
---
# ADW Analyze Production

## Overview

Use this skill to inspect production feedback after deployment and decide whether to continue, rollback, or open follow-up work.

## When to Use

- Post-deploy smoke checks fail.
- Users report a regression.
- Monitoring, logs, or error-monitoring systems indicate errors.
- Deployment health is uncertain.

## Required Context

Load `adw-core` first. Read the project adapter from `.adw/ADW.md`, or `.hermes/ADW.md` for an existing project, and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults. Shared playbooks are named from the `adw-core` skill; this skill's own templates are under `assets/`.

## Workflow

1. Read `references/incident_response.md` from the `adw-core` skill, then identify the manifest environment, deployment, immutable source/artifact identity, time window, and reported symptom.
2. Run `mise run adw:check` and `mise run adw:describe`, then collect `mise run adw:deploy:status <environment>`, `mise run adw:health <environment>`, and `mise run adw:readiness <environment>` evidence when supported.
3. Collect additional non-sensitive project-owned logs, metrics, traces, and endpoint evidence without bypassing the canonical task results.
4. Classify severity and user impact.
5. Recommend continue, fix-forward, rollback, or deeper investigation.
6. If bugfix is needed, hand off to `adw-plan` with `type=bugfix`.
7. If rollback is needed, hand off to `adw-rollback-deployment`.

## Output

- Production feedback summary
- Evidence and impact
- Severity
- Recommended next action
- Follow-up artifact links

## Common Pitfalls

1. Pasting secrets from logs or environment output.
2. Treating one endpoint result as full health.
3. Delaying rollback recommendation for severe regressions.

## Verification Checklist

- [ ] Environment and artifact identity recorded
- [ ] Evidence is redacted and meaningful
- [ ] Severity and recommendation are explicit
- [ ] Follow-up skill/artifact is identified

## Guardrails

<!-- adw:guardrails:start -->
- Never fake or upgrade results; `skipped` and `unsupported` are not `passed`.
- Run no deterministic operation without a valid manifest; report `blocked` and do not improvise commands.
- Require explicit human approval for merge, production-class deploy, rollback, secrets, destructive changes, and history rewrites.
- Inference is never approval.
- Resolve missing parameters through `adw-core`: repository → adapter → context → ask.
- Report status, completed work, risks/blockers, and the next action.
<!-- adw:guardrails:end -->
