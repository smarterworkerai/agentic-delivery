# Task brief

## Objective
<One or two paragraphs describing the delegated implementation objective.>

## Repository and branch
- Repository URL: `<repo-url>`
- Base branch: `<base-branch>`
- Target implementation branch: `<feature-branch>`
- Linked issue: `<issue-url-or-number>`
- Approved plan artifact: `<plan-url-or-path>`

## Scope
- In scope: `<exactly what the worker may change>`
- Out of scope: `<explicit non-scope>`

## Required deliverable

- Delivery mode: `<approved PR/MR | local commit | patch/artifacts>`
- Approved PR/MR source/target/replacement route: `<exact route | not approved>`

Open a PR/MR only when the exact route above is approved. Otherwise return a local commit or reviewable patches/artifacts.

Required result fields:

- approved PR/MR URL, or local commit/patch artifact reference and no-PR reason
- implementation branch
- commit SHA
- changed-file summary
- verification commands and results
- blockers / remaining risks
- explicit statement that no merge/deploy was performed

If PR/MR creation is not approved or cannot be performed, state that explicitly and provide the local commit or patches/artifacts under `result/`.

## Context summary
<Concise context needed by the worker. Prefer summarized markdown over raw dumps.>
