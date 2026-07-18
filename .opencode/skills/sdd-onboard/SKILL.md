---
name: sdd-onboard
description: 'Spec-Driven Development onboarding: SDD workflow phases, role-based onboarding path, mental model, first-week checklist, common pitfalls and their solutions. Trigger: When onboarding new developers to SDD workflow, training teams, or first-time SDD project setup.'
version: 1.0
metadata:
  phase:
    - inception
  layer:
    - business
  enforcement: recommended
  depends_on:
    - governance-constitution
  consumed_by:
    - project-bootstrap
  agent_roles:
    - design-agent
  validation_profile: documentation
  mcp_usage: none
---

## Purpose

Define the onboarding pattern for teams adopting Spec-Driven Development in the framework. Moves developers from "code-first" to "spec-first" thinking through a structured learning path with role-based milestones, a first-week checklist, and a catalog of common pitfalls that new SDD practitioners face. Ensures teams can adopt SDD without disruption to existing workflows.

## When to use this skill

Activate this skill when:

- Onboarding a new team member to an SDD project
- Migrating an existing project to SDD
- Training developers on the spec-first workflow
- Creating onboarding documentation for an SDD project

**Do not** activate when:

- Explaining a single SDD phase (use phase-specific skills)
- Configuring SDD tooling (use spec-kit or project-bootstrap)
- Defining project governance (use `governance-constitution`)

## SDD Mental Model

### The Big Mindset Shift

| Old Way (Code-First) | New Way (Spec-First) |
|----------------------|---------------------|
| "I'll figure it out as I code" | "The spec is the blueprint" |
| Specs are documentation you write after | Specs are executable — they generate code |
| Tests come after implementation | Tests ARE the specification |
| PR reviews catch design issues | Design issues are caught at spec phase |
| "It works" is good enough | "It passes the spec gates" is the minimum |

### The 6 Phases of SDD

```
Constitution ──► Specify ──► Plan ──► Tasks ──► Implement ──► Converge
  (principles)    (what)    (how)   (steps)    (code)       (verify)
```

| Phase | Question | Output | Duration |
|-------|----------|--------|----------|
| **Constitution** | What principles govern everything? | `constitution.md` | Once per project |
| **Specify** | What are we building and why? | `spec.md` | 1-4 hours |
| **Plan** | How will we build it, technically? | `plan.md` | 1-2 hours |
| **Tasks** | What are the ordered, executable steps? | `tasks.md` | 30 min - 1 hour |
| **Implement** | Execute each task, test-first | Code + tests | Per sprint |
| **Converge** | Does the code match the spec? | Acceptance report | At milestones |

## Role-Based Onboarding Path

### Developer Path

**Week 1: Understand the workflow**
- [ ] Day 1: Read the constitution. Understand the 9 non-negotiable principles.
- [ ] Day 2: Pair with a senior on a Specify phase. Learn to write a good spec.
- [ ] Day 3: Implement a task from an existing tasks.md. See spec→code in action.
- [ ] Day 4: Write your first spec. Have it reviewed by a senior.
- [ ] Day 5: Run converge on your work. Fix spec-code mismatches.

**Week 2: Own the workflow**
- [ ] Lead a specify session for a small feature
- [ ] Generate a plan from your spec
- [ ] Break the plan into tasks
- [ ] Implement all tasks test-first
- [ ] Run converge independently

### Tech Lead Path

**Week 1: Master the process**
- [ ] Review the constitution with the team. Clarify ambiguities.
- [ ] Review 2-3 specs from team members. Focus on "what" not "how".
- [ ] Establish spec quality bar for the team.

**Week 2: Govern the workflow**
- [ ] Run analyze on specs to detect cross-artifact inconsistencies
- [ ] Establish review cadence: daily for tasks, per-feature for specs
- [ ] Set up SDD CI gates: constitution check, spec-to-code traceability

### Architect Path

**Week 1: Shape the system**
- [ ] Own the constitution. Every architectural decision flows from it.
- [ ] Review all plans. Ensure technical approach respects constitution.
- [ ] Establish anti-pattern catalog for the codebase.

**Week 2: Evolve the system**
- [ ] Propose constitution amendments (requires team consensus)
- [ ] Run analysis on accumulated specs. Identify emerging patterns.
- [ ] Maintain the "why" documentation — reasons behind architectural choices

## First-Week Checklist

```markdown
## SDD Onboarding Checklist

### Environment Setup
- [ ] SDD tool installed (Spec Kit CLI or equivalent)
- [ ] IDE extensions configured (SDD templates, spec validation)
- [ ] Project cloned and running locally

### Knowledge Foundation
- [ ] Constitution read and understood
- [ ] At least 1 existing spec reviewed (see `/specs/` directory)
- [ ] At least 1 existing plan reviewed (see `/plans/` directory)
- [ ] At least 1 implementation trace reviewed (see spec→code)

### First Hands-On
- [ ] Implement 1 task from existing tasks.md
- [ ] Write tests first, then code
- [ ] Run converge to verify spec-code alignment
- [ ] Submit for review

### Reflection
- [ ] Discuss: What was different from your previous workflow?
- [ ] Discuss: What felt natural? What felt forced?
- [ ] Identify 1 improvement to the SDD process for your team
```

## Common Pitfalls & Solutions

### Pitfall 1: "The spec is a wish list, not a contract"

**Symptom:** Spec says "users can search" but implementation doesn't match.
**Root cause:** Spec written without implementation in mind — too vague.
**Solution:** Every spec requirement must be testable. If you can't write a test for it, it's not a requirement.

```markdown
# Bad spec requirement
"The system should be fast."

# Good spec requirement
"Search results for queries with <1000 records must return in <200ms (P95)."
```

### Pitfall 2: "Plan is a duplicate of spec"

**Symptom:** Plan just repeats spec with different words.
**Root cause:** Developer doesn't understand the difference between "what" and "how".
**Solution:** Spec = problem domain language. Plan = technical domain language (APIs, tables, services).

### Pitfall 3: "Tasks are too granular"

**Symptom:** 50 tiny tasks that could be 10.
**Root cause:** Over-decomposition. Every code change doesn't need a separate task.
**Solution:** A task is a unit of work that can be completed in 2-4 hours and verified with tests.

### Pitfall 4: "Implement phase ignores the spec"

**Symptom:** Developer codes what they think is right, not what the spec says.
**Root cause:** Developer doesn't trust the spec or didn't read it.
**Solution:** Converge phase catches this. Make converge mandatory before PR review.

### Pitfall 5: "Converge is skipped for small changes"

**Symptom:** "It was just a small fix, I didn't need converge."
**Root cause:** Converge feels like overhead for small changes.
**Solution:** Automate converge via CI. If it takes <2 min, no one skips it.

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|-------------------|
| New developer joins | "Read the docs" | Structured onboarding with mentor |
| Spec is ambiguous | Guess and code | Clarify phase: mark [NEEDS CLARIFICATION] |
| Plan is too detailed | Accept it | Push back — plan is "how", not "step by step" |
| Task takes >4 hours | Keep going | Break it down further |
| Converge finds mismatches | "Ship it anyway" | Fix mismatches before merge |

## Verification checklist

- [ ] Onboarding path defined per role
- [ ] First-week checklist available
- [ ] Common pitfalls documented with solutions
- [ ] SDD phases clearly differentiated
- [ ] Spec-quality bar established
- [ ] Converge phase automated in CI
- [ ] Constitution accessible to all team members
