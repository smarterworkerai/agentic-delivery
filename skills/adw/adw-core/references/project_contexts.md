# Project Context and Adapter Resolution

Generic ADW skills are intentionally project-agnostic. When a short human command depends on branch policy, deployment tooling, artifact names, validation suites, or admin closure rules, resolve those details through an explicit lower layer instead of baking them into generic ADW.

## Layer Order

1. **Generic ADW skill** — owns workflow mechanics, safety gates, templates, and report shape.
2. **Project adapter** — usually `.hermes/ADW.md` in the target repository. It declares concrete project facts and may declare a context helper.
3. **Context helper** — optional organization/team/user environment policy shared by compatible repositories.
4. **Live inspection** — current git, issue, PR, CI, deployment, and runtime state.
5. **Human confirmation** — required for unsafe or ambiguous choices.

## Project Adapter Contract

A repository-local adapter should answer:

- project identity and repo path;
- context helper to load, if any;
- branch and environment map;
- deployable units and artifacts;
- validation matrix;
- issue/PR/admin conventions;
- deployment and rollback expectations;
- secret-handling rules;
- project-specific pitfalls.

The adapter may point to context helper skills or repositories, but the generic ADW skill should not know their concrete names in advance.

## Context Helper Contract

A context helper may answer:

- organization or team branch conventions;
- release, deployment, and artifact policies;
- approved non-secret access-handle categories;
- delegation policy;
- evidence and communication defaults;
- reusable validators or templates.

It must not replace the project adapter for concrete service names, domains, sidecars, exact runtime routes, or project-specific tests.

## Resolution Rules

- Prefer explicit adapter declarations over inferred defaults.
- Treat mutable hosts, domains, deployment targets, and runtime state as candidates that require live verification.
- Do not persist secrets in adapters, context helpers, PR bodies, logs, screenshots, or chat.
- If exactly one safe candidate exists, report the assumption and ask before a side effect.
- If multiple candidates exist or the result affects merge, deployment, rollback, secrets, destructive changes, or history rewrite, ask for explicit human confirmation.

## Common Adapter Heading Template

A project adapter does not need to use these exact headings, but generic ADW and context helper authors should design around this shape:

```markdown
# <Project> ADW Adapter

## Context Layer
- Declared context helper: <none|skill/repo name>

## Project Identity
- Repository:
- Default local path:

## Branch and Environment Map

## Deployable Units and Artifacts

## Deployment Targets

## Access and Host Inventory

## Validation Matrix

## Command Expansions

## Admin Closure

## Known Pitfalls
```
