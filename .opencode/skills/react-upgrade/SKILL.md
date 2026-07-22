---
name: react-upgrade
description: 'React/Vite/Next.js version upgrade patterns: migration guides, dependency updates, breaking changes, incremental updates, and regression testing. Trigger: When upgrading React, Vite, or Next.js major versions or migrating from class components/legacy patterns to hooks.'
version: 2.0
metadata:
  phase:
    - operations
  layer:
    - frontend
  enforcement: optional
  depends_on:
    - react
  consumed_by:
    - framework-operations-evolution
  agent_roles:
    - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Provide a repeatable process for upgrading React applications (Vite or Next.js) and migrating from legacy patterns (class components, HOCs-heavy state) to modern patterns (function components, hooks).

## When to use this skill

Activate when:
- Upgrading React to a new major version
- Upgrading Vite or Next.js to a new major version
- Migrating from class components to function components + hooks

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|--------------|
| `react` | depends_on | Base patterns |
| `typescript` | depends_on | Type changes |
| `framework-operations-evolution` | consumer | Deprecation/version policy |

## Critical Rules

1. Upgrade one major version at a time (e.g., React 17 → 18 → 19).
2. Read the official React/Next.js/Vite upgrade guide before touching code.
3. Migrate class components to function components + hooks incrementally per feature.
4. Keep a feature branch and run the full regression suite (unit + Playwright E2E).
5. Update lint rules (`eslint-plugin-react-hooks`), test config, and third-party deps together.

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Upgrade plan | `docs/operations/react-upgrade-{version}.md` | Steps and risks |
| Migration script | `scripts/migrate-to-hooks.ts` | Codemod if needed |
| Test report | CI output | Regression results |

## Example: upgrade commands

```bash
npm install react@19 react-dom@19
npx types-react-codemod@latest preset-19 ./src
npm install vite@latest    # or: npx @next/codemod@canary upgrade latest
```

## Checklist

- [ ] Upgrade plan approved
- [ ] Dependency versions bumped and installed without peer-dep conflicts
- [ ] Class-to-hooks migration applied incrementally
- [ ] Tests pass (unit + E2E)
- [ ] Third-party deps compatible (react-router-dom, @tanstack/react-query, etc.)
- [ ] Breaking changes documented
