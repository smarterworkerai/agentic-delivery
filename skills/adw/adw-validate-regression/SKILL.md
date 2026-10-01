---
name: adw-validate-regression
description: >-
  Runs targeted or broad regression checks against a pull request, branch, deployment, or release candidate and records honest evidence. Use for risk-based validation, regression investigation, or pre-release confidence.
license: MIT
compatibility: Requires git and the GitHub CLI. Deterministic steps require mise and an ADW task manifest.
metadata:
  suite: agentic-delivery
  version: "2.2.0"
  author: smarterworkerai
  requires: adw-core
  router-tokens: "validate-regression"
  hermes-tags: "adw testing regression validation"
  hermes-related-skills: "adw-core adw-test-feature"
  human-gate: "Any remote-write or billable test"
---
# ADW Validate Regression

## Overview

Use this skill to run regression checks beyond the basic PR validation flow.

## When to Use

- A change touches critical behavior.
- A bugfix needs regression proof.
- A release candidate needs broader smoke/API/E2E validation.

## Required Context

Load `adw-core` first. Read the project adapter from `.adw/ADW.md`, or `.hermes/ADW.md` for an existing project, and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults. Shared playbooks are named from the `adw-core` skill; this skill's own templates are under `assets/`.

## Workflow

1. Identify validation target: PR, branch, manifest environment, or artifact.
2. Run `mise run adw:check` and `mise run adw:describe`, then select only manifest-supported canonical capabilities.
3. For local regression, run the needed `adw:test:unit`, `adw:test:integration:fast`, `adw:lint`, or `adw:static-analysis` tasks; use `mise run adw:verify:full` for broad/release validation. For a deployed target, pass the explicit environment to `mise run adw:validate-deployment <environment>`. `adw:test:integration:full` and `adw:test:e2e:fast`/`adw:test:e2e:full` are optional independent suites; require per-run approval for remote-write E2E and do not call absence a pass or require a waiver. Persistent services require write-path validation when runtime behavior is in scope.
4. Capture task evidence, artifact identity, runtime environment, and failures.
5. Report pass/fail with remediation recommendations using `references/github_traceability.md` from the `adw-core` skill for file-backed Markdown when posting to GitHub.

## Output

- Target under test
- Artifact/deployment identity when runtime validation is in scope
- Check list and command evidence
- Write-path evidence for persistent services, or a documented blocker/waiver
- Pass/fail result
- Risks and recommended next action

## Common Pitfalls

1. Running generic tests that do not cover the changed behavior.
2. Hiding flaky or inconclusive results.
3. Forgetting to document environment and artifact identity.
4. Treating liveness or HTTP 200 checks as enough for database/filesystem-backed services.
5. Posting multiline validation results with visible backslash-n escape sequences.

## Verification Checklist

- [ ] Target identity recorded
- [ ] Checks are risk-based
- [ ] Runtime/artifact identity recorded when applicable
- [ ] Persistent write-path checks run or blocker/waiver documented
- [ ] Evidence is concrete
- [ ] Failures produce a bugfix or remediation path
- [ ] GitHub-facing reports use readable Markdown with real line breaks

## Guardrails

<!-- adw:guardrails:start -->
- Never fake or upgrade results; `skipped` and `unsupported` are not `passed`.
- Run no deterministic operation without a valid manifest; report `blocked` and do not improvise commands.
- Require explicit human approval for merge, production-class deploy, rollback, secrets, destructive changes, and history rewrites.
- Inference is never approval.
- Resolve missing parameters through `adw-core`: repository → adapter → context → ask.
- Report status, completed work, risks/blockers, and the next action.
<!-- adw:guardrails:end -->
