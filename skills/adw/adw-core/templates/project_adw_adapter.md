# <Project> ADW Adapter

> This template is generic. Replace placeholders with repository-specific facts and keep secrets out of the file.

## Context Layer

- Declared context helper: `<none|context-helper-skill-or-repo>`
- Required generic ADW skills: `adw-core` plus the operational `adw-*` skill for the current stage.

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

## Compose / Environment / Runtime Sync

Document where configuration examples live, how live secrets are preserved, and which config changes require deployment verification.

## Validation Matrix

- Unit/build:
- Integration:
- Smoke/API/UI:
- E2E/regression:
- Logs/metrics:

## Command Expansions

Map short, context-specific human commands to ADW skills plus concrete project checks.

## Admin Closure

Document issue, PR, release note, and deployment report expectations.

## Known Pitfalls

List project-specific pitfalls that should not be baked into generic ADW.

## Verification Checklist

- [ ] Context helper declaration is current.
- [ ] Branch/environment mapping is explicit.
- [ ] Deployment targets use non-secret identifiers only.
- [ ] Validation matrix has exact commands or documented blockers.
- [ ] Secret handling rules preserve live credentials and never store placeholder secrets over real values.
