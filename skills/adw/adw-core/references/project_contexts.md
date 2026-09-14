# Project Context and Adapter Resolution

Generic ADW skills are project-agnostic. Repository policy, opaque environment values, capability support, deployment topology, and current runtime facts must come from explicit lower layers rather than generic defaults.

## Responsibility Layers

1. **Generic ADW package** — owns workflow mechanics, safety gates, shared templates, and the canonical `adw:*` ABI.
2. **Optional context snapshot** — owns proven shared task definitions and non-secret variables for compatible repositories. One immutable context pin controls both.
3. **Project-local adapter** — owns concrete task implementations, local overrides, `.hermes/adw-task-manifest.json`, and narrative `.hermes/ADW.md` policy.
4. **Live inspection** — verifies current Git, issue, PR, CI, deployment, and runtime state.
5. **Human confirmation** — authorizes unsafe or ambiguous choices.

Mise include precedence is generic ADW → optional context → project-local override. Shared generic/context sources are pinned to immutable Git commit SHAs and verified by SHA-256; normal execution uses reviewed local or vendored content rather than depending on a mutable remote include.

## Machine-Readable Contract

`.hermes/adw-task-manifest.json` is the machine-readable source of truth for:

- contract compatibility;
- source provenance and checksums;
- canonical capability support;
- fixed side-effect classes;
- opaque environment values;
- verification graphs;
- required secret environment-variable names, never values.

Missing or invalid manifests block deterministic project operations. Generic ADW must not substitute package-manager, provider, or infrastructure commands.

## Narrative Project Adapter

Repository-local `.hermes/ADW.md` explains facts that require human or agent interpretation:

- project and repository identity;
- declared context snapshot, if any;
- branch/release policy when the project uses one;
- deployable units and artifact identity;
- meanings of opaque environment values;
- validation and approval policy;
- deployment and rollback expectations;
- non-secret access aliases;
- project-specific pitfalls.

It documents the manifest and adapter; it does not redefine canonical task semantics or embed secret values.

## Context Snapshot Boundary

A context snapshot may supply organization/team conventions, reusable deterministic task definitions, non-secret logical aliases, and evidence/communication defaults. It must not invent concrete service names, domains, routes, or project-specific tests, and it must not carry credentials or raw key paths.

Context updates are explicit synchronization operations that produce a reviewable diff. Runtime execution never silently advances a context pin.

## Resolution Rules

- Prefer manifest and project-local declarations over inference.
- Treat hosts, domains, deployment targets, and runtime state as candidates until live verification.
- Environment names are opaque manifest values; generic ADW does not derive them from branch names.
- Keep secrets out of manifests, adapters, context snapshots, evidence, logs, screenshots, and chat.
- Ask for explicit human approval for merge, production-class deployment, rollback, secret handling, destructive actions, or history rewrite.
