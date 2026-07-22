---
name: a11y-testing
description: 'Automated accessibility testing: axe-core, Playwright a11y snapshots, keyboard navigation tests, and WCAG 2.2 AA validation. Trigger: When implementing accessibility tests, auditing components, or validating WCAG compliance.'
version: 1.0
metadata:
  phase:
    - quality
  layer:
    - frontend
    - testing
  enforcement: recommended
  depends_on:
    - accesibilidad
    - playwright
  consumed_by:
    - security-testing
    - uat-acceptance
  agent_roles:
    - control-agent
    - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define automated accessibility testing for React applications using axe-core, Playwright, and keyboard navigation tests to ensure WCAG 2.2 AA compliance.

## When to use this skill

Activate when:
- Adding a11y tests to CI
- Auditing components for WCAG compliance
- Validating keyboard navigation and screen reader support

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `accesibilidad` | depends_on | A11y implementation patterns |
| `playwright` | depends_on | E2E test framework |
| `security-testing` | consumer | Quality gate |

## Critical Rules

1. Run axe-core in unit tests (Jasmine/Karma) and E2E tests (Playwright).
2. Test keyboard navigation for every interactive flow.
3. Verify focus management on route changes and modals.
4. Fail CI on critical or serious axe violations.
5. Test with at least one screen reader scenario per critical flow.

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| A11y test utility | `src/testing/a11y.ts` | axe-core wrapper |
| E2E a11y tests | `e2e/a11y/*.spec.ts` | Playwright + axe |
| Keyboard tests | `e2e/keyboard/*.spec.ts` | Tab/Enter/Space flows |

## Example: Playwright + axe

```typescript
import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

test('homepage has no accessibility violations', async ({ page }) => {
  await page.goto('/');
  await injectAxe(page);
  await checkA11y(page, undefined, {
    includedImpacts: ['critical', 'serious', 'moderate']
  });
});
```

## Checklist

- [ ] axe-core integrated in unit/E2E tests
- [ ] Keyboard navigation tests for critical flows
- [ ] Focus management verified
- [ ] CI fails on critical/serious violations
- [ ] Screen reader scenarios documented
