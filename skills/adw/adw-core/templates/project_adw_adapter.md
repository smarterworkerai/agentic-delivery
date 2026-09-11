# <Project> ADW Adapter

> This template is generic. Replace placeholders with repository-specific facts and keep secrets out of the file.

## Context Layer

- Declared context helper: `<none|context-helper-skill-or-repo>`
- Required generic ADW skills: `adw-core` plus the operational `adw-*` skill for the current stage.

## Machine-Readable Operation Contract

- Manifest: `.hermes/adw-task-manifest.json`
- Contract range: `<accepted-semver-range>`
- Vendored generic source: `<40-character-commit-sha-and-sha256>`
- Vendored context source: `<40-character-commit-sha-and-sha256-or-none>`

This file is narrative. Do not duplicate capability states, environment enums, task source paths, or checksums from the manifest.

## Project Identity

- Repository: `<owner>/<repo>`
- Default local path: `<path>`
- Primary language/runtime: `<runtime>`

## Branch and Environment Map

Document branch-to-environment semantics and which actions require explicit approval.

## Deployable Units and Artifacts

List applications, packages, images, build outputs, and immutable artifact identifiers.

## Deployment Targets

List deployment tools, environments, services, domains, and rollback expectations. Use non-secret identifiers only.

## Access and Host Inventory

List approved non-secret handles such as host aliases, port labels, username/key names, token variable names, and file-exchange paths. Do not include credentials or private key material.

## Deployment Configuration

Document configuration ownership, live-secret preservation rules, and which manifest-declared config tasks are supported. Provider methods and file formats belong in project-owned mise helpers, not generic ADW.

## Validation Matrix

- Minimal local gate: `adw:verify:minimal`
- Full local gate: `adw:verify:full`
- Deployment validation: `adw:health`, `adw:readiness`, `adw:e2e`, `adw:validate-deployment`
- Logs/metrics: `<project-owned observation source or blocker>`

## Command Expansions

Map short, context-specific human commands to ADW skills and canonical `adw:*` tasks. Concrete commands remain encapsulated in project-owned mise task definitions/helpers.

## Admin Closure

Document issue, PR, release note, and deployment report expectations.

## Known Pitfalls

List project-specific pitfalls that should not be baked into generic ADW.

## Verification Checklist

- [ ] Context helper declaration is current.
- [ ] Branch/environment mapping is explicit.
- [ ] Deployment targets use non-secret identifiers only.
- [ ] Manifest exists and passes `mise run adw:check`.
- [ ] Validation matrix references canonical tasks or documented blockers.
- [ ] Secret handling rules preserve live credentials and never store placeholder secrets over real values.
