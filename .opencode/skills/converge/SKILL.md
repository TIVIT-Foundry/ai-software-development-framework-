---
name: converge
description: 'Verify that implemented code matches its spec (api-first-spec or
  feature-spec) and that all tasks in tasks.md are actually done, before a PR is
  created. Trigger: Before creating a PR for a spec-driven feature, or when asked
  to check spec-code alignment.'
version: 1.1
metadata:
  phase:
  - quality
  layer:
  - testing
  enforcement: recommended
  depends_on:
  - api-first-spec
  - feature-spec
  - tasks
  consumed_by:
  - acceptance-test-automation
  - framework-qa-validation
  - pull-request
  - sdd-onboard
  agent_roles:
  - control-agent
  validation_profile: skill-contract
mcp_usage: none
---

## Purpose

Catch the gap between "the spec says X" and "the code actually does X" before it reaches review. Without this, spec-driven development degrades into spec-then-forget: the spec is written once, implementation drifts, and nobody notices until a bug report. This skill is the **Converge** phase referenced by `sdd-onboard` — it is what makes "spec-first" a closed loop instead of a one-way door.

## Honesty about what this is today

This skill is an **agent-executed review checklist**, not a deterministic script. The control agent reads the spec, reads the diff/code, and reports mismatches — the same trust model as every other skill in this framework. It catches structural and behavioral drift reliably; it does not guarantee byte-for-byte conformance the way a parser-based diff would.

A deterministic version is a natural next step: `.opencode/scaffold/generate.py` already parses `api-first-spec` markdown (entities, endpoints, DTOs) — that parser could be extended into a standalone checker that diffs a spec against generated route/schema files and runs in CI. That is future work, tracked as a `framework-operations-evolution` candidate, not something this skill claims to do today.

Note the scope split: this skill catches **structural** drift (spec says X, code doesn't implement X). It does not execute acceptance criteria to catch **behavioral** drift (code implements X, but not correctly for real inputs) — that is what `acceptance-test-automation` does, feeding the same go/no-go decision from a different angle.

## When to use this skill

Activate when:
- A feature implemented from `api-first-spec` or `feature-spec` is ready for PR
- Someone asks "does this match the spec?" mid-implementation
- `framework-qa-validation` needs traceability evidence for a go/no-go gate

**Do not** activate when:
- There is no spec to converge against — nothing to check
- The change is a trivial bugfix with no spec (expected — not every change needs one)

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|--------------|
| `api-first-spec` / `feature-spec` | Input | The source of truth this skill checks against |
| `tasks` | Input | Verifies each task's `Verify` step actually passes |
| `framework-qa-validation` | Consumer | Uses this as one input to the go/no-go decision |
| `pull-request` | Consumer | Should run before the PR is opened, not after |
| `acceptance-test-automation` | Consumer | Runs alongside this skill's structural check to add behavioral evidence (acceptance criteria pass/fail) |

## What the agent must do

1. Read the spec (`docs/specs/{feature-name}.md` or `docs/api-first/{MODULE}.md`) in full.
2. Read the corresponding `tasks.md`, if one exists.
3. Read the actual diff/implementation — not a summary of it.
4. For each spec requirement (Behavior Spec entries, Endpoints, Business Rules, Error Codes), find the implementing code and confirm it matches. Mark anything that doesn't as a mismatch.
5. For each task's `Verify` step, confirm it actually holds — run the test if one exists, reason through it if not.
6. Report **extra behavior not in the spec** too, not just missing behavior — undocumented surface area is its own risk.
7. Produce the traceability report below. Do not silently fix mismatches while writing the report — report first, fix as a separate explicit step.

## Critical Rules

1. **Read the code, not a description of the code.** Summaries hide drift.
2. **A missing test is a mismatch.** If the spec has a testable requirement and no test covers it, that's a finding, not a pass.
3. **Extra endpoints/fields/branches not in the spec are findings.** Silent scope creep is exactly what this phase exists to catch.
4. **No partial credit in the report.** A requirement is Met, Not Met, or Partially Met with an explicit reason — never left ambiguous.
5. **This runs before the PR, not as part of PR review.** Catching drift here is cheaper than catching it in review.

## Outputs produced

| Artifact | Format | Description |
|----------|--------|--------------|
| Traceability report | Markdown, inline or `docs/specs/{feature-name}.converge.md` | Spec requirement → implementation location → status |

## Template

```markdown
# Converge report: {feature-name}

Spec: docs/specs/{feature-name}.md
Tasks: docs/specs/{feature-name}.tasks.md

## Requirement traceability

| Spec requirement | Implementation | Status | Notes |
|-------------------|----------------|--------|-------|
| Given no permission, Export button hidden | `ExportButton.tsx:14` | Met | — |
| Export >10k rows queues background job | `export.api.ts` | Not Met | Still synchronous — spec assumed async |
| (undocumented) Retry button on failed export | `ExportButton.tsx:32` | Extra | Not in spec — confirm intended, then update spec |

## Task verification

| Task | Verify step | Result |
|------|-------------|--------|
| T1 | Submitting valid credentials navigates to /dashboard | Pass |
| T2 | Invalid credentials show inline error | Fail — error shown as toast, not inline |

## Decision

[CONVERGED / NOT CONVERGED — N mismatches found]
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|---------------------|
| Code does more than the spec says | Ignore it, it's "just extra" | Report as Extra — either update the spec or remove the behavior |
| Spec requirement has no matching code | Assume it was skipped intentionally | Report as Not Met; confirm with the author before closing |
| Task's Verify step wasn't actually run | Mark Pass because the code "looks right" | Run it or mark it unverified — never assume |
| Small last-minute fix, no time for full converge | Skip converge entirely | Run a scoped converge on just the changed requirements |

## Verification checklist

- [ ] Every spec requirement has a traceability row (Met/Not Met/Partially Met)
- [ ] Every task's Verify step was actually checked, not assumed
- [ ] Extra/undocumented behavior is called out explicitly
- [ ] Report has an explicit CONVERGED/NOT CONVERGED decision
- [ ] If NOT CONVERGED, mismatches are fixed (or the spec is updated) before the PR is opened
