# 0002: Pull Request as Delivery Unit

Status: Accepted

## Context

Agentic coding can produce changes quickly, but safe delivery requires human-reviewable artifacts and gates.

## Decision

Use the pull request as the central delivery unit. Plans, issues, branches, review, preview validation, merge, deployment, and rollback notes should all link back to the PR when implementation exists.

## Consequences

- Meaningful changes do not bypass review.
- Validation evidence is attached to a durable artifact.
- Rejected PRs block merge and deployment.
- Operational reports can refer to one canonical implementation record.
