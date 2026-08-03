---
name: acceptance-test-automation
description: 'Executes confirmed acceptance criteria (from hu-template, uat-acceptance, or requirements-intake) against the real implementation and produces structured pass/fail/ambiguous evidence per criterion — for both standard web/API flows and non-UI domain fixtures (audio, documents, images). Trigger: Before opening a PR for a feature with confirmed acceptance criteria, or when asked to verify behavior against acceptance criteria automatically.'
version: 1.0
metadata:
  phase:
  - quality
  layer:
  - testing
  enforcement: recommended
  depends_on:
  - hu-template
  - uat-acceptance
  - converge
  consumed_by:
  - framework-qa-validation
  - pull-request
  agent_roles:
  - control-agent
  - delivery-agent
  validation_profile: skill-contract
mcp_usage: none
---

## Propósito

Cerrar el hueco entre "los criterios de aceptación están confirmados" y "alguien verificó manualmente, uno por uno, que el código los cumple". `converge` ya compara spec contra código (drift estructural); esta skill ejecuta los criterios de aceptación **comportamentales** (la tabla "Datos de Prueba" de `hu-template`, los AC-N de `uat-acceptance`, o la sección 7 del Documento Cero de `requirements-intake`) contra la implementación real, y produce evidencia estructurada por criterio — pass, fail, o ambiguo — antes de abrir el PR.

`converge/SKILL.md` ya documenta esto como pendiente ("a deterministic version is a natural next step... not something this skill claims to do today"). Esta skill es esa pieza, acotada a lo que se puede automatizar hoy con las herramientas del framework.

## Cuándo usar esta skill

Activar cuando:
- Un feature con criterios de aceptación confirmados está listo para PR.
- Se necesita evidencia objetiva de que la implementación cumple lo acordado con el cliente, no solo que "se ve bien".
- La funcionalidad involucra procesar datos de entrada variables (audio, documentos, imágenes) donde el criterio de éxito es "clasificar/detectar correctamente", no solo "la pantalla se ve así".

**No activar** cuando no hay criterios de aceptación confirmados todavía (correr `hu-template` o `uat-acceptance` primero), o para bugfixes triviales sin AC asociado.

## Dos modos de ejecución

Esta skill no reimplementa runners de test — orquesta y agrega. La mecánica de ejecución se delega a las skills que ya la tienen.

### Modo 1: Flujos web/API estándar

| Paso | Detalle |
|------|---------|
| Input | Fila de AC (`uat-acceptance`) o fila de "Datos de Prueba" (`hu-template`): escenario, input, output esperado |
| Ejecución | Se delega a `playwright` (E2E), `unit-testing` o `integration-testing` según el tipo de criterio |
| Evidencia en fallo | Screenshot (Playwright) o payload de respuesta capturado (integration) |

### Modo 2: Fixtures de dominio no-UI

Para funcionalidades donde el criterio de éxito no es una pantalla sino un resultado sobre datos variables (ej. "detectar si el audio confirma la compra", visto en la reunión) — no cubierto por `playwright`/`agent-qa`, que asumen web/API.

```
tests/fixtures/{feature}/
├── inputs/           # audio-01.wav, doc-02.pdf, ...
├── expected/         # audio-01.expected.json, doc-02.expected.json
└── run.{py,ts}        # itera inputs/, corre la función real, compara vs expected/
```

| Regla | Rationale |
|-------|-----------|
| Cada fixture tiene un input real y un expected explícito, no un umbral genérico | Reproducibilidad — el mismo fixture debe dar el mismo resultado siempre |
| Un resultado que no calza pero tampoco contradice el expected se marca "ambiguo", no "fail" | Reusa la regla de `requirements-intake`: un vacío/duda nunca se resuelve en silencio |
| La carpeta de fixtures crece con cada caso real que falló en producción | Convierte cada bug encontrado en regresión permanente, igual que un test unitario |

## Formato de evidencia

Mismo patrón que `react-doctor`/`angular-doctor`/`requirements-intake`: salida por consola para feedback rápido, y un archivo estructurado para trazabilidad.

```json
{
  "feature": "carestino-audio-confirmation",
  "run_at": "2026-08-10T14:00:00Z",
  "criteria": [
    { "id": "AC-01", "source": "uat-acceptance", "status": "pass", "evidence": "tests/fixtures/carestino-audio/inputs/audio-01.wav" },
    { "id": "AC-02", "source": "hu-template#datos-de-prueba", "status": "fail", "evidence": "tests/fixtures/carestino-audio/inputs/audio-07.wav", "detail": "Esperado: confirmado. Obtenido: ambiguo (confianza 0.42)" },
    { "id": "AC-03", "source": "requirements-intake#7", "status": "ambiguous", "evidence": "tests/fixtures/carestino-audio/inputs/audio-12.wav", "detail": "Ruido de fondo impide clasificar con confianza suficiente" }
  ],
  "summary": { "pass": 1, "fail": 1, "ambiguous": 1, "total": 3 }
}
```

| Estado | Significado | Acción |
|--------|-------------|--------|
| `pass` | El resultado real coincide con el esperado | Ninguna |
| `fail` | El resultado real contradice el esperado | Bloqueante — no abrir PR sin resolver o documentar excepción |
| `ambiguous` | No se puede determinar con confianza (aplica sobre todo a Modo 2) | Revisar manualmente; no se resuelve por defecto como pass ni fail |

## Fuera de alcance (explícito)

**Integración con un tracker externo (Jira u otro) para archivar hallazgos automáticamente NO está construida.** En la reunión de gerencia del 2026-07-31 quedó explícito que el licenciamiento de Jira todavía estaba en evaluación. Esta skill produce el JSON/reporte de evidencia; conectarlo a un tracker es una extensión futura opcional cuando se decida la herramienta — no se asume ninguna integración hoy, y no hay ningún MCP de tracking registrado en `mcp-metadata.json`.

## Relación con otras skills

| Skill | Relación | Descripción |
|-------|----------|--------------|
| `hu-template` / `uat-acceptance` / `requirements-intake` | Input | Fuente de los criterios de aceptación a ejecutar |
| `playwright` / `unit-testing` / `integration-testing` | Ejecutor | Mecánica real de correr cada test (Modo 1) |
| `converge` | Complementario | `converge` verifica spec-vs-código (estructural); esta skill verifica criterio-vs-comportamiento (funcional) — ambos alimentan el mismo go/no-go |
| `framework-qa-validation` | Consumidor | Usa el reporte de evidencia como insumo objetivo para el go/no-go |
| `pull-request` | Consumidor | Debe correr antes de abrir el PR, no después |

## Verification checklist

- [ ] Todo criterio de aceptación confirmado tiene una fila en el reporte de evidencia (ninguno queda sin ejecutar)
- [ ] Cero `fail` sin excepción documentada antes de abrir el PR
- [ ] Todo `ambiguous` fue revisado manualmente, no se asumió como pass
- [ ] Para Modo 2, la carpeta de fixtures se actualiza cuando se descubre un caso real que falló en producción
- [ ] El reporte de evidencia queda referenciado en el resumen del PR (skill `pull-request`)
