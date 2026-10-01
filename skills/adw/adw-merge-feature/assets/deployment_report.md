# Deployment Report

## Target

- Environment: `<opaque manifest value>`
- Release target: `<adapter-declared target>`

## Identity

- Source revision: `<immutable revision>`
- Artifact identity: `<immutable identity or not applicable>`
- Deployment identity: `<provider-neutral deployment reference>`

## Configuration

- `adw:deploy:config:pull`: `<evidence>`
- `adw:deploy:config:plan`: `<evidence>`
- `adw:deploy:config:apply`: `<evidence or not requested>`

## Deployment Status

- `adw:deploy:apply`: `<evidence>`
- `adw:deploy:status`: `<evidence>`

## Runtime Verification

- Health/readiness: `<evidence or unsupported>`
- E2E/business semantics: `<evidence or unsupported>`
- Deployment validation: `<evidence or unsupported>`
- Non-sensitive logs: `<evidence or unavailable with compensation>`

## Rollback Path

<adapter-declared strategy and last-known-good identity>

## Risks / Blockers

- `<risk or None>`
