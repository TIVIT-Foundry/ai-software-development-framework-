---
name: feature-spec
description: 'Generate a spec-first document for features without a REST API surface
  (UI-only work, data-only migrations, cross-cutting changes). Trigger: When specifying
  a feature that api-first-spec does not cover — no new endpoints, or the endpoints
  already exist and only UI/data behavior is changing.'
version: 1.0
metadata:
  phase:
  - inception
  layer:
  - business
  enforcement: recommended
  depends_on:
  - hu-template
  consumed_by:
  - converge
  - framework-conception
  - sdd-onboard
  - tasks
  agent_roles:
  - design-agent
  validation_profile: documentation
mcp_usage: none
---

## Purpose

Give every feature a spec before code, not just the ones with a REST API. `api-first-spec` is mandatory and rigorous for backend-surfaced modules (ERD, endpoints, DTOs, error codes), but a UI-only feature, a data-migration-only feature, or a cross-cutting change (e.g. adding a new permission check across five screens) has no natural home in that structure. Without one, those features fall back to `hu-template` alone, which is lighter-weight and not testable the way a spec needs to be.

This skill closes that gap: same spec-first discipline as `api-first-spec`, without forcing an API section that doesn't apply.

## When to use this skill

Activate when:
- The feature touches no new backend endpoints (pure frontend, pure data, or config-only)
- Existing endpoints are reused unchanged and only business logic/UI changes
- A cross-cutting change spans multiple modules and doesn't belong to one API spec

**Do not** activate when:
- The feature introduces or changes REST endpoints → use `api-first-spec`
- You only need a short description for planning, not a testable spec → `hu-template` alone is enough

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|--------------|
| `hu-template` | Input | User stories provide scope and initial acceptance criteria |
| `api-first-spec` | Sibling | Same discipline, for features with a REST API surface |
| `tasks` | Consumer | Breaks this spec into ordered, verifiable implementation tasks |
| `converge` | Consumer | Verifies the final code matches this spec |
| `framework-conception` | Consumer | Uses this spec as input for framework-level conception work |

## Document structure

Produce `docs/specs/{feature-name}.md` with these sections — skip a section only if genuinely not applicable, and say so explicitly rather than leaving it out silently:

| # | Section | Content | When required |
|---|---------|---------|----------------|
| 1 | **Scope** | Included/excluded behavior, boundaries | Always |
| 2 | **Actors & Triggers** | Who/what initiates this feature, under what conditions | Always |
| 3 | **Data Touched** | Entities read/written, even if no schema changes | If the feature reads or writes data |
| 4 | **Behavior Spec** | Testable statements: "Given X, when Y, then Z" | Always |
| 5 | **UI States** | Loading, empty, error, success, disabled — per screen/component | If the feature has UI |
| 6 | **Business Rules** | Validation, permissions, edge cases | Always |
| 7 | **Non-Goals** | What this explicitly does not do, to prevent scope creep | Always |
| 8 | **Acceptance Criteria** | Checklist a reviewer can verify without reading the code | Always |

## Critical Rules

1. **Every requirement must be testable.** "The list should feel fast" is not a requirement. "The list renders within 200ms for 50 items" is.
2. **No implementation details in the spec.** Component names, hook names, file paths belong in the plan/implementation, not here — the spec describes behavior, not code.
3. **Non-Goals are mandatory, not optional.** A spec without an explicit boundary invites scope creep during implementation.
4. **Unclear requirements get flagged, not guessed.** Mark them `[NEEDS CLARIFICATION: ...]` and resolve before moving to `tasks`.
5. **The spec is versioned with the code.** Store it in `docs/specs/`, update it if behavior changes — it is not a write-once artifact.

## Outputs produced

| Artifact | Path | Description |
|----------|------|--------------|
| Feature spec | `docs/specs/{feature-name}.md` | The 8-section document above |
| Open questions | Inline `[NEEDS CLARIFICATION: ...]` markers | Must be resolved before `tasks` starts |

## Example: Behavior Spec entries

```markdown
## Behavior Spec

- Given a user without the `reports:export` permission, when they open the reports page,
  then the Export button is not rendered (not just disabled).
- Given an export in progress, when the user navigates away and back,
  then the export continues in the background and the progress indicator resumes.
- Given an export request for >10,000 rows, when the user clicks Export,
  then the system queues a background job instead of a synchronous download.
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|---------------------|
| Feature adds a new endpoint | Write a `feature-spec` | Use `api-first-spec` instead |
| Requirement is vague ("should be intuitive") | Write it down as-is | Rewrite as a testable Given/When/Then, or flag `[NEEDS CLARIFICATION]` |
| Spec section doesn't apply | Leave it blank | State explicitly why it's skipped |
| Spec finished, code diverges later | Leave the spec stale | Update the spec alongside the code change |

## Verification checklist

- [ ] All 8 sections present or explicitly marked not applicable
- [ ] Every Behavior Spec entry is testable (Given/When/Then or equivalent)
- [ ] Non-Goals section is not empty
- [ ] No `[NEEDS CLARIFICATION]` markers remain before handoff to `tasks`
- [ ] Acceptance Criteria checklist is verifiable without reading the implementation
