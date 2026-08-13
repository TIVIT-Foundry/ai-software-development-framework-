---
# ──────────────────────────────────────────────────────────────────
# SKILL TEMPLATE — Framework Agéntico
# ──────────────────────────────────────────────────────────────────
# Completa todos los campos YAML. Los que tienen "❌" son obligatorios.
# Los que tienen "OPCIONAL" pueden dejarse sin el comentario.
# ──────────────────────────────────────────────────────────────────
name: {skill-name}                           # ❌ Lowercase, hyphens only
description: '{1-2 sentence description. Must include "Trigger: When..." clause}'  # ❌
version: 1.0                                  # ❌ Semver, start at 1.0
# when_to_use:                               # OPCIONAL — lista de situaciones de activación
#   - Cuando se necesita ...
metadata:
  phase:                                      # ❌ Array, uno o más valores
    - construction                            #   governance | discovery | conception | architecture
                                              #   platform | scaffold | construction | quality | operations
  layer:                                      # ❌ Array, uno o más valores
    - backend                                 #   frontend | backend | database | testing
                                              #   e2e | process | governance | operations
                                              #   business | design | implementation
                                              #   infrastructure | platform
  enforcement: recommended                    # ❌ mandatory | recommended | optional
  depends_on: []                              # ❌ Array de skill IDs que requiere
  consumed_by: []                             # ❌ Array de skill IDs que lo consumen
  agent_roles:                                # ❌ Array de agentes que pueden invocarlo
    - delivery-agent                          #   orchestrator-agent | design-agent
    - design-agent                            #   control-agent | delivery-agent
                                              #
                                              # SEMÁNTICA (validada por check-agent-roles):
                                              # = agente del routing (SKILL-ROUTING, si la skill
                                              #   tiene nivel Nxx) UNION agentes que la listan en
                                              #   AGENT-MODEL (owner/consulta/stack). No editar a
                                              #   mano sin actualizar esas dos fuentes.
  validation_profile: documentation           # ❌ documentation | skill-contract |
                                              #   architecture | security | null
  mcp_usage: none                             # ❌ none | context7 | playwright |
                                              #   docker | package-registry | filesystem |
                                              #   github | postgres | (o array)
---

## Purpose

[1-2 paragraphs describing the problem this skill solves, what it produces, and why it exists in the framework.]

## When to use this skill

Activate this skill when:

- [situation 1]
- [situation 2]
- [situation 3]

**Do not** activate when:

- [when NOT to use]

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `{skill-id}` | Predecesora / Consumidora | Description of relationship |
| `{skill-id}` | Complementaria | Description |

## Critical Rules

1. **[Rule 1]** — Explanation
2. **[Rule 2]** — Explanation
3. **[Rule 3]** — Explanation

## What the agent must do

1. **Step 1** — Description of what to do
2. **Step 2** — Description of what to do
3. **Step 3** — Description of what to do

## Inputs expected

| Input | Source | Required | Description |
|-------|--------|----------|-------------|
| {input name} | {skill or file} | Yes/No | What this input provides |

## Outputs produced

| Artifact | Format | Description |
|----------|--------|-------------|
| {artifact name} | {file format} | What the artifact contains |

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|-------------------|
| {scenario} | {incorrect} | {correct} |

## Code patterns

### Python FastAPI

```python
# Example code
```

## Examples

### Example 1 — {Title}

{brief description}

```{language}
# Code or content
```

## Verification checklist

- [ ] Requirement 1 met
- [ ] Requirement 2 met
- [ ] Lint/pass criteria verified

> **Note**: This template follows the Framework Agéntico conventions.
> See `skill-creator` SKILL.md for detailed creation instructions.
