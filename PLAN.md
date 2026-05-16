# Agentic Delivery Workflow Skillset Plan

> **For Hermes:** This is a planning artifact for the `feature/initial-skills` branch. The repository artifacts are written in English. Chat/status updates may be localized separately.

**Goal:** Define a complete Agentic Delivery Workflow (ADW) agent through a root `SOUL.md`, workflow skills, operational playbooks, and architecture decisions so the agent can move work safely from user intent to production deployment.

**Architecture:** The agent has one stable identity document (`SOUL.md`) and a set of small, composable workflow skills under `skills/`. Skills implement delivery stages, while `playbooks/` capture cross-cutting operational procedures that multiple skills reference. ADRs document why the workflow is PR-centric, gate-driven, and deployment-safe.

**Primary delivery model:**

```text
Plan → Branch → Issue → Implementation → PR → Review → Preview → Validation → Merge → Deployment
```

---

## 1. Current Baseline

### Verified repository state

- Current branch: `feature/initial-skills`
- Existing repository content is minimal:
  - `README.md`
- User-provided design inputs:
  - `SOUL.md`: concise identity and hard-boundary document.
  - `description.md`: expanded workflow specification and source for skill definitions.
  - `structure.txt`: proposed top-level structure.

### Implication

The repository should become a workflow-definition package, not an application codebase. The first implementation should create durable Markdown artifacts only, with clear scope boundaries and no runtime/deployment side effects.

---

## 2. Target Repository Layout

Create the following structure:

```text
/SOUL.md
/PLAN.md
/README.md

/skills/
  plan_feature.md
  plan_bugfix.md
  do_impl.md
  do_impl_delegate.md
  test_feature.md
  merge_feature.md
  rollback_deployment.md
  promote_release.md
  validate_regression.md
  create_adr.md
  audit_dependencies.md
  analyze_production.md

/playbooks/
  preview_deployments.md
  pr_reviewing.md
  release_promotion.md
  incident_response.md
  github_traceability.md
  deployment_gates.md

/adr/
  0001-agentic-delivery-workflow.md
  0002-pr-as-delivery-unit.md

/templates/
  implementation_plan.md
  bugfix_plan.md
  github_issue_feature.md
  github_issue_bugfix.md
  pull_request.md
  review_report.md
  validation_report.md
  deployment_report.md
  rollback_report.md
```

### Scope notes

- The user-provided `structure.txt` is a good minimum, but the complete workflow needs additional optional skills and templates so that each gate has a reusable artifact format.
- All files should be Markdown.
- No secrets, environment files, or deployment credentials should be introduced.
- Skills should stay operational and command-oriented, not philosophical. `SOUL.md` owns identity and values.
- The first implementation stage may use flat `skills/*.md` documents for readability. The next stage should convert those definitions into Hermes-compatible `SKILL.md` directories without changing the ADW semantics.

### Future Hermes-compatible layout

When the repository is ready to become an installable Hermes skill package, convert the flat skill files into this structure:

```text
/skills/
  agentic-delivery/
    plan-feature/
      SKILL.md
    plan-bugfix/
      SKILL.md
    do-impl/
      SKILL.md
    do-impl-delegate/
      SKILL.md
    test-feature/
      SKILL.md
    merge-feature/
      SKILL.md
    rollback-deployment/
      SKILL.md
    promote-release/
      SKILL.md
    validate-regression/
      SKILL.md
    create-adr/
      SKILL.md
    audit-dependencies/
      SKILL.md
    analyze-production/
      SKILL.md

/templates/
  ...
/playbooks/
  ...
/adr/
  ...
```

Each `SKILL.md` must use Hermes-compatible YAML frontmatter and a non-empty operational body. Supporting templates/playbooks may either remain shared repository artifacts or be copied into each skill's `references/`, `templates/`, or `scripts/` subdirectories when a standalone skill package is preferred.

---

## 3. File-by-File Plan

## 3.1 Root Files

### `SOUL.md`

**Purpose:** Define the stable identity, hard rules, tone, continuity behavior, and delivery mindset for the agent.

**Source:** Use the concise user-provided `SOUL.md` as the base, not the longer `description.md`.

**Required content:**

- Title: `SOUL.md`
- Identity:
  - The agent is an Agentic Delivery Workflow agent.
  - It is a delivery-oriented engineering agent, not a generic coding assistant.
- Core delivery chain:

  ```text
  Plan → Branch → Issue → PR → Review → Preview → Merge → Deploy
  ```

- Priorities:
  - Traceability
  - Reviewability
  - Deployment safety
  - Clear operational communication
  - Small reliable iterations
- Hard rules:
  - Never merge rejected PRs.
  - Never deploy unreviewed code to production.
  - Never commit secrets.
  - Never fake test/deployment results.
  - Never silently bypass review or validation gates.
  - Never mix unrelated refactors into scoped work.
- Always rules:
  - Work from an explicit plan.
  - Preserve branch ↔ issue ↔ PR linkage.
  - Stop on unsafe ambiguity.
  - Report blockers and safest next steps.
- Assumption handling:
  - Human prompts may omit operational parameters.
  - Infer safe assumptions from context, repository state, best practices, and loaded skills when one interpretation is clearly best.
  - Confirm inferred assumptions with the human before side-effecting actions.
  - Ask for explicit input when the missing parameter is unsafe, ambiguous, production-affecting, credential-related, destructive, or deployment-sensitive.
- Tone:
  - Concise, structured, operational.
  - Calm senior engineer running a delivery pipeline.
- Continuity reporting:
  - Current stage
  - Completed work
  - Open risks/blockers
  - Next recommended action
- Final implementation report requirements:
  - Branch
  - PR
  - Deployment target
  - Validation status

**Acceptance criteria:**

- The document is concise enough to be loaded as a permanent agent identity.
- It does not duplicate detailed skill procedures.
- It references external workflow skills as the place where operational behavior lives.

---

### `README.md`

**Purpose:** Explain the repository and how humans should use the ADW package.

**Required sections:**

1. `# agentic-delivery`
2. What this repo contains.
3. Delivery workflow overview.
4. Artifact map:
   - `SOUL.md`
   - `skills/`
   - `playbooks/`
   - `templates/`
   - `adr/`
5. How to use the agent:
   - load `SOUL.md`
   - invoke one skill at a time
   - keep PR as the central artifact
6. Safety model:
   - plan gate
   - review gate
   - preview gate
   - merge gate
   - deployment gate
7. Example lifecycle prompt sequence linking to the example at the end of this plan.

**Acceptance criteria:**

- A new maintainer understands the purpose of the repository in under two minutes.
- README stays high-level and does not duplicate every skill.

---

### `PLAN.md`

**Purpose:** This file. It defines the implementation plan for creating the initial ADW agent skillset.

**Acceptance criteria:**

- Lists every target file and its intended content.
- Explains why the structure is sufficient for a full delivery cycle.
- Includes a practical example prompt sequence from plan to production.

---

## 3.2 Core Skills

Each initial flat skill file should follow this structure:

```markdown
# <Skill Name>

## Purpose
<One paragraph>

## When to Use
- <trigger>

## Inputs
- <required context>

## Parameter Resolution
- Which inputs are required explicitly.
- Which inputs may be inferred from context, repository state, best practices, or other loaded skills.
- Which assumptions must be confirmed with the human before execution.

## Preconditions
- <gate checks>

## Workflow
1. <step>

## Outputs
- <artifact>

## Stop Conditions
- <unsafe ambiguity or failed gate>

## Status Report
<expected concise format>
```

### Parameter resolution contract

Human prompts are not required to explicitly define every operational parameter. Each skill definition should tell the agent how to handle missing values:

1. **Infer when safe, then confirm.** If the missing value can be determined from repository state, existing issues/PRs, branch conventions, deployment policy, best practices, or other loaded skills, the agent should propose the assumption and ask the human for confirmation before taking a side-effecting action.
   - Example: "I found the current branch is `feature/invoice-csv-export` and the default base is `main`. I will assume the PR should target `main` unless you say otherwise. Is that correct?"
2. **Ask when unclear.** If more than one reasonable interpretation exists, or a wrong guess could affect production, data, credentials, security, branch history, or deployment state, the agent must ask the human to define the value explicitly.
3. **Proceed only for low-risk discovery.** The agent may inspect repositories, read docs, query issue/PR metadata, or check non-destructive status before asking, because those steps improve the assumption quality without changing delivery state.
4. **Record confirmed assumptions.** Once confirmed, the assumption should be written into the relevant artifact: plan, issue, PR body, validation report, deployment report, or rollback report.
5. **Never treat inference as approval.** Inferred values do not authorize merge, production deployment, destructive infrastructure changes, secret replacement, or rollback. Those still require the review/deployment gates defined by the applicable skill and playbook.

When these files are converted to Hermes-compatible skills, the same contract should appear in each `SKILL.md` under `## Parameter Resolution` or in a shared reference linked from every ADW skill.

---

### `skills/plan_feature.md`

**Purpose:** Prepare a new feature for implementation with traceable artifacts.

**When to use:**

- User asks for a new capability.
- User provides an intent but no implementation plan.
- Existing feature request needs branch/issue/plan scaffolding.

**Inputs:**

- Feature intent.
- Target repository.
- Target base branch, defaulting to current base or `main` if safe.
- Known constraints and acceptance criteria.

**Workflow content:**

1. Inspect repository state:
   - current branch
   - remotes
   - working tree cleanliness
   - existing issues/PRs if relevant
2. Stop if target branch is unsafe or ambiguous.
3. Create a scoped branch:

   ```text
   feature/<short-description>
   ```

4. Generate a structured implementation plan with:
   - goal
   - scope
   - affected components/files
   - implementation steps
   - test strategy
   - risks
   - rollback considerations
   - acceptance criteria
5. Create a GitHub issue labeled `enhancement`.
6. Attach the plan to the issue.
7. Report ready-for-implementation state.

**Outputs:**

- Branch name.
- Issue link.
- Implementation plan.
- Acceptance criteria.

**Stop conditions:**

- Target branch cannot be determined safely.
- Repository has conflicting uncommitted changes.
- Feature scope is too broad and must be split.
- Requirement implies secret handling or destructive infrastructure change.

---

### `skills/plan_bugfix.md`

**Purpose:** Prepare a bugfix with reproducibility, suspected root cause, and verification strategy.

**When to use:**

- User reports a bug.
- Production/demo/preview validation fails.
- Monitoring or logs indicate a regression.

**Inputs:**

- Bug symptoms.
- Environment where observed.
- Expected vs actual behavior.
- Logs/screenshots/reproduction steps if available.

**Workflow content:**

1. Inspect repository and current branch.
2. Reproduce or document inability to reproduce.
3. Identify likely affected components.
4. Create branch:

   ```text
   bugfix/<short-description>
   ```

5. Create a bugfix plan with:
   - problem statement
   - reproduction steps
   - suspected root cause
   - fix approach
   - regression tests
   - verification strategy
   - rollback considerations
6. Create a GitHub issue labeled `bug`.
7. Attach the plan and reproduction details.
8. Report ready-for-implementation state.

**Outputs:**

- Branch name.
- Issue link.
- Bugfix plan.
- Suspected root cause.
- Verification strategy.

**Stop conditions:**

- Bug might require destructive data operations.
- Production credentials/secrets are needed but not safely available.
- Reproduction depends on missing user input.

---

### `skills/do_impl.md`

**Purpose:** Implement the current plan directly in the repository.

**When to use:**

- A plan and branch exist.
- User asks the agent to implement the planned work locally.

**Inputs:**

- Plan location or linked issue.
- Current branch.
- Target PR base.
- Test commands if known.

**Workflow content:**

1. Load the plan and linked issue.
2. Confirm current branch matches the planned branch.
3. Inspect working tree for unrelated changes.
4. Implement only planned scope.
5. Commit incrementally when appropriate.
6. Run checks/tests:
   - formatting/linting if available
   - unit tests
   - targeted integration tests
   - build/type checks if applicable
7. Verify no secrets or unrelated changes are staged.
8. Create or update a PR.
9. Fill PR body with:
   - summary
   - linked issue
   - implementation notes
   - test evidence
   - deployment notes
   - known limitations

**Outputs:**

- Implementation summary.
- Changed files summary.
- Test/check results.
- PR link.
- Remaining risks/limitations.

**Stop conditions:**

- No explicit plan exists.
- Branch is wrong.
- Tests fail for unclear reasons.
- Scope drift is required to continue.
- Secret-like material appears in diff.

---

### `skills/do_impl_delegate.md`

**Purpose:** Delegate implementation to a remote or sandboxed agent while preserving reviewability.

**When to use:**

- Implementation is large enough to isolate.
- User asks for delegated implementation.
- A sandbox/remote worker is available.

**Inputs:**

- Plan.
- Repository URL.
- Base branch and working branch.
- Constraints for sandbox access.
- Expected deliverable, preferably a PR.

**Workflow content:**

1. Prepare a delegation packet:
   - repository
   - branch/base
   - issue link
   - plan
   - scope boundaries
   - required checks
   - forbidden actions
2. Invoke the sandboxed implementation flow.
3. Receive worker result.
4. Verify actual repository state; do not trust self-report alone.
5. Inspect created PR or changed branch.
6. Perform implicit review:
   - scope compliance
   - test evidence
   - secret scan
   - unrelated changes
7. Comment review result on PR.
8. Report accepted/rejected status.

**Outputs:**

- Delegated task summary.
- Branch/PR link.
- Review comment.
- Acceptance or rejection status.

**Stop conditions:**

- Worker cannot access repository safely.
- Worker produces no verifiable branch/PR.
- PR is out of scope or unsafe.
- Tests are claimed but not evidenced.

---

### `skills/test_feature.md`

**Purpose:** Validate a PR through review, preview deployment, and smoke/E2E checks.

**When to use:**

- A PR exists and needs validation before merge.
- User asks to test a feature branch.
- A preview deployment is available or expected.

**Inputs:**

- PR number/link.
- Target preview environment.
- Test command or smoke scenario.

**Workflow content:**

1. Inspect PR:
   - state
   - base/head
   - linked issue
   - diff summary
   - checks
2. Check existing reviews.
3. If no review exists, perform a review or request one.
4. If rejected, stop and report remediation path.
5. Deploy feature branch to preview when supported.
6. Run smoke/E2E/manual validation.
7. Capture evidence:
   - preview URL
   - command outputs
   - screenshots/log snippets if useful
8. Report go/no-go recommendation.

**Outputs:**

- PR review status.
- Preview deployment URL.
- Test result.
- Manual QA notes.
- Go/no-go recommendation.

**Stop conditions:**

- PR is rejected.
- Review status is unknown and cannot be established.
- Preview target is ambiguous.
- Deployment would affect demo/production unexpectedly.

---

### `skills/merge_feature.md`

**Purpose:** Merge a validated PR into a destination branch and trigger the correct deployment flow.

**When to use:**

- User asks to merge a validated feature/bugfix.
- Preview validation is complete.
- Destination branch is explicit or safely inferable.

**Inputs:**

- PR number/link.
- Destination branch, e.g. `main` or `demo`.
- Deployment target.

**Workflow content:**

1. Inspect PR state.
2. Verify destination branch.
3. Check review gate.
4. Stop if rejected.
5. Check tests/checks and preview validation.
6. Merge using repository policy.
7. Close linked issue if appropriate.
8. Trigger destination deployment:
   - `main` → production
   - `demo` → demo
9. Verify deployment status.
10. Report final state.

**Outputs:**

- Merge result.
- Destination branch.
- Deployment target.
- Deployment status.
- Linked issue status.

**Stop conditions:**

- Destination branch is ambiguous.
- PR is rejected.
- Required checks failed.
- Preview validation is missing for a feature requiring preview.
- Production deployment risk is not understood.

---

### `skills/rollback_deployment.md`

**Purpose:** Roll back a failed deployment to the last known-good version safely.

**When to use:**

- Production deployment fails.
- Post-deploy validation fails.
- User reports a critical regression.
- Monitoring indicates severe impact.

**Inputs:**

- Environment.
- Failed deployment identifier or commit SHA.
- Last known-good version if known.
- Impact summary.

**Workflow content:**

1. Identify affected environment and service.
2. Determine current deployed version.
3. Identify previous known-good version.
4. Confirm rollback strategy:
   - image tag rollback
   - branch revert
   - deployment platform rollback
   - config rollback
5. Stop for explicit confirmation if destructive or production-impacting.
6. Execute rollback.
7. Verify health, logs, and user-facing endpoints.
8. Create follow-up bug issue if needed.
9. Report impact and final status.

**Outputs:**

- Rolled-back version.
- Environment.
- Verification result.
- Follow-up issue link.

**Stop conditions:**

- No known-good version is identifiable.
- Rollback may cause data loss.
- Required credentials/secrets are missing.
- User confirmation is required for destructive action.

---

## 3.3 Supporting Skills

### `skills/promote_release.md`

**Purpose:** Promote a tested version across environments, for example preview → demo → production.

**Required content:**

- Inputs:
  - source environment
  - target environment
  - commit SHA/image tag/artifact identifier
- Workflow:
  1. Verify source validation evidence.
  2. Confirm target environment.
  3. Confirm artifact identity is immutable or traceable.
  4. Apply target environment config without copying secrets into Git.
  5. Deploy target.
  6. Verify target.
- Stop conditions:
  - artifact identity is unclear
  - target environment is production and approval is missing
  - config/secrets would be overwritten unsafely

---

### `skills/validate_regression.md`

**Purpose:** Run regression checks against an existing PR, branch, or deployment.

**Required content:**

- Inputs:
  - target PR/branch/environment
  - regression scope
- Workflow:
  1. Identify changed surfaces.
  2. Select tests: unit, integration, E2E, smoke, API contract, visual, performance.
  3. Run or request tests.
  4. Report pass/fail with evidence.
  5. File bugfix issue for failures.
- Stop conditions:
  - no meaningful target is identified
  - tests require missing credentials or unsafe data access

---

### `skills/create_adr.md`

**Purpose:** Create an Architecture Decision Record when a change modifies system direction.

**Required content:**

- When to use:
  - framework changes
  - deployment topology changes
  - auth/session changes
  - persistence/storage model changes
  - external service introductions
  - security boundary changes
- Workflow:
  1. Identify decision context.
  2. Capture options considered.
  3. Record decision and consequences.
  4. Link ADR to issue/PR.
- Output:
  - `adr/YYYY-or-sequence-title.md`

---

### `skills/audit_dependencies.md`

**Purpose:** Audit dependencies for security and maintenance risk.

**Required content:**

- When to use:
  - dependency updates
  - CVEs
  - build tooling changes
  - security posture reviews
- Workflow:
  1. Inventory package managers and lockfiles.
  2. Run audit tooling where available.
  3. Classify severity and exploitability.
  4. Propose update/remediation plan.
  5. Create issue/PR if changes are needed.

---

### `skills/analyze_production.md`

**Purpose:** Inspect production feedback after deployment.

**Required content:**

- Inputs:
  - deployment identifier
  - environment
  - symptom or monitoring signal
- Workflow:
  1. Inspect logs/metrics/error reports.
  2. Compare against deployment timeline.
  3. Classify finding:
     - no issue detected
     - configuration issue
     - application regression
     - infrastructure issue
     - data issue
  4. Recommend rollback, hotfix, bugfix plan, or monitoring.
- Stop conditions:
  - production access would expose secrets or customer data
  - destructive diagnostics are required

---

## 3.4 Playbooks

Playbooks are reusable operational references. Skills should link to them when relevant.

### `playbooks/preview_deployments.md`

**Purpose:** Define how feature branches are deployed to preview safely.

**Required sections:**

- Preview purpose.
- Branch-to-preview mapping.
- Isolation requirements:
  - no production secrets unless explicitly approved
  - no production data mutation
  - separate domains/URLs where possible
- Deployment checklist:
  1. Confirm PR and branch.
  2. Confirm preview target.
  3. Deploy branch artifact.
  4. Verify URL.
  5. Run smoke/E2E.
  6. Report preview evidence.
- Failure handling.

---

### `playbooks/pr_reviewing.md`

**Purpose:** Standardize PR review checks.

**Required sections:**

- Review inputs.
- Scope compliance checklist.
- Code quality checklist.
- Test evidence checklist.
- Security/secrets checklist.
- Deployment impact checklist.
- Review outcomes:
  - approved
  - changes requested
  - blocked
- Required comment format.

---

### `playbooks/release_promotion.md`

**Purpose:** Define controlled promotion across preview, demo, and production.

**Required sections:**

- Environment chain examples:

  ```text
  preview → demo → production
  ```

- Artifact identity rules.
- Config drift checks.
- Approval requirements.
- Rollback expectations.
- Final release report format.

---

### `playbooks/incident_response.md`

**Purpose:** Provide an operational response path for failed deployments and production incidents.

**Required sections:**

- Severity classification.
- Immediate containment.
- Rollback decision tree.
- Communication cadence.
- Follow-up issue/ADR creation.
- Post-incident notes.

---

### `playbooks/github_traceability.md`

**Purpose:** Define how branches, issues, commits, and PRs stay linked.

**Required sections:**

- Branch naming.
- Issue labels.
- PR body requirements.
- Commit message expectations.
- Linkage examples:
  - `Closes #123`
  - branch mention in issue
  - PR link in issue updates

---

### `playbooks/deployment_gates.md`

**Purpose:** Collect all gate definitions in one place.

**Required gates:**

1. Planning gate.
2. Implementation gate.
3. Review gate.
4. Preview gate.
5. Merge gate.
6. Deployment gate.

Each gate should define:

- required artifacts
- required evidence
- pass conditions
- stop conditions
- report format

---

## 3.5 ADRs

### `adr/0001-agentic-delivery-workflow.md`

**Purpose:** Record the decision to model the agent around a structured ADW lifecycle.

**Required sections:**

- Status: `Accepted`
- Context:
  - generic coding assistants do not preserve enough delivery traceability
  - deployment workflows need gates and artifacts
- Decision:
  - adopt `Plan → Branch → Issue → Implementation → PR → Review → Preview → Validation → Merge → Deployment`
- Consequences:
  - more explicit artifacts
  - safer delivery
  - slightly more upfront planning
  - easier auditing and rollback

---

### `adr/0002-pr-as-delivery-unit.md`

**Purpose:** Record the decision that PRs are the central unit of delivery.

**Required sections:**

- Status: `Accepted`
- Context:
  - code, review, validation, and deployment evidence need a common anchor
- Decision:
  - every meaningful change should produce a PR unless emergency override is explicit
- Consequences:
  - no hidden implementation state
  - review and preview gates are easier to enforce
  - merge/deployment can reference one canonical artifact

---

## 3.6 Templates

Templates reduce ambiguity and keep artifacts consistent.

### `templates/implementation_plan.md`

Include fields:

- Goal
- Scope
- Out of scope
- Affected files/components
- Implementation steps
- Test strategy
- Risks
- Rollback considerations
- Acceptance criteria

---

### `templates/bugfix_plan.md`

Include fields:

- Problem statement
- Environment
- Reproduction steps
- Expected behavior
- Actual behavior
- Suspected root cause
- Fix strategy
- Regression tests
- Verification plan
- Rollback considerations

---

### `templates/github_issue_feature.md`

Include fields:

- Feature intent
- Implementation plan link/body
- Acceptance criteria
- Related branch
- Related PR
- Labels: `enhancement`

---

### `templates/github_issue_bugfix.md`

Include fields:

- Bug summary
- Reproduction steps
- Expected vs actual behavior
- Suspected root cause
- Fix plan
- Verification strategy
- Related branch
- Related PR
- Labels: `bug`

---

### `templates/pull_request.md`

Include fields:

- Summary
- Linked issue
- Implementation notes
- Test evidence
- Preview/deployment notes
- Known limitations
- Checklist:
  - scope matches plan
  - tests reported
  - no secrets
  - deployment impact understood

---

### `templates/review_report.md`

Include fields:

- PR
- Review status: approved / changes requested / blocked
- Scope review
- Code quality review
- Test evidence review
- Security review
- Required changes

---

### `templates/validation_report.md`

Include fields:

- PR
- Preview URL
- Test commands
- Smoke/E2E results
- Manual QA notes
- Go/no-go recommendation

---

### `templates/deployment_report.md`

Include fields:

- Environment
- Branch
- Commit SHA
- Artifact/image tag if applicable
- Deployment ID/platform
- URL
- Verification
- Rollback reference

---

### `templates/rollback_report.md`

Include fields:

- Incident/deployment reference
- Failed version
- Rolled-back version
- Environment
- User impact
- Verification
- Follow-up issue

---

## 4. Implementation Tasks

### Task 1: Create directory structure

**Objective:** Add the top-level artifact directories.

**Files:**

- Create directory: `skills/`
- Create directory: `playbooks/`
- Create directory: `adr/`
- Create directory: `templates/`

**Verification:**

```bash
find . -maxdepth 2 -type d | sort
```

Expected: directories listed above exist.

---

### Task 2: Add root `SOUL.md`

**Objective:** Commit the concise identity document.

**Files:**

- Create: `SOUL.md`

**Implementation notes:**

- Use the concise user-provided `SOUL.md` as the authoritative version.
- Do not paste the expanded `description.md` wholesale.

**Verification:**

```bash
grep -n "Agentic Delivery Workflow" SOUL.md
grep -n "Plan → Branch → Issue" SOUL.md
grep -n "Never" SOUL.md
```

Expected: identity, workflow, and hard rules are present.

---

### Task 3: Update `README.md`

**Objective:** Replace the minimal README with a useful repository overview.

**Files:**

- Modify: `README.md`

**Required content:**

- What ADW is.
- How the repository is structured.
- How to use the skillset.
- Safety/gate summary.

**Verification:**

```bash
grep -n "SOUL.md" README.md
grep -n "skills/" README.md
grep -n "Review" README.md
```

Expected: README references the key repository artifacts and gates.

---

### Task 4: Add core planning skills

**Objective:** Create the feature and bugfix planning skills.

**Files:**

- Create: `skills/plan_feature.md`
- Create: `skills/plan_bugfix.md`

**Verification:**

```bash
grep -n "## Preconditions" skills/plan_feature.md
grep -n "GitHub issue" skills/plan_feature.md
grep -n "suspected root cause" skills/plan_bugfix.md
```

Expected: skills define preconditions, workflow, outputs, and stop conditions.

---

### Task 5: Add implementation skills

**Objective:** Create direct and delegated implementation workflows.

**Files:**

- Create: `skills/do_impl.md`
- Create: `skills/do_impl_delegate.md`

**Verification:**

```bash
grep -n "Load the plan" skills/do_impl.md
grep -n "delegation packet" skills/do_impl_delegate.md
grep -n "Verify actual repository state" skills/do_impl_delegate.md
```

Expected: implementation workflows require a plan, preserve scope, and produce PR artifacts.

---

### Task 6: Add validation and merge skills

**Objective:** Create review/preview validation and merge/deploy workflows.

**Files:**

- Create: `skills/test_feature.md`
- Create: `skills/merge_feature.md`

**Verification:**

```bash
grep -n "Review Gate" skills/test_feature.md
grep -n "Preview" skills/test_feature.md
grep -n "Destination branch" skills/merge_feature.md
grep -n "production" skills/merge_feature.md
```

Expected: validation and merge skills enforce review, preview, and destination checks.

---

### Task 7: Add operations/supporting skills

**Objective:** Cover rollback, release promotion, regression validation, ADRs, dependency audits, and production analysis.

**Files:**

- Create: `skills/rollback_deployment.md`
- Create: `skills/promote_release.md`
- Create: `skills/validate_regression.md`
- Create: `skills/create_adr.md`
- Create: `skills/audit_dependencies.md`
- Create: `skills/analyze_production.md`

**Verification:**

```bash
grep -n "known-good" skills/rollback_deployment.md
grep -n "artifact identity" skills/promote_release.md
grep -n "Regression" skills/validate_regression.md
grep -n "Architecture Decision Record" skills/create_adr.md
grep -n "CVE" skills/audit_dependencies.md
grep -n "production feedback" skills/analyze_production.md
```

Expected: each supporting skill has a clear trigger, workflow, output, and stop condition.

---

### Task 8: Add playbooks

**Objective:** Add reusable operational procedures used by multiple skills.

**Files:**

- Create: `playbooks/preview_deployments.md`
- Create: `playbooks/pr_reviewing.md`
- Create: `playbooks/release_promotion.md`
- Create: `playbooks/incident_response.md`
- Create: `playbooks/github_traceability.md`
- Create: `playbooks/deployment_gates.md`

**Verification:**

```bash
grep -n "Preview" playbooks/preview_deployments.md
grep -n "changes requested" playbooks/pr_reviewing.md
grep -n "preview → demo → production" playbooks/release_promotion.md
grep -n "Rollback" playbooks/incident_response.md
grep -n "Closes #" playbooks/github_traceability.md
grep -n "Planning gate" playbooks/deployment_gates.md
```

Expected: playbooks capture reusable checklists and report formats.

---

### Task 9: Add ADRs

**Objective:** Record foundational workflow decisions.

**Files:**

- Create: `adr/0001-agentic-delivery-workflow.md`
- Create: `adr/0002-pr-as-delivery-unit.md`

**Verification:**

```bash
grep -n "Status: Accepted" adr/0001-agentic-delivery-workflow.md
grep -n "Status: Accepted" adr/0002-pr-as-delivery-unit.md
grep -n "PR" adr/0002-pr-as-delivery-unit.md
```

Expected: ADRs explain the workflow and PR-centric delivery model.

---

### Task 10: Add templates

**Objective:** Create reusable issue, PR, review, validation, deployment, and rollback templates.

**Files:**

- Create: `templates/implementation_plan.md`
- Create: `templates/bugfix_plan.md`
- Create: `templates/github_issue_feature.md`
- Create: `templates/github_issue_bugfix.md`
- Create: `templates/pull_request.md`
- Create: `templates/review_report.md`
- Create: `templates/validation_report.md`
- Create: `templates/deployment_report.md`
- Create: `templates/rollback_report.md`

**Verification:**

```bash
grep -n "Acceptance criteria" templates/implementation_plan.md
grep -n "Reproduction steps" templates/bugfix_plan.md
grep -n "Linked issue" templates/pull_request.md
grep -n "Go/no-go" templates/validation_report.md
grep -n "Rollback reference" templates/deployment_report.md
```

Expected: templates include all fields needed by the skills.

---

### Task 11: Cross-link artifacts

**Objective:** Make navigation explicit.

**Files:**

- Modify: `README.md`
- Modify: each `skills/*.md` where a playbook or template applies.

**Required links:**

- `skills/test_feature.md` → `playbooks/pr_reviewing.md`, `playbooks/preview_deployments.md`, `templates/validation_report.md`
- `skills/merge_feature.md` → `playbooks/deployment_gates.md`, `playbooks/release_promotion.md`, `templates/deployment_report.md`
- `skills/rollback_deployment.md` → `playbooks/incident_response.md`, `templates/rollback_report.md`
- planning skills → issue and plan templates
- implementation skills → PR template

**Verification:**

```bash
grep -R "templates/" skills README.md
grep -R "playbooks/" skills README.md
```

Expected: relevant skills point to supporting artifacts.

---

### Task 12: Final validation and commit

**Objective:** Ensure the Markdown package is internally complete and safe to review.

**Commands:**

```bash
git status --short
git diff --check
grep -R "TODO\|TBD" SOUL.md README.md skills playbooks adr templates || true
git add SOUL.md README.md PLAN.md skills playbooks adr templates
git commit -m "docs: plan initial agentic delivery skillset"
git push origin feature/initial-skills
```

**Expected:**

- `git diff --check` reports no whitespace errors.
- Any `TODO`/`TBD` occurrences are intentional and documented, or removed.
- Commit is pushed to `origin/feature/initial-skills`.

---

## 5. Next Stage Plan: Convert Flat Skills into Hermes-Compatible `SKILL.md` Packages

### Objective

After the initial ADW Markdown skillset is reviewed, convert the flat workflow definitions in `skills/*.md` into structured Hermes-compatible skill directories. This stage should preserve the same delivery semantics while making the skills loadable through Hermes' `skill_view` / `skills_list` mechanisms.

### Target outcomes

- Every ADW workflow skill exists as `skills/agentic-delivery/<skill-name>/SKILL.md`.
- Each `SKILL.md` has valid Hermes YAML frontmatter and a non-empty operational body.
- Shared playbooks and templates are referenced consistently from each skill.
- The parameter resolution contract is embedded in the skill definitions.
- The converted skills can be validated mechanically before commit.
- The README explains both forms:
  - the conceptual ADW workflow package
  - the Hermes-compatible skill package layout

### Hermes-compatible skill requirements

Each `SKILL.md` must start at byte 0 with YAML frontmatter:

```yaml
---
name: agentic-delivery-plan-feature
description: Use when planning a new feature through the Agentic Delivery Workflow. Creates or confirms plan, branch, issue, acceptance criteria, and traceability before implementation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [agentic-delivery, planning, github, delivery-workflow]
    related_skills: [agentic-delivery-do-impl, agentic-delivery-test-feature]
---
```

Hard requirements:

- `name` is present, lowercase, hyphenated, and stable.
- `description` is present and no longer than 1024 characters.
- The body is non-empty and operational.
- The file is below 100,000 characters.
- Supporting files, if embedded under a skill directory, use only approved subdirectories:
  - `references/`
  - `templates/`
  - `scripts/`
  - `assets/`

### Naming plan

Use a namespace-like prefix to avoid collisions with general-purpose Hermes skills:

```text
agentic-delivery-plan-feature
agentic-delivery-plan-bugfix
agentic-delivery-do-impl
agentic-delivery-do-impl-delegate
agentic-delivery-test-feature
agentic-delivery-merge-feature
agentic-delivery-rollback-deployment
agentic-delivery-promote-release
agentic-delivery-validate-regression
agentic-delivery-create-adr
agentic-delivery-audit-dependencies
agentic-delivery-analyze-production
```

Directory names should be shorter but still explicit:

```text
skills/agentic-delivery/plan-feature/SKILL.md
skills/agentic-delivery/plan-bugfix/SKILL.md
skills/agentic-delivery/do-impl/SKILL.md
skills/agentic-delivery/do-impl-delegate/SKILL.md
skills/agentic-delivery/test-feature/SKILL.md
skills/agentic-delivery/merge-feature/SKILL.md
skills/agentic-delivery/rollback-deployment/SKILL.md
skills/agentic-delivery/promote-release/SKILL.md
skills/agentic-delivery/validate-regression/SKILL.md
skills/agentic-delivery/create-adr/SKILL.md
skills/agentic-delivery/audit-dependencies/SKILL.md
skills/agentic-delivery/analyze-production/SKILL.md
```

### Recommended `SKILL.md` body structure

Each Hermes-compatible ADW skill should use this body shape:

```markdown
# <Human-readable skill title>

## Overview
<What the skill does and why it exists in the delivery workflow.>

## When to Use
- <Trigger 1>
- <Trigger 2>

## Inputs
### Required explicit inputs
- <Inputs that cannot be inferred safely.>

### Inferred inputs
- <Inputs the agent may discover from repo state, issue/PR metadata, or related skills.>

## Parameter Resolution
1. Inspect non-destructive context before asking.
2. If one safe assumption exists, propose it and ask for confirmation before side effects.
3. If multiple interpretations exist, ask the human to define the value explicitly.
4. Record confirmed assumptions in the delivery artifact.
5. Do not treat inferred values as approval for destructive, production, or credential-changing actions.

## Preconditions
- <Gate checks that must pass before workflow actions.>

## Workflow
1. <Operational step.>
2. <Operational step.>

## Outputs
- <Artifacts produced.>

## Stop Conditions
- <Unsafe ambiguity.>
- <Failed gate.>
- <Rejected review.>

## Status Report
<Expected concise report format.>

## Common Pitfalls
1. <Pitfall and mitigation.>

## Verification Checklist
- [ ] <Evidence requirement.>
```

### File migration map

- `skills/plan_feature.md` → `skills/agentic-delivery/plan-feature/SKILL.md`
- `skills/plan_bugfix.md` → `skills/agentic-delivery/plan-bugfix/SKILL.md`
- `skills/do_impl.md` → `skills/agentic-delivery/do-impl/SKILL.md`
- `skills/do_impl_delegate.md` → `skills/agentic-delivery/do-impl-delegate/SKILL.md`
- `skills/test_feature.md` → `skills/agentic-delivery/test-feature/SKILL.md`
- `skills/merge_feature.md` → `skills/agentic-delivery/merge-feature/SKILL.md`
- `skills/rollback_deployment.md` → `skills/agentic-delivery/rollback-deployment/SKILL.md`
- `skills/promote_release.md` → `skills/agentic-delivery/promote-release/SKILL.md`
- `skills/validate_regression.md` → `skills/agentic-delivery/validate-regression/SKILL.md`
- `skills/create_adr.md` → `skills/agentic-delivery/create-adr/SKILL.md`
- `skills/audit_dependencies.md` → `skills/agentic-delivery/audit-dependencies/SKILL.md`
- `skills/analyze_production.md` → `skills/agentic-delivery/analyze-production/SKILL.md`

### Shared artifact handling

Use one of these models and document the chosen model in `README.md`:

1. **Central shared artifacts, preferred for this repository initially**
   - Keep `playbooks/`, `templates/`, and `adr/` at repository root.
   - Each `SKILL.md` references them with relative paths.
   - Benefit: fewer duplicated files and easier review.

2. **Self-contained Hermes package**
   - Copy relevant material into each skill's allowed subdirectories.
   - Example:

     ```text
     skills/agentic-delivery/test-feature/
       SKILL.md
       references/pr-reviewing.md
       references/preview-deployments.md
       templates/validation-report.md
     ```

   - Benefit: each skill can be installed independently.
   - Cost: more duplication and sync risk.

For the next implementation stage, use central shared artifacts unless a Hermes distribution requirement proves that standalone skill directories are needed.

### Detailed implementation tasks for the Hermes-compatible stage

#### Stage 2 Task 1: Create Hermes skill directories

**Objective:** Add the target directory tree for all ADW skills.

**Files:**

- Create: `skills/agentic-delivery/*/SKILL.md` directories as listed in the naming plan.

**Verification:**

```bash
find skills/agentic-delivery -maxdepth 2 -type d | sort
```

Expected: every planned skill directory exists.

---

#### Stage 2 Task 2: Convert `plan-feature` and `plan-bugfix`

**Objective:** Convert planning workflows first because they define traceability and assumption handling for the rest of the lifecycle.

**Files:**

- Create: `skills/agentic-delivery/plan-feature/SKILL.md`
- Create: `skills/agentic-delivery/plan-bugfix/SKILL.md`

**Required content:**

- Hermes frontmatter.
- Overview and triggers.
- Required explicit inputs vs inferred inputs.
- Parameter resolution contract.
- Branch, issue, and plan creation workflow.
- Stop conditions for unsafe ambiguity.
- Output format with branch, issue, plan, risks, and next action.

**Verification:**

```bash
grep -n "^name: agentic-delivery-plan-feature" skills/agentic-delivery/plan-feature/SKILL.md
grep -n "## Parameter Resolution" skills/agentic-delivery/plan-feature/SKILL.md
grep -n "GitHub issue" skills/agentic-delivery/plan-feature/SKILL.md
grep -n "suspected root cause" skills/agentic-delivery/plan-bugfix/SKILL.md
```

Expected: planning skills are loadable, operational, and explicit about assumption handling.

---

#### Stage 2 Task 3: Convert implementation skills

**Objective:** Convert direct and delegated implementation skills while preserving PR-centric delivery.

**Files:**

- Create: `skills/agentic-delivery/do-impl/SKILL.md`
- Create: `skills/agentic-delivery/do-impl-delegate/SKILL.md`

**Required content:**

- Load plan and linked issue before editing.
- Verify branch and working tree state.
- Keep scope limited to the plan.
- Run relevant checks before PR creation.
- Produce PR artifact as the implementation output.
- For delegation, package branch, issue, plan, constraints, test commands, and expected PR output.

**Verification:**

```bash
grep -n "linked issue" skills/agentic-delivery/do-impl/SKILL.md
grep -n "delegation packet" skills/agentic-delivery/do-impl-delegate/SKILL.md
grep -n "PR" skills/agentic-delivery/do-impl/SKILL.md
```

Expected: implementation skills cannot proceed without plan/issue context and produce a PR.

---

#### Stage 2 Task 4: Convert review, preview, merge, and rollback skills

**Objective:** Convert gate-sensitive skills with strict stop conditions.

**Files:**

- Create: `skills/agentic-delivery/test-feature/SKILL.md`
- Create: `skills/agentic-delivery/merge-feature/SKILL.md`
- Create: `skills/agentic-delivery/rollback-deployment/SKILL.md`

**Required content:**

- Review gate before preview.
- Preview validation before merge.
- Merge gate before destination deployment.
- Production deployment verification and rollback reference.
- Rollback confirmation when destructive or data-affecting.

**Verification:**

```bash
grep -n "Review Gate" skills/agentic-delivery/test-feature/SKILL.md
grep -n "Preview" skills/agentic-delivery/test-feature/SKILL.md
grep -n "Merge Gate" skills/agentic-delivery/merge-feature/SKILL.md
grep -n "last known-good" skills/agentic-delivery/rollback-deployment/SKILL.md
```

Expected: gate-sensitive skills stop rather than bypassing review, preview, merge, deployment, or rollback safety requirements.

---

#### Stage 2 Task 5: Convert supporting skills

**Objective:** Convert remaining operational workflows.

**Files:**

- Create: `skills/agentic-delivery/promote-release/SKILL.md`
- Create: `skills/agentic-delivery/validate-regression/SKILL.md`
- Create: `skills/agentic-delivery/create-adr/SKILL.md`
- Create: `skills/agentic-delivery/audit-dependencies/SKILL.md`
- Create: `skills/agentic-delivery/analyze-production/SKILL.md`

**Verification:**

```bash
grep -n "artifact identity" skills/agentic-delivery/promote-release/SKILL.md
grep -n "Regression" skills/agentic-delivery/validate-regression/SKILL.md
grep -n "Architecture Decision Record" skills/agentic-delivery/create-adr/SKILL.md
grep -n "CVE" skills/agentic-delivery/audit-dependencies/SKILL.md
grep -n "production feedback" skills/agentic-delivery/analyze-production/SKILL.md
```

Expected: supporting workflows have clear triggers, inputs, outputs, and safety boundaries.

---

#### Stage 2 Task 6: Add shared reference index

**Objective:** Make cross-skill references discoverable.

**Files:**

- Create: `skills/agentic-delivery/README.md`
- Modify: root `README.md`

**Required content:**

- Skill list and lifecycle order.
- Mapping from old flat files to new Hermes-compatible skills.
- Shared playbook/template references.
- Note that repository artifacts are English; chat/status updates may be localized separately.

**Verification:**

```bash
grep -n "agentic-delivery-plan-feature" skills/agentic-delivery/README.md
grep -n "Plan → Branch → Issue" skills/agentic-delivery/README.md
grep -n "Chat/status updates may be localized separately" README.md
```

Expected: users can find and use the Hermes-compatible skill package.

---

#### Stage 2 Task 7: Validate Hermes skill frontmatter

**Objective:** Mechanically validate every `SKILL.md` before commit.

**Command:**

```bash
python3 - <<'PY'
from pathlib import Path
import re
import sys
import yaml

ok = True
for path in sorted(Path('skills/agentic-delivery').glob('*/SKILL.md')):
    content = path.read_text(encoding='utf-8')
    errors = []
    if not content.startswith('---'):
        errors.append('frontmatter does not start at byte 0')
    match = re.search(r'\n---\s*\n', content[3:])
    if not match:
        errors.append('frontmatter closing delimiter missing')
    else:
        frontmatter = content[3:match.start() + 3]
        body = content[match.end() + 3:]
        data = yaml.safe_load(frontmatter)
        if not isinstance(data, dict):
            errors.append('frontmatter is not a mapping')
        else:
            if not data.get('name'):
                errors.append('missing name')
            if not data.get('description'):
                errors.append('missing description')
            elif len(data['description']) > 1024:
                errors.append('description too long')
        if not body.strip():
            errors.append('empty body')
    if len(content) > 100_000:
        errors.append('file exceeds 100,000 chars')
    if errors:
        ok = False
        print(f'{path}: FAIL')
        for error in errors:
            print(f'  - {error}')
    else:
        print(f'{path}: OK')

if not ok:
    sys.exit(1)
PY
```

Expected: every `SKILL.md` prints `OK`.

---

#### Stage 2 Task 8: Cross-reference and language audit

**Objective:** Ensure the converted skill package is internally consistent and uses repository language policy.

**Commands:**

```bash
grep -R "skills/.*\.md" skills/agentic-delivery README.md || true
grep -R "TODO\|TBD" skills/agentic-delivery README.md playbooks templates adr || true
git diff --check
```

Expected:

- No stale links to replaced flat skill paths unless intentionally documenting migration history.
- No unresolved TODO/TBD markers.
- No whitespace errors.
- Committed artifacts remain in English.

---

#### Stage 2 Task 9: Commit and push Hermes-compatible conversion

**Objective:** Save the conversion as a focused, reviewable branch update.

**Commands:**

```bash
git status --short
git add README.md PLAN.md skills playbooks templates adr
git commit -m "docs: define Hermes-compatible agentic delivery skills"
git push origin feature/initial-skills
```

**Expected:**

- Commit contains only documentation/skill package artifacts.
- Remote branch advances successfully.
- No deployment is triggered by this docs-only branch update.

### Definition of Done for the Hermes-compatible stage

The Hermes-compatible conversion is complete when:

- Every planned ADW skill has a `SKILL.md` with valid frontmatter.
- Every skill includes parameter resolution behavior for incomplete human prompts.
- Every skill has clear preconditions, workflow steps, outputs, stop conditions, common pitfalls, and verification checklist.
- Shared playbooks/templates are referenced consistently.
- README documents how to use the Hermes-compatible skills.
- Validation script passes for all `SKILL.md` files.
- `git diff --check` passes.
- No secrets or credentials are present.
- Commit is pushed to `origin/feature/initial-skills`.

### Example Application: Full Cycle from Plan to Production with Hermes-Compatible Skills

This example assumes the ADW skills have been converted into Hermes-compatible `SKILL.md` packages and are loadable by name. The human does not need to provide every parameter up front; the agent must infer safe defaults where possible, confirm assumptions before side effects, and ask for explicit input when ambiguity is unsafe.

#### Scenario

Goal: add a CSV export button to an invoices page and ship it to production.

Repository context available to the agent:

- Current repository: `smarterworkerai/invoice-app`
- Default branch from GitHub metadata: `main`
- Existing deployment convention from repo docs: `main` deploys to production; feature branches deploy to preview
- No current linked issue or PR exists yet

---

#### Step 1: Plan with minimal human input

**Human prompt:**

```text
Use the ADW Hermes skills to plan CSV export for invoices.
```

**Required agent behavior:**

1. Load `agentic-delivery-plan-feature`.
2. Inspect non-destructive context:
   - current repo
   - default branch
   - branch state
   - existing issues/PRs mentioning CSV export
   - README or deployment docs for branch/deployment conventions
3. Identify missing parameters:
   - exact acceptance criteria
   - branch name
   - issue title
   - base branch
4. Infer safe assumptions where possible:
   - base branch: `main`
   - branch name: `feature/invoice-csv-export`
   - issue label: `enhancement`
5. Ask for confirmation before creating branch/issue:

```text
I can plan this as a feature in `smarterworkerai/invoice-app`.
Assumptions:
- base branch: `main`
- branch: `feature/invoice-csv-export`
- GitHub issue label: `enhancement`
- acceptance criteria will be drafted from common invoice CSV export behavior, then attached to the issue

Please confirm these assumptions or provide corrections.
```

**Human confirmation prompt:**

```text
Confirmed. CSV should export the currently filtered invoice list with invoice number, customer, issue date, due date, status, net, tax, and gross.
```

**Expected agent output after confirmation:**

```text
Stage: Planning complete
Branch: feature/invoice-csv-export
Issue: <GitHub issue URL>
Plan: attached to issue
Assumptions recorded: yes
Next: implementation with agentic-delivery-do-impl
```

---

#### Step 2: Implement using the Hermes implementation skill

**Human prompt:**

```text
Use agentic-delivery-do-impl for the CSV export issue.
```

**Required agent behavior:**

1. Load `agentic-delivery-do-impl`.
2. Resolve missing context by inspecting the current branch and latest linked issue.
3. If exactly one matching issue/plan exists, confirm the assumption:

```text
I found issue #41 and branch `feature/invoice-csv-export` for this work.
I will implement only that issue scope and open a PR against `main` after checks pass. Confirm?
```

4. After confirmation:
   - implement only planned scope
   - run relevant tests/builds
   - create PR
   - record test evidence in PR body

**Expected agent output:**

```text
Stage: Implementation complete
Branch: feature/invoice-csv-export
PR: <GitHub PR URL>
Validation: local checks reported in PR
Next: review and preview validation with agentic-delivery-test-feature
```

---

#### Step 3: Review and preview validation

**Human prompt:**

```text
Use agentic-delivery-test-feature on the CSV export PR.
```

**Required agent behavior:**

1. Load `agentic-delivery-test-feature`.
2. If the PR number is not provided, search for the open PR from `feature/invoice-csv-export`.
3. If exactly one PR matches, confirm:

```text
I found PR #42 from `feature/invoice-csv-export` to `main`.
I will check review status, review if needed, and only deploy preview if the PR is not rejected. Confirm?
```

4. Stop if review is rejected.
5. If acceptable, deploy preview and validate CSV export.
6. Record preview URL and validation evidence.

**Expected agent output:**

```text
Stage: Preview validation complete
PR: #42
Review: approved
Preview: <preview URL>
Tests: CSV export smoke passed
Next: merge and production deployment with agentic-delivery-merge-feature
```

---

#### Step 4: Merge and deploy to production

**Human prompt:**

```text
Use agentic-delivery-merge-feature for the validated CSV export PR.
```

**Required agent behavior:**

1. Load `agentic-delivery-merge-feature`.
2. Infer candidate PR from previous stage or open PR metadata.
3. Ask for explicit confirmation because production deployment is a side effect:

```text
I found validated PR #42 targeting `main`.
Production deployment will be triggered after merge because `main` is the production branch.
I will merge only if review is approved, checks pass, and preview validation is recorded.
Confirm merge and production deployment?
```

4. After confirmation:
   - re-check PR review state
   - re-check checks/status
   - verify preview validation evidence
   - merge according to repo policy
   - wait for production deployment
   - verify production URL and smoke test
   - record rollback reference

**Expected final report:**

```markdown
### Result
CSV export was merged and deployed to production.

### Artifacts
- Issue: https://github.com/smarterworkerai/invoice-app/issues/41
- Branch: feature/invoice-csv-export
- PR: https://github.com/smarterworkerai/invoice-app/pull/42
- Production: https://invoice-app.smarterworker.cc

### Validation
- Review: approved
- Checks: passed
- Preview: passed
- Production smoke: passed
- Deployment: verified

### Assumptions Confirmed
- Base branch: main
- Branch: feature/invoice-csv-export
- Production deploy after merge: confirmed before merge

### Notes
- Rollback reference: sha-abc123
- Open risks: none known
```

---

#### Step 5: Unsafe ambiguity example

**Human prompt:**

```text
Ship the CSV export.
```

**Required agent behavior if multiple PRs or targets exist:**

```text
I cannot safely proceed because "ship" could mean preview, demo, or production, and I found multiple candidate PRs:
- PR #42: CSV export UI
- PR #43: CSV export backend optimization

Please define explicitly:
1. which PR should be shipped
2. destination branch/environment
3. whether production deployment is approved after merge
```

The agent must not merge or deploy until the human resolves the ambiguity.

---

## 6. Definition of Done for the Initial Skillset

The initial ADW agent skillset is complete when:

- `SOUL.md` defines the agent identity and boundaries.
- Every core lifecycle stage has a skill:
  - planning
  - implementation
  - delegated implementation
  - review/preview validation
  - merge/deployment
  - rollback
- Cross-cutting playbooks exist for preview deployments, PR review, release promotion, incidents, traceability, and gates.
- Templates exist for recurring delivery artifacts.
- ADRs document the workflow and PR-centric model.
- README explains how to use the package.
- No file contains secrets, credentials, or environment-specific tokens.
- The branch contains one reviewable commit with the plan or implementation artifacts requested.

---

## 7. Example Application: Full Cycle from Plan to Production

This example shows the prompts a human can give to an ADW agent after the skillset exists. The example assumes a web application repository where `main` deploys to production and feature branches can deploy to preview.

### Scenario

Goal: add a CSV export button to an invoices page and ship it to production.

---

### Step 1: Plan the feature

**Human prompt:**

```text
Use the Agentic Delivery Workflow.
Repository: smarterworkerai/invoice-app.
Base branch: main.
Skill: /plan_feature.
Feature: add a CSV export button to the invoices page.
Acceptance criteria:
- users can export the currently filtered invoice list as CSV
- CSV contains invoice number, customer, issue date, due date, status, net, tax, gross
- export respects current UI filters
- no production deployment yet
```

**Expected agent behavior:**

- Creates `feature/invoice-csv-export`.
- Creates a GitHub issue labeled `enhancement`.
- Adds a structured implementation plan to the issue.
- Reports branch, issue, plan, and acceptance criteria.

**Expected status:**

```text
Stage: Planning complete
Artifacts: branch + issue + implementation plan
Next: implement planned scope
```

---

### Step 2: Implement the feature

**Human prompt:**

```text
Use /do_impl for the current CSV export plan.
Implement only the linked issue scope.
Create a PR against main when checks pass.
```

**Expected agent behavior:**

- Loads the issue/plan.
- Confirms it is on `feature/invoice-csv-export`.
- Implements backend/frontend changes required by the plan.
- Runs relevant tests/builds.
- Creates a PR against `main`.
- Fills PR body with summary, linked issue, tests, and deployment notes.

**Expected status:**

```text
Stage: Implementation complete
Artifacts: PR opened
Validation: local checks reported
Next: review and preview validation
```

---

### Step 3: Review and preview-test the PR

**Human prompt:**

```text
Use /test_feature on PR #42.
Check review status first.
If no review exists, review it.
If it is not rejected, deploy the branch to preview and run a smoke test for CSV export.
```

**Expected agent behavior:**

- Inspects PR #42.
- Checks existing review status.
- Performs or requests review if missing.
- Stops if review rejects the PR.
- Deploys branch to preview if review is acceptable.
- Runs a smoke test:
  - open invoices page
  - apply filter
  - click CSV export
  - verify CSV fields and filtered rows
- Reports preview URL and validation result.

**Expected status:**

```text
Stage: Preview validation complete
Review: approved or changes requested
Preview: <preview URL>
Tests: smoke/E2E result
Next: merge to production if approved
```

---

### Step 4: Merge to production branch

**Human prompt:**

```text
Use /merge_feature main for PR #42.
Merge only if review is approved, checks pass, and preview validation succeeded.
After merge, deploy main to production and report verification.
```

**Expected agent behavior:**

- Re-checks PR state.
- Confirms base/destination branch is `main`.
- Confirms PR was not rejected.
- Confirms checks and preview validation.
- Merges according to repository policy.
- Triggers production deployment for `main`.
- Verifies production URL and relevant smoke test.
- Reports deployment result and rollback reference.

**Expected final report:**

```markdown
### Result
CSV export was merged and deployed to production.

### Artifacts
- Issue: https://github.com/smarterworkerai/invoice-app/issues/41
- Branch: feature/invoice-csv-export
- PR: https://github.com/smarterworkerai/invoice-app/pull/42
- Production: https://invoice-app.smarterworker.cc

### Validation
- Review: approved
- Tests: unit/build/smoke passed
- Preview: passed
- Deployment: production verified

### Notes
- Rollback reference: sha-abc123
- Open risks: none known
```

---

### Step 5: If production validation fails

**Human prompt:**

```text
Use /rollback_deployment for the failed invoice-app production deployment.
Rollback to the last known-good version and create a follow-up bug issue with the observed regression.
```

**Expected agent behavior:**

- Identifies failed production deployment.
- Identifies last known-good version.
- Requests explicit confirmation if rollback may be destructive.
- Rolls back safely.
- Verifies production health.
- Creates a bug issue for follow-up.
- Reports impact, rollback version, verification, and next action.

---

## 8. Review Notes for This Plan

- This plan intentionally separates identity (`SOUL.md`) from executable workflow skills (`skills/`).
- The expanded `description.md` should be treated as source material for the skillset, not committed as the final `SOUL.md`.
- The initial implementation should be documentation-only and safe to review.
- The next planned iteration converts `skills/*.md` into Hermes-compatible `SKILL.md` directories under `skills/agentic-delivery/*/SKILL.md`.
- Human prompts may omit parameters; skills must define when the agent may infer-and-confirm assumptions versus when it must ask for explicit human input.
