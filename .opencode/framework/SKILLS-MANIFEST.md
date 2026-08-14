# SKILLS-MANIFEST.md — Catálogo de Skills del Framework

**TIVIT Foundry — Framework Agéntico**
**Versión:** 2.3.0
**Última actualización:** 14 de agosto de 2026
**Total de skills:** 114

---

## Convenciones

- **Fase:** inception | conception | governance | architecture | scaffold | construction | quality | operations | closure
- **Layer:** business | design | implementation | infrastructure | testing | operations | backend | frontend | database | governance | process | scaffold | testing/frontend
- **Enforcement:** mandatory | recommended | optional
- **Stack:** Python/FastAPI | React o Angular | Bun/TypeScript | PostgreSQL | Multi

---

## Skills por Dominio

### Framework-* (12 skills) — Governance del Framework

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| framework-governance | governance | governance | mandatory | Constitución del framework: principios, reglas, estándares, excepciones |
| framework-discovery | inception | business | mandatory | Discovery de vertical: problema, actores, procesos, datos |
| framework-conception | conception | business | mandatory | Concepción funcional: capacidades, agentes, flujos, MVP |
| framework-architecture | architecture | design | mandatory | Arquitectura técnica: 7 capas, componentes, contratos, Build vs Buy |
| framework-core-design | architecture | design | mandatory | Core agéntico: SDK, orquestación, router, MCP tools, trazabilidad |
| framework-pack-design | architecture | design | mandatory | Pack vertical como producto: capacidades, agentes, prompts, runbooks |
| framework-data-memory-compliance | architecture | design | mandatory | Datos, memoria y compliance: taxonomía, stores, retención, cifrado |
| framework-security | architecture | design | mandatory | Seguridad: RBAC, guardrails, secretos, auditoría, tool calling |
| framework-platform | operations | infrastructure | mandatory | Plataforma: K8s, despliegue, namespaces, mensajería, observabilidad |
| framework-scaffold-implementation | scaffold | implementation | mandatory | Scaffold: repos, módulos, SDK, core, pack, entorno local |
| framework-qa-validation | quality | implementation | mandatory | QA: contract tests, integración, validación, go/no-go |
| framework-operations-evolution | operations | operations | mandatory | Operación: monitoreo, incidentes, SLOs, versionado, deprecación |

### Gobernanza (3 skills)

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| governance-constitution | governance | governance | mandatory | Constitución: principios inmutables, reglas no negociables, gates de arquitectura, anti-patrones |
| sdd-onboard | inception | business | recommended | Onboarding a Spec-Driven Development: fases del flujo, ruta por rol, checklist de primera semana |
| documentation | construction | implementation | recommended | Documentación como fase SDLC de primera clase: ADRs, docs de API, guías de codebase, docs-as-code |

### Agent Meta-Skills (4 skills) — Orquestación de Agentes

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| agent-backend | construction | implementation | optional | Activa todas las skills backend en secuencia |
| agent-frontend | construction | implementation | optional | Activa todas las skills frontend en secuencia |
| agent-fullstack | construction | implementation | optional | Activa backend + frontend completo |
| agent-qa | quality | testing | optional | Activa todas las skills de testing |

### API-* (11 skills) — Diseño e Implementación de APIs

| Skill | Fase | Layer | Enforcement | Stack | Descripción |
|-------|------|-------|-------------|-------|-------------|
| api-first-spec | inception | backend | mandatory | Multi | Especificación API completa por módulo |
| api-first-backend | construction | backend | mandatory | Python | Backend desde OpenAPI: SP → Handler → DTOs → Endpoint |
| api-first-frontend | construction | frontend | mandatory | React/Angular | Frontend desde OpenAPI: types → hooks/services → components |
| api-first-testing | quality | testing | mandatory | Multi | Tests desde OpenAPI: contract, E2E, schema validation |
| api-catalog | operations | backend | recommended | Multi | Inventario DB → Endpoint → Service ID → Screen → Route |
| api-gateway | construction | backend | recommended | Multi | API Gateway: routing, auth, rate limiting, NGINX |
| api-integration | construction | backend | mandatory | Python | DB-to-API: error mapping, paginación, validación |
| api-resilience | construction | backend | recommended | Python | Resiliencia: rate limiting, circuit breakers, retry |
| api-versioning | construction | backend | mandatory | Python | Versionado: URI, headers, deprecation, backward compat |
| api-contracts | construction | backend/frontend | mandatory | Multi | Contratos compartidos: Pydantic, TypeScript, OpenAPI components |
| openapi-docs | construction/operations | backend | mandatory | Python | Generación y mantenimiento de documentación OpenAPI/Swagger |

### Database-* (8 skills) — Base de Datos PostgreSQL

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| database-modeling | inception | database | mandatory | Modelado y convenciones: tablas, constraints, índices, CTEs, schemas, naming, parámetros |
| database-audit | construction | database | mandatory | Auditoría: columnas audit, soft delete, log tables |
| database-migrations | construction | database | mandatory | Migraciones: Alembic, naming, rollback, multi-tenancy |
| database-seeding | construction | database | mandatory | Seeding: UPSERT, multi-tenant, fixtures, catalogs |
| database-security | construction | database | mandatory | Seguridad: validación, injection prevention, error codes |
| database-sp | construction | database | mandatory | Stored Procedures: CRUD templates PL/pgSQL |
| pgvector | construction | database | recommended | Vector search y RAG: embeddings, HNSW/IVFFlat, hybrid search |
| postgresql-backup | operations | database | recommended | Backup, restore, PITR, DR de PostgreSQL |

### Data-* (2 skills) — Acceso y Migración de Datos

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| data-access | construction | backend | mandatory | Data access handlers: SQLAlchemy 2.0 async, repositorios |
| data-migration | construction | database | recommended | Migración de datos: ETL, transformación, verificación |

### React (2 skills) — Frontend

| Skill | Fase | Layer | Enforcement | Stack | Descripción |
|-------|------|-------|-------------|-------|-------------|
| react | construction | frontend | mandatory | React | Function components, hooks, routing, code-splitting |
| react-services | construction | frontend | mandatory | React | Data hooks, @tanstack/react-query, Zustand, fetch client |

### Angular (2 skills) — Frontend (alternativa a React, ver ADR-005)

| Skill | Fase | Layer | Enforcement | Stack | Descripción |
|-------|------|-------|-------------|-------|-------------|
| angular | construction | frontend | recommended | Angular | Component architecture, signals, DI, routing, CDK |
| angular-services | construction | frontend | recommended | Angular | Services, RxJS, @ngneat/query, signals, toSignal() |

### Testing (11 skills) — Aseguramiento de Calidad

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| unit-testing | quality | testing | mandatory | Unit: pytest, Vitest, TestBed, AAA pattern |
| integration-testing | quality | testing | mandatory | Integration: TestContainers, contract tests |
| load-testing | quality | testing | recommended | Load: k6, Locust, perfiles de carga, SLOs |
| security-testing | quality | testing | recommended | Security: SAST, DAST, dependency scanning |
| playwright | quality | testing | mandatory | E2E: Page Objects, selectors, API testing |
| a11y-testing | quality | testing/frontend | recommended | A11y automatizado: axe-core, Playwright, keyboard nav |
| react-doctor | quality | testing/frontend | recommended | Gate automatizado (npx react-doctor): anti-patrones React, deterministico |
| angular-doctor | quality | testing/frontend | recommended | Gate automatizado (npx angular-doctor): lint Angular-aware, health score, dead code |
| acceptance-test-automation | quality | testing | recommended | Ejecuta criterios de aceptación confirmados contra la implementación real (web/API + fixtures no-UI), evidencia pass/fail/ambiguo por criterio |
| review-adversarial | quality | testing | recommended | Revisión adversarial: instancias paralelas desde ángulos distintos, veredictos con evidencia |
| uat-acceptance | quality | business | recommended | UAT: criterios de aceptación, sign-off de stakeholders, entorno UAT, decisión go/no-go |

### Seguridad (4 skills)

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| security | construction | implementation | mandatory | OWASP Top 10, CORS, injection prevention, headers |
| authentication | construction | backend | mandatory | JWT, OAuth2/OIDC, Keycloak, sesiones |
| authorization | construction | backend | mandatory | RBAC, permisos por recurso, FastAPI Depends |
| oauth2-jwt | construction | backend/frontend | recommended | OAuth2/JWT puro: token issuance, validation, scopes, refresh |

### Infraestructura (10 skills)

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| ci-cd | operations | operations | mandatory | GitHub Actions, GitLab CI, pipelines, secrets |
| docker-local | construction | infrastructure | recommended | Docker Compose, multi-stage builds, servicios |
| infrastructure-as-code | operations | infrastructure | mandatory | Terraform: módulos, state, drift detection |
| terraform | operations | infrastructure | recommended | Terraform multi-cloud: AWS/GCP/Azure, workspaces, modules |
| kubernetes | operations | infrastructure | recommended | K8s manifests, Helm, namespaces, HPA, NetworkPolicies |
| redis | construction | backend | recommended | Cache, sesiones, rate limiting, locks, colas livianas |
| github-actions | operations | infrastructure | recommended | Pipelines con GitHub Actions |
| gitlab-ci | operations | infrastructure | recommended | Pipelines con GitLab CI/CD |
| disaster-recovery | operations | operations | recommended | Backup/restore, failover, RTO/RPO, DR drills |
| incident-response | operations | operations | mandatory | Respuesta a incidentes: severidad, runbooks, escalamiento, postmortems blameless |

### Observabilidad (5 skills)

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| observabilidad | operations | operations | mandatory | Logs, metrics, traces, OpenTelemetry, Langfuse, Prometheus |
| costos-llm | operations | governance | recommended | Token tracking, pgvector cache, LangChain, Langfuse |
| prometheus-grafana | operations | operations | recommended | Métricas, dashboards, alertas, SLOs/SLIs |
| opentelemetry | construction/operations | infrastructure | recommended | Trazas distribuidas, instrumentación, context propagation |
| langfuse | construction/operations | backend | recommended | Observabilidad de LLM: prompts, costos, feedback |

### Backend General (8 skills)

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| backend-api | construction | backend | mandatory | Estructura FastAPI: modules, endpoints, Pydantic |
| bun-backend | construction | backend | recommended | Backend con Bun/TypeScript: routing, validación, tests |
| app-bootstrap | construction | backend | mandatory | Entry point: FastAPI app, middleware, health checks |
| error-handling | construction | implementation | mandatory | Errores: taxonomy, handlers, ApiResponse, correlation IDs |
| shared-libs | construction | implementation | recommended | Librerías compartidas: contratos, excepciones, middleware |
| real-time | construction | backend | recommended | WebSockets, SSE, pub/sub, Redis backplane |
| file-upload | construction | backend | recommended | Upload: multipart, storage, MIME, CDN |
| notifications | construction | backend | recommended | Notificaciones: in-app, email, push, webhook |

### Frontend General (11 skills)

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| typescript | construction | frontend | mandatory | TypeScript estricto: const types, Zod, discriminated unions |
| design-system | inception | frontend | recommended | Tokens, tipografía, spacing, theming, Storybook |
| accesibilidad | quality | frontend | mandatory | WCAG 2.2 AA, ARIA, keyboard nav, axe-core |
| html-prototype | inception | frontend | optional | Mockups HTML + CSS + JS, interactive prototypes |
| microfrontend | construction | frontend | recommended | Module Federation, Host/Child, Import Maps |
| i18n | construction | frontend | recommended | react-i18next, locale files, RTL, Intl formatting |
| mobile-pwa | construction | frontend | optional | PWA: service workers, offline, push notifications |
| react-upgrade | operations | frontend | optional | Migración de versiones React/Vite/Next.js y legacy → moderno |
| angular-upgrade | operations | frontend | optional | Migración de versiones Angular, NgModules → standalone/signals |
| export-excel | construction | database/backend/frontend | recommended | Export a Excel: query → handler → endpoint → download hook |
| feature-flags | construction | frontend | recommended | Feature flags: rollout progresivo, A/B testing, kill switches, targeting |

### Proceso (7 skills)

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| client-readiness-checklist | inception | business | recommended | Checklist de qué necesita el framework para operar en un cliente/proyecto nuevo |
| requirements-intake | inception | business | recommended | "Documento Cero": convierte input funcional ambiguo del cliente en línea base confirmada |
| hu-template | inception | business | mandatory | Template de Historias de Usuario |
| pull-request | closure | implementation | mandatory | PR template, conventional commits, changelog |
| code-review | quality | implementation | recommended | Checklist de revisión: backend, frontend, database |
| readme | closure | implementation | optional | Template README para módulos |
| framework-extensions | construction | implementation | recommended | Sistema de extensiones: plugin architecture, manifest schema, hooks |

### Spec-Driven Development (3 skills)

Cierran el ciclo que `sdd-onboard` enseña: spec → tasks → converge. `api-first-spec` ya cubre el caso con API; estas skills completan el resto del ciclo y los features sin API.

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| feature-spec | inception | business | recommended | Spec-first para features sin superficie REST (UI-only, data-only, cross-cutting) |
| tasks | inception | business | recommended | Descompone un spec en tareas ordenadas y verificables (2-4h c/u) |
| converge | quality | testing | recommended | Verifica que el código implementado coincide con el spec, antes del PR |

### Especializadas (6 skills) — LangChain, Keycloak, Kafka, GraphQL

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| langchain | construction | backend | mandatory | LangChain/LangGraph: chains, agents, tools, memory, RAG |
| keycloak | construction | backend | mandatory | Keycloak: OIDC, JWT validation, RBAC, realms, user sync |
| kafka | construction | backend | recommended | Apache Kafka: producers, consumers, topics, DLQ |
| graphql | construction | backend | recommended | GraphQL: schema, resolvers, Strawberry, Apollo |
| skill-creator | operations | implementation | optional | Crea nuevas skills del framework |
| memory-protocol | construction | backend | mandatory | Protocolo de memoria persistente para agentes: decisiones, bugs, sesiones, resolución de conflictos |

### Otros (5 skills)

| Skill | Fase | Layer | Enforcement | Descripción |
|-------|------|-------|-------------|-------------|
| project-architecture | inception | design | mandatory | Vertical Slice, Modular Monolith, naming |
| project-bootstrap | inception | scaffold | mandatory | Onboarding a proyecto nuevo |
| repo-structure | inception | scaffold | recommended | Convenciones de repositorio |
| performance | construction | database/backend/frontend | recommended | Paginación, caching, query optimization, manejo de datos grandes |
| progress-artifact | operations | process | recommended | Dashboard de progreso (artifact HTML): módulos de negocio, fases N0-N49, dónde quedó la IA — para dev, IA y supervisores |

---

## Fases del Framework

| Fase | Niveles | Skills | Confirmaciones |
|------|---------|--------|---------------|
| A — Gobierno | N0-N4 | requirements-intake, framework-governance, framework-discovery, framework-conception, hu-template | 5 |
| B — Arquitectura | N5-N9 | framework-architecture, framework-core-design, framework-pack-design, framework-data-memory-compliance, framework-security, framework-platform | 5 |
| C — Scaffold | N10-N15 | framework-scaffold-implementation, project-architecture, project-bootstrap, repo-structure, app-bootstrap, backend-api | 1 |
| D — Especificación | N16 | api-first-spec | 1 |
| E — Backend | N17-N31 | api-first-backend, data-access, database-*, pgvector, authentication, authorization, oauth2-jwt, error-handling, shared-libs, api-integration, api-resilience, api-versioning, api-gateway, redis, real-time, file-upload, notifications, costos-llm | 1 |
| F — Frontend | N32-N37 | api-first-frontend, react, angular, react-services, angular-services, typescript, design-system, i18n, mobile-pwa | 1 |
| G — Calidad | N38-N44 | unit-testing, integration-testing, playwright, security-testing, load-testing, code-review, accesibilidad, a11y-testing, acceptance-test-automation | 1 |
| H — Operación | N45-N49 | ci-cd, github-actions, gitlab-ci, observabilidad, prometheus-grafana, opentelemetry, infrastructure-as-code, terraform, kubernetes, disaster-recovery, postgresql-backup, pull-request, langfuse, framework-operations-evolution | 1 |

> **N0 (`requirements-intake`) es condicional**: solo se activa cuando el cliente no trae documentación funcional formal — ver `client-readiness-checklist`. No cuenta como confirmación extra cuando se omite.
>
> `api-contracts` se activa junto a la Fase D o E cuando el módulo define contratos compartidos (sin nivel propio).
>
> `framework-platform` se ejecuta al cierre de Fase B (prerequisito de N10) y `framework-operations-evolution` al cierre de Fase H — ambos sin nivel propio (precedente: `acceptance-test-automation`), para no renumerar la secuencia existente.

**Nota:** Las fases suman 16 confirmaciones con N0 activo (A=5, B=5, C-H=6); en modo Hybrid el total es **15** porque N0 no cuenta cuando se omite (A queda en 4). Las skills `recommended`/`optional` se activan bajo demanda según el contexto del proyecto. Las skills del catálogo que no tienen nivel propio en las fases (p. ej. `react-upgrade`, `angular-upgrade`, `github-actions`, `gitlab-ci`, `terraform`, `kubernetes`, `prometheus-grafana`, `opentelemetry`, `postgresql-backup`, `feature-spec`, `tasks`, `converge`, `bun-backend`) se activan por routing de cambio de tipo (ver SKILL-ROUTING).
