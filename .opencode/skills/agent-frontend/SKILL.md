---
name: agent-frontend
description: 'Meta-skill: activates all frontend skills in sequence for frontend-only
  work. Trigger: When implementing a frontend feature end-to-end (types → services →
  components).'
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - frontend
  enforcement: recommended
  depends_on:
  - react
  - react-services
  - typescript
  consumed_by:
  - agent-fullstack
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: skill-contract
  mcp_usage: governed
---

## Purpose
This meta-skill activates all frontend skills in the correct sequence for frontend feature development.
Load each skill in order before generating artifacts.

## Frontend Workflow

| Step | Skill | Artifacts |
|------|-------|-----------|
| 1 | `typescript` | Types, interfaces, const patterns |
| 2 | `design-system` | Color tokens, spacing, component wrappers |
| 3 | `react` | Feature folder structure, pages, function components |
| 4 | `react-services` | Query hooks, mutation hooks (`@tanstack/react-query`) |
| 5 | `api-first-frontend` | Frontend code from spec |
| 6 | `microfrontend` | (if applicable) Module Federation setup |
| 7 | `export-excel` | (if applicable) Export button and service |
| 8 | `performance` | Caching strategy, placeholderData |

## Sequence Diagram
```
[Types] → [Feature Structure] → [Query Services] → [Mutation Services] →
[Logic Service] → [Components] → [Page] → [Export (optional)]
```

## How to Use
1. Activate this meta-skill
2. Load each referenced skill in workflow table order
3. Generate types first, then services, then components
4. Never generate UI before types/services are defined

## Quality Gates
After each group, verify:
- [ ] Types (Step 1): No `any`, flat interfaces, `T | null` for nullable fields
- [ ] Services (Steps 3-4): Query/mutation/logic services separated
- [ ] Components (Step 5): Component stylesheets used, no inline styles
- [ ] Performance (Step 8): staleTime set, placeholderData on paginated queries
- [ ] Accessibility: All interactive elements have aria labels, keyboard navigation works

## Fallback Patterns

| Situation | Action |
|-----------|--------|
| Backend API not ready | Mock response types in a separate `.mock.ts` file, never couple UI to unfinished API |
| Design system token missing | Use nearest existing token and file a design debt ticket — never use raw color values |
| Microfrontend not configured | Build as standalone feature, extract to microfrontend later — the feature folder structure supports both modes |

## Common Mistakes

- **Types from guesswork**: Never create TypeScript interfaces from assumptions. Always derive from OpenAPI spec or backend DTOs.
- **Services too broad**: Split query services from mutation services. A single service doing both violates single responsibility.
- **Missing loading/error states**: Every data-fetching component must handle loading, error, and empty states (via `@tanstack/react-query` status flags).
- **Export before feature complete**: Implement export (Excel/CSV) only after the main feature is reviewed. It's always optional.
- **Global styles over component stylesheets**: The framework standard is CSS Modules / Tailwind scoped to the component. Only deviate with documented justification.

## Quality Gates

Los siguientes gates deben verificarse antes de considerar la meta-skill completada:

| Gate | Título | Descripción |
|------|--------|-------------|
| 1 | TypeScript compila sin errores | Los tipos TypeScript compilan sin errores (npm run typecheck) |
| 2 | Services con tipos correctos | Los hooks de @tanstack/react-query devuelven los tipos correctos |
| 3 | Componentes sin errores de consola | Los componentes renderizan sin errores de consola |
| 4 | i18n completa en todos los idiomas | La internacionalización muestra claves en todos los idiomas configurados |
| 5 | Feature flags no rompen la UI | Los feature flags no rompen la UI cuando están desactivados |
| 6 | Upload integrado con backend | Los archivos de upload funcionan con el backend (integración E2E) |

## Flujo de ejecución detallado

Cada nivel se ejecuta de forma secuencial y obligatoria. Un nivel no comienza hasta que el anterior pasa su validation gate.

### Nivel 1: typescript

| Campo | Detalle |
|-------|---------|
| **Inputs** | OpenAPI spec del módulo, DTOs del backend, API endpoints documentados |
| **Outputs** | `types/<modulo>.types.ts`, `types/<modulo>.enums.ts`, `types/<modulo>.requests.ts`, `api/<modulo>.ts` con fetch client |
| **Validation gate** | `npm run typecheck` sin errores. `no-explicit-any` en lint. Interfaces planas (sin anidación > 2 niveles) |
| **Tiempo estimado** | 15-30 min por módulo estándar (5-10 endpoints) |
| **Pitfalls comunes** | Tipos adivinados sin consultar spec real; usar `any` como escape; interfaces no exportadas; no alinear nombres con backend; faltan tipos para `T \| null` en campos opcionales |

### Nivel 2: react-services

| Campo | Detalle |
|-------|---------|
| **Inputs** | Tipos del Nivel 1, endpoints de API, patrón `@tanstack/react-query` (`useQuery`/`useMutation`) |
| **Outputs** | `hooks/use-<entidad>-query.ts`, `hooks/use-<entidad>-mutation.ts`, `hooks/use-<entidad>.ts` (lógica), `hooks/use-<entidad>-infinite-query.ts` (si aplica) |
| **Validation gate** | Hooks separados por responsabilidad (query ≠ mutation). Tipos conectados correctamente. `staleTime` definido. Casos loading/error cubiertos vía flags de react-query |
| **Tiempo estimado** | 20-40 min por módulo |
| **Pitfalls comunes** | Hook único que mezcla query y mutation; omitir estado `isPending`; no tipar el retorno de `useMutation`; faltan `onError` handlers; no usar `queryKey` correctamente; mezclar estado local mal alcance en lugar de `useState`/`useMemo` |

### Nivel 3: react

| Campo | Detalle |
|-------|---------|
| **Inputs** | Hooks del Nivel 2, diseño UI (Figma o spec), estructura de routing |
| **Outputs** | `components/<Entidad>Table.tsx`, `components/<Entidad>Form.tsx` (`react-hook-form` + `zodResolver`), `pages/<Entidad>Page.tsx`, `pages/<Entidad>FormPage.tsx`, `index.ts` barrels |
| **Validation gate** | Renderizado sin errores de consola. Estados loading/error/empty visibles. CSS Modules/Tailwind, sin estilos inline. Layout responsivo |
| **Tiempo estimado** | 40-90 min por módulo (según complejidad de la UI) |
| **Pitfalls comunes** | No manejar estado vacío; componentes monolíticos > 300 líneas; mezclar lógica de negocio en el JSX; olvidar `key` estable en listas mapeadas; no memoizar callbacks pesados (`useCallback`/`useMemo`); reimplementar patrones con clases en lugar de hooks |

### Nivel 4: i18n

| Campo | Detalle |
|-------|---------|
| **Inputs** | Textos de la UI del Nivel 3, archivos de locale existentes, spec de idiomas soportados |
| **Outputs** | `locales/es/<modulo>.json`, `locales/en/<modulo>.json` (y demás idiomas), claves integradas en componentes vía hook `useTranslation()` (react-i18next) |
| **Validation gate** | Todas las claves existen en todos los idiomas configurados. Sin texto hardcodeado en la UI. Prueba visual con cambio de locale |
| **Tiempo estimado** | 15-25 min por módulo |
| **Pitfalls comunes** | Texto hardcodeado olvidado; claves faltantes en un idioma; no usar el componente `<Trans>` para HTML inline; traducciones literales que no respetan contexto; olvidar pluralización |

### Nivel 5: feature-flags

| Campo | Detalle |
|-------|---------|
| **Inputs** | Especificación de toggles, flags existentes, componentes del Nivel 3 |
| **Outputs** | `feature-flags/index.ts` con definición de flags, componente `<FeatureFlag name="xxx">` y hook `useFeatureFlag()` en componentes |
| **Validation gate** | UI no se rompe con flag desactivado. Flag kill switch funcional. Sin fugas de código de feature inactiva en producción |
| **Tiempo estimado** | 10-20 min por flag |
| **Pitfalls comunes** | Flags sin cleanup plan; anidar múltiples flags creando matrix de pruebas imposible; no probar estado "off"; flags en middleware sin test |

### Nivel 6: design-system

| Campo | Detalle |
|-------|---------|
| **Inputs** | Tokens existentes, spec visual del módulo, componentes del Nivel 3 |
| **Outputs** | Variables CSS (`:root`), wrappers de componentes base (`<Button>`, `<Input>`, `<Modal>` sobre Radix UI/shadcn), `theme.css` |
| **Validation gate** | Colores y espaciados consistentes con design tokens. Sin valores raw (ej. `#fff`) en componentes de negocio. Modo oscuro funcional si aplica |
| **Tiempo estimado** | 20-40 min (setup inicial) + 10 min por componente wrapper |
| **Pitfalls comunes** | Usar valores raw en lugar de tokens; no actualizar tokens cuando cambia diseño; componentes wrapper demasiado rígidos; omitir focus visible |

### Nivel 7: accesibilidad

| Campo | Detalle |
|-------|---------|
| **Inputs** | Componentes del Nivel 3, criterios WCAG 2.2 AA |
| **Outputs** | Atributos ARIA en componentes, `role` y `aria-label`, manejo de foco, etiquetas `<label>` en formularios, contraste de color verificado |
| **Validation gate** | `axe-core` sin violations. Navegación por teclado funcional (Tab, Enter, Escape). Contraste > 4.5:1 en texto normal. `aria-live` en regiones dinámicas |
| **Tiempo estimado** | 15-30 min por módulo (auditoría + fixes) |
| **Pitfalls comunes** | ARIA duplicado con HTML semántico nativo; focus trap mal implementado en modales; contraste solo verificado en modo claro; no anunciar cambios dinámicos |

### Nivel 8: file-upload

| Campo | Detalle |
|-------|---------|
| **Inputs** | Endpoints de upload del backend, spec de types aceptados, límites de tamaño |
| **Outputs** | `hooks/use-file-upload.ts`, `components/FileUploader.tsx`, `components/FilePreview.tsx` |
| **Validation gate** | Upload funciona con backend real. MIME validation client-side. Barra de progreso visible. Manejo de errores (archivo muy grande, tipo no soportado). Preview de imagen funcional |
| **Tiempo estimado** | 25-40 min |
| **Pitfalls comunes** | No validar tipo MIME antes de enviar; no mostrar progreso en uploads grandes; olvidar cleanup de object URLs (memory leak, vía `useEffect` cleanup); no manejar cancelación; no limitar tamaño en cliente |

### Nivel 9: export-excel

| Campo | Detalle |
|-------|---------|
| **Inputs** | Endpoint de exportación del backend, columnas del listado, formato esperado |
| **Outputs** | `hooks/use-export-excel.ts`, `components/ExportButton.tsx` con indicador de descarga |
| **Validation gate** | Archivo descargado con datos correctos. Formato .xlsx/.csv válido. Encoding correcto (UTF-8). Progreso/loader visible durante exportación |
| **Tiempo estimado** | 15-25 min |
| **Pitfalls comunes** | Export sin feedback visual; no descargar en background (bloquea UI); archivos corruptos por encoding incorrecto; no manejar errores del endpoint de exportación; export sin limitación de filas |

## Prompt templates por nivel

### typescript — Prompt para generar tipos

```
Eres un agente de tipos TypeScript. Genera los archivos de tipos para el módulo [nombre].
API endpoints: [lista de endpoints]
DTOs del backend: [DTOs]

Reglas:
1. Crea interfaces planas (max 2 niveles de anidación)
2. Usa T | null para campos opcionales
3. No uses any — crea tipos específicos
4. Exporta todo
5. Crea enums para campos con valores fijos
6. Genera api/<modulo>.ts con fetch client tipado

Archivos a crear:
- types/<modulo>.types.ts
- types/<modulo>.enums.ts (si aplica)
- api/<modulo>.ts
```

### react-services — Prompt para generar hooks

```
Eres un agente de @tanstack/react-query. Genera los hooks para el módulo [nombre].
Tipos disponibles: [referencia archivo]
Endpoints API: [lista]

Reglas:
1. Separa hooks de query de hooks de mutation
2. Define queryKey como constante
3. Tipa estrictamente el retorno de useMutation
4. Incluye onError handler
5. staleTime mínimo de 30s
6. Crea hook de lógica separado si hay más de 3 pasos
7. Usa useState/useMemo/useCallback para estado local y useEffect solo para side effects
8. Usa useQuery/useMutation de @tanstack/react-query

Archivos a crear:
- hooks/use-<entidad>-query.ts
- hooks/use-<entidad>-mutation.ts
```

### react — Prompt para generar componentes

```
Eres un agente de React. Genera function components y páginas para [módulo].
Hooks disponibles: [lista]
Diseño UI: [descripción]

Reglas:
1. CSS Modules/Tailwind — nunca inline styles
2. Maneja loading / error / empty states (vía flags de react-query)
3. Componentes < 300 líneas
4. Function components con props tipadas estrictamente (interfaces)
5. Usa los hooks generados en nivel anterior
6. Formularios con react-hook-form + zodResolver
7. Barrels (index.ts) para exportar
8. Usa una `key` estable en listas mapeadas con `.map()`

Archivos a crear:
- components/<Entidad>List.tsx
- components/<Entidad>Form.tsx
- pages/<Entidad>Page.tsx
```

### i18n — Prompt para internacionalizar

```
Eres un agente de i18n. Internacionaliza el módulo [nombre].
Idiomas: es, en [y otros]
Componentes a traducir: [lista]

Reglas:
1. Extrae todo texto visible a claves i18n
2. Sin texto hardcodeado en plantillas
3. Todas las claves en todos los idiomas
4. Usa el hook useTranslation() para texto simple, el componente <Trans> para HTML
5. Agrupa claves por componente

Archivos:
- public/locales/es/<modulo>.json
- public/locales/en/<modulo>.json
```

### feature-flags — Prompt para implementar flags

```
Eres un agente de feature flags. Implementa flags para [módulo].
Flags necesarios: [lista]
Tipo de flag: boolean / multivariate

Reglas:
1. Define flag en feature-flags/index.ts
2. Crea componente <FeatureFlag name="xxx"> si es visible
3. Crea hook useFeatureFlag() si afecta lógica
4. Estado off debe ser seguro (no rompe UI)
5. Documenta cleanup date
```

### design-system — Prompt para wrappers

```
Eres un agente de design system. Crea/extiende componentes base para [necesidad].
Tokens existentes: [referencia]

Reglas:
1. Usa var(--token-xxx) — nunca valores raw
2. Soporta modo oscuro con media query o clase
3. Wrapper debe ser flexible (className prop, props tipadas, children) — usa forwardRef cuando el componente exponga un DOM ref
4. Documenta variantes disponibles
```

### accesibilidad — Prompt para auditar y corregir

```
Eres un agente de accesibilidad WCAG 2.2 AA. Audita y corrige [componente/módulo].

Checklist:
1. Roles ARIA correctos (no duplicar HTML semántico)
2. aria-label en elementos sin texto visible
3. Navegación por Tab orden lógico
4. Focus visible en todos los interactive
5. aria-live en regiones dinámicas
6. Contraste > 4.5:1 (texto normal), > 3:1 (grande)
7. Formularios con <label> asociado

Corrige cada violación encontrada.
```

### file-upload — Prompt para componente de upload

```
Eres un agente de file upload. Implementa upload para [módulo].
Endpoint: POST /api/[ruta]
Tipos aceptados: [lista MIME]
Tamaño máximo: [límite]

Reglas:
1. Validación client-side de tipo y tamaño
2. Barra de progreso
3. Preview de imagen inmediata (createObjectURL)
4. Cleanup de object URLs en el cleanup function de useEffect
5. Manejo de errores (tipo, tamaño, red)
6. Cancelación de upload en progreso
```

### export-excel — Prompt para exportación

```
Eres un agente de exportación Excel. Implementa export para [módulo].
Endpoint: GET /api/[ruta]/export
Columnas: [lista]

Reglas:
1. Descarga en background (no bloquea UI)
2. Loader/indicador de progreso
3. Manejo de errores (timeout, fallo de red)
4. Nombre de archivo descriptivo
5. Encoding UTF-8 para caracteres especiales
```

## Integración con meta-skill fullstack

### Handoff agent-backend ↔ agent-frontend

El flujo completo entre `agent-backend` y `agent-frontend` sigue esta secuencia:

```
agent-backend (Niveles 16-31) → OpenAPI spec → agent-frontend (Niveles 32-37)
```

**Handoff explícito**: `agent-backend` entrega un artefacto `api-spec/<modulo>-openapi.json` que contiene:
- Endpoints con request/response completos
- DTOs tipados
- Códigos de error
- Ejemplos de respuesta

`agent-frontend` consume ese spec como **única fuente de verdad** para generar tipos. No se genera frontend sin este spec aprobado.

### Supuestos del frontend sobre el backend

El frontend asume que el backend ya:
1. Implementó todos los endpoints según el spec
2. Devuelve `ApiResponse<T>` con estructura `{ data, success, message, errors }`
3. Maneja paginación con `{ items, total, page, pageSize, totalPages }`
4. Expone OpenAPI spec actualizado
5. Los códigos de error HTTP siguen el catálogo acordado (400, 401, 403, 404, 422, 500)

Si el backend no está listo, el frontend **no espera** — usa mocking.

### Testing frontend con backend mockeado

Estrategias ordenadas por preferencia:

| Estrategia | Cuándo usarla | Implementación |
|------------|---------------|----------------|
| **MSW (Mock Service Worker)** | Por defecto — equipos con experiencia en MSW | Intercepta fetch a nivel de service worker. Los tests y dev corren contra un server mock que replica las respuestas del spec |
| **json-server** | Prototipado rápido / MVP | Crea `db.json` con datos de ejemplo basados en el spec. Levanta API REST falsa en < 1 min |
| **Storybook mocks** | Desarrollo de componentes aislados | Cada story define su propio mock de datos. Útil para visualizar estados sin depender de red |
| **api-mocks.ts** | Equipos pequeños, sin infraestructura extra | Archivo con respuestas mock exportadas. Se intercambia el fetch client en desarrollo |

### Patrón de fixtures compartidos

```
shared-mocks/
  fixtures/
    <modulo>.fixtures.ts    # datos de ejemplo basados en el spec
    <modulo>.handlers.ts    # handlers MSW
  server.ts                 # servidor MSW centralizado
  browser.ts                # worker browser MSW
```

### Flujo de trabajo con mock

1. `agent-frontend` recibe el spec
2. Genera tipos desde el spec
3. Crea fixtures de prueba desde ejemplos del spec
4. Configura MSW/json-server con esos fixtures
5. Desarrolla services y componentes contra mock
6. Cambia a backend real cuando esté disponible (un solo import swap)

### Verificación final contra backend real

Cuando el backend esté deployado:

```
npm run test:integration  # corre contra backend real
```

Cada suite valida que:
- Las respuestas reales coinciden con las interfaces TypeScript
- Los códigos de error reales coinciden con los manejados
- La paginación real funciona con los services existentes
- Los uploads reales completan el flujo end-to-end
