---
name: documentation
description: 'Documentation as first-class SDLC phase: architecture decision records (ADRs), API docs, codebase guides, cognitive documentation design, documentation review gates, docs-as-code workflow. Trigger: When creating, reviewing, or maintaining project documentation.'
version: 1.1
metadata:
  phase:
    - construction
  layer:
    - implementation
  enforcement: recommended
  depends_on:
    - governance-constitution
    - readme
  consumed_by:
    - pull-request
  agent_roles:
    - delivery-agent
    - design-agent
  validation_profile: documentation
  mcp_usage: context7
---

## Purpose

Define documentation as a first-class phase in the SDLC. Documentation is not an afterthought done before the PR — it is a continuous practice that starts at inception and evolves with the codebase. This skill ensures every project has ADRs for decisions, cognitive documentation for mental models, and API docs as executable contracts.

## When to use this skill

Activate this skill when:

- Creating Architecture Decision Records (ADR)
- Building a codebase guide with mental models
- Documenting APIs beyond OpenAPI specs
- Reviewing documentation quality before PR merge
- Setting up docs-as-code workflow
- Designing cognitive documentation (maps, decision trees)

**Do not** activate when:

- Writing inline code comments
- Generating OpenAPI specs (use `openapi-docs`)
- Creating README files (use `readme`)

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `readme` | Complementaria | README for project overview. Documentation for deep knowledge |
| `governance-constitution` | Predecesora | Constitution is the root document |
| `api-first-spec` | Complementaria | API specs are part of the documentation ecosystem |
| `pull-request` | Consumidora | PRs require documentation review gate |

## Documentation as Code

```
docs/
├── README.md                    # Project overview (how to run, contribute)
├── ARCHITECTURE.md              # System architecture, 7 layers mapping
├── CODEBASE-GUIDE.md            # Mental model, repository map
├── adr/                         # Architecture Decision Records
│   ├── 0001-use-postgresql.md
│   ├── 0002-use-keycloak-for-auth.md
│   └── 0003-use-pgvector-for-embeddings.md
├── api/                         # API documentation (beyond OpenAPI)
│   ├── authentication.md
│   ├── error-codes.md
│   └── rate-limiting.md
├── operations/                  # Operations documentation
│   ├── runbooks/
│   ├── deployment.md
│   └── monitoring.md
├── guides/                      # How-to guides
│   ├── local-setup.md
│   ├── adding-new-module.md
│   └── troubleshooting.md
└── decisions/                   # Decision log (lighter than ADR)
    └── 2026-07.md
```

## Architecture Decision Records (ADR)

```markdown
# ADR-0001: Use PostgreSQL + pgvector for embeddings

## Status
Accepted | Proposed | Deprecated | Superseded by ADR-XXXX

## Date
2026-07-17

## Context
We need to store and search vector embeddings for RAG pipelines.
Options considered:
1. PostgreSQL + pgvector extension
2. Dedicated vector DB (Qdrant, Pinecone, Weaviate)
3. In-memory with periodic persistence

## Decision
Use PostgreSQL + pgvector.

## Rationale
- Single database reduces operational complexity
- pgvector supports IVFFlat and HNSW indexes
- No additional service to manage, monitor, or pay for
- Team already has PostgreSQL expertise
- Adequate performance for our scale (<100M vectors)

## Consequences
- Positive: Simpler architecture, lower ops overhead
- Negative: Limited to PostgreSQL vector operations
- Risk: May need dedicated vector DB at >100M vectors — monitor

## Alternatives Considered
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| pgvector | Single DB, low ops | Scale ceiling at ~100M | ✅ Chosen |
| Qdrant | Purpose-built, fast | New service, new ops | ❌ Added complexity |
| In-memory | Fastest, zero ops | No persistence | ❌ Data loss risk |
```

## Codebase Guide (Mental Model)

```markdown
# Codebase Guide: {project-name}

## Mental Model

Think of this project as a **3-layer system**:

1. **AI/ML Core** (`src/ai/`) — Python FastAPI with LangChain
   - Orchestrates LLM calls, manages RAG pipelines
   - Uses pgvector for embeddings
   - Callbacks to Langfuse for observability

2. **Backend General** (`src/api/`) — Bun TypeScript
   - High-performance CRUD operations
   - Kafka event producers/consumers
   - Redis caching layer

3. **Frontend** (`src/web/`) — React (Vite) o Angular, según elección del proyecto
   - Function components with hooks
   - @tanstack/react-query for server state
   - react-hook-form with Zod validation

## Data Flow
User → React/Angular → Bun API → (Kafka events) → Python AI → pgvector
                    ↓
                  Redis cache
                    ↓
                PostgreSQL

## Key Decisions
- [ADR-003](../../docs/adr/ADR-003-postgresql-pgvector.md): PostgreSQL + pgvector
- [ADR-002](../../docs/adr/ADR-002-backend-dual.md): Keycloak for auth
- [ADR-001](../../docs/adr/ADR-001-angular.md): Bun for general backend

## Repository Map
| Directory | Purpose | Language | Owner |
|-----------|---------|----------|-------|
| `src/ai/` | AI orchestrator | Python | AI team |
| `src/api/` | General backend | TypeScript/Bun | Backend team |
| `src/web/` | Frontend SPA | React o Angular (según proyecto) | Frontend team |
| `database/` | Migrations, seeds | SQL | Data team |
| `infra/` | Terraform, K8s | HCL | DevOps |
| `docs/` | Documentation | Markdown | Everyone |
```

## Documentation Review Gate

Antes de mergear un PR, la documentación debe pasar este gate:

```python
class DocumentationGate:
    def review(self, pr: PullRequest) -> GateResult:
        issues = []
        
        # Check 1: New ADR for architectural decisions
        if self.has_architectural_change(pr) and not self.has_new_adr(pr):
            issues.append(GateIssue.CRITICAL(
                "Architectural change without ADR. Create adr/NNNN-{title}.md"
            ))
        
        # Check 2: API changes have doc updates
        if self.has_api_change(pr) and not self.has_api_doc_update(pr):
            issues.append(GateIssue.HIGH(
                "API change without documentation update"
            ))
        
        # Check 3: New service/module has runbook
        if self.has_new_service(pr) and not self.has_new_runbook(pr):
            issues.append(GateIssue.HIGH(
                "New service without runbook. Create docs/operations/runbooks/{service}.md"
            ))
        
        # Check 4: Breaking changes have migration guide
        if self.has_breaking_change(pr) and not self.has_migration_guide(pr):
            issues.append(GateIssue.CRITICAL(
                "Breaking change without migration guide"
            ))
        
        # Check 5: Codebase guide updated for new directories
        if self.has_new_top_level_dir(pr) and not self.has_codebase_guide_update(pr):
            issues.append(GateIssue.MEDIUM(
                "New top-level directory not documented in CODEBASE-GUIDE.md"
            ))
        
        return GateResult(
            passed=len([i for i in issues if i.severity == Severity.CRITICAL]) == 0,
            issues=issues
        )
```

## Cognitive Documentation Design

La documentación debe seguir el principio de **progressive disclosure**:

```
Capa 1: README.md (1 min)
  └─> ¿Qué hace este proyecto? ¿Cómo lo ejecuto?

Capa 2: ARCHITECTURE.md (5 min)
  └─> ¿Cómo está estructurado? ¿Qué decisiones importantes se tomaron?

Capa 3: CODEBASE-GUIDE.md (15 min)
  └─> ¿Cómo navego el código? ¿Dónde está cada cosa?

Capa 4: ADRs + API docs (según necesidad)
  └─> ¿Por qué se tomó esta decisión? ¿Cómo uso esta API?

Capa 5: Runbooks + Playbooks (on-demand)
  └─> ¿Qué hago si el servicio falla? ¿Cómo despliego?
```

## Docs-as-Code Workflow

```yaml
# .github/workflows/docs.yml
name: Documentation Check
on: [pull_request]

jobs:
  docs-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check for broken links
        run: |
          npx markdown-link-check docs/**/*.md
      
      - name: Validate ADR format
        run: |
          python scripts/validate-adrs.py docs/adr/
      
      - name: Check API docs match OpenAPI
        run: |
          diff <(cat openapi.json | jq '.paths | keys') \
               <(ls docs/api/ | sed 's/.md//')
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|-------------------|
| Architecture change | Code only | Code + ADR + CODEBASE-GUIDE update |
| New endpoint | Just the code | Code + API doc + OpenAPI spec |
| New service | Just the code | Code + runbook + monitoring dashboard |
| Breaking change | Changelog line | Changelog + migration guide + ADR |
| Docs outdated | "I'll update later" | Update in same PR as the change |

## Verification checklist

- [ ] ADR exists for every architectural decision
- [ ] CODEBASE-GUIDE.md updated when directory structure changes
- [ ] API documentation matches OpenAPI spec
- [ ] Every service has a runbook
- [ ] Documentation review gate configured in CI
- [ ] Docs-as-code workflow running on PRs
- [ ] Cognitive documentation follows progressive disclosure (5 layers)
- [ ] Migration guides for breaking changes
