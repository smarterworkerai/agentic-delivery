# <Project> ADW Adapter

> Narrative repository policy for humans and agents. The machine-readable source of truth is `.hermes/adw-task-manifest.json`; concrete deterministic commands remain in project-owned mise tasks or `mise-helper/`. Never place secrets here.

## Project Identity

- Repository: `<owner/repo>`
- Default local path: `<path or logical workspace alias>`
- Default branch: `<inspect repository metadata; do not assume>`

## Contract and Context

- Manifest: `.hermes/adw-task-manifest.json`
- Generic ADW source: `<immutable 40-character commit SHA and reviewed local/vendored path>`
- Context snapshot: `<none or immutable 40-character commit SHA and reviewed local/vendored path>`
- Context synchronization policy: `<reviewable explicit update process>`
- Include precedence: `generic ADW → optional context → project-local override`

## Branch and Release Policy

Describe issue/branch/PR linkage and release targets. If environments are related to branches, declare that project-specific mapping explicitly; otherwise state that no branch-to-environment mapping exists.

## Deployable Units and Artifact Identity

List deployable units and how immutable source/artifact identity is proven. Do not use mutable tags as sole release identity.

## Opaque Environments

List only values also declared by the manifest. Explain their purpose and whether they are disposable, production-class, or otherwise restricted. Generic ADW does not derive environment names.

## Access Aliases

List approved logical host, provider, or runtime aliases only. Do not include raw infrastructure addresses, key paths, credentials, tokens, or connection strings.

## Validation and Evidence

Baseline contract validation: `mise run adw:check`.

Map acceptance criteria to supported canonical `adw:*` capabilities and evidence expectations. Record unsupported capabilities honestly; never replace them with ad-hoc package-manager/provider commands.

## Deployment and Rollback Policy

Describe approval requirements, immutable identity checks, stateful risks, and the adapter-declared rollback strategy. Concrete execution remains behind canonical configuration, deployment, status, health, readiness, E2E, and deployment-validation tasks.

## Secrets

List required secret environment-variable names only when necessary. Values belong in approved secret stores and must not appear in this file, the manifest, source control, or evidence.

## Admin Closure

Describe issue/PR updates, release notes, deployment reporting, and any explicit human approvals required to close work.

## Known Pitfalls

- `<project-specific, current, non-secret constraint>`
