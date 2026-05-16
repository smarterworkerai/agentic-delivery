# Incident Response Playbook

## Purpose

Respond to production regressions or failed deployments safely.

## Procedure

1. Confirm affected environment and severity.
2. Preserve evidence without exposing secrets.
3. Determine whether to continue, fix-forward, or rollback.
4. If rollback is needed, invoke `adw-rollback-deployment`.
5. If bugfix is needed, invoke `adw-plan-bugfix`.
6. Report current impact, mitigation, and follow-up owner/artifact.
