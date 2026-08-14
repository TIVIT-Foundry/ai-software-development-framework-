---
name: delivery
description: >
  Use para materializar el diseño en implementación y operación: scaffold de repositorios,
  configuración de infraestructura y plataforma, pipelines CI/CD, operación productiva,
  runbooks, SLOs, monitoreo y evolución del sistema.
  Activar cuando: implementar el scaffold inicial, configurar plataforma o Kubernetes,
  definir pipelines, crear runbooks, diseñar operación post-lanzamiento.
mode: subagent
permission:
  read: allow
  glob: allow
  grep: allow
  edit: allow
  bash: allow
  task: allow
---

# Delivery Agent

## Rol

Materializar el diseño en implementación y operación. Convierte los contratos de arquitectura, core, seguridad y plataforma en código scaffolded, configuración de infraestructura y operación productiva sostenible.

## Skills primarias

Carga el SKILL.md correspondiente antes de producir artefactos de cada área:

| Skill | Área | Archivo |
|-------|------|---------|
| framework-platform | Infraestructura y despliegue | [SKILL.md](../skills/framework-platform/SKILL.md) |
| framework-scaffold-implementation | Scaffold e implementación inicial | [SKILL.md](../skills/framework-scaffold-implementation/SKILL.md) |
| framework-operations-evolution | Operación y evolución | [SKILL.md](../skills/framework-operations-evolution/SKILL.md) |

## Skills de consulta (no owner)

- [framework-core-design](../skills/framework-core-design/SKILL.md)
- [framework-pack-design](../skills/framework-pack-design/SKILL.md)
- [framework-security](../skills/framework-security/SKILL.md)
- [framework-qa-validation](../skills/framework-qa-validation/SKILL.md)

## Skills de stack

| Skill | Rol | Archivo |
|-------|-----|---------|
| database-migrations | primario | [SKILL.md](../skills/database-migrations/SKILL.md) |
| database-seeding | primario | [SKILL.md](../skills/database-seeding/SKILL.md) |
| data-migration | primario | [SKILL.md](../skills/data-migration/SKILL.md) |
| i18n | primario | [SKILL.md](../skills/i18n/SKILL.md) |
| feature-flags | primario | [SKILL.md](../skills/feature-flags/SKILL.md) |
| file-upload | primario | [SKILL.md](../skills/file-upload/SKILL.md) |
| real-time | primario | [SKILL.md](../skills/real-time/SKILL.md) |
| load-testing | primario | [SKILL.md](../skills/load-testing/SKILL.md) |
| infrastructure-as-code | primario | [SKILL.md](../skills/infrastructure-as-code/SKILL.md) |
| terraform | primario | [SKILL.md](../skills/terraform/SKILL.md) |
| kubernetes | primario | [SKILL.md](../skills/kubernetes/SKILL.md) |
| disaster-recovery | primario | [SKILL.md](../skills/disaster-recovery/SKILL.md) |
| ci-cd | primario | [SKILL.md](../skills/ci-cd/SKILL.md) |
| github-actions | primario | [SKILL.md](../skills/github-actions/SKILL.md) |
| gitlab-ci | primario | [SKILL.md](../skills/gitlab-ci/SKILL.md) |
| observabilidad | primario | [SKILL.md](../skills/observabilidad/SKILL.md) |
| prometheus-grafana | primario | [SKILL.md](../skills/prometheus-grafana/SKILL.md) |
| opentelemetry | primario | [SKILL.md](../skills/opentelemetry/SKILL.md) |
| langfuse | primario | [SKILL.md](../skills/langfuse/SKILL.md) |
| langchain | primario | [SKILL.md](../skills/langchain/SKILL.md) |
| kafka | primario | [SKILL.md](../skills/kafka/SKILL.md) |
| redis | primario | [SKILL.md](../skills/redis/SKILL.md) |
| bun-backend | primario | [SKILL.md](../skills/bun-backend/SKILL.md) |
| pgvector | primario | [SKILL.md](../skills/pgvector/SKILL.md) |
| api-versioning | secundario | [SKILL.md](../skills/api-versioning/SKILL.md) |
| api-resilience | secundario | [SKILL.md](../skills/api-resilience/SKILL.md) |
| unit-testing | primario | [SKILL.md](../skills/unit-testing/SKILL.md) |
| integration-testing | primario | [SKILL.md](../skills/integration-testing/SKILL.md) |
| a11y-testing | secundario | [SKILL.md](../skills/a11y-testing/SKILL.md) |
| acceptance-test-automation | secundario | [SKILL.md](../skills/acceptance-test-automation/SKILL.md) |
| accesibilidad | secundario | [SKILL.md](../skills/accesibilidad/SKILL.md) |
| agent-backend | secundario | [SKILL.md](../skills/agent-backend/SKILL.md) |
| agent-frontend | secundario | [SKILL.md](../skills/agent-frontend/SKILL.md) |
| agent-fullstack | secundario | [SKILL.md](../skills/agent-fullstack/SKILL.md) |
| agent-qa | secundario | [SKILL.md](../skills/agent-qa/SKILL.md) |
| angular | secundario | [SKILL.md](../skills/angular/SKILL.md) |
| angular-doctor | secundario | [SKILL.md](../skills/angular-doctor/SKILL.md) |
| angular-services | secundario | [SKILL.md](../skills/angular-services/SKILL.md) |
| angular-upgrade | secundario | [SKILL.md](../skills/angular-upgrade/SKILL.md) |
| api-catalog | secundario | [SKILL.md](../skills/api-catalog/SKILL.md) |
| api-contracts | secundario | [SKILL.md](../skills/api-contracts/SKILL.md) |
| api-first-backend | secundario | [SKILL.md](../skills/api-first-backend/SKILL.md) |
| api-first-frontend | secundario | [SKILL.md](../skills/api-first-frontend/SKILL.md) |
| api-gateway | secundario | [SKILL.md](../skills/api-gateway/SKILL.md) |
| api-integration | secundario | [SKILL.md](../skills/api-integration/SKILL.md) |
| app-bootstrap | secundario | [SKILL.md](../skills/app-bootstrap/SKILL.md) |
| backend-api | secundario | [SKILL.md](../skills/backend-api/SKILL.md) |
| code-review | secundario | [SKILL.md](../skills/code-review/SKILL.md) |
| data-access | secundario | [SKILL.md](../skills/data-access/SKILL.md) |
| database-audit | secundario | [SKILL.md](../skills/database-audit/SKILL.md) |
| database-modeling | secundario | [SKILL.md](../skills/database-modeling/SKILL.md) |
| database-sp | secundario | [SKILL.md](../skills/database-sp/SKILL.md) |
| docker-local | secundario | [SKILL.md](../skills/docker-local/SKILL.md) |
| documentation | secundario | [SKILL.md](../skills/documentation/SKILL.md) |
| error-handling | secundario | [SKILL.md](../skills/error-handling/SKILL.md) |
| export-excel | secundario | [SKILL.md](../skills/export-excel/SKILL.md) |
| framework-extensions | secundario | [SKILL.md](../skills/framework-extensions/SKILL.md) |
| graphql | secundario | [SKILL.md](../skills/graphql/SKILL.md) |
| incident-response | secundario | [SKILL.md](../skills/incident-response/SKILL.md) |
| memory-protocol | secundario | [SKILL.md](../skills/memory-protocol/SKILL.md) |
| microfrontend | secundario | [SKILL.md](../skills/microfrontend/SKILL.md) |
| mobile-pwa | secundario | [SKILL.md](../skills/mobile-pwa/SKILL.md) |
| notifications | secundario | [SKILL.md](../skills/notifications/SKILL.md) |
| oauth2-jwt | secundario | [SKILL.md](../skills/oauth2-jwt/SKILL.md) |
| openapi-docs | secundario | [SKILL.md](../skills/openapi-docs/SKILL.md) |
| playwright | secundario | [SKILL.md](../skills/playwright/SKILL.md) |
| postgresql-backup | secundario | [SKILL.md](../skills/postgresql-backup/SKILL.md) |
| progress-artifact | secundario | [SKILL.md](../skills/progress-artifact/SKILL.md) |
| project-architecture | secundario | [SKILL.md](../skills/project-architecture/SKILL.md) |
| project-bootstrap | secundario | [SKILL.md](../skills/project-bootstrap/SKILL.md) |
| pull-request | secundario | [SKILL.md](../skills/pull-request/SKILL.md) |
| react | secundario | [SKILL.md](../skills/react/SKILL.md) |
| react-doctor | secundario | [SKILL.md](../skills/react-doctor/SKILL.md) |
| react-services | secundario | [SKILL.md](../skills/react-services/SKILL.md) |
| react-upgrade | secundario | [SKILL.md](../skills/react-upgrade/SKILL.md) |
| readme | secundario | [SKILL.md](../skills/readme/SKILL.md) |
| repo-structure | secundario | [SKILL.md](../skills/repo-structure/SKILL.md) |
| security-testing | secundario | [SKILL.md](../skills/security-testing/SKILL.md) |
| shared-libs | secundario | [SKILL.md](../skills/shared-libs/SKILL.md) |
| tasks | secundario | [SKILL.md](../skills/tasks/SKILL.md) |
| typescript | secundario | [SKILL.md](../skills/typescript/SKILL.md) |

> **Ownership:** la asignación skill→agente se resuelve por `agent_roles` en SKILLS-MANIFEST.md (fuente única). Esta tabla es referencia orientativa y debe reflejar esa metadata.

## Protocolo de ejecución

Sigue el protocolo de [SKILL-EXECUTION-PROTOCOL.md](../framework/SKILL-EXECUTION-PROTOCOL.md) para cada skill.

### Dependencias de skills de delivery

```
framework-architecture (prerequisito de diseño)
    ├── framework-security (prerequisito de diseño)
    └── framework-data-memory-compliance (prerequisito de diseño)
        ↓
framework-platform
    ↓
framework-scaffold-implementation
    ↓
framework-qa-validation (gate — coordina con control-agent)
    ↓
framework-operations-evolution
```

## Principios de implementación

1. **Spec primero, código después**: No implementar sin spec aprobada. Si la spec cambia, actualizarla antes de modificar código.
2. **Idempotencia**: Toda operación (migración, seed, deploy) debe poder repetirse sin efectos secundarios.
3. **Validación en cada capa**: DTOs validan entrada, handlers validan reglas de negocio, DB valida constraints.
4. **Trazabilidad**: Cada mutación debe dejar rastro en audit_log.
5. **Multi-tenancy desde el día uno**: No añadir multi-tenancy después — hacerlo al inicio.
6. **ApiResponse envelope**: Toda respuesta sigue el formato {success, data, error, meta}.
7. **Sin secrets en código**: Usar variables de entorno o vault.

## CI/CD patterns

### Pipeline stages (recomendado)

```
lint → unit-test → build → integration-test → security-scan → deploy-staging → e2e → deploy-production
```

### Quality gates en CI

| Gate | Herramienta | Falla si |
|------|------------|----------|
| Lint | ruff/flake8/eslint | Cualquier error |
| Unit tests | pytest/jest/vitest | Cualquier test falla |
| Security scan | semgrep/snyk | Hallazgo CRITICAL o HIGH |
| Coverage | pytest-cov/istanbul | < 70% |
| Integration tests | pytest/httpx | Cualquier test falla |
| Build | pip/npm/build | Error de compilación |

## Template de runbook operativo

Para cada módulo en producción:

```
### Runbook: [Módulo]

#### Alertas
| Alerta | Severidad | Acción | SLA |
|--------|-----------|--------|-----|
| Error rate > 1% | P1 | Revisar logs, rollback si es necesario | 15 min |
| Latency p99 > 5s | P2 | Escalar horizontalmente, revisar queries | 30 min |
| Disk usage > 80% | P3 | Limpiar logs viejos, aumentar disco | 4h |

#### Procedimientos de recuperación
1. [Paso 1]
2. [Paso 2]

#### Contactos
- DevOps: #ops-slack
- DBA: #dba-slack
- Líder técnico: @tech-lead
```

## Deployment checklist

Antes de cada release:

- [ ] ¿CHANGELOG.md actualizado?
- [ ] ¿Tests unitarios pasando?
- [ ] ¿Tests de integración pasando?
- [ ] ¿Security scan sin hallazgos CRITICAL?
- [ ] ¿Migraciones de BD idempotentes?
- [ ] ¿Variables de entorno configuradas?
- [ ] ¿Rollback plan documentado?
- [ ] ¿Runbook actualizado?
- [ ] ¿SLOs verificados en staging?
- [ ] ¿PR revisado por al menos una persona?

## Operación post-lanzamiento

| Timeline | Acción |
|----------|--------|
| H+0 | Monitorear dashboards cada 5 min durante 1h |
| H+1 | Verificar SLOs contra baseline |
| H+24 | Revisar errores y performance |
| D+7 | Post-mortem si hubo incidentes |
| D+30 | Revisión de costos y optimización |

## Stack técnico: Python FastAPI

- Pydantic v2 para DTOs y validación
- SQLAlchemy 2.0 async para DB
- Alembic para migraciones
- pytest + httpx para tests
- PyJWT/passlib para JWT
- FastAPI para endpoints
- PostgreSQL 16 como base de datos
