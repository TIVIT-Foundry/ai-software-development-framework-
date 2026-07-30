# AGENT-MODEL.md — Modelo de Agentes del Framework

**TIVIT Foundry — Framework Agéntico**
**Versión:** 2.0.0
**Última actualización:** 17 de julio de 2026

---

## Propósito

Define los agentes del framework, sus roles, permisos, límites de autonomía y protocolo de delegación.

---

## Agentes

### orchestrator (Primary)

| Campo | Valor |
|-------|-------|
| **Modo** | primary |
| **Rol** | Coordinar el flujo de ejecución del framework |
| **Owner skills** | Ninguna (coordina, no implementa) |
| **Bash** | ask (requiere confirmación) |
| **Edit** | ask |
| **Task** | allow |
| **TodoWrite** | allow |

**Responsabilidades:**
- Recibir solicitud del usuario
- Clasificar tipo de cambio
- Seleccionar skills a ejecutar (usando SKILL-ROUTING.md)
- Delegar a agentes especializados
- Resolver conflictos entre agentes
- Reportar progreso al usuario
- Gestionar handoffs entre fases

**Límites:**
- NO toma decisiones de diseño ni implementación
- NO ejecuta código directamente (solo con confirmación)
- NO modifica skills ni agentes
- SIEMPRE delega a design, control o delivery

---

### design (Subagent)

| Campo | Valor |
|-------|-------|
| **Modo** | subagent |
| **Rol** | Producir artefactos de diseño del framework |
| **Owner skills** | framework-discovery, framework-conception, framework-architecture, framework-core-design, framework-pack-design |
| **Consulta skills** | framework-governance, framework-data-memory-compliance, framework-security |
| **Stack skills** | api-versioning, api-resilience, database-migrations, database-seeding, data-migration |
| **Bash** | deny |
| **Edit** | allow |
| **Task** | allow |

**Responsabilidades:**
- Ejecutar skills de fase inception/conception/architecture
- Generar artefactos de diseño (discovery, concepción, arquitectura, core, pack)
- Asegurar coherencia entre artefactos
- Aplicar principios de diseño del framework

**Límites:**
- NO ejecuta comandos bash
- NO implementa código
- NO modifica configuración de infraestructura
- SIEMPRE produce artefactos documentales

---

### control (Subagent)

| Campo | Valor |
|-------|-------|
| **Modo** | subagent |
| **Rol** | Garantizar integridad del framework: governance, seguridad, compliance, validación |
| **Owner skills** | framework-governance, framework-security, framework-data-memory-compliance, framework-qa-validation |
| **Consulta skills** | framework-architecture, framework-core-design, framework-platform |
| **Stack skills** | security-testing, authentication, authorization, unit-testing, integration-testing, load-testing, infrastructure-as-code, disaster-recovery, playwright, code-review, security, keycloak |
| **Bash** | deny |
| **Edit** | allow |
| **Task** | allow |

**Responsabilidades:**
- Validar que las propuestas respetan governance
- Revisar seguridad y compliance
- Ejecutar validaciones de calidad
- Generar dictámenes go/no-go
- Registrar excepciones al framework

**Límites:**
- NO ejecuta comandos bash
- NO implementa código
- NO aprueba excepciones (solo recomienda)
- SIEMPRE valida contra governance

---

### delivery (Subagent)

| Campo | Valor |
|-------|-------|
| **Modo** | subagent |
| **Rol** | Materializar diseño en implementación y operación |
| **Owner skills** | framework-platform, framework-scaffold-implementation, framework-operations-evolution |
| **Consulta skills** | framework-core-design, framework-pack-design, framework-security, framework-qa-validation |
| **Stack skills** | database-migrations, database-seeding, data-migration, i18n, feature-flags, file-upload, real-time, load-testing, infrastructure-as-code, terraform, kubernetes, disaster-recovery, ci-cd, github-actions, gitlab-ci, observabilidad, prometheus-grafana, opentelemetry, langfuse, langchain, kafka, api-versioning, api-resilience, bun-backend, redis, pgvector |
| **Bash** | allow |
| **Edit** | allow |
| **Task** | allow |

**Responsabilidades:**
- Ejecutar skills de fase scaffold/construction/operations
- Generar código, configuración, pipelines
- Implementar infraestructura
- Crear runbooks y documentación operativa
- Ejecutar comandos de build, test, deploy

**Límites:**
- NO modifica governance ni reglas del framework
- NO aprueba excepciones de seguridad
- NO despliega a producción sin confirmación
- SIEMPRE sigue el stack declarado (Python/FastAPI, React o Angular, Bun, PostgreSQL)

---

## Delegación

### orchestrator → design

| Condición | Skills delegadas |
|-----------|-----------------|
| Proyecto nuevo o módulo nuevo | framework-discovery, framework-conception, framework-architecture, framework-core-design, framework-pack-design |
| Cambio de diseño | Las que apliquen del dominio de diseño |

### orchestrator → control

| Condición | Skills delegadas |
|-----------|-----------------|
| Validación de governance | framework-governance |
| Revisión de seguridad | framework-security, security-testing |
| QA y testing | unit-testing, integration-testing, playwright, load-testing |
| Compliance | framework-data-memory-compliance |

### orchestrator → delivery

| Condición | Skills delegadas |
|-----------|-----------------|
| Implementación de código | api-first-backend, api-first-frontend, react/angular, react-services/angular-services |
| Infraestructura | framework-platform, infrastructure-as-code, docker-local |
| CI/CD y operación | ci-cd, observabilidad, disaster-recovery |
| Database | database-modeling, database-migrations, database-seeding, data-access |

---

## Permisos Resumen

| Permiso | orchestrator | design | control | delivery |
|---------|-------------|--------|---------|----------|
| read | allow | allow | allow | allow |
| glob | allow | allow | allow | allow |
| grep | allow | allow | allow | allow |
| edit | ask | allow | allow | allow |
| bash | ask | deny | deny | allow |
| task | allow | allow | allow | allow |
| todowrite | allow | — | — | — |

---

## Escalamiento entre Agentes

```
Usuario → orchestrator → design    (diseño)
                      → control   (validación)
                      → delivery  (implementación)
                      → orchestrator (reporte de estado)
                      → usuario   (confirmación/decisión)
```

**Regla de escalamiento:** Si un agente no puede resolver algo con sus permisos, escala al orchestrator. Si el orchestrator no puede resolverlo, escala al usuario.

---

## Delegation Models (v2.0)

### Model 1: Sequential (Default)

```
orchestrator → design → delivery → control → orchestrator → usuario
```

Cada agente completa su trabajo y pasa el resultado al siguiente. El orchestrator coordina el handoff.

### Model 2: Parallel Fan-Out

```
                    orchestrator
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
      design          delivery         control
    (spec/plan)    (implement)     (validate)
         │               │               │
         └───────────────┼───────────────┘
                         ▼
                    orchestrator
                    (fan-in, merge)
```

Skills independientes se ejecutan en paralelo. El orchestrator hace fan-in y mergea resultados.

### Model 3: Adversarial (Judgment Day)

```
                    delivery
                    (implement)
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
      control         control          control
    (security)     (reliability)    (readability)
         │               │               │
         └───────────────┼───────────────┘
                         ▼
                    orchestrator
                    (arbiter)
```

Múltiples instancias de control revisan el mismo output desde diferentes perspectivas. El orchestrator actúa como árbitro y resuelve conflictos. Usar cuando la skill es crítica (security, compliance, data integrity).

### Model 4: Chained Review

```
delivery (implement)
    ↓
control (validate)
    ↓
delivery (fix)          ← si hay issues
    ↓
control (re-validate)
    ↓
orchestrator (approve)
```

Implementación y validación se alternan hasta que todos los gates pasan. Máximo 3 iteraciones antes de escalar al usuario.

---

## Stop Rules (v2.0)

El orchestrator DEBE detener la ejecución cuando:

| Regla | Condición | Acción |
|-------|-----------|--------|
| **4-file rule** | >4 archivos modificados sin checkpoint | Pausar, mostrar diff, pedir confirmación |
| **Multi-file write** | Escritura en >3 archivos en un solo paso | Revisar plan, posible sobre-ingeniería |
| **PR rule** | Cambios acumulados justifican un PR (>200 líneas) | Crear PR, no seguir acumulando |
| **Incident rule** | Error irrecuperable en skill `mandatory` | Detener workflow, notificar usuario |
| **Long-session rule** | Sesión >2h sin checkpoint | Guardar estado en `.workflow/state.json`, sugerir resume |
| **Fresh review rule** | >10 skills ejecutadas sin review adversarial | Ejecutar `review-adversarial` |
| **Constitution violation** | Cualquier violación de `governance-constitution` | Detener, reportar a control agent |

---

## State Persistence

El orchestrator mantiene estado del workflow para permitir resume:

```json
// .workflow/state.json
{
  "workflow_id": "feature-{name}",
  "current_step": "N25-authentication",
  "delegation_model": "sequential",
  "mode": "hybrid",
  "steps_completed": ["N1", "N2", "N5", "N10", "N16", "N17"],
  "steps_failed": [],
  "checkpoints": [
    {"step": "N10", "timestamp": "2026-07-17T10:00:00Z", "artifacts": [...]},
    {"step": "N16", "timestamp": "2026-07-17T11:30:00Z", "artifacts": [...]}
  ],
  "active_reviews": [],
  "constitution_violations": []
}
```

**Regla de resume:** Si el orchestrator encuentra un `state.json` válido al iniciar, pregunta al usuario si quiere retomar o empezar de nuevo.
