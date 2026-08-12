# MCP Setup — TIVIT Foundry

Guía de configuración de los MCP servers del framework. Referenciada desde `.env.example`.

## Estado

| MCP | Estado | Variable de entorno requerida |
|-----|--------|-------------------------------|
| context7 | activo | — |
| playwright | activo | — |
| docker | activo | — |
| package-registry | activo | — |
| filesystem | activo | — |
| github | activo | `GITHUB_PERSONAL_ACCESS_TOKEN` |
| postgres | activo | `POSTGRES_CONNECTION_STRING` |
| notion | desactivado (opcional) | `NOTION_TOKEN` |
| gcloud | desactivado (opcional) | `GOOGLE_APPLICATION_CREDENTIALS` |
| observability | desactivado (opcional) | `GOOGLE_APPLICATION_CREDENTIALS` |

## Setup

1. Copiar `.env.example` a `.env` (el `.env` está en `.gitignore`, nunca se commitea).
2. Completar las variables `[REQUIRED]` de los MCPs que se usen.
3. opencode carga los MCPs al iniciar: **reiniciar opencode** después de editar `.env` u `opencode.json`.

## Habilitar/deshabilitar un MCP

En `opencode.json`, sección `mcp`:

```json
"notion": {
  "type": "local",
  "command": ["npx", "-y", "@notionhq/notion-mcp-server"],
  "enabled": false
}
```

- `enabled: false` mantiene el MCP definido pero inactivo.
- Variables marcadas `[REQUIRED]` en `.env.example` solo aplican cuando el MCP está `enabled: true`.

## Gobernanza

Cada MCP declarado en `opencode.json` debe tener su entrada en `.opencode/mcp-metadata.json`
(purpose, risk_tier, authorized_by, authorized_date, review_date, allowed_agents).
`check-mcp-config.py` valida la consistencia y advierte si un MCP activo no tiene fechas de
autorización/revisión.
