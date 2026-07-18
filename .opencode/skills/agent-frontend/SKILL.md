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
  - angular
  - angular-services
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
| 3 | `angular` | Feature folder structure, pages, standalone components |
| 4 | `angular-services` | Query services, mutation services (signals + @ngneat/query) |
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
- **Missing loading/error states**: Every data-fetching component must handle loading, error, and empty states (via signals/computed).
- **Export before feature complete**: Implement export (Excel/CSV) only after the main feature is reviewed. It's always optional.
- **Global styles over component stylesheets**: The framework standard is Angular component stylesheets. Only deviate with documented justification.

## Quality Gates

Los siguientes gates deben verificarse antes de considerar la meta-skill completada:

| Gate | Título | Descripción |
|------|--------|-------------|
| 1 | TypeScript compila sin errores | Los tipos TypeScript compilan sin errores (npm run typecheck) |
| 2 | Services con tipos correctos | Los services de @ngneat/query devuelven los tipos correctos |
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

### Nivel 2: angular-services

| Campo | Detalle |
|-------|---------|
| **Inputs** | Tipos del Nivel 1, endpoints de API, patrón @ngneat/query (injectQuery/injectMutation) + signals |
| **Outputs** | `services/<entidad>-query.service.ts`, `services/<entidad>-mutation.service.ts`, `services/<entidad>.service.ts` (lógica), `services/<entidad>-infinite-query.service.ts` (si aplica) |
| **Validation gate** | Services separados por responsabilidad (query ≠ mutation). Tipos conectados correctamente. `staleTime` definido. Casos loading/error cubiertos vía signals/computed |
| **Tiempo estimado** | 20-40 min por módulo |
| **Pitfalls comunes** | Service único que mezcla query y mutation; omitir estado `isPending`; no tipar el retorno de `injectMutation`; faltan `onError` handlers; no usar `queryKey` correctamente; mezclar `useState`/`useEffect` en lugar de `signal()`/`effect()` |

### Nivel 3: angular

| Campo | Detalle |
|-------|---------|
| **Inputs** | Services del Nivel 2, diseño UI (Figma o spec), estructura de routing |
| **Outputs** | `components/<entidad>-table.component.ts` + `.component.html`, `components/<entidad>-form.component.ts` (Reactive Forms: FormBuilder/FormGroup), `pages/<entidad>-page.component.ts`, `pages/<entidad>-form-page.component.ts`, `index.ts` barrels |
| **Validation gate** | Renderizado sin errores de consola. Estados loading/error/empty visibles. Component stylesheets, sin estilos inline. Layout responsivo |
| **Tiempo estimado** | 40-90 min por módulo (según complejidad de la UI) |
| **Pitfalls comunes** | No manejar estado vacío; componentes monolíticos > 300 líneas; mezclar lógica de negocio en la plantilla; olvidar `trackBy` en `*ngFor`; no usar standalone components; usar `forwardRef` en lugar de patrones Angular (DI, @ViewChild, ContentProjection) |

### Nivel 4: i18n

| Campo | Detalle |
|-------|---------|
| **Inputs** | Textos de la UI del Nivel 3, archivos de locale existentes, spec de idiomas soportados |
| **Outputs** | `locales/es/<modulo>.json`, `locales/en/<modulo>.json` (y demás idiomas), claves integradas en componentes vía `translate` pipe/directive |
| **Validation gate** | Todas las claves existen en todos los idiomas configurados. Sin texto hardcodeado en la UI. Prueba visual con cambio de locale |
| **Tiempo estimado** | 15-25 min por módulo |
| **Pitfalls comunes** | Texto hardcodeado olvidado; claves faltantes en un idioma; no usar `TranslateModule` para HTML inline; traducciones literales que no respetan contexto; olvidar pluralización |

### Nivel 5: feature-flags

| Campo | Detalle |
|-------|---------|
| **Inputs** | Especificación de toggles, flags existentes, componentes del Nivel 3 |
| **Outputs** | `feature-flags/index.ts` con definición de flags, directivas `<appFeatureFlag>` y signals `featureFlag()` en componentes |
| **Validation gate** | UI no se rompe con flag desactivado. Flag kill switch funcional. Sin fugas de código de feature inactiva en producción |
| **Tiempo estimado** | 10-20 min por flag |
| **Pitfalls comunes** | Flags sin cleanup plan; anidar múltiples flags creando matrix de pruebas imposible; no probar estado "off"; flags en middleware sin test |

### Nivel 6: design-system

| Campo | Detalle |
|-------|---------|
| **Inputs** | Tokens existentes, spec visual del módulo, componentes del Nivel 3 |
| **Outputs** | Variables CSS (`:root`), wrappers de componentes base (`<appButton>`, `<appInput>`, `<appModal>`), `theme.css` |
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
| **Outputs** | `services/file-upload.service.ts`, `components/file-uploader.component.ts` + `.component.html`, `components/file-preview.component.ts` |
| **Validation gate** | Upload funciona con backend real. MIME validation client-side. Barra de progreso visible. Manejo de errores (archivo muy grande, tipo no soportado). Preview de imagen funcional |
| **Tiempo estimado** | 25-40 min |
| **Pitfalls comunes** | No validar tipo MIME antes de enviar; no mostrar progreso en uploads grandes; olvidar cleanup de object URLs (memory leak); no manejar cancelación; no limitar tamaño en cliente |

### Nivel 9: export-excel

| Campo | Detalle |
|-------|---------|
| **Inputs** | Endpoint de exportación del backend, columnas del listado, formato esperado |
| **Outputs** | `services/export-excel.service.ts`, `components/export-button.component.ts` + `.component.html` con indicador de descarga |
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

### angular-services — Prompt para generar services

```
Eres un agente de @ngneat/query + signals. Genera los services para el módulo [nombre].
Tipos disponibles: [referencia archivo]
Endpoints API: [lista]

Reglas:
1. Separa query services de mutation services
2. Define queryKey como constante
3. Tipa estrictamente el retorno de injectMutation
4. Incluye onError handler
5. staleTime mínimo de 30s
6. Crea service de lógica separado si hay más de 3 pasos
7. Usa signal() para estado local y effect() para side effects (no useState/useEffect)
8. Usa injectQuery/injectMutation de @ngneat/query (no useQuery/useMutation)

Archivos a crear:
- services/<entidad>-query.service.ts
- services/<entidad>-mutation.service.ts
```

### angular — Prompt para generar componentes

```
Eres un agente de Angular. Genera componentes y páginas standalone para [módulo].
Services disponibles: [lista]
Diseño UI: [descripción]

Reglas:
1. Component stylesheets — nunca inline styles
2. Maneja loading / error / empty states (vía signals/computed)
3. Componentes < 300 líneas
4. Standalone components con inputs/signals tipados estrictamente
5. Usa los services generados en nivel anterior
6. Formularios con Reactive Forms (FormBuilder, FormGroup) — no react-hook-form
7. Barrels (index.ts) para exportar
8. Usa trackBy en *ngFor

Archivos a crear:
- components/<entidad>-list.component.ts + .component.html
- components/<entidad>-form.component.ts + .component.html
- pages/<entidad>-page.component.ts + .component.html
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
4. Usa translate pipe para texto simple, TranslateModule para HTML
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
2. Crea directiva <appFeatureFlag name="xxx"> si es visible
3. Crea signal featureFlag() si afecta lógica
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
3. Wrapper debe ser flexible (class, @Input(), ContentProjection) — usa patrones Angular, no forwardRef
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
4. Cleanup de object URLs en ngOnDestroy / destroyRef
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
