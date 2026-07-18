# TIVIT Foundry — Framework Agéntico

> Framework interno de skills y agentes para desarrollo de software asistido por IA
> 
> **TIVIT — Latin America Technology**

## Información del Proyecto

- **Proyecto**: TIVIT Foundry — Laboratorio Interno de Inteligencia Artificial
- **Organización**: TIVIT (empresa brasileña de tecnología)
- **Autor**: Manuel Aliaga — Ingeniero de IA, TIVIT Foundry
- **Clasificación**: Proyecto privado interno — Uso exclusivo TIVIT
- **Última actualización**: 17 de julio de 2026

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
| **Frontend** | Angular 17+, TypeScript |
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
2. **Abres OpenCode** en tu proyecto → detecta 102 skills + 4 agentes automáticamente
3. **Pides lo que necesitas**: "Crea un módulo de usuarios con login, CRUD y roles"
4. **El orchestrator planifica**: descompone tu solicitud en fases (gobernanza → diseño → backend → frontend → testing)
5. **Los agentes ejecutan**: design diseña, delivery implementa, control valida
6. **Tú confirmas** en puntos clave (15 confirmaciones en modo Hybrid)
7. **Obtienes código listo para producción**: FastAPI + Angular + PostgreSQL, con tests, CI/CD, y seguridad

📖 **[Guía completa de flujo de usuario →](QUICKSTART.md)**

---

## Estructura del Proyecto

| Carpeta | Descripción |
|---------|-------------|
| `.opencode/skills/` | 102 skills organizadas por dominio |
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
- Frontend: Angular con TypeScript
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

102 skills organizadas por dominio (las categorías no son mutuamente excluyentes):

- **Framework** (12): governance, discovery, conception, architecture, core-design, pack-design, data-memory-compliance, security, platform, scaffold-implementation, qa-validation, operations-evolution
- **Gobernanza** (3): governance-constitution, sdd-onboard, documentation
- **Backend** (12): backend-api, bun-backend, data-access, api-integration, api-gateway, app-bootstrap, shared-libs, error-handling, file-upload, real-time, api-resilience, notifications
- **Frontend** (11): angular, angular-services, microfrontend, design-system, typescript, export-excel, accesibilidad, i18n, feature-flags, mobile-pwa, angular-upgrade
- **Database** (9): database-modeling, database-audit, database-security, database-sp, database-migrations, database-seeding, data-migration, pgvector, postgresql-backup
- **Testing/Calidad** (9): unit-testing, integration-testing, load-testing, security-testing, playwright, code-review, review-adversarial, uat-acceptance, a11y-testing
- **API/Spec** (9): openapi-docs, api-first-spec, api-first-backend, api-first-frontend, api-first-testing, api-catalog, api-versioning, api-resilience, api-contracts
- **Seguridad/Auth** (5): security, authentication, authorization, keycloak, oauth2-jwt
- **Operaciones** (11): ci-cd, github-actions, gitlab-ci, observabilidad, prometheus-grafana, opentelemetry, infrastructure-as-code, terraform, kubernetes, disaster-recovery, incident-response, postgresql-backup
- **AI/LLM** (4): langchain, costos-llm, kafka, memory-protocol
- **Observabilidad LLM** (1): langfuse
- **Proceso** (7): pull-request, hu-template, readme, html-prototype, project-bootstrap, skill-creator, framework-extensions
- **Arquitectura** (6): project-architecture, repo-structure, graphql, docker-local, performance, api-versioning
- **Meta-Skills** (4): agent-backend, agent-frontend, agent-fullstack, agent-qa

**Nuevas skills del catálogo expandido:** `bun-backend`, `redis`, `terraform`, `github-actions`, `gitlab-ci`, `kubernetes`, `prometheus-grafana`, `opentelemetry`, `langfuse`, `pgvector`, `postgresql-backup`, `oauth2-jwt`, `api-contracts`, `mobile-pwa`, `angular-upgrade`, `a11y-testing`

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
| **Framework y skills** | Manuel Aliaga — TIVIT Foundry |
| **Arquitectura y diseño** | TIVIT Foundry — Laboratorio de IA |

---

## Licencia

© 2024-2026 TIVIT. Todos los derechos reservados.

**Propiedad intelectual de TIVIT.** Uso exclusivo interno del laboratorio TIVIT Foundry. Prohibida su distribución, copia o modificación fuera de TIVIT sin autorización expresa.
