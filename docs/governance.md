# Governance del Framework — TIVIT Foundry

**Versión:** 1.0
**Fecha:** 2026-08-14
**Alcance:** registro de excepciones, deuda técnica/de seguridad y aprobadores del framework. Los proyectos adoptantes copian este documento a `docs/governance.md` y lo mantienen por proyecto.

## Reglas

- Las reglas del framework (enforcement mandatory/recommended/variable) viven en `framework-governance` y `SKILLS-MANIFEST.md`.
- Ninguna excepción se aplica sin registro (abajo) con owner y fecha de revisión.
- La deuda aceptada NO es una excepción aprobada: se registra como `DEUDA-NNN`.
- Las skills framework-\* son obligatorias: ninguna excepción sin registro en este documento.

## Excepciones (EXC-NNN)

Se considera excepción cualquier propuesta que:

- omita una de las 7 capas;
- procese requests sin tenant resuelto;
- mezcle datos o memoria entre tenants;
- acople un pack a un único LLM o proveedor;
- elimine trazabilidad o auditoría;
- quite guardrails o gestión de secretos;
- haga que la lógica propia dependa de una nube o plataforma no portable.

Toda excepción se documenta con el siguiente formato (control-agent recomienda y documenta; **la aprobación final la decide el owner del proyecto / usuario**):

```
### EXC-NNN
- Fecha: YYYY-MM-DD
- Solicitante: [agente/usuario]
- Regla violada: [referencia]
- Justificación: [razón de negocio/técnica]
- Alcance: [qué cubre]
- Riesgo: [impacto concreto]
- Mitigación: [control parcial aplicado]
- Owner: [responsable]
- Revisión: YYYY-MM-DD
- Estado: ACTIVA | VENCIDA | RESUELTA
```

## Deuda técnica y de seguridad (DEUDA-NNN)

| ID | Tipo | Descripción | Riesgo si no se paga | Mitigación temporal | Owner | Revisión |
|----|------|-------------|----------------------|---------------------|-------|----------|
| (sin deuda registrada) | | | | | | |

- **Tipo**: `seguridad` | `técnica` | `calidad`.
- La deuda no puede quedar solo en el state del workflow (`.workflow/state.json`): se registra aquí.
- **Deuda de seguridad**: revisión en máximo 30 días.

## Aprobadores

| Área | Aprobador |
|------|-----------|
| Excepciones al framework | Owner del proyecto (HITL) — control-agent recomienda, no aprueba |
| Releases / go-no-go | control-agent (QA gate) + owner |
| Cambios a `.opencode/framework/**` y `.opencode/agents/**` | Confirmación explícita del usuario |
| MCP servers nuevos | control-agent (risk tier) + registro en `mcp-metadata.json` |
| Cambios de routing / fases | control-agent + registro en `SKILL-ROUTING.md` (versionado propio) |
