---
name: adw-audit-dependencies
description: >-
  Audits dependency, build-tool, and toolchain changes for security, maintenance, compatibility, and release risk. Use for upgrade PRs, lockfile changes, supply-chain review, or dependency health checks.
license: MIT
compatibility: Requires git and the GitHub CLI. Deterministic steps require mise and an ADW task manifest.
metadata:
  suite: agentic-delivery
  version: "2.2.0"
  author: smarterworkerai
  requires: adw-core
  router-tokens: "audit-dependencies"
  hermes-tags: "adw dependencies security audit"
  hermes-related-skills: "adw-core adw-plan adw-test-feature"
  human-gate: "—"
---
# ADW Audit Dependencies

## Overview

Use this skill to assess dependency and build-tool risk.

## When to Use

- Dependency updates are requested.
- CVEs are reported.
- Build tooling changes.
- Production security posture is under review.

## Required Context

Load `adw-core` first. Read the project adapter from `.adw/ADW.md`, or `.hermes/ADW.md` for an existing project, and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults. Shared playbooks are named from the `adw-core` skill; this skill's own templates are under `assets/`.

## Workflow

1. Inventory affected dependency files and package managers.
2. Identify direct and transitive risk where tooling supports it.
3. Check licenses, maintenance status, and breaking-change notes when relevant.
4. Recommend update, pin, replacement, or no-action.
5. Attach audit result to issue/PR/validation report.

## Output

- Dependency scope
- Risk findings
- Recommended action
- Required tests/checks

## Common Pitfalls

1. Treating version bump as risk-free.
2. Ignoring runtime image/package dependencies.
3. Reporting vulnerabilities without exploitability or scope.

## Verification Checklist

- [ ] Dependency files inspected
- [ ] CVE/security findings summarized without secrets
- [ ] Required tests/checks are identified
- [ ] Recommendation is actionable

## Guardrails

<!-- adw:guardrails:start -->
- Never fake or upgrade results; `skipped` and `unsupported` are not `passed`.
- Run no deterministic operation without a valid manifest; report `blocked` and do not improvise commands.
- Require explicit human approval for merge, production-class deploy, rollback, secrets, destructive changes, and history rewrites.
- Inference is never approval.
- Resolve missing parameters through `adw-core`: repository → adapter → context → ask.
- Report status, completed work, risks/blockers, and the next action.
<!-- adw:guardrails:end -->
