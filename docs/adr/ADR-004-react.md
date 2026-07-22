# ADR-004 — Reemplazo de Angular por React como framework frontend

**Estado:** Aceptado
**Fecha:** 2026-07-21
**Autor:** Manuel Aliaga — TIVIT Foundry
**Supersede:** [ADR-001](ADR-001-angular.md)

## Contexto

TIVIT Foundry estandarizó Angular como frontend en ADR-001. La dirección del laboratorio pidió reemplazar Angular por React como stack frontend estándar del framework, manteniendo el mismo nivel de rigor: skills completas con patrones concretos (no solo "usa React"), scaffold generator actualizado, y gobierno consistente en toda la documentación.

## Decisión

Se elige **React** (con dos variantes aceptadas) como framework frontend estándar:

| Variante | Cuándo usar | Notas |
|----------|-------------|-------|
| **React + Vite (default)** | Apps internas de CRUD/admin, dashboards — el mismo perfil que cubría Angular | El scaffold generator (`.opencode/scaffold/`) emite esta variante por defecto |
| **Next.js (App Router)** | Páginas públicas que necesitan SSR/SSG/SEO | Documentada en la skill `react`; no se scaffoldea automáticamente |

## Reemplazos por pieza del stack

| Angular (ADR-001) | React (esta decisión) | Razón |
|---|---|---|
| Standalone components + signals | Componentes funcionales + hooks | Equivalente directo, sin NgModules que evitar |
| `inject(HttpClient)` + RxJS | `fetch` envuelto en `apiFetch()` + `@tanstack/react-query` | Mismo TanStack Query que ya se usaba vía `@ngneat/query`, ahora en su forma nativa |
| Signal-based Store | Zustand | API casi idéntica a un signal store (`create()`, selectors, actions) |
| Reactive Forms | `react-hook-form` + `zodResolver` | Reutiliza Zod, que el framework ya usa en el backend Bun |
| Angular Router (`loadComponent`) | `react-router-dom` + `React.lazy()`/`Suspense` | Mismo patrón de code-splitting por ruta |
| Angular CDK | Radix UI primitives / shadcn/ui | Primitivas headless equivalentes (overlay, dialog, etc.) |
| `@ngx-translate` | `react-i18next` | Estándar de facto en React |
| `@angular/pwa` | `vite-plugin-pwa` | Integra con Vite igual que `@angular/pwa` con Angular CLI |
| Jasmine/Karma/TestBed | Vitest + React Testing Library, MSW | Playwright E2E no cambia (ya era agnóstico de framework) |

## Consecuencias

- Las skills `angular` y `angular-services` fueron renombradas a `react` y `react-services` con contenido completamente reescrito.
- Se creó `react-upgrade` (reemplaza `angular-upgrade`).
- El scaffold generator (`.opencode/scaffold/`) genera componentes `.tsx` (React + Vite) en vez de pares `.component.ts`/`.html` (Angular).
- `check-scaffold-stack.py` fue invertido: ahora falla si reaparece contenido Angular (`@angular/*`, `@ngneat/query`, etc.) en vez de exigirlo.
- Todas las skills que mencionaban Angular como referencia de stack (testing, seguridad, CI/CD, performance, i18n, notificaciones, etc.) fueron actualizadas a sus equivalentes React.
- ADR-001 queda marcado como *Superseded* y se conserva solo como registro histórico.

## Alternativas consideradas

- **Mantener Angular:** descartado por decisión explícita de la dirección de TIVIT Foundry.
- **Vue:** no evaluado — el pedido fue específicamente React.
- **Next.js como default del scaffold:** descartado para el generador automático porque la mayoría de módulos generados son CRUD internos (SPA), no páginas públicas que necesiten SSR; Next.js queda documentado como variante aceptada, no como default.
