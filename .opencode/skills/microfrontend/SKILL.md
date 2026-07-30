---
name: microfrontend
description: 'Microfrontend setup with React Module Federation (@originjs/vite-plugin-federation
  for Vite, or @module-federation/nextjs-mf for Next.js): Host/Shell configuration,
  remote exposes, shared dependencies. Trigger: When setting up microfrontends,
  creating remote apps, or configuring shell exports.'
version: 3.1
metadata:
  phase:
  - construction
  layer:
  - frontend
  enforcement: recommended
  depends_on:
  - react
  - angular
  - typescript
  consumed_by:
  - agent-frontend
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: architecture-consistency
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Host uses `eager: true` for shared deps | ALWAYS | Immediate load |
| Remote uses `eager: false` for shared deps | ALWAYS | Deferred load |
| Remote exposes only one entry point per feature | ALWAYS | Single entry point |
| Use shared libraries to consume Host exports | ALWAYS | Abstraction layer |
| Match dependency versions Host ↔ Remote (`react`, `react-dom`, `react-router-dom` as `singleton`) | ALWAYS | Avoid two React copies / hook errors |

## Architecture
```
Host/Shell (Layout + Auth + State)
  Exposes: ./hooks, ./context, ./guards, ./utils
  Shared: react, react-dom, react-router-dom, UI library
  └── Remotes: Remote A (./routes), Remote B (./routes), Remote C (./routes)
```

## Host Exports Pattern

| Export | Functions |
|--------|-----------|
| `./hooks` | `useAuth`, `useNotifications`, `useApiClient` |
| `./context` | `AuthContext`, `ThemeContext` |
| `./guards` | `RequireAuth`, `RequireRole`, `RequireFeatureFlag` |
| `./utils` | `apiFetch`, `formatDate`, `formatCurrency` |

## Naming Conventions

| Field | Location | Convention | Example |
|-------|----------|------------|---------|
| `name` | `vite.config.ts` | English lowercase | `cases` |
| `name` (display) | registry | Display name | `Cases` |
| `path` | registry | English lowercase | `cases` |
| Package name | `package.json` | `remote-{module}` | `remote-cases` |

## Host vs Remote Configuration

| Aspect | Host | Remote |
|--------|------|--------|
| `eager` | `true` | `false` |
| `exposes` | hooks, context, guards, utils | Only feature routes |
| Port | Fixed (e.g., 5173) | Unique per remote |

## Shared Dependencies (Host eager:true)
```ts
shared: {
  react: { eager: true, singleton: true, requiredVersion: '^18.3.0' },
  'react-dom': { eager: true, singleton: true, requiredVersion: '^18.3.0' },
  'react-router-dom': { eager: true, singleton: true },
}
```

## Shared Dependencies (Remote eager:false)
```ts
shared: {
  react: { eager: false, singleton: true, requiredVersion: '^18.3.0' },
  'react-dom': { eager: false, singleton: true, requiredVersion: '^18.3.0' },
  'react-router-dom': { eager: false, singleton: true },
}
```

## Shared Dependencies (Remote eager:false) — Angular
```json
{
  "@angular/core": { "eager": false, "singleton": true },
  "@angular/router": { "eager": false, "singleton": true },
  "@angular/common": { "eager": false, "singleton": true }
}
```

## Bootstrap Remote (main.ts, Angular)
```typescript
// Remote main.ts should be minimal — no providers
// Auth, interceptors, theme come from Host
import { loadManifest } from '@angular-architects/module-federation';

loadManifest('/assets/mf.manifest.json')
  .catch(err => console.error(err))
  .then(_ => import('./bootstrap'))
  .catch(err => console.error(err));
```

## Bootstrap (bootstrap.ts, Angular)
```typescript
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

platformBrowserDynamic()
  .bootstrapModule(AppModule)
  .catch(err => console.error(err));
```

## Module Declaration File (remote-types.d.ts, Angular)
```typescript
declare module 'host/services' {
  export const DataService: any;
  export const NotificationService: any;
  export const AuthService: any;
}
declare module 'host/guards' { ... }
declare module 'host/interceptors' { ... }
```

## Checklist
- [ ] Host `eager: true` for all shared deps
- [ ] Remote `eager: false` for all shared deps
- [ ] Remote exposes only feature routes
- [ ] Shared modules created for all Host imports
- [ ] Remote module types declared (`remote-types.d.ts`)
- [ ] Port unique per remote
- [ ] `react`/`react-dom` marked `singleton` on both sides (avoid "Invalid hook call" from duplicate React copies)

## React Module Federation (Vite variant — default)

### 1. Setup con @originjs/vite-plugin-federation

El ecosistema Vite usa Rollup para producción, y Module Federation se integra mediante `@originjs/vite-plugin-federation`.

**Instalación:**

```bash
npm install -D @originjs/vite-plugin-federation
```

**Configuración del Host (vite.config.ts):**

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import federation from '@originjs/vite-plugin-federation';

export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'shell',
      remotes: {
        cases: 'http://localhost:4201/assets/remoteEntry.js',
        tasks: 'http://localhost:4202/assets/remoteEntry.js',
      },
      shared: {
        react: { eager: true, singleton: true, requiredVersion: '^18.3.0' },
        'react-dom': { eager: true, singleton: true, requiredVersion: '^18.3.0' },
        'react-router-dom': { eager: true, singleton: true },
      },
    }),
  ],
  build: { target: 'esnext', modulePreload: false, cssCodeSplit: false },
});
```

**Configuración del Remote (vite.config.ts):**

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import federation from '@originjs/vite-plugin-federation';

export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'cases',
      filename: 'remoteEntry.js',
      exposes: {
        './routes': './src/routes.tsx',
      },
      shared: {
        react: { eager: false, singleton: true, requiredVersion: '^18.3.0' },
        'react-dom': { eager: false, singleton: true, requiredVersion: '^18.3.0' },
        'react-router-dom': { eager: false, singleton: true },
      },
    }),
  ],
  build: { target: 'esnext', modulePreload: false, cssCodeSplit: false },
});
```

**Consideraciones específicas de Vite + Module Federation:**

| Aspecto | Detalle |
|---------|---------|
| Build target | `esnext` obligatorio — Module Federation en Vite requiere ESM nativo |
| Dev server | Cada remote corre en su propio puerto (`vite --port 4201`); el Host los consume por URL o manifest |
| HMR | HMR completo dentro de cada app; cambios cross-remote requieren rebuild del remote |
| SSR | Limitado — para SSR real, evaluar Next.js con `@module-federation/nextjs-mf` |
| Routing | Cada remote expone rutas de `react-router-dom` que el Host monta como rutas anidadas |

**Consumo del remote en el Host (lazy):**

```tsx
import { lazy, Suspense } from 'react';

const CasesRoutes = lazy(() => import('cases/routes'));

<Suspense fallback={<div>Loading Cases...</div>}>
  <CasesRoutes />
</Suspense>
```

**Module Declaration File (remote-types.d.ts):**

```typescript
declare module 'cases/routes' {
  import type { RouteObject } from 'react-router-dom';
  const routes: RouteObject[];
  export default routes;
}
declare module 'host/hooks' {
  export const useAuth: () => { user: unknown; isAuthenticated: boolean };
}
```

## Next.js variant (`@module-federation/nextjs-mf`)

Para proyectos que ya usan Next.js (SSR/SSG), Module Federation se configura vía `next.config.js` con `@module-federation/nextjs-mf`. La API de `remotes`/`exposes`/`shared` es equivalente conceptualmente a la de Vite, pero la integración con SSR añade complejidad (hidratación cruzada entre Host y Remote). Usar solo si el proyecto ya requiere Next.js por SEO/SSR — no adoptar Next.js únicamente para tener MFE.

---

## Angular Module Federation (@angular-architects/module-federation)

### 1. Angular Module Federation — setup con @angular-architects/module-federation

El ecosistema Angular usa Webpack internamente (via Angular CLI), por lo que Module Federation se integra mediante `@angular-architects/module-federation`, que abstrae la configuración de Webpack y proporciona schematics para generar la configuración automáticamente.

**Instalación:**

```bash
ng add @angular-architects/module-federation --project shell --port 4200
ng add @angular-architects/module-federation --project remote-cases --port 4201
```

**Configuración del Host (webpack.config.js):**

```javascript
const { share, withModuleFederationPlugin } = require('@angular-architects/module-federation/webpack');

module.exports = withModuleFederationPlugin({
  remotes: {
    cases: 'http://localhost:4201/remoteEntry.js',
    tasks: 'http://localhost:4202/remoteEntry.js',
  },

  shared: share({
    '@angular/core': { singleton: true, eager: true },
    '@angular/router': { singleton: true, eager: true },
    '@angular/common': { singleton: true, eager: true },
    '@angular/common/http': { singleton: true, eager: true },
  }),
});
```

**Configuración del Remote (webpack.config.js):**

```javascript
const { share, withModuleFederationPlugin } = require('@angular-architects/module-federation/webpack');

module.exports = withModuleFederationPlugin({
  name: 'cases',
  exposes: {
    './routes': './src/app/app.routes.ts',
  },

  shared: share({
    '@angular/core': { singleton: true, eager: false },
    '@angular/router': { singleton: true, eager: false },
    '@angular/common': { singleton: true, eager: false },
  }),
});
```

**Manifest de remotes (mf.manifest.json):**

```json
{
  "cases": "http://localhost:4201/remoteEntry.js",
  "tasks": "http://localhost:4202/remoteEntry.js"
}
```

**Consideraciones específicas de Angular CLI + Module Federation:**

| Aspecto | Detalle |
|---------|---------|
| Modo de build | Angular CLI maneja Webpack internamente; la configuración se extiende via `webpack.config.js` |
| Dev server | Los remotes se ejecutan en puertos separados (`ng serve --port 4201`); el Host los consume via manifest |
| HMR | HMR completo en el Host; los remotes tienen HMR limitado (rebuild en cada cambio) |
| SSR | Soportado con configuración adicional via `@angular-architects/module-federation` |
| Assets | Los assets estáticos del Remote se sirven desde su propio `ng serve` |
| Routing | Los remotes exponen rutas Angular que se integran en el router del Host |

**Patrón bootstrap para Angular:**

```typescript
// remote-cases/src/main.ts
import { loadManifest } from '@angular-architects/module-federation';

loadManifest('/assets/mf.manifest.json')
  .catch(err => console.error('Error loading manifest', err))
  .then(_ => import('./bootstrap'))
  .catch(err => console.error('Error loading bootstrap', err));

// remote-cases/src/bootstrap.ts
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

platformBrowserDynamic()
  .bootstrapModule(AppModule)
  .catch(err => console.error(err));
```

> Angular requiere la doble importación (main → bootstrap) para que Module Federation pueda resolver las dependencias compartidas antes de ejecutar el bootstrap del módulo.

**Configuración de rutas del Remote:**

```typescript
// remote-cases/src/app/app.routes.ts
import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./cases/cases.component').then(m => m.CasesComponent),
  },
  {
    path: ':id',
    loadComponent: () =>
      import('./cases-detail/cases-detail.component').then(m => m.CasesDetailComponent),
  },
];
```

**Carga de rutas remotas en el Host:**

```typescript
// shell/src/app/app.routes.ts
import { Routes } from '@angular/router';
import { loadRemoteModule } from '@angular-architects/module-federation';
import { ShellComponent } from './shell/shell.component';

export const routes: Routes = [
  {
    path: '',
    component: ShellComponent,
    children: [
      {
        path: 'cases',
        loadChildren: () =>
          loadRemoteModule({
            type: 'module',
            remoteEntry: 'http://localhost:4201/remoteEntry.js',
            exposedModule: './routes',
          }).then(m => m.routes),
      },
      {
        path: 'tasks',
        loadChildren: () =>
          loadRemoteModule({
            type: 'manifest',
            remoteName: 'tasks',
            exposedModule: './routes',
          }).then(m => m.routes),
      },
    ],
  },
];
```

**TypeScript configuration para Module Federation:**

```json
// tsconfig.json (Host)
{
  "compilerOptions": {
    "baseUrl": "src",
    "paths": {
      "host/*": ["./types/host/*"]
    }
  }
}

// tsconfig.json (Remote)
{
  "compilerOptions": {
    "baseUrl": "src",
    "paths": {
      "host/*": ["./types/host/*"]
    }
  }
}
```

### 2. Import Maps — carga de módulos nativa en el navegador

Los **Import Maps** son un estándar web que permite mapear identificadores de módulos a URLs, sin necesidad de bundler. Son una alternativa lightweight a Module Federation para casos simples.

**Definición en HTML:**

```html
<script type="importmap">
{
  "imports": {
    "react": "https://esm.sh/react@18.3.0",
    "react-dom": "https://esm.sh/react-dom@18.3.0",
    "cases-app": "http://localhost:4201/main.js"
  }
}
</script>
<script type="module">
  import CasesApp from 'cases-app';
  // ...
</script>
```

**Comparativa Import Maps vs Module Federation:**

| Característica | Import Maps | Module Federation |
|----------------|-------------|-------------------|
| Dependencias compartidas | Solo deduplicación por URL | Deduplicación + versión negociada |
| Shared state | No (cada módulo es independiente) | Sí (singleton, eager/lazy) |
| Fallback de versión | No (una sola URL por módulo) | Sí (requiredVersion, versión fallback) |
| SSR | No nativamente | Varía (Next.js sí, Vite limitado) |
| Complejidad | Baja | Media-Alta |
| Dinamismo | Estático (definido en HTML) | Dinámico (carga remotes en runtime) |
| Caso de uso ideal | Micro-frontends simples, pocos remotes | Micro-frontends complejos, muchos remotes |

**Cuándo usar Import Maps:**

- 2-3 micro-frontends con dependencias mínimas compartidas
- Equipos que no necesitan shared state (ej: solo comparten UI libs)
- Proyectos donde la simplicidad de deployment es prioritaria
- Integración progresiva: migrar de monolito a MFE sin overhead de build

---

### 3. Cuándo usar microfrontends vs SPA monolítica — marco de decisión

**Usa microfrontends cuando:**

| Criterio | Condición |
|----------|-----------|
| Equipos | 3+ equipos frontend independientes |
| Escalabilidad de deploy | Cada equipo necesita deployar de forma autónoma |
| Dominio funcional | Módulos del negocio claramente delimitados (casos, tareas, reportes) |
| Stack heterogéneo | Necesidad de mantener múltiples versiones de React coexistiendo |
| Velocidad de build | El monolito tarda >5 min en build completo |
| Autonomía organizacional | Cada equipo es dueño de su módulo end-to-end |

**Usa SPA monolítica cuando:**

| Criterio | Condición |
|----------|-----------|
| Equipos | 1-2 equipos frontend |
| Coherencia UX | La aplicación requiere transiciones fluidas entre módulos sin carga |
| Simplicidad | Prioridad por DX simple: un repo, un build, un deploy |
| Dependencias compartidas | Alta cantidad de estado compartido entre módulos |
| Latencia | La carga inicial debe ser mínima (sin fetch de remotes) |
| Fase inicial | MVP o producto en validación de mercado |

**Matriz de decisión rápida:**

```
¿3+ equipos frontend? ─── Sí ──→ Microfrontends
        │
        No
        │
¿Módulos independientes con deploy separado? ─── Sí ──→ Microfrontends
        │
        No
        │
¿Build >5 min con dolor de integración? ─── Sí ──→ Considerar MFE
        │
        No
        │
→ SPA monolítica con modularidad interna (feature folders)
```

**Antipatrones comunes:**

- Microfrontends para 1 solo equipo → overhead sin beneficio
- MFE sin contrato de shared deps → conflictos de versión en runtime ("Invalid hook call" por dos copias de React)
- MFE con estado compartido excesivo → acoplamiento que MFE debería eliminar
- Monolito sin modularización interna → candidatos futuros a MFE pero no todavía

---

### 4. Vite Module Federation vs Webpack directo — trade-offs

| Aspecto | Webpack Module Federation (directo) | Vite + @originjs/vite-plugin-federation |
|---------|------------------------------------|------------------------------------------|
| **Madurez** | Producción estable, usado por grandes empresas | Producción estable, adopción creciente |
| **Dev experience** | Configuración manual de Webpack | Configuración declarativa en `vite.config.ts` |
| **HMR** | HMR completo en Host y Remotes | HMR completo dentro de cada app |
| **SSR** | Soportado nativamente | Limitado — usar Next.js + `@module-federation/nextjs-mf` si se necesita |
| **Type safety** | Requiere `@module-federation/typescript` | Declaraciones manuales (`remote-types.d.ts`) |
| **Shared deps** | Negociación de versión avanzada con fallback | Negociación vía objeto `shared` del plugin |
| **Dynamic remotes** | Promesas para cargar remotes en runtime | `import()` dinámico + `React.lazy` |
| **Bundle size** | Mayor (Webpack runtime + MFE runtime) | Menor (build de Vite/Rollup + MFE runtime) |
| **Community** | Module Federation Initiative (webpack.org) | Comunidad Vite + `@originjs` |

**Recomendación por escenario:**

| Escenario | Recomendación |
|-----------|---------------|
| Proyecto React nuevo (SPA) | **Vite + vite-plugin-federation** — consistencia con el stack |
| Proyecto React existente (Vite) | **Vite + vite-plugin-federation** — no migrar a Webpack directo |
| SSR requerido | **Next.js + @module-federation/nextjs-mf** |
| Prototipo / MVP rápido | **Vite + vite-plugin-federation** — setup rápido |
| Migración gradual desde monolito React | **Vite + vite-plugin-federation** — no mezclar configuración |
| Multi-framework (React + otro) | **Webpack directo** — mayor flexibilidad cross-framework |

> **Regla**: Un proyecto React = Vite end-to-end (o Next.js end-to-end si necesita SSR). Si necesitas MFE cross-framework, evalúa Webpack directo pero mantén consistencia dentro de cada proyecto.
