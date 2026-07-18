---
name: uat-acceptance
description: 'User Acceptance Testing: acceptance criteria definition, stakeholder sign-off workflow, UAT environment setup, test scenario generation, feedback collection, go/no-go decision framework. Trigger: When preparing for UAT, defining acceptance criteria, or managing stakeholder sign-off before production deployment.'
version: 1.0
metadata:
  phase:
    - quality
  layer:
    - business
  enforcement: recommended
  depends_on:
    - framework-qa-validation
    - hu-template
  consumed_by:
    - agent-qa
  agent_roles:
    - control-agent
  validation_profile: architecture
  mcp_usage: none
---

## Purpose

Define the User Acceptance Testing (UAT) pattern for the framework. UAT is the final quality gate before production — real users validate that the system meets their needs in a production-like environment. This skill ensures stakeholders sign off with clear acceptance criteria, traceable test scenarios, and a structured go/no-go decision.

## When to use this skill

Activate this skill when:

- Preparing for a release to production
- Defining acceptance criteria with stakeholders
- Setting up UAT environment
- Running UAT sessions with end users
- Making go/no-go decisions before deployment
- Collecting and triaging UAT feedback

**Do not** activate when:

- Writing automated tests (use `unit-testing`, `integration-testing`, `playwright`)
- Defining requirements (use `hu-template` or `api-first-spec`)
- Doing adversarial code review (use `review-adversarial`)

## Acceptance Criteria Format

Every user story must have acceptance criteria:

```markdown
## HU-042: Búsqueda de productos por categoría

### Acceptance Criteria (UAT)

| # | Criterio | Dado | Cuando | Entonces | Prioridad |
|---|----------|------|--------|----------|-----------|
| AC-1 | Búsqueda básica | Usuario en página de productos | Selecciona categoría "Electrónicos" | Ve solo productos de esa categoría | P0 |
| AC-2 | Filtro combinado | Usuario en página de productos | Selecciona categoría + rango de precio | Ve productos que cumplen ambos filtros | P0 |
| AC-3 | Sin resultados | Usuario en página de productos | Busca categoría sin productos | Ve mensaje "No se encontraron productos" | P1 |
| AC-4 | Rendimiento | Hay 10,000 productos en la categoría | Usuario filtra | Resultados en <2 segundos | P0 |
| AC-5 | Paginación | Hay >20 productos en resultado | Usuario hace scroll | Ve paginación correcta | P1 |

### UAT Test Scenarios

| Escenario | Pasos | Resultado esperado | Estado |
|-----------|-------|-------------------|--------|
| UAT-1: Búsqueda feliz | 1. Abrir /productos<br>2. Seleccionar "Electrónicos" | Ver lista de productos de electrónicos | ⬜ |
| UAT-2: Sin resultados | 1. Abrir /productos<br>2. Buscar "xyz123" | Ver mensaje vacío amigable | ⬜ |
| UAT-3: Móvil | 1. Abrir en móvil<br>2. Filtrar por categoría | UI responsive, filtros accesibles | ⬜ |
```

## UAT Environment

```yaml
# uat/docker-compose.yml
version: "3.8"
services:
  api:
    image: registry/org/api:uat
    environment:
      - APP_ENV=uat
      - DATABASE_URL=postgresql://uat_user:password@db:5432/uat_db
    depends_on:
      - db
  
  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=uat_db
    volumes:
      - ./seed-uat.sql:/docker-entrypoint-initdb.d/seed.sql
  
  web:
    image: registry/org/web:uat
    ports:
      - "4200:80"
```

**Reglas del entorno UAT:**
- Datos anonimizados (no producción real)
- Mismo hardware que producción para pruebas de rendimiento
- Feature flags activados según lo que se va a probar
- Acceso restringido al equipo de UAT + stakeholders

## Sign-Off Workflow

```
Feature completada → QA aprueba tests automatizados
    ↓
Deploy a UAT → Stakeholders notificados
    ↓
Período UAT (1-5 días) → Stakeholders ejecutan escenarios
    ↓
Feedback recolectado → Issues clasificados
    ↓
┌─────────────────────────────────────┐
│ ¿Todos los criterios P0 aprobados?  │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        │ Sí          │ No
        ▼             ▼
   Go Decision    Fix + Re-test
        │             │
        ▼             └────→ Volver a UAT
   Sign-Off Formal
        │
        ▼
   Deploy a Producción
```

## Sign-Off Document

```markdown
# UAT Sign-Off: {feature-name}

## Release Information
- **Versión**: v{major}.{minor}.{patch}
- **Fecha UAT inicio**: {date}
- **Fecha UAT fin**: {date}
- **Stakeholders**: {list of names and roles}

## Acceptance Criteria Status
| # | Criterio | Prioridad | Estado | Probado por | Fecha |
|---|----------|-----------|--------|-------------|-------|
| AC-1 | Búsqueda básica | P0 | ✅ Aprobado | María López | 2026-07-15 |
| AC-2 | Filtro combinado | P0 | ✅ Aprobado | María López | 2026-07-15 |
| AC-3 | Sin resultados | P1 | ✅ Aprobado | Juan Pérez | 2026-07-16 |
| AC-4 | Rendimiento | P0 | ⚠️ Condicional | María López | 2026-07-16 |
| AC-5 | Paginación | P1 | ✅ Aprobado | Juan Pérez | 2026-07-16 |

## Issues Found
| # | Descripción | Severidad | Resolución | Estado |
|---|-------------|-----------|------------|--------|
| UAT-1 | Filtro de precio no funciona en Safari | Alta | Corregido en v1.2.1 | ✅ |
| UAT-2 | Texto de "sin resultados" en inglés | Baja | i18n key faltante | ✅ |
| UAT-3 | Tiempo de carga >3s con 10k productos | Media | Aceptado con plan de mejora | ⚠️ |

## Decision

- [x] **GO** — Todos los criterios P0 aprobados. Issues P1/P2 aceptados o con plan.
- [ ] **NO-GO** — Criterios P0 pendientes o issues bloqueantes sin resolver.
- [ ] **CONDITIONAL GO** — Aprobado con condiciones (ej: hotfix antes del lunes).

## Signatures

| Rol | Nombre | Firma | Fecha |
|-----|--------|-------|-------|
| Product Owner | {name} | ________ | {date} |
| Tech Lead | {name} | ________ | {date} |
| QA Lead | {name} | ________ | {date} |
| Stakeholder | {name} | ________ | {date} |
```

## Go/No-Go Decision Framework

```python
from enum import Enum
from dataclasses import dataclass

class Decision(Enum):
    GO = "go"
    NO_GO = "no_go"
    CONDITIONAL_GO = "conditional_go"

@dataclass
class UATDecision:
    decision: Decision
    blocking_issues: list[Issue]
    conditional_issues: list[Issue]
    signoffs: dict[str, bool]  # stakeholder -> signed
    recommendation: str

class UATDecisionMaker:
    def decide(self, uat_results: UATResults) -> UATDecision:
        # Rule 1: All P0 criteria must pass
        failed_p0 = [
            c for c in uat_results.criteria 
            if c.priority == Priority.P0 and c.status != Status.APPROVED
        ]
        if failed_p0:
            return UATDecision(
                Decision.NO_GO, failed_p0, [],
                uat_results.signoffs,
                f"Bloqueado: {len(failed_p0)} criterios P0 no aprobados"
            )
        
        # Rule 2: No blocking issues (severity Critical or High unresolved)
        blocking = [
            i for i in uat_results.issues 
            if i.severity in (Severity.CRITICAL, Severity.HIGH) 
            and i.status != Status.RESOLVED
        ]
        if blocking:
            return UATDecision(
                Decision.NO_GO, blocking, [],
                uat_results.signoffs,
                f"Bloqueado: {len(blocking)} issues sin resolver"
            )
        
        # Rule 3: All required stakeholders signed off
        unsigned = [
            s for s in uat_results.required_signoffs 
            if s not in uat_results.signoffs
        ]
        if unsigned:
            return UATDecision(
                Decision.NO_GO, [], [],
                uat_results.signoffs,
                f"Bloqueado: {len(unsigned)} stakeholders sin firmar"
            )
        
        # Rule 4: Conditional issues exist
        conditional = [
            i for i in uat_results.issues 
            if i.resolution == Resolution.ACCEPTED_WITH_PLAN
        ]
        if conditional:
            return UATDecision(
                Decision.CONDITIONAL_GO, [], conditional,
                uat_results.signoffs,
                f"Aprobado con {len(conditional)} condiciones"
            )
        
        return UATDecision(
            Decision.GO, [], [],
            uat_results.signoffs,
            "Todos los criterios aprobados, sin issues bloqueantes"
        )
```

## Feedback Collection & Triage

```python
class UATFeedback:
    issue_id: str
    reported_by: str
    scenario: str
    expected: str
    actual: str
    severity: Severity
    category: FeedbackCategory  # BUG | UX | PERFORMANCE | MISSING_FEATURE
    screenshot_url: str | None
    timestamp: datetime

class FeedbackTriager:
    async def triage(self, feedback: UATFeedback) -> TriageResult:
        if feedback.category == FeedbackCategory.BUG:
            # Create issue in backlog
            issue = await self.create_issue(feedback)
            severity = await self.classify_severity(feedback)
            return TriageResult.BACKLOG(issue, severity)
        
        if feedback.category == FeedbackCategory.UX:
            # Route to design team
            return TriageResult.DESIGN_REVIEW(feedback)
        
        if feedback.category == FeedbackCategory.MISSING_FEATURE:
            # Route to product owner for scope decision
            return TriageResult.SCOPE_REVIEW(feedback)
        
        if feedback.category == FeedbackCategory.PERFORMANCE:
            # Route to performance review
            return TriageResult.PERF_REVIEW(feedback)
```

## UAT Session Template

```markdown
# UAT Session — {feature-name}

## Session Info
- **Date**: {date}
- **Tester**: {name} ({role})
- **Environment**: UAT ({url})
- **Duration**: {start} — {end}

## Test Scenarios
| # | Scenario | Steps | Expected | Actual | Pass/Fail | Notes |
|---|----------|-------|----------|--------|-----------|-------|
| 1 | | | | | ⬜ | |
| 2 | | | | | ⬜ | |

## Overall Assessment
- [ ] Feature works as expected
- [ ] Found minor issues (documented below)
- [ ] Found major issues (needs rework)

## Issues Found
[Link to issue tracker or inline description]

## Tester Signature
_____________ Date: {date}
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|-------------------|
| P0 criterion fails | "Close enough, ship it" | NO-GO — fix before deploy |
| Stakeholder unavailable | Skip their sign-off | Escalate — find alternate approver |
| Minor UX issue found | Block the release | Classify as P2 — fix next sprint |
| UAT environment differs from prod | "It's fine" | Match prod config — UAT must reflect reality |
| Tester reports vague issue | Create task anyway | Ask for reproduction steps + screenshot |

## Verification checklist

- [ ] Acceptance criteria defined for all P0 user stories
- [ ] UAT environment matches production configuration
- [ ] UAT test data anonymized and representative
- [ ] Stakeholders identified and notified
- [ ] Sign-off document template ready
- [ ] Go/no-go criteria explicitly defined
- [ ] Feedback triage process documented
- [ ] UAT session templates available for testers
