# MCP-GOVERNANCE.md — Gobernanza de MCP Servers del Framework

**Versión:** 1.0
**Fecha:** 2026-08-14
**Alcance:** clasificación de riesgo, autorización y revisión de los MCP servers configurados en `opencode.json` y registrados en `mcp-metadata.json`.

## Risk Tiers

| Tier | Definición | Ejemplos | Controles |
|------|------------|----------|-----------|
| `low` | Lectura de información pública / documentación; sin escritura ni datos sensibles | context7, package-registry | Autorización: control-agent. Sin auditoría obligatoria |
| `medium` | Acceso a recursos del proyecto o automatización acotada | playwright, docker, filesystem, github | Autorización: control-agent. Auditoría habilitada |
| `medium-high` | Datos sensibles, infraestructura o escritura de alto impacto | postgres, gcloud | Autorización: control-agent + framework-governance (+ SLA review para infraestructura cloud) |
| `high` | Producción, datos críticos o ejecución no reversible | (ninguno autorizado hoy) | Requiere governance + revisión de seguridad formal |

## Proceso de autorización de un MCP nuevo

1. **Clasificar** el MCP en un risk tier según la tabla.
2. **Registrar** en `mcp-metadata.json`: `type`, `risk_tier`, `purpose`, `authorized_by`, `authorized_date`, `scope`, `allowed_agents`, `secrets_managed_by`, `audit_enabled`, `review_date`.
3. **Validar** con `check-mcp-config.py` (forma parte de `run-all.ps1`): sin entrada de metadata, un MCP activo genera WARN; fechas vacías advierten siempre; `review_date` vencida advierte siempre.
4. **Configurar** en `opencode.json` con `enabled: true` solo cuando el MCP está autorizado y tiene credenciales disponibles.

## Política de revisión

- Cada MCP autorizado tiene `review_date` (por defecto 6-12 meses desde `authorized_date`).
- Un `review_date` vencida genera WARN del validador: renovar la autorización o deshabilitar el servidor.
- Los MCP deshabilitados con metadata incompleta (`authorized_date`/`review_date` vacíos) quedan como deuda de gobernanza visible (WARN permanente) hasta completar o eliminar su registro.

## Secretos

- `secrets_managed_by`: `none` | `env` (variable de entorno vía `{env:VAR}` en opencode.json) | `oauth` (token gestionado por el host, p. ej. `opencode mcp auth`).
- Nunca pegar tokens literales en `opencode.json` (especialmente en headers JSON inline): usar siempre `{env:VAR}`.
