# TIVIT Foundry — Framework Agéntico

> Framework interno de skills y agentes para desarrollo de software asistido por IA
> 
> **TIVIT — Latin America Technology**

## Información del Proyecto

- **Proyecto**: TIVIT Foundry — Laboratorio Interno de Inteligencia Artificial
- **Organización**: TIVIT (empresa brasileña de tecnología)
- **Autor**: Manuel Aliaga — Ingeniero de IA, TIVIT Foundry
- **Clasificación**: Proyecto privado interno — Uso exclusivo TIVIT
- **Última actualización**: 3 de agosto de 2026

## Confidencialidad

Este repositorio contiene propiedad intelectual de **TIVIT** y está destinado exclusivamente para uso interno del laboratorio TIVIT Foundry.

**No compartir fuera de TIVIT sin autorización expresa de la dirección.**

---

## Stack Tecnológico

| Capa | Tecnologías |
|------|-------------|
| **AI/ML Core** | Python 3.12 / FastAPI |
| **Backend General** | Bun (TypeScript) |
| **Orchestration LLM** | LangChain / LangGraph |
| **Frontend** | React 18+ (Vite, o Next.js App Router para SSR/SEO) o Angular 17+, TypeScript (elección por proyecto) |
| **Database** | PostgreSQL 16 + pgvector |
| **Cache/Colas** | Redis + Kafka |
| **Auth** | OAuth2/JWT / Keycloak |
| **Observability** | Prometheus + Grafana + OpenTelemetry |
| **LLM Observability** | Langfuse |
| **IaC** | Terraform |
| **CI/CD** | GitHub Actions / GitLab CI |
| **Containers** | Docker + Kubernetes |
| **Arquitectura** | Vertical Slice, Modular Monolith |

---

## Cómo funciona (Flujo de usuario)

1. **Clonas** el framework en tu proyecto (solo la carpeta `.opencode/` + `opencode.json` + `AGENTS.md`)
2. **Abres OpenCode** en tu proyecto → detecta 114 skills + 4 agentes automáticamente
3. **Pides lo que necesitas**: "Crea un módulo de usuarios con login, CRUD y roles"
4. **El orchestrator planifica**: descompone tu solicitud en fases (gobernanza → diseño → backend → frontend → testing)
5. **Los agentes ejecutan**: design diseña, delivery implementa, control valida
6. **Tú confirmas** en puntos clave (15 confirmaciones en modo Hybrid)
7. **Obtienes código listo para producción**: FastAPI + React/Angular + PostgreSQL, con tests, CI/CD, y seguridad

📖 **[Guía completa de flujo de usuario →](QUICKSTART.md)**
🗺️ **[Roadmap →](docs/ROADMAP.md)**

---

## Estructura del Proyecto

| Carpeta | Descripción |
|---------|-------------|
| `.opencode/skills/` | 114 skills organizadas por dominio |
| `.opencode/agents/` | 4 agentes especializados |
| `.opencode/validators/` | Scripts PowerShell de validación |
| `.opencode/scaffold/` | Generador de código desde specs |
| `opencode.json` | Configuración principal de OpenCode |
| `AGENTS.md` | Instrucciones base del framework |

---

## Inicio Rápido

### Requisitos previos

- **OpenCode** — instalado y configurado
- **Python 3.12+**
- **Node.js 18+** (para servidores MCP)
- **PostgreSQL 16**
- **Git** configurado
- **Docker** (opcional)

### Verificar que el framework está activo

1. Abre OpenCode en este workspace
2. Escribe: `¿Qué skills tienes disponibles?`
3. Deberías ver una lista de skills del framework

### Crear tu primer módulo

```
Quiero crear un nuevo proyecto agéntico.

Vertical: Productividad / Gestión interna de tareas.

Tecnologías:
- Backend: Python 3.12 con FastAPI
- Frontend: React o Angular con TypeScript
- Base de datos: PostgreSQL

El primer módulo es Gestión de Tareas:
- ID (entero, auto-generado)
- Título (texto, requerido, máximo 200 caracteres)
- Descripción (texto, opcional, máximo 1000 caracteres)
- Estado (enum: Pendiente, Completada)
- Fecha de creación (datetime, auto-generado)
```

---

## Agentes

| Agente | Rol | Invocación |
|--------|-----|-----------|
| `orchestrator` | Coordinar flujo de ejecución | `/orchestrator` |
| `design` | Artefactos de diseño | `/design` |
| `control` | Governance y seguridad | `/control` |
| `delivery` | Implementación y operación | `/delivery` |

---

## Modos de Ejecución

| Modo | Confirmaciones | Cuándo usar |
|------|---------------|-------------|
| **Hybrid** (default) | 15 | Proyectos nuevos, balance calidad-velocidad |
| **Meta-Skills** | 6 | Módulos adicionales repetitivos |
| **Per-Skill** | 49 | Proyectos críticos, aprendizaje |

---

## Scripts PowerShell

### Validadores

```powershell
# Configurar entorno virtual
.\.opencode\validators\setup-venv.ps1

# Ejecutar todos los validadores
.\.opencode\validators\run-all.ps1
```

### Renombrar skills

```powershell
.\.opencode\validators\rename-skill.ps1 <old-name> <new-name>
```

---

## Skills Disponibles

114 skills organizadas por dominio (las categorías no son mutuamente excluyentes):

- **Framework** (12): framework-governance, framework-discovery, framework-conception, framework-architecture, framework-core-design, framework-pack-design, framework-data-memory-compliance, framework-security, framework-platform, framework-scaffold-implementation, framework-qa-validation, framework-operations-evolution
- **Gobernanza** (3): governance-constitution, sdd-onboard, documentation
- **Backend** (13): backend-api, bun-backend, data-access, api-integration, api-gateway, app-bootstrap, shared-libs, error-handling, file-upload, real-time, api-resilience, notifications, redis
- **Frontend** (14): react, react-services, react-upgrade, angular, angular-services, angular-upgrade, microfrontend, design-system, typescript, export-excel, accesibilidad, i18n, feature-flags, mobile-pwa
- **Database** (9): database-modeling, database-audit, database-security, database-sp, database-migrations, database-seeding, data-migration, pgvector, postgresql-backup
- **Testing/Calidad** (12): unit-testing, integration-testing, load-testing, security-testing, playwright, code-review, review-adversarial, uat-acceptance, a11y-testing, acceptance-test-automation, react-doctor, angular-doctor
- **API/Spec** (9): openapi-docs, api-first-spec, api-first-backend, api-first-frontend, api-first-testing, api-catalog, api-versioning, api-resilience, api-contracts
- **Seguridad/Auth** (5): security, authentication, authorization, keycloak, oauth2-jwt
- **Operaciones** (12): ci-cd, github-actions, gitlab-ci, observabilidad, prometheus-grafana, opentelemetry, infrastructure-as-code, terraform, kubernetes, disaster-recovery, incident-response, postgresql-backup
- **AI/LLM** (4): langchain, costos-llm, kafka, memory-protocol
- **Observabilidad LLM** (1): langfuse
- **Proceso** (9): pull-request, hu-template, readme, html-prototype, project-bootstrap, skill-creator, framework-extensions, requirements-intake, client-readiness-checklist
- **Spec-Driven Development** (3): feature-spec, tasks, converge
- **Arquitectura** (6): project-architecture, repo-structure, graphql, docker-local, performance, api-versioning
- **Meta-Skills** (4): agent-backend, agent-frontend, agent-fullstack, agent-qa

---

## Para agentes AI

El framework está diseñado para que los agentes AI **se autoconfiguren al llegar** a un proyecto:

1. **Carga automática**: `opencode.json` inyecta `.opencode/AGENT-ONBOARDING.md` en cada sesión — el agente arranca con un checklist de verificación (versión del framework, integridad con validators, dónde quedó el trabajo).
2. **Orientación**: `.workflow/state.json` (resume_hint) + `docs/artifacts/progress.html` (dashboard visual de módulos/fases) + `.workflow/framework-notes.md` (errores conocidos).
3. **Routing**: `.opencode/framework/SKILL-ROUTING.md` decide qué skill activar según el tipo de cambio y la fase N0-N49.
4. **Auto-update**: si el proyecto tiene una versión del framework desactualizada, el agente ofrece `update-framework.ps1` (backup + sync + validators) antes de trabajar.
5. **Auto-reporte**: al cerrar fase/bundle, el agente regenera el dashboard de progreso (skill `progress-artifact`).

Los agentes que no carguen el onboarding automáticamente deben leer `.opencode/AGENT-ONBOARDING.md` por ruta directa al iniciar la sesión.

---

## Seguridad

- Prevención de SQL Injection — Queries parametrizadas
- Prevención de XSS — Sanitización de contenido
- OWASP Top 10 — Controles integrados
- Gestión de Secretos — Variables de entorno, nunca en código

---

## Soporte

| Tipo de consulta | Contacto |
|------------------|----------|
| **Framework y skills** | Matías Méndez — TIVIT Foundry |
| **Arquitectura y diseño** | Manuel Aliaga — TIVIT Foundry |

---

## Licencia

© 2024-2026 TIVIT. Todos los derechos reservados.

**Propiedad intelectual de TIVIT.** Uso exclusivo interno del laboratorio TIVIT Foundry. Prohibida su distribución, copia o modificación fuera de TIVIT sin autorización expresa.
