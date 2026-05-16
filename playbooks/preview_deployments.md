# Preview Deployments Playbook

## Purpose

Validate feature or bugfix branches in an isolated preview environment before merge.

## Procedure

1. Confirm PR, branch, target base, and review status.
2. Stop if the PR was rejected.
3. Identify preview environment and URL convention.
4. Deploy the feature branch or immutable preview artifact.
5. Verify deployment status and logs.
6. Run smoke/E2E/manual QA checks.
7. Record preview URL and validation result in the PR.

## Safety Rules

- Never deploy preview branches to production.
- Never reuse production secrets unless explicitly approved and designed for preview.
- Treat preview as validation evidence, not merge approval by itself.
