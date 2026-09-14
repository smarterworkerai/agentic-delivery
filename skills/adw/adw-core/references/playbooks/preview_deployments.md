# Preview Deployments Playbook

## Purpose

Validate a feature or bugfix revision in an adapter-declared disposable environment before merge.

## Procedure

1. Confirm the PR, source revision, target branch, review status, and whether the project manifest declares a disposable validation environment.
2. Stop if the PR was rejected or the environment is ambiguous.
3. Run `mise run adw:check` and `mise run adw:describe`; treat a missing manifest, unknown environment, or unsupported required capability as blocked.
4. Resolve the explicit opaque environment value and non-secret target metadata from the project adapter and manifest.
5. Run `mise run adw:deploy:config:pull <environment>` and `mise run adw:deploy:config:plan <environment>`. Inspect the plan and apply it only after the external approval gate with `mise run adw:deploy:config:apply <environment>`.
6. Confirm that the intended revision has an immutable deployable identity when the project uses build artifacts. Do not substitute an older or mutable artifact.
7. Deploy with `mise run adw:deploy:apply <environment>` and inspect `mise run adw:deploy:status <environment>` evidence.
8. Validate with the manifest-supported `adw:health`, `adw:readiness`, `adw:e2e`, and `adw:validate-deployment` tasks. Validate response and business semantics, not only liveness.
9. For persistent services, require a write-path check through the project-owned E2E/deployment-validation implementation or record an explicit blocker/waiver.
10. Record the environment, non-secret target reference, source revision, immutable artifact identity when applicable, canonical task evidence, and validation result in the PR.

## Safety Rules

- Never infer an environment name or deployment target.
- Never deploy a validation revision to a non-disposable or production-class environment without separate explicit authorization.
- Never copy secrets from another environment or overwrite live values with examples, blanks, or masked placeholders.
- Treat preview evidence as validation, not merge approval.
- Do not claim readiness from mutable artifact names or liveness-only checks.
- Use file-backed Markdown for substantial GitHub updates and verify rendered content.
