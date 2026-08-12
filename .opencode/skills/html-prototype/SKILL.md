---
name: html-prototype
description: 'Generates interactive HTML mockups that look like the final app using HTML + CSS + minimal JS. Trigger: After Requirements Analysis when stakeholder approval of screens is needed before API design.'
when_to_use:
  - After requirements analysis, before API design, when stakeholders need to approve screens
  - When validating UX flows before committing to implementation
  - When creating clickable prototypes for user testing
  - When the team needs visual alignment on layout, navigation, and interaction patterns
  - When exploring design alternatives before investing in full frontend code
version: 1.1
metadata:
  phase:
  - inception
  layer:
  - frontend
  enforcement: optional
  depends_on:
  - hu-template
  consumed_by:
  - api-first-spec
  - react
  - angular
  - design-system
  agent_roles:
  - design-agent
  validation_profile: documentation
  mcp_usage: none
---

# html-prototype

## Propósito

Generar mockups HTML interactivos que se ven como la aplicación final, usando HTML puro + CSS + JS mínimo, para validar pantallas con stakeholders antes de diseñar la API o escribir código de producción.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué pantallas necesita el módulo y cómo se relacionan entre sí?
2. ¿Cuál es el flujo de navegación y qué estados de la UI deben prototiparse?
3. ¿Cómo se representan los datos, errores y estados vacíos antes de tener un backend?
4. ¿Cómo se mapean los tokens del design system a CSS custom properties?
5. ¿Qué feedback de stakeholders se captura antes de pasar a implementación?

## Relación con otras skills

- `hu-template` aporta las historias de usuario que definen qué pantallas prototipar.
- `design-system` aporta los tokens de color, tipografía y spacing que el prototipo debe usar.
- `api-first-spec` consume el prototipo validado para diseñar los endpoints que sirven los datos mostrados.
- `react` / `angular` consume el prototipo como referencia visual para implementar los componentes reales (según el framework elegido por el proyecto).
- Esta skill no reemplaza a `design-system`; solo traduce tokens a CSS para el prototipo.

## Qué debe hacer el agente cuando esta skill está activa

1. Leer las historias de usuario de `hu-template` para identificar las pantallas necesarias.
2. Definir los tokens del design system como CSS custom properties en un archivo `tokens.css`.
3. Generar un archivo HTML por pantalla con navegación entre ellos.
4. Incluir `data-testid` en cada elemento interactivo para futuras pruebas E2E.
5. Implementar estados de la UI: loading, empty, error, success, disabled.
6. Usar navegación por hash (`#/recurso`, `#/recurso/nuevo`) sin framework JavaScript.
7. Copiar CSS y JS embebidos en cada HTML para máxima portabilidad (offline).
8. Documentar las decisiones de UI tomadas en el prototipo.

## Entradas esperadas

Esta skill asume que ya existe:
- Lista de historias de usuario (de `hu-template`);
- Definición de tokens del design system (de `design-system`);
- Acuerdo sobre el alcance del MVP;
- Contexto del proyecto (de `project-bootstrap`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- Archivos HTML por pantalla con CSS embebido;
- Sistema de tokens CSS (custom properties);
- Navegación SPA-like con hash routing;
- Componentes interactivos: acordeones, tabs, modales, formularios, tablas con paginación;
- Estados de UI: loading, empty, error, disabled;
- Prototipo responsive (mobile-first);
- Documento de decisiones de UI.

La fase no incluye todavía:
- Código React o Angular de producción;
- Conexión a APIs reales;
- Tests unitarios o E2E (eso es `playwright`);
- Tokens compilados para producción (eso es `design-system`).

## Principios que siempre debe respetar

- **Zero dependencias externas**: Todo CSS y JS va embebido. No se usa Bootstrap, Tailwind CDN ni ninguna librería externa.
- **CSS custom properties como tokens**: Colores, tipografía, spacing, bordes y sombras provienen de `tokens.css`.
- **Un archivo HTML por pantalla**: Cada pantalla es un archivo independiente que funciona sin servidor.
- **`data-testid` en todo elemento interactivo**: Cada botón, link, input, tab y modal tiene `data-testid` para `playwright`.
- **Mobile-first responsive**: Los estilos empiezan en mobile y se escalan con `@media (min-width: ...)`.
- **Labels en idioma del proyecto**: Los textos visibles van en el idioma del usuario. Los identificadores CSS y `data-testid` van en inglés.
- **Offline primero**: El prototipo debe abrirse desde el sistema de archivos sin servidor HTTP.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- Qué pantallas se prototipan y en qué orden;
- Cómo se estructura la navegación entre pantallas;
- Qué estados de la UI se muestran (loading, empty, error);
- Qué tokens CSS se definen y sus valores por defecto;
- La estructura de archivos del prototipo.

Esta skill delega:
- Los colores exactos y tipografía → `design-system`;
- Los datos y endpoints → `api-first-spec`;
- Los componentes React o Angular reales → `react` / `angular`;
- Los flujos E2E → `playwright`.

## Qué debe definir el diseño

### 1. Sistema de tokens CSS

Definir `tokens.css` con custom properties:

```css
:root {
  /* Color */
  --color-primary-600: #1d4ed8;
  --color-primary-500: #3b82f6;
  --color-primary-400: #60a5fa;
  --color-gray-900: #111827;
  --color-gray-500: #6b7280;
  --color-gray-100: #f3f4f6;
  --color-error-500: #ef4444;
  --color-success-500: #22c55e;
  --color-warning-500: #f59e0b;

  /* Typography */
  --font-family: 'Inter', system-ui, -apple-system, sans-serif;
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;

  /* Spacing */
  --spacing-1: 0.25rem;
  --spacing-2: 0.5rem;
  --spacing-3: 0.75rem;
  --spacing-4: 1rem;
  --spacing-6: 1.5rem;
  --spacing-8: 2rem;

  /* Border */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;

  /* Shadow */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);

  /* Transition */
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;
}
```

### 2. Estructura de archivos y navegación

```
docs/inception/prototypes/
├── index.html          # Dashboard o landing
├── list.html           # Listado con filtros y paginación
├── form.html           # Crear/Editar recurso
├── detail.html         # Vista de detalle
├── tokens.css          # Design tokens (shared)
└── prototype.js        # Interactividad mínima (shared)
```

Navegación SPA-like con hash:
- `#/` → Dashboard
- `#/recurso` → Listado
- `#/recurso/nuevo` → Formulario crear
- `#/recurso/123` → Detalle
- `#/recurso/123/editar` → Formulario editar

### 3. Componentes interactivos

Definir el comportamiento de cada componente sin framework:

| Componente | Elementos | Comportamiento |
|---|---|---|
| Navegación | `<nav>`, `<a data-navigate>` | Hash routing, active state |
| Tabs | `<div data-tab-group>`, `<button data-tab>` | Toggle panels, active state |
| Modal | `<div class="modal-overlay">`, `<button data-toggle>` | Show/hide, close on overlay click |
| Acordeón | `<details>`, `<summary>` | HTML nativo, no JS needed |
| Formulario | `<form>`, `<input>`, `<select>` | Validación HTML5 + `data-validate-error` |
| Tabla paginada | `<table>`, `<nav class="pagination">` | Paginación con datos estáticos |
| Loading | `<div class="skeleton">` | Skeleton screens CSS-only |
| Empty state | `<div class="empty-state">` | Ilustración + acción |
| Error state | `<div class="error-state">` | Mensaje + retry |
| Toast | `<div class="toast">` | Auto-dismiss con CSS animation |

### 4. Estados de la UI

Todo prototipo debe incluir estos estados por pantalla:

| Estado | Cuándo | Cómo se representa |
|---|---|---|
| Loading | Mientras cargan datos | Skeleton screens con animación CSS |
| Empty | Sin datos | Ilustración + texto + botón de acción |
| Error | Fallo de operación | Mensaje de error + botón de retry |
| Success | Operación completada | Toast/mensaje de confirmación |
| Disabled | Sin permisos o sin datos | Botones y campos en estado `disabled` |
| Validation | Datos inválidos | Mensajes de error inline junto a campos |

## Preguntas guía

### 1. Sobre las pantallas
- ¿Qué pantallas necesita el módulo para cubrir todas las historias de usuario?
- ¿Cuál es el flujo de navegación principal? ¿Y el flujo alternativo?
- ¿Qué estados de la UI son críticos para validar con stakeholders?

### 2. Sobre los tokens
- ¿Los tokens CSS coinciden con el design system del proyecto?
- ¿Hay tokens de color que no existen en el design system?
- ¿La tipografía y spacing son consistentes con la app en producción?

### 3. Sobre la interactividad
- ¿Los formularios muestran validación inline?
- ¿Las tablas muestran estados de paginación correctos?
- ¿Los modales se cierran con Escape y click en overlay?

## Salidas esperadas

### A. Archivos de prototipo
- `tokens.css` con custom properties de design system;
- Un archivo HTML por pantalla (`list.html`, `form.html`, `detail.html`, etc.);
- `prototype.js` con interactividad mínima (tabs, modales, navegación);
- `index.html` como punto de entrada.

### B. Documento de decisiones de UI
- Pantallas prototipadas y sus estados;
- Tokens usados y su mapeo al design system;
- Decisiones pendientes (colores,tipografía aprobados vs. por aprobarr);
- Lista de `data-testid` generados para cada pantalla.

### C. Feedback de stakeholders
- Screenshot de cada pantalla con comentarios;
- Lista de cambios solicitados;
- Pantallas aprobadas sin cambios.

### D. Consumidores de esta skill
- `api-first-spec` — usa las pantallas para definir los endpoints necesarios;
- `react` / `angular` — usa el prototipo como referencia visual para componentes;
- `playwright` — usa los `data-testid` como selectores E2E.

## Criterios de calidad

- Todo elemento interactivo tiene `data-testid` descriptivo;
- Todo archivo HTML funciona offline (sin servidor HTTP);
- Los tokens CSS coinciden con el design system documentado;
- Loading, empty, error y success states existen por cada pantalla con datos;
- La navegación por hash funciona sin errores en consola;
- El prototipo es responsive (mínimo mobile y desktop);
- No hay dependencias externas (CDN, frameworks);
- Los labels están en el idioma del proyecto;
- Los identificadores CSS y `data-testid` están en inglés.

## Comportamiento esperado del agente

Cuando un stakeholder pide cambiar un flujo completo, el agente debe actualizar el prototipo y documentar la decisión antes de pasar a implementación.

Cuando el design system no tiene un token necesario, el agente debe agregarlo como propuesta en `tokens.css` y marcarlo como pendiente de aprobación.

Cuando una pantalla tiene muchos estados posibles, el agente debe priorizar loading, empty y error antes de estados edge case.

Cuando se descubren pantallas no contempladas en las historias de usuario, el agente debe documentarlas y consultar antes de prototiparlas.

## Plantilla de respuesta recomendada

1. Resumen de pantallas prototipadas.
2. Estructura de archivos generada.
3. Tokens CSS definidos y mapeo al design system.
4. Estados de la UI implementados por pantalla.
5. Flujo de navegación entre pantallas.
6. Decisiones de UI tomadas.
7. Decisiones pendientes de aprobación.
8. Lista de `data-testid` por pantalla.

## Ejemplos de uso

### Ejemplo 1: Módulo CRUD de Incidentes

Consulta: "Necesito prototipar el módulo de incidentes para validación con el equipo de operaciones."

Respuesta esperada:
- `index.html` — Dashboard con KPIs de incidentes abiertos;
- `list.html` — Tabla de incidentes con filtros (estado, severidad, fecha), paginación, búsqueda;
- `form.html` — Formulario de crear incidente con validación inline (título, descripción, severidad, asignado);
- `detail.html` — Vista de detalle con timeline de comentarios, cambio de estado, botones de acción;
- `tokens.css` — Tokens del design system aplicados;
- `prototype.js` — Navegación, tabs entre secciones de detalle, modal de confirmación de cierre;
- Estados: loading skeleton en tabla, empty state "sin incidentes", error al cargar, validación inline en formulario.

### Ejemplo 2: Wizard de Onboarding Multi-paso

Consulta: "Prototipar el flujo de onboarding para nuevos usuarios con 4 pasos."

Respuesta esperada:
- `wizard.html` — Wizard de 4 pasos (datos personales → preferencias → integraciones → confirmación);
- `tokens.css` — Tokens con stepper visual;
- `prototype.js` — Navegación entre pasos, validación por paso, progreso;
- Step indicator con estados: completed, active, upcoming;
- Botón "Anterior" deshabilitado en paso 1, "Siguiente" validado por paso, "Finalizar" con modal de confirmación;
- Estados: error en paso con campos inválidos, success con toast al completar.

## Checklist final de la skill

- ¿Se definieron tokens CSS que mapean al design system?
- ¿Cada pantalla tiene su archivo HTML independiente?
- ¿Los estados loading, empty, error están implementados?
- ¿La navegación funciona sin servidor ni frameworks?
- ¿Todo elemento interactivo tiene `data-testid`?
- ¿El prototipo es responsive (mobile + desktop)?
- ¿Las decisiones de UI están documentadas?
- ¿Se identificaron decisiones pendientes de aprobación?

## Notas de edición

Esta skill fue expandida desde 72 líneas a contenido completo con sistema de tokens, componentes interactivos, estados de UI, y ejemplos concretos. Los principios de zero dependencias y offline-first se mantienen del contenido original. Se agregó conexión explícita con `design-system`, `api-first-spec`, `react`/`angular` y `playwright`.