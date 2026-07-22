---
name: tasks
description: 'Break a spec (api-first-spec or feature-spec) into ordered, small,
  independently verifiable implementation tasks. Trigger: When a spec is approved
  and ready to move into implementation, or when re-planning after scope changes
  mid-feature.'
version: 1.0
metadata:
  phase:
  - inception
  layer:
  - business
  enforcement: recommended
  depends_on:
  - api-first-spec
  - feature-spec
  consumed_by:
  - converge
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: documentation
mcp_usage: none
---

## Purpose

Turn an approved spec into a `tasks.md`: an ordered list of small units of work, each completable in 2-4 hours and independently verifiable with a test. This is the missing link between "we know what to build" (spec) and "we're building it" (skill execution) — without it, a large spec gets implemented as one undifferentiated blob, which is exactly what `converge` (spec-to-code verification) has no clean way to check incrementally.

## When to use this skill

Activate when:
- A `feature-spec` or `api-first-spec` has been approved and has no open `[NEEDS CLARIFICATION]` markers
- Scope changed mid-implementation and the task list needs re-planning
- A large feature needs to be handed off across multiple implementation sessions or people

**Do not** activate when:
- The change is a single-file bugfix with an obvious, unambiguous scope — the spec/tasks overhead isn't worth it
- The spec itself isn't finished yet — finish it first

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|--------------|
| `api-first-spec` / `feature-spec` | Input | The spec this skill decomposes |
| `converge` | Consumer | Verifies each task's implementation against its acceptance criteria |
| `SKILL-EXECUTION-PROTOCOL` | Complementary | Each task is typically executed as one pass through the 7-step skill protocol |

## Critical Rules

1. **A task is 2-4 hours of work, not 20 minutes and not 2 days.** Fewer than that: merge with a neighbor. More than that: split it.
2. **Every task has an explicit verification step.** "Write the login form" is incomplete. "Write the login form; verify: submitting valid credentials navigates to /dashboard, submitting invalid credentials shows an inline error" is a task.
3. **Tasks are ordered by dependency, not by convenience.** Data model before service layer before UI, unless there's a documented reason to parallelize.
4. **Tests are part of the task, not a separate task.** "Implement X" implicitly includes "and its tests" — never split "write code" and "write tests" into two tasks for the same unit of behavior.
5. **Re-planning is expected, not a failure.** If reality diverges from the task list mid-implementation, update `tasks.md` — don't silently drift from it.

## Outputs produced

| Artifact | Path | Description |
|----------|------|--------------|
| Task list | `docs/specs/{feature-name}.tasks.md` | Ordered, numbered tasks with verification steps |

## Template

```markdown
# Tasks: {feature-name}

Spec: docs/specs/{feature-name}.md

## T1 — {short title}
**Depends on:** none
**Estimate:** 2h
**Work:** {what to build, in implementation terms — this is where file/component names belong, unlike the spec}
**Verify:** {test or manual check that proves this task is done}

## T2 — {short title}
**Depends on:** T1
**Estimate:** 3h
**Work:** ...
**Verify:** ...
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|---------------------|
| Task has no clear verification step | Write it anyway | Split or clarify until it has one |
| 50 tiny tasks for a small feature | Keep them all | Merge related ones — over-decomposition is as bad as under-decomposition |
| A task depends on an external team's work | Silently block | Mark `**Depends on:** [EXTERNAL: team/system]` and flag it |
| Mid-implementation scope change | Keep coding against the stale list | Update `tasks.md` first, then continue |

## Verification checklist

- [ ] Every task has a `Depends on`, `Estimate`, `Work`, and `Verify` field
- [ ] No task estimated above 4 hours (split it) or below ~1 hour (merge it)
- [ ] Task order respects dependencies (no task references work from a later task)
- [ ] Tests are embedded in the task they belong to, not split out
- [ ] The list traces back to specific sections of the source spec — no task should be un-traceable to a requirement
