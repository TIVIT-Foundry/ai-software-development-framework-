# SKILL-ROUTING.md — Tabla de Routing de Skills

**TIVIT Foundry — Framework Agéntico**
**Versión:** 1.2.0
**Última actualización:** 3 de agosto de 2026

---

## Propósito

Este documento define qué skill(s) se activan según el tipo de cambio solicitado. El orchestrator lo usa para decidir qué ejecutar y en qué orden.

---

## Tabla de Routing por Tipo de Cambio

| Tipo de Cambio | Skills Primarias | Skills Secundarias | Agente |
|----------------|-----------------|-------------------|--------|
| **Cliente/proyecto nuevo (onboarding comercial)** | client-readiness-checklist → framework-discovery | requirements-intake (si aplica), project-bootstrap | orchestrator |
| **Requerimientos funcionales ambiguos o inexistentes** | requirements-intake → hu-template | framework-discovery | design |
| **Proyecto nuevo completo** | framework-governance → framework-discovery → framework-conception → framework-architecture → framework-core-design → framework-pack-design → framework-scaffold-implementation | Todas las skills de construction | orchestrator |
| **Nuevo módulo vertical** | framework-conception → framework-pack-design → api-first-spec → api-first-backend → api-first-frontend | database-modeling, database-sp, unit-testing | orchestrator |
| **Nuevo módulo backend** | api-first-spec → api-first-backend → data-access | database-sp, error-handling, shared-libs | delivery |
| **Nuevo módulo frontend** | api-first-spec → api-first-frontend → react (o angular, según elección del proyecto) | typescript, design-system, i18n | delivery |
| **Feature spec-first sin API** | feature-spec → tasks → (skills de implementación) → converge | hu-template, framework-conception | design → delivery → control |
| **Cambio transversal de seguridad** | framework-security → security → authentication → authorization | security-testing, database-security | control |
| **Cambio de base de datos** | database-modeling → database-migrations → database-seeding | database-audit, database-sp | delivery |
| **Cambio de API** | api-versioning → api-integration → api-resilience | api-catalog, openapi-docs | delivery |
| **Cambio de infraestructura** | framework-platform → infrastructure-as-code → docker-local | ci-cd, disaster-recovery | delivery |
| **Cambio de observabilidad** | observabilidad → costos-llm | ci-cd | delivery |
| **LLM/Agentic workflow** | langchain → costos-llm | keycloak, kafka | delivery |
| **Integración Keycloak** | keycloak → authentication → authorization | security | control |
| **Event-driven messaging** | kafka → real-time | observabilidad, docker-local | delivery |
| **Bugfix backend** | error-handling → api-integration | unit-testing | delivery |
| **Bugfix frontend** | react o angular (según el framework del proyecto) → typescript | unit-testing | delivery |
| **Incidente en producción** | incident-response → observabilidad → disaster-recovery | ci-cd | delivery |
| **UAT / Aceptación** | uat-acceptance → framework-qa-validation | hu-template | control |
| **Documentación de producto** | documentation → readme | governance-constitution, api-catalog, openapi-docs | design / delivery |
| **Testing y calidad** | unit-testing → integration-testing → playwright → security-testing | code-review, load-testing, a11y-testing | control |
| **Operación y despliegue** | ci-cd → observabilidad → disaster-recovery | framework-operations-evolution, prometheus-grafana, opentelemetry | delivery |
| **Infraestructura cloud** | framework-platform → infrastructure-as-code → terraform → kubernetes | docker-local, github-actions, gitlab-ci | delivery |
| **Bun backend** | bun-backend → api-contracts | shared-libs, error-handling | delivery |
| **Vector / RAG** | pgvector → langchain | database-modeling, costos-llm | delivery |
| **Auth con JWT** | oauth2-jwt → authentication → authorization | security-testing | control |

---

## Routing por Fase del Framework

### Fase A — Gobierno (N0-N4)

```
N0: requirements-intake      → design    (condicional: cliente sin documentación funcional formal)
N1: framework-governance     → control
N2: framework-discovery      → design
N3: framework-conception     → design
N4: hu-template              → design
```

`client-readiness-checklist` corre antes de N0/N1, como parte del onboarding comercial, y decide si N0 se activa.

### Fase B — Arquitectura (N5-N9)

```
N5: framework-architecture              → design
N6: framework-core-design               → design
N7: framework-pack-design               → design
N8: framework-data-memory-compliance    → control
N9: framework-security                  → control
```

### Fase C — Scaffold (N10-N15)

```
N10: framework-scaffold-implementation  → delivery
N11: project-architecture               → delivery
N12: project-bootstrap                  → delivery
N13: repo-structure                     → delivery
N14: app-bootstrap                      → delivery
N15: backend-api                        → delivery
```

### Fase D — Especificación (N16)

```
N16: api-first-spec → design
```

### Fase E — Backend (N17-N31)

```
N17: api-first-backend      → delivery
N18: database-modeling       → delivery
N19: database-sp             → delivery
N20: data-access             → delivery
N21: database-audit          → delivery
N22: database-migrations     → delivery
N23: database-seeding        → delivery
N24: database-security       → control
N25: authentication          → control
N26: authorization           → control
N27: error-handling          → delivery
N28: shared-libs             → delivery
N29: api-integration         → delivery
N30: api-resilience          → delivery
N31: api-versioning          → delivery
```

### Fase F — Frontend (N32-N37)

```
N32: api-first-frontend  → delivery
N33: react/angular        → delivery
N34: react-services/angular-services → delivery
N35: typescript           → delivery
N36: design-system        → design
N37: i18n                 → delivery
```

### Fase G — Calidad (N38-N44)

```
N38: unit-testing           → control
N39: integration-testing    → control
N40: playwright             → control
N41: security-testing       → control
N42: load-testing           → control
N43: code-review            → control
N44: accesibilidad          → control
```

### Fase H — Operación (N45-N49)

```
N45: ci-cd                       → delivery
N46: observabilidad              → delivery
N47: infrastructure-as-code      → delivery
N48: disaster-recovery           → delivery
N49: pull-request                → delivery
```

---

## Verificación de Prerequisitos

Antes de activar una skill, el orchestrator verifica:

1. **Dependencias directas:** Todas las skills en `depends_on` fueron completadas
2. **Artefactos de entrada:** Los archivos que esta skill necesita existen
3. **Permisos del agente:** El agente que ejecutará tiene los permisos necesarios
4. **Contexto del usuario:** El input del usuario es suficiente para continuar; si no, solicitar aclaraciones.

Si falta algún prerequisito, el orchestrator:
1. Intenta resolverlo automáticamente (si es posible)
2. Solicita al usuario la información faltante
3. Salta la skill y continúa con la siguiente (si es optional)

---

## Resolución de Conflictos

Cuando dos skills entran en conflicto:

1. **Governance wins:** Si `framework-governance` dice X y otra skill dice Y, prevalece governance
2. **Mandatory > Recommended:** Si una skill es `mandatory` y otra `recommended`, prevalece la mandatory
3. **Explicit > Implicit:** Si el usuario dijo explícitamente algo, prevalece sobre defaults
4. **Nuevo > Existente:** Si hay que elegir entre mantener algo existente o crear algo nuevo que lo reemplace, prevalece el nuevo (si fue aprobado)
