# PR Reviewing Playbook

## Purpose

Review PRs as delivery artifacts, not only code diffs.

## Checklist

- Scope matches linked plan and issue.
- No unrelated refactors or generated artifacts.
- No secrets, credentials, tokens, or customer data.
- Tests/checks are meaningful and reported.
- Deployment impact is documented.
- Rollback considerations are present when relevant.
- Comments are resolved or explicitly accepted.

## Outcomes

- `approved` — ready for preview/validation.
- `changes requested` — stop workflow and remediate.
- `blocked` — missing context, failing checks, or unsafe ambiguity.
