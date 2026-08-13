---
name: angular-upgrade
description: 'Angular version upgrade patterns: migration guides, dependency updates, breaking changes, incremental updates, and regression testing. Trigger: When upgrading Angular major versions or migrating from legacy patterns to standalone/signals.'
version: 1.0
metadata:
  phase:
    - operations
  layer:
    - frontend
  enforcement: optional
  depends_on:
    - angular
  consumed_by:
    - framework-operations-evolution
  agent_roles:
    - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Provide a repeatable process for upgrading Angular applications and migrating from legacy patterns (NgModules, RxJS-heavy state) to modern patterns (standalone components, signals).

## When to use this skill

Activate when:
- Upgrading Angular to a new major version
- Migrating from NgModules to standalone components
- Refactoring to signals-based state management

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `angular` | depends_on | Base patterns |
| `typescript` | depends_on | Type changes |
| `framework-operations-evolution` | consumer | Deprecation/version policy |

## Critical Rules

1. Upgrade one major version at a time (e.g., 16 → 17 → 18).
2. Run `ng update` and follow Angular Update Guide.
3. Migrate to standalone components incrementally per module.
4. Keep a feature branch and run full regression suite.
5. Update lint rules, test config, and third-party deps together.

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Upgrade plan | `docs/operations/angular-upgrade-{version}.md` | Steps and risks |
| Migration script | Codemod (`ng generate @angular/core:standalone`) — crear en el proyecto si aplica | Codemod if needed |
| Test report | CI output | Regression results |

## Example: ng update

```bash
ng update @angular/core@17 @angular/cli@17
ng update @angular/material@17
ng generate @angular/core:standalone
```

## Checklist

- [ ] Upgrade plan approved
- [ ] `ng update` ran without errors
- [ ] Standalone migration applied incrementally
- [ ] Tests pass (unit + E2E)
- [ ] Third-party deps compatible
- [ ] Breaking changes documented
