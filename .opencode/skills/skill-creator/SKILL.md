---
name: skill-creator
description: 'Creates new AI agent skills following framework conventions (Python/React or Angular/Bun). Includes
  frontmatter templates, naming conventions, content guidelines, and sync instructions.
  Trigger: When asked to create a new skill, add agent instructions, or document patterns
  for AI.'
version: 1.1
metadata:
  phase:
  - construction
  - operations
  - inception
  layer:
  - process
  enforcement: optional
  depends_on: []
  consumed_by: []
  agent_roles:
  - orchestrator-agent
  - design-agent
  validation_profile: skill-contract
  mcp_usage: none
---

## Purpose

Create a new skill for the Framework Agéntico. This skill documents the **process, conventions, and templates** for adding new skills to the `.opencode/skills/` directory.

A skill encapsulates a **reusable pattern** that an AI agent can follow when a specific task is detected. Good skills are concrete, actionable, and framework-aware.

## When to create a skill

### Create a skill when:
- A pattern is used repeatedly across projects (3+ occurrences)
- A complex workflow needs step-by-step guidance (5+ steps)
- A project introduces new technology or domain conventions
- A specialized agent needs a dedicated playbook
- Existing documentation exists but is scattered across multiple files

### Don't create a skill when:
- The task is a one-off or prototype
- Existing documentation already covers the pattern
- The pattern is trivial (1-2 steps with no decisions)
- The pattern is already covered by another skill (check `depends_on` instead)
- The task is purely operational (use a runbook instead)

## Skill Structure

```
.opencode/skills/{skill-name}/
├── SKILL.md              # Required — the skill itself
├── assets/               # Optional — templates, schemas, examples, scripts
│   ├── templates/        # Reusable templates (code, config, docs)
│   ├── schemas/          # JSON Schema / OpenAPI / XSD fragments
│   └── scripts/          # Helper scripts (bash, python, etc.)
└── references/           # Optional — links to local docs
    ├── links.md          # External references (docs, blog posts, specs)
    └── examples/         # Concrete examples from real projects
```

**Key Rule:** Keep SKILL.md under 200 lines of instructional content. Heavy content (templates, long examples, scripts) goes to `assets/`.

## Creating a new skill — task-based workflow

### Task 1: Identify if a skill is needed

Ask yourself:
1. **Is this a new pattern?** Check `depends_on` of related skills to avoid duplication.
2. **Is this framework-specific or general?** General patterns (React, Angular, SQL) go in `skills/`. Framework-specific patterns (multi-tenant routing) go in `skills/framework-*`.
3. **Who will use it?** Machine (automated trigger) or human (manual activation)?
4. **What layer does it affect?** frontend, backend, database, testing, e2e, process, or governance?

If the pattern is new, framework-relevant, and used 3+ times → **proceed**.

### Task 2: Choose the skill name

| Type | Pattern | Examples |
|------|---------|----------|
| Generic technology | `{technology}` | `react`, `angular`, `typescript`, `docker-local` |
| Workflow | `{action}-{target}` | `skill-creator`, `api-first-spec`, `code-review` |
| Domain aspect | `{domain}-{aspect}` | `database-sp`, `database-audit`, `framework-security` |
| Agent orchestrator | `agent-{role}` | `agent-backend`, `agent-fullstack` |
| Meta-skill | `agent-{target}` | `agent-qa`, `agent-delivery` |

Rules:
- Lowercase only, hyphens as separators.
- Prefix framework-specific skills with `framework-`.
- Prefix meta-skills with `agent-`.
- Max 3 hyphens per name (e.g., `framework-data-memory-compliance` is borderline).

### Task 3: Create the skill directory

```bash
mkdir -p .opencode/skills/{skill-name}
touch .opencode/skills/{skill-name}/SKILL.md
mkdir -p .opencode/skills/{skill-name}/assets
mkdir -p .opencode/skills/{skill-name}/references
```

### Task 4: Write the SKILL.md frontmatter

Use this canonical template:

```yaml
---
name: {skill-name}
description: '{1-2 sentence description of what the skill does. Must include "Trigger: When..." clause.}'
version: 1.0
metadata:
  phase: [inception | construction | operations | closure]
  layer: [frontend | backend | database | testing | e2e | process | governance | operations]
  enforcement: [mandatory | recommended | optional]
  depends_on: [list of skill IDs this skill requires as input]
  consumed_by: [list of skill IDs that consume this skill's output]
  agent_roles: [which agents can invoke this skill]
  validation_profile: [documentation | skill-contract | architecture | security | null]
  mcp_usage: [none | list of MCP tools used]
---
```

### Frontmatter field reference

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `name` | Yes | Lowercase, hyphens | Must match folder name exactly |
| `description` | Yes | String with "Trigger:" clause | What + when the skill activates |
| `version` | Yes | Semver string | Start at 1.0 |
| `phase` | Yes | Array | One or more of: inception, construction, operations, closure |
| `layer` | Yes | Array | One or more of: frontend, backend, database, testing, e2e, process, governance, operations |
| `enforcement` | Yes | Enum | `mandatory`: cannot be skipped. `recommended`: should run but can be waived. `optional`: project team decides |
| `depends_on` | Yes | Array | Skill IDs required before this one. Empty `[]` if none |
| `consumed_by` | Yes | Array | Skill IDs that depend on this one. Empty `[]` if none |
| `agent_roles` | Yes | Array | Agentes que invocan/usan la skill. **Semántica**: agente del routing (SKILL-ROUTING, si la skill tiene nivel Nxx) UNION agentes que la listan en AGENT-MODEL (owner/consulta/stack). Al crear/editar una skill, actualizar también esas dos fuentes; el validador `check-agent-roles` exige el agente del routing |
| `validation_profile` | Yes | String | Links to a validation profile in `VALIDATION-PROFILES.md` |
| `mcp_usage` | Yes | String/Array | `none` or list of MCP tool IDs |

### Task 5: Write the SKILL.md body

Follow these content sections in order:

```
## Purpose
[1-2 paragraphs describing the problem this skill solves]

## When to use this skill
[When it should be activated, when it should NOT]

## Relation to other skills
[Table: Skill | Relation | Description]

## Critical Rules
[Non-negotiable rules the agent must follow]

## What the agent must do
[Numbered steps the agent executes]

## Inputs expected
[Table: Input | Source | Required | Description]

## Outputs produced
[Table: Artifact | Format | Description]

## Decision table
[Table: Situation | Wrong response | Expected response]

## Examples
[1-2 concrete examples with code]

## Checklist
[Final verification steps]
```

### Task 5a — Stack skills (backend, frontend, database)

For technical stack skills, additionally include:

```
## Multi-stack patterns
[Examples for Python FastAPI, React/Angular, Bun TypeScript]

## Configuration
[Environment variables, config files, dependencies]
```

### Task 5b — Framework skills (framework-*)

For framework governance skills, use narrative format starting with "Usa esta skill para...".

```
## Propósito
Usa esta skill para [acción principal]. Sirve para [resultado esperado].

## Cuándo usarla
[When to use]

## Relación con otras skills del framework
[Dependencies and consumers within the framework]
```

### Task 6: Update consumed_by of dependent skills

For each skill listed in `consumed_by`, add the new skill's name to their `depends_on` list.

For each skill listed in `depends_on`, add the new skill's name to their `consumed_by` list.

This keeps the dependency graph consistent.

### Task 7: Sync framework metadata

After creating the skill:

1. **Register in SKILLS-MANIFEST.md**:
   - Add entry to Skills Catalog table
   - Update Agent-to-Skill map if applicable
   - Add auto-invoke keywords if the skill can be triggered automatically

2. **Sync consumed_by references** across all affected skills.

3. **Link in relevant agent files** if the skill should be auto-suggested to specific agents.

4. **Run validators** to verify structural integrity:

```bash
python3 .opencode/validators/check-skill-ids.py
python3 .opencode/validators/check-content-quality.py
bash .opencode/validators/run-all.sh
```

5. **Update SKILL-ALIASES.json** if the new skill replaces a deprecated one.

## Decision: assets/ vs references/

| Scenario | Location | Example |
|----------|----------|---------|
| Code/SQL/JSON templates | `assets/` | `assets/templates/sp_crud.sql.j2` |
| Configuration examples | `assets/` | `assets/examples/docker-compose.yml` |
| OpenAPI schema fragments | `assets/` | `assets/schemas/pagination.json` |
| Helper scripts | `assets/` | `assets/scripts/generate-catalog.sh` |
| Links to existing docs | `references/` | `references/links.md` → `docs/adr/ADR-001.md` |
| External reference links | `references/` | `references/links.md` → `https://example.com/docs` |
| Project examples | `references/` | `references/examples/erp-orders/README.md` |

## Content guidelines

### DO
- Start each skill with clear **Critical Rules** section (if applicable).
- Use tables for structured information.
- Include concrete examples rather than abstract descriptions.
- Reference `assets/` for templates and long examples.
- Keep sentences short and actionable.
- Use active voice: "El agente ejecuta..." not "Los pasos son ejecutados por..."
- Include a "Trigger:" clause in the description field.

### DON'T
- Duplicate content that exists in other skills — use `depends_on` instead.
- Write lengthy explanations when a table or list suffices.
- Include complete inline templates longer than 30 lines (put in `assets/`).
- Exceed 200 lines of instructional content (applies to SKILL.md body only).
- Use markdown that won't render well in terminal (e.g., complex HTML tables).
- Reference files that don't exist (every link must resolve).

## Example: Creating a "graphql" skill from scratch

### Step 1: Identify
The project uses GraphQL across 3+ services. Existing REST skills don't cover schema design, resolvers, or DataLoader. → Skill needed.

### Step 2: Name
`graphql` — generic technology, no prefix needed.

### Step 3: Directory

```bash
mkdir -p .opencode/skills/graphql/{assets,references}
```

### Step 4: Frontmatter

```yaml
---
name: graphql
description: 'GraphQL API design: schema, resolvers, DataLoader, mutations, subscriptions,
  auth, error handling, pagination. Trigger: When designing or implementing GraphQL
  APIs in Python or Bun (TypeScript).'
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: recommended
  depends_on:
  - project-architecture
  - api-first-spec
  consumed_by: []
  agent_roles:
  - delivery-agent
  - design-agent
  validation_profile: architecture
  mcp_usage: context7
---
```

### Step 5: Body structure

```
## Purpose
## When to use
## Relation to other skills
## Critical Rules
## Schema Design Patterns
## Resolver Patterns (DataLoader, N+1)
## Mutation Patterns
## Subscription Patterns
## Auth and Authorization
## Error Handling
## Pagination (Cursor-based)
## Multi-stack examples (Python Strawberry, Bun Elysia)
## Checklist
```

### Step 6: Update graph

```python
# Add `graphql` to consumed_by of `project-architecture` and `api-first-spec`
```

### Step 7: Sync

```bash
python3 .opencode/validators/check-skill-ids.py  # Verify new skill ID is recognized
python3 .opencode/validators/sync-manifest.py    # Regenerate SKILLS-MANIFEST.md
```

## Sync automation

### Batch update of SKILLS-MANIFEST.md

After creating or modifying a skill, the manifest must be updated. Use `skill-creator` alongside `framework-operations-evolution` to track when skills are added, modified, or deprecated.

```python
# Pseudocode for manifest update
def sync_manifest():
    for skill_dir in skills:
        fm = parse_frontmatter(skill_dir / "SKILL.md")
        manifest.add_or_update(skill_dir.name, fm)
    manifest.validate_consumed_by()
    manifest.write()
```

## Best practices

1. **One concern per skill**: A skill should do one thing well. If a skill covers two distinct patterns, split it.
2. **Framework-* skills are mandatory**: Skills starting with `framework-` must have `enforcement: mandatory`.
3. **Consumer-first**: Design skills with their consumers in mind (what does `api-first-frontend` need from `api-first-spec`?).
4. **Concrete over abstract**: An example with real code is worth 3 paragraphs of explanation.
5. **Keep skills up-to-date**: When a technology changes (e.g., React 19 features or a new Angular major version), update the corresponding skill. See `framework-operations-evolution` for deprecation policy.
6. **Test every skill**: After creating a skill, run the validators. A skill that doesn't pass `check-content-quality` will produce noise in every agent session.

## Antipatterns

| Antipattern | Why it's bad | Better approach |
|-------------|--------------|-----------------|
| Skill with no "Trigger:" in description | Agent can't detect when to activate it | Always include "Trigger: When..." |
| Skill with empty `depends_on: []` and `consumed_by: []` | Not wired into the dependency graph | If truly standalone, document why in a comment |
| Skill that duplicates existing content | Confuses agents, causes stale docs | Use `depends_on` to reference instead of copy |
| Skill with 400+ lines of body | Hard to maintain, hard for agents to process | Move templates to `assets/`, keep SKILL.md focused |
| Skill that references deleted skills | Broken links in every agent session | Run `check-skill-ids.py` before every commit |
| Skill that doesn't specify `mcp_usage` | Agent doesn't know which tools to use | Always set `mcp_usage: none | [tool list]` |

## Verification checklist

Before marking a new skill as complete:

- [ ] **Name matches folder name exactly** — case-sensitive, verified by `check-skill-ids.py`.
- [ ] **Frontmatter complete** — all required fields present and valid.
- [ ] **Description has "Trigger:" clause** — ≥ 20 characters after "Trigger:".
- [ ] **`depends_on` and `consumed_by` wired** — both lists populated (or explicitly empty).
- [ ] **Multi-stack examples** — at least 2 stacks for technical skills (e.g., Python + Bun, Python + React/Angular).
- [ ] **assets/ and references/ created** — even if empty initially.
- [ ] **SKILLS-MANIFEST.md updated** — skill appears in catalog table and auto-invoke table if applicable.
- [ ] **Validators pass** — `check-content-quality.py`, `check-skill-ids.py`, `run-all.sh`.
- [ ] **No broken links** — all local link references resolve to existing files.
- [ ] **Consistent style** — matches existing skills in tone, format, and section order.
