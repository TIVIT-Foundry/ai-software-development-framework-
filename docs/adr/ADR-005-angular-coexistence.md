# ADR-005 — Restauración de Angular como frontend alternativo (coexistencia con React)

**Estado:** Aceptado
**Fecha:** 2026-07-30
**Autor:** Manuel Aliaga — TIVIT Foundry
**Relacionado:** [ADR-001](ADR-001-angular.md) (Angular original), [ADR-004](ADR-004-react.md) (reemplazo por React)

## Contexto

ADR-004 (2026-07-21) reemplazó Angular por React como stack frontend estándar del framework, reescribiendo ~40 skills, el scaffold generator y el validador `check-scaffold-stack.py` para bloquear cualquier residuo de Angular. Esa migración asumía "un solo frontend estándar" — el mismo modelo que el framework nunca aplicó al backend, donde Python/FastAPI y Bun/TypeScript coexisten como opciones válidas seleccionables vía `--backend python|bun` en el scaffold generator, sin que una reemplace a la otra.

La dirección del laboratorio pidió corregir esta asimetría: en vez de forzar React como único frontend, el framework debe ofrecer **React o Angular, elegido por el equipo del proyecto**, con el mismo nivel de soporte para ambos — igual que ya ocurre entre Python y Bun en el backend.

## Decisión

Se restaura **Angular** como stack frontend de primera clase, coexistiendo con React (que se mantiene como default cuando no se especifica lo contrario):

- Las skills `angular`, `angular-services` y `angular-upgrade` se recrean (recuperadas del historial previo a ADR-004, adaptadas al estado actual del framework) y coexisten con `react`, `react-services` y `react-upgrade`.
- Las skills transversales que ya usaban el patrón de secciones múltiples por stack (ej. `### 1. Python Backend`, `### 2. React Frontend`, `### 3. Bun TypeScript Backend` en `unit-testing`) ganan una sección paralela `### N. Angular Frontend` con contenido completo (no solo una mención) — mismo patrón replicado en `integration-testing`, `ci-cd`, `security`, `performance`, `playwright`, `i18n`, `notifications`, `real-time`, `feature-flags`, `accesibilidad`, `code-review`, `project-architecture`, `typescript`, `repo-structure`, `api-first-frontend`, `design-system`, `microfrontend`, `mobile-pwa`, y las skills con bloques de código sustanciales (`api-integration`, `authentication`, `authorization`, `export-excel`, `graphql`, `keycloak`).
- Las skills que solo mencionaban Angular en una tabla de stack o una línea de texto se actualizan para reflejar ambas opciones ("React o Angular, según elección del proyecto") sin duplicar contenido.
- El scaffold generator (`.opencode/scaffold/generate.py`) gana un flag `--frontend react|angular` (default `react`), independiente de `--backend`. Las plantillas Angular viven en `.opencode/scaffold/templates/angular/` (mismo mecanismo de aislamiento por filename/subdirectorio que ya separaba los templates Python de los Bun) para no colisionar con las plantillas React (`.tsx`).
- `check-scaffold-stack.py` deja de tratar Angular como residuo prohibido: ahora valida que **ambos** stacks estén completos y sean internamente consistentes (templates presentes, sin cross-contaminación de imports entre stacks), en vez de fallar si aparece cualquier patrón Angular.

## Reemplazos revertidos (parcialmente) de ADR-004

| ADR-004 (solo React) | Esta decisión (React o Angular) |
|---|---|
| `angular`/`angular-services` renombradas a `react`/`react-services` | Ambos pares de skills coexisten como directorios independientes |
| `react-upgrade` reemplaza `angular-upgrade` | Ambas skills de upgrade coexisten |
| Scaffold genera solo `.tsx` | Scaffold genera `.tsx` (React, default) o `.component.ts`/`.html` (Angular) según `--frontend` |
| `check-scaffold-stack.py` falla si aparece Angular | `check-scaffold-stack.py` falla si **falta** cualquiera de los dos stacks o si hay cross-contaminación |

## Consecuencias

- El catálogo de skills crece de 105 a 108 (se recuperan `angular`, `angular-services`, `angular-upgrade`).
- `enforcement` de las skills Angular se fija en `recommended` (no `mandatory`) — React sigue siendo el default cuando el proyecto no especifica frontend; Angular es una elección explícita.
- Cualquier skill con `depends_on`/`consumed_by` apuntando a `react`/`react-services` gana la entrada paralela `angular`/`angular-services` donde aplica.
- ADR-001 se marca como "Vigente en paralelo con ADR-004" en vez de "Superseded" — su contenido histórico no se reescribe.
- ADR-004 **no se modifica** — sigue siendo el registro histórico correcto de la decisión de 2026-07-21; esta ADR-005 documenta la decisión posterior que la matiza, no la reemplaza (React sigue siendo el stack recomendado por defecto del scaffold generator).
- Los desarrolladores que generan un módulo nuevo sin pasar `--frontend` siguen obteniendo React, preservando la mayoría del comportamiento post-ADR-004; el cambio es aditivo, no rompe proyectos ya scaffoldeados en React.

## Alternativas consideradas

- **Mantener solo React (statu quo de ADR-004):** descartado por pedido explícito de la dirección de TIVIT Foundry — hay proyectos y equipos internos que ya usan Angular y no van a migrar solo porque el framework cambió de opinión.
- **Volver a Angular como único default:** descartado — perdería el trabajo de ADR-004 y las apps ya scaffoldeadas en React sin necesidad; el objetivo es coexistencia, no un segundo reemplazo.
- **Angular como "modo legacy" de solo mención, sin templates ni scaffold:** descartado — el mismo estándar de calidad que exige el framework para el backend dual (Python/Bun, ambos con soporte completo) debe aplicar al frontend; una skill Angular sin scaffold funcional no sería utilizable en la práctica.
