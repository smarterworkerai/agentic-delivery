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
7. Manifest-supported `adw:health`, `adw:readiness`, `adw:e2e`, and `adw:validate-deployment` tasks verify runtime and business semantics, not only transport success.
8. Persistent services include write-path validation or an explicit blocker/waiver.
9. Non-sensitive logs show no startup or write-path failure, or unavailable logs are explicitly compensated by other runtime evidence.
10. Routed endpoint and TLS expectations are verified when declared by the adapter.
11. The adapter-declared rollback path is known.
12. The delivery report cites source revision, immutable artifact identity when applicable, target, canonical task evidence, and remaining risks.

## Production Rule

A production-class deployment requires explicit human approval even when the target is unambiguous. The manifest describes capabilities and side effects; it does not grant authorization.
