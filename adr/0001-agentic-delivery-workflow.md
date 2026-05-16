# 0001: Agentic Delivery Workflow

Status: Accepted

## Context

The repository defines an agent that moves software changes from intent to deployment through reviewable, traceable stages.

## Decision

Model the agent around the Agentic Delivery Workflow:

```text
Plan → Branch → Issue → Implementation → PR → Review → Preview → Validation → Merge → Deployment
```

The root `SOUL.md` defines identity and hard boundaries. Hermes-compatible skills under `skills/adw/` implement operational stages. Shared playbooks and templates remain repository-level artifacts.

## Consequences

- Delivery artifacts are explicit and reviewable.
- PRs are the central unit of delivery.
- Skills can be invoked independently while still composing into one workflow.
- Shared templates/playbooks avoid drift and duplication.
