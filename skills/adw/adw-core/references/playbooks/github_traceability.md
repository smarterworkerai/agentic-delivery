# GitHub Traceability Playbook

## Purpose

Preserve branch ↔ issue ↔ PR linkage across the ADW lifecycle.

## Required Links

- Issue links to plan and branch.
- Branch name appears in issue or plan.
- PR links to issue and summarizes validation.
- Validation/deployment reports link back to PR.
- Follow-up bugs link to the failed PR/deployment.

## Labels

Use consistent labels: `enhancement`, `bug`, `hotfix`, `chore`, `documentation`, `security`.

## Issue Closure After Merge

When a feature or bugfix PR is merged into a non-feature/non-bugfix destination branch, close the linked issue as part of delivery closure after validation/deployment evidence is available. Add a final issue comment before or during closure that includes:

- merged PR link;
- destination branch and merge SHA;
- validation/deployment evidence;
- final status;
- rollback or follow-up notes when relevant.

When the PR is merged into another feature or bugfix branch, do not close the issue yet. Add an intermediate status comment that records the merge target and next expected delivery branch.

## Markdown and Newline Hygiene

GitHub issues, pull request bodies, review reports, and comments must render as readable Markdown. Do not publish bodies containing literal escaped newline sequences such as `\n` unless the text is intentionally documenting an escape sequence.

Before creating or updating GitHub text:

- Prefer writing the body/comment to a temporary Markdown file and pass it with `gh issue create --body-file`, `gh issue edit --body-file`, `gh pr create --body-file`, `gh pr edit --body-file`, `gh issue comment --body-file`, or `gh pr comment --body-file`.
- If using shell variables or inline bodies, verify they contain real newline characters, not backslash-plus-n text.
- Preview or inspect the generated Markdown before posting when the content is more than a short one-line comment.
- After posting important issue/PR documentation, reopen it with `gh issue view`, `gh pr view`, or the GitHub URL and confirm headings, bullet lists, checkboxes, and code blocks render normally.
