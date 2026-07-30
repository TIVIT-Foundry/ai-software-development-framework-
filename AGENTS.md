# TIVIT Foundry — Framework Agéntico

**Proyecto**: TIVIT Foundry — Laboratorio Interno de IA
**Organización**: TIVIT (Latin America Technology)
**Autor**: Manuel Aliaga — Ingeniero de IA, TIVIT Foundry
**Última actualización**: 17 de julio de 2026

Este workspace contiene el **Framework Agéntico de TIVIT Foundry**: 108 skills, 4 agentes, 10 MCPs activos para diseñar, implementar y operar aplicaciones con agentes AI.

**Stack de referencia:**

| Capa | Tecnologías |
|------|-------------|
| AI/ML core | Python + FastAPI |
| Backend general | Bun (TypeScript) |
| Orchestration LLM | LangChain/LangGraph |
| Frontend | React (Vite) o Angular (elección por proyecto) |
| Database | PostgreSQL + pgvector |
| Cache/Colas | Redis + Kafka |
| Auth | OAuth2/JWT o Keycloak |
| Observability | Prometheus + Grafana + OpenTelemetry |
| LLM Observability | Langfuse |
| IaC | Terraform |
| CI/CD | GitHub Actions / GitLab CI |
| Containers | Docker + Kubernetes |

**Plataforma:** Windows (PowerShell)

## Cómo trabajar

- Consulta el catálogo de skills en `.opencode/skills/` para mapear tarea → skill
- Carga el `SKILL.md` de la skill activa antes de producir artefactos
- Sigue el protocolo de 7 pasos de [SKILL-EXECUTION-PROTOCOL.md](.opencode/framework/SKILL-EXECUTION-PROTOCOL.md)
- Usa agentes especializados según el dominio
- Revisa el routing de skills en [SKILL-ROUTING.md](.opencode/framework/SKILL-ROUTING.md)
- Revisa el modelo de agentes en [AGENT-MODEL.md](.opencode/framework/AGENT-MODEL.md)

## Agentes

| Agente | Rol | Invocación |
|--------|-----|-----------|
| `orchestrator` | Coordinar flujo de ejecución | `/orchestrator` |
| `design` | Artefactos de diseño (discovery, arquitectura, core) | `/design` |
| `control` | Governance, seguridad, compliance, validación | `/control` |
| `delivery` | Implementación, scaffold, plataforma, operación | `/delivery` |

Ver [AGENT-MODEL.md](.opencode/framework/AGENT-MODEL.md) para permisos, responsabilidades y límites de cada agente.

## Modos de ejecución

| Modo | Confirmaciones | Cuándo usar |
|------|---------------|-------------|
| **Hybrid** (default) | 15 | Nuevos packs verticales, balance calidad-velocidad |
| **Meta-Skills** | 6 | Módulos adicionales del mismo pack |
| **Per-Skill** | 49 | Audit, onboarding, escenarios de alta criticidad |

Por defecto se usa **Hybrid**:
- **Fases A-B** (N1-N9): modo individual — confirmas cada skill
- **Fases C-H** (N10-N49): modo bundle — ejecuto 6 bundles sin pausas internas

## Reglas de ejecución

1. **Modo Hybrid por defecto**: Fases A-B per-skill (N1-N9), fases C-H por bundle (N10-N49)
2. **Confirmación explícita**: Al completar cada skill (A-B) o cada bundle (C-H), mostrar resumen y esperar confirmación
3. **Meta-skills solo cuando el usuario las pide explícitamente**: `agent-backend`, `agent-frontend`, `agent-fullstack`, `agent-qa` no se activan automáticamente
4. **Framework-* skills son obligatorias**: Ninguna excepción sin registro en governance

## Documentos clave

| Área | Documentos |
|------|-----------|
| Framework | [SKILL-EXECUTION-PROTOCOL.md](.opencode/framework/SKILL-EXECUTION-PROTOCOL.md) · [SKILLS-MANIFEST.md](.opencode/framework/SKILLS-MANIFEST.md) · [SKILL-ROUTING.md](.opencode/framework/SKILL-ROUTING.md) · [AGENT-MODEL.md](.opencode/framework/AGENT-MODEL.md) |
| Configuración | [opencode.json](opencode.json) · [README.md](README.md) |
