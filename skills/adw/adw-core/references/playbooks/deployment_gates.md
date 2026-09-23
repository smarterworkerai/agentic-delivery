# Deployment Gates Playbook

## Purpose

Define the evidence required before ADW reports an adapter-declared deployment complete.

## Gates

1. The target and opaque environment value are explicit and manifest-declared.
2. Review and external approval requirements are satisfied before any mutating task.
3. `adw:check` and `adw:describe` pass for the intended source revision.
4. A deployable artifact has immutable identity tied to that revision when the project uses artifacts.
5. `adw:deploy:config:pull` and `adw:deploy:config:plan` evidence match the target; `adw:deploy:config:apply` runs only after approval and preserves secret values.
6. `adw:deploy:apply` completes and `adw:deploy:status` reports the intended deployment identity.
7. Manifest-supported `adw:health`, `adw:readiness`, and `adw:validate-deployment` tasks verify runtime and business semantics, not only transport success.
8. Persistent services include write-path validation or an explicit blocker/waiver.
9. Non-sensitive logs show no startup or write-path failure, or unavailable logs are explicitly compensated by other runtime evidence.
10. Routed endpoint and TLS expectations are verified when declared by the adapter.
11. The adapter-declared rollback path is known.
12. The delivery report cites source revision, immutable artifact identity when applicable, target, canonical task evidence, and remaining risks.

## Required quality and exact-tree reuse

Before integrating a PR, wait for a successful required quality check (an executed `adw:verify:full` graph or a successful proof check) attached to that PR's current source and intended destination. Review and human merge authorization remain independent. A pending, skipped, failed, stale, or unrelated check cannot authorize merge.

A context-specific proof engine may reuse prior required quality evidence only after read-only validation of the actual tested tree (including any synthetic merge result), source and destination revisions, compatible contract and check identity, immutable evidence provenance, integration topology, and live destination readback. Identical source SHA alone is insufficient. Follow bounded proof links to a real executed required gate; cyclic or optional-suite-only evidence is not quality proof. On changed or untrusted trees run `adw:verify:full`; on unresolved PR review/check/target identity block integration. After integration, verify the destination source/tree and running artifact independently. Provider API details and branch names belong to context or project policy, never this playbook.

`adw:verify:minimal` is feature-branch feedback, not promotable evidence. Optional `adw:test:integration:full` and fast/full E2E results are not required to exist and their absence is not a waiver. Remote-write E2E runs require their own per-run approval; deployment validation does not implicitly invoke them.

## Production Rule

A production-class deployment requires explicit human approval even when the target is unambiguous. The manifest describes capabilities and side effects; it does not grant authorization.
