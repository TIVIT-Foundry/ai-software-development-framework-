---
name: progress-artifact
description: 'Genera y mantiene el dashboard de progreso del proyecto (artifact HTML autocontenido):
  esquema de módulos de negocio con estado, fases del framework N0-N49, y panel "dónde quedó
  la IA". Sirve a tres audiencias: dev (dónde quedó el trabajo), la IA (guía para reanudar
  sesiones) y supervisores (vista visual entendible). Trigger: Al cerrar una fase o bundle,
  al reanudar una sesión tras interrupción, o cuando se pide un reporte de avance.'
version: 1.0
metadata:
  phase:
  - construction
  - operations
  layer:
  - process
  enforcement: recommended
  depends_on: []
  consumed_by: []
  agent_roles:
  - delivery-agent
  validation_profile: architecture-consistency
  mcp_usage: none
---

# progress-artifact

## Propósito

El proyecto necesita visibilidad de avance sin abrir 10 documentos. Esta skill genera un
**artifact HTML autocontenido** (`docs/artifacts/progress.html`) que se abre en cualquier
navegador y muestra, en una sola página:

1. **Módulos de negocio** (vista principal, para el supervisor): cada spec de
   `docs/api-first/*.md` como tarjeta con semáforo, % de tareas, endpoints, fecha,
   responsable y link a la spec.
2. **Fases del framework** (para dev/IA): tabla A-H (N0-N49) con estado por fase.
3. **¿Dónde quedó la IA?**: paso actual, último checkpoint y conteo de pasos completados.

## Cuándo usar esta skill

Activar cuando:
- Se cierra una fase o bundle (paso 7 Registro del protocolo) — regenerar el artifact.
- Se reanuda una sesión interrumpida — regenerar para ver dónde quedó todo.
- Un supervisor o stakeholder pide un reporte de avance visual.
- Se abre una sesión nueva para un proyecto en curso — leer el HTML (o el JSON de estado)
  antes de empezar a trabajar.

No activar cuando:
- Solo se necesita el estado crudo — leer directamente `.workflow/state.json`.
- El proyecto no usa specs por módulo ni `.workflow` — primero formalizar el flujo.

## Relación con otras skills

| Skill | Relación | Descripción |
|-------|----------|-------------|
| `api-first-spec` | Fuente | Las specs de `docs/api-first/*.md` definen los módulos |
| `tasks` | Fuente | `tasks.md` alimenta el % de tareas por módulo |
| `framework-scaffold-implementation` | Complementaria | Define `.workflow/state.json` que alimenta el estado |
| `html-prototype` | Complementaria | Patrones de HTML autocontenido (sin dependencias) |

## Qué debe hacer el agente

1. **Regenerar** al final de cada fase o bundle:
   ```
   python .opencode/scripts/generate-progress.py .
   ```
   (desde la raíz del proyecto; el script detecta el directorio automáticamente si se
   ejecuta dentro del proyecto).
2. **Actualizar el estado manual** cuando la heurística no alcance: editar
   `docs/artifacts/progress-state.json` con el estado real por módulo:
   ```json
   {
     "auth": { "status": "wip", "fecha": "2026-08-10", "responsable": "Nombre",
               "notas": "Falta frontend login" },
     "talent": { "status": "ok", "fecha": "2026-08-11", "responsable": "Nombre" }
   }
   ```
   Estados válidos: `ok` | `wip` | `blocked` | `pending`. Sin este archivo, el estado se
   deriva automáticamente (ver heurística abajo).
3. **Declarar módulos sin spec formal** (p. ej. auth sin `docs/api-first/auth.md`) con
   `_extra` en el mismo JSON:
   ```json
   {
     "_extra": [
       { "slug": "auth", "title": "Autenticación (Sprint 1)", "path": "docs/sprints.md" }
     ]
   }
   ```
4. **Verificar** que el HTML se genera sin errores y que los links a specs resuelven.
5. **Commitear** el HTML y el `progress-state.json` junto con el cierre de la fase
   (el artifact es parte del reporte, no un archivo temporal).

## Heurística automática de estado (multi-nivel)

El generador deriva el estado por módulo sin override, en este orden:

1. **Paso actual** (`state.json.current_step`) que mencione el módulo → `wip`
2. **Pasos fallidos** (`steps_failed`) que mencionen el módulo → `blocked`
3. **Pasos completados** (`steps_completed`) que mencionen el módulo → `ok`
4. Sin coincidencias → `pending`

El match normaliza texto (sin acentos/case) y compara el slug del módulo **y las
palabras del título** contra cada paso — así `SPRINT-1-auth-backend`,
`SPRINT-2-bundle-E-ventas-backend` o `SPRINT-3-talent-census` mapean a sus módulos
automáticamente (tokens genéricos de sprint como bundle/fix/tests se ignoran).

## Fuentes y derivación de estado

| Fuente | Qué aporta | Prioridad |
|--------|-----------|-----------|
| `docs/artifacts/progress-state.json` | Estado manual por módulo (override) + `_extra` (módulos sin spec) | 1 |
| `.workflow/state.json` | steps completados/fallidos/actual (heurística automática) | 2 |
| `tasks.md` | % de tareas por módulo (checkboxes) | 3 |
| `docs/api-first/*.md` | Lista de módulos y endpoints | 4 |

## Reglas

1. El HTML debe ser **autocontenido** (CSS inline, cero dependencias externas, sin JS) —
   se abre con doble clic en cualquier máquina.
2. Nunca inventar estados: si no hay fuente, la tarjeta queda `pending`.
3. El `progress-state.json` es la única forma de override manual; documentar siempre
   fecha y responsable cuando se usa.
4. Regenerar el artifact **antes** de declarar una fase completa (el reporte es parte
   del handoff del protocolo).

## Verificación

- [ ] El comando de generación corre sin errores
- [ ] Cada módulo de `docs/api-first/` tiene su tarjeta
- [ ] Los links "Ver spec" resuelven a la spec real
- [ ] El panel "¿Dónde quedó la IA?" muestra el checkpoint real
- [ ] El HTML se abre en navegador sin errores de consola (solo favicon 404 tolerable)
