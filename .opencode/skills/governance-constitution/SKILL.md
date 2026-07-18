---
name: governance-constitution
description: 'Constitutional governance: immutable project principles, non-negotiable rules, architecture gates, anti-patterns. Trigger: When establishing project governance, creating a project constitution, or defining non-negotiable principles for code quality and architecture.'
version: 1.0
metadata:
  phase:
    - governance
  layer:
    - governance
  enforcement: mandatory
  depends_on:
    - framework-governance
  consumed_by:
    - framework-architecture
    - framework-security
  agent_roles:
    - design-agent
    - control-agent
  validation_profile: architecture
  mcp_usage: none
---

## Purpose

Define the constitutional governance pattern for projects in the framework. A constitution is a set of immutable principles that govern all code generation, design decisions, and implementation choices. Modeled after the Spec Kit constitution pattern with 9 articles, this skill ensures every agent and every decision respects the project's foundational principles. The constitution is validated automatically via `/analyze` gates before any code is committed.

## When to use this skill

Activate this skill when:

- Starting a new project and defining its architectural principles
- Establishing non-negotiable rules that all agents must follow
- Setting up Phase -1 gates (quality gates that run before any code is written)
- Defining anti-patterns that must never appear in the codebase
- Creating a shared understanding of "what good looks like" for the project

**Do not** activate when:

- Defining per-skill rules (those go in each SKILL.md)
- Configuring CI/CD pipelines (use `ci-cd`)
- Setting up RBAC (use `authorization`)

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `framework-governance` | Predecesora | Constitution inherits and extends framework governance |
| `framework-architecture` | Consumidora | Architecture decisions must pass constitution gates |
| `code-review` | Consumidora | Reviews validate against constitution principles |

## Constitution Template

Every project must define a `constitution.md` with these 9 articles:

### Article 1: Core Principles

```markdown
## Article 1: Core Principles

The following principles are NON-NEGOTIABLE and govern all code in this project:

1. **[Principle Name]**: [One sentence defining the principle]
2. ...

**Phase -1 Gate**: Before ANY code is written, verify that the proposed design
respects ALL core principles. If any principle is violated, stop and redesign.
```

### Article 2: Stack & Dependencies

```markdown
## Article 2: Stack & Dependencies

- **Language(s)**: [Python 3.12 / TypeScript / etc.]
- **Framework(s)**: [FastAPI / Angular / Bun / etc.]
- **Database**: [PostgreSQL 16 + pgvector]
- **Library-First Rule**: New functionality MUST be implemented as a reusable
  library before being integrated into an application.
- **Dependency Addition Gate**: Adding a new dependency requires:
  1. Justification document
  2. Comparison with 2+ alternatives
  3. License compatibility check
```

### Article 3: CLI Interface

```markdown
## Article 3: CLI Interface

- Every new feature MUST expose a CLI interface before any GUI or API.
- CLI must support: --help, --verbose, --quiet, --json (machine-readable)
- CLI must validate all inputs and provide clear error messages.
```

### Article 4: Test-First (NON-NEGOTIABLE)

```markdown
## Article 4: Test-First

**NON-NEGOTIABLE**: All code MUST be written test-first.

1. Write the test that defines the expected behavior.
2. Run the test — it MUST fail (red).
3. Write the minimum code to pass the test (green).
4. Refactor while keeping tests green.

**Gate**: No code is accepted without corresponding tests that:
- Cover the happy path
- Cover edge cases
- Cover error conditions
- Run in CI pipeline
```

### Article 5: Integration Testing

```markdown
## Article 5: Integration Testing

- Every external interface MUST have integration tests:
  - Database operations
  - API endpoints
  - Message queue consumers/producers
  - File I/O
  - External service calls (mocked with contract tests)

- Integration tests run against real dependencies (TestContainers).
```

### Article 6: Observability

```markdown
## Article 6: Observability

- Every service MUST expose: health endpoint, metrics, structured logging.
- Tracing MUST propagate correlation IDs across service boundaries.
- LLM calls MUST be tracked in Langfuse.
- Error budgets defined as SLOs (99.9% availability, P95 < 200ms).
```

### Article 7: Versioning & Breaking Changes

```markdown
## Article 7: Versioning & Breaking Changes

- Semantic versioning: MAJOR.MINOR.PATCH.
- Breaking changes: deprecation warning for ONE major version before removal.
- API versioning via URI: /api/v{N}/resource.
- CHANGELOG.md updated with every release.
```

### Article 8: Simplicity

```markdown
## Article 8: Simplicity

- Prefer simple solutions over clever ones.
- If a junior developer cannot understand the code after reading it once, it's too complex.
- DRY is a guideline, not a religion. Some duplication is acceptable if it improves clarity.
- Maximum function length: 30 lines. Maximum file length: 500 lines.
```

### Article 9: Anti-Abstraction

```markdown
## Article 9: Anti-Abstraction

- Do NOT create abstractions for hypothetical future use cases.
- One concrete implementation before one interface.
- Interfaces are only justified when there are 2+ production implementations.
- If you're not sure you need an abstraction, you don't need it.
```

## Phase -1 Gates

Before any code is written, the following gates MUST pass:

| Gate | Question | Pass Condition |
|------|----------|---------------|
| **Simplicity Gate** | Is this the simplest possible solution? | No unnecessary abstractions, patterns, or complexity |
| **Anti-Abstraction Gate** | Do we need every abstraction? | All abstractions justified by current (not future) use cases |
| **Integration-First Gate** | How will this be tested end-to-end? | Integration test plan exists before implementation |
| **Library-First Gate** | Can this be a reusable library? | Functionality extracted before application integration |
| **Test-First Gate** | Are tests defined before code? | Test suite skeleton exists and fails |

## Anti-Patterns (Must Never Appear)

```markdown
## Forbidden Patterns

The following patterns MUST NEVER appear in this codebase:

1. **God Classes**: Classes with >10 public methods or >500 lines.
2. **Magic Numbers**: Unnamed numeric literals in business logic.
3. **Silent Failures**: Catching exceptions without logging or re-raising when appropriate.
4. **Hardcoded Secrets**: API keys, passwords, tokens in code.
5. **SELECT * in Production**: Always explicit column lists.
6. **N+1 Queries**: Always eager-load or batch-query.
7. **Mixing Concerns**: Business logic in controllers/handlers.
```

## Constitution Validation

```python
# Phase -1 validation that runs before any code generation
class ConstitutionValidator:
    def __init__(self, constitution: Constitution):
        self.constitution = constitution
        self.violations: list[Violation] = []
    
    def validate_design(self, design: Design) -> list[Violation]:
        self.check_simplicity(design)
        self.check_anti_abstraction(design)
        self.check_integration_first(design)
        self.check_library_first(design)
        self.check_test_first(design)
        return self.violations
    
    def validate_code(self, code: Code) -> list[Violation]:
        self.check_forbidden_patterns(code)
        self.check_dependency_additions(code)
        self.check_breaking_changes(code)
        return self.violations

# Usage in governance pipeline
constitution = load_constitution("constitution.md")
validator = ConstitutionValidator(constitution)

violations = validator.validate_design(proposed_design)
if violations:
    raise GovernanceViolation(
        f"Design violates constitution: {violations}"
    )
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|-------------------|
| Add new dependency | Just `pip install` | Justification doc + comparison + license check |
| Need an interface | Create it immediately | Wait for 2+ concrete implementations |
| Function growing | "I'll refactor later" | Split or simplify now |
| Test seems hard | Skip it | The test IS the specification |
| Found a pattern violation | Leave it | Flag immediately, fix in this PR |

## Verification checklist

- [ ] All 9 articles defined for the project
- [ ] Phase -1 gates validated before implementation
- [ ] Anti-patterns documented and enforced
- [ ] Constitution loaded by all agents at session start
- [ ] Violations tracked and resolved
- [ ] Constitution version-controlled
