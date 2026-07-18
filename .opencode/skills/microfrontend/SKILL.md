---
name: microfrontend
description: 'Microfrontend setup with Angular Module Federation (@angular-architects/module-federation):
  Host/Shell configuration, remote exposes, shared dependencies. Trigger: When
  setting up microfrontends, creating remote apps, or configuring shell exports.'
version: 2.0
metadata:
  phase:
  - construction
  layer:
  - frontend
  enforcement: recommended
  depends_on:
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
| Match dependency versions Host ↔ Remote | ALWAYS | Avoid conflicts |

## Architecture
```
Host/Shell (Layout + Auth + State)
  Exposes: ./services, ./pipes, ./guards, ./interceptors, ./utils
  Shared: @angular/core, @angular/router, @angular/common, UI library
  └── Remotes: Remote A (./routes), Remote B (./routes), Remote C (./routes)
```

## Host Exports Pattern

| Export | Functions |
|--------|-----------|
| `./services` | `DataService`, `NotificationService`, `AuthService` |
| `./pipes` | `DateFormatPipe`, `CurrencyFormatPipe`, `TruncatePipe` |
| `./guards` | `AuthGuard`, `RoleGuard`, `FeatureGuard` |
| `./interceptors` | `AuthInterceptor`, `ErrorInterceptor`, `LoadingInterceptor` |
| `./utils` | `ApiHelper`, `FormHelper`, `DateHelper` |

## Naming Conventions

| Field | Location | Convention | Example |
|-------|----------|------------|---------|
| `name` | `webpack.config.js` | English lowercase | `cases` |
| `name` (display) | registry | Display name | `Cases` |
| `path` | registry | English lowercase | `cases` |
| Package name | `package.json` | `remote-{module}` | `remote-cases` |

## Host vs Remote Configuration

| Aspect | Host | Remote |
|--------|------|--------|
| `eager` | `true` | `false` |
| `exposes` | services, guards, interceptors, etc. | Only feature routes |
| HTML plugin | enabled | disabled (`false`) |
| Port | Fixed (e.g., 4200) | Unique per remote |

## Shared Dependencies (Host eager:true)
```json
{
  "@angular/core": { "eager": true, "singleton": true },
  "@angular/router": { "eager": true, "singleton": true },
  "@angular/common": { "eager": true, "singleton": true },
  "@angular/common/http": { "eager": true, "singleton": true }
}
```

## Shared Dependencies (Remote eager:false)
```json
{
  "@angular/core": { "eager": false, "singleton": true },
  "@angular/router": { "eager": false, "singleton": true },
  "@angular/common": { "eager": false, "singleton": true }
}
```

## Bootstrap Remote (main.ts) — Angular
```typescript
// Remote main.ts should be minimal — no providers
// Auth, interceptors, theme come from Host
import { loadManifest } from '@angular-architects/module-federation';

loadManifest('/assets/mf.manifest.json')
  .catch(err => console.error(err))
  .then(_ => import('./bootstrap'))
  .catch(err => console.error(err));
```

## Bootstrap (bootstrap.ts)
```typescript
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

platformBrowserDynamic()
  .bootstrapModule(AppModule)
  .catch(err => console.error(err));
```

## Module Declaration File (remote-types.d.ts)
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
- [ ] Host eager: true for all shared deps
- [ ] Remote eager: false for all shared deps
- [ ] Remote exposes only feature routes
- [ ] Shared libraries created for all Host imports
- [ ] Module declarations in remote-types.d.ts
- [ ] No providers in remote main.ts (inherited from Host)
- [ ] Port unique per remote

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

---

### 2. Import Maps — carga de módulos nativa en el navegador

Los **Import Maps** son un estándar web que permite mapear identificadores de módulos a URLs, sin necesidad de bundler. Son una alternativa lightweight a Module Federation para casos simples.

**Definición en HTML:**

```html
<script type="importmap">
{
  "imports": {
    "@angular/core": "https://cdn.jsdelivr.net/npm/@angular/core@16.2.0/+esm",
    "@angular/router": "https://cdn.jsdelivr.net/npm/@angular/router@16.2.0/+esm",
    "cases-app": "http://localhost:4201/main.js"
  }
}
</script>
<script type="module">
  import { bootstrapApplication } from '@angular/platform-browser';
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
| SSR | No nativamente | Varía (Webpack sí, Vite limitado) |
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
| Stack heterogéneo | Necesidad de mantener múltiples versiones de Angular |
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
- MFE sin contrato de shared deps → conflictos de versión en runtime
- MFE con estado compartido excesivo → acoplamiento que MFE debería eliminar
- Monolito sin modularización interna → candidatos futuros a MFE pero no todavía

---

### 4. Angular CLI + Module Federation vs Webpack directo — trade-offs

| Aspecto | Webpack Module Federation (directo) | Angular CLI + @angular-architects/module-federation |
|---------|------------------------------------|---------------------------------------------------|
| **Madurez** | Producción estable, usado por grandes empresas | Producción estable, integrado con Angular CLI |
| **Dev experience** | Configuración manual de Webpack | Schematics generan configuración automáticamente |
| **HMR** | HMR completo en Host y Remotes | HMR hereda de Angular CLI; limitado en remotes |
| **SSR** | Soportado nativamente | Soportado con configuración adicional |
| **Type safety** | Requiere `@module-federation/typescript` | Integrado con TypeScript de Angular |
| **Shared deps** | Negociación de versión avanzada con fallback | Negociación vía `share()` helper de @angular-architects |
| **Dynamic remotes** | Promesas para cargar remotes en runtime | `loadManifest()` o `loadRemoteModule()` con dynamic import |
| **Ecosistema plugins** | Amplio ecosistema (MFE storybook, debugging) | Integrado con Angular CLI; menos herramientas externas |
| **Bundle size** | Mayor (Webpack runtime + MFE runtime) | Similar (Angular CLI + MFE runtime) |
| **Community** | Module Federation Initiative (webpack.org) | @angular-architects + comunidad Angular |

**Recomendación por escenario:**

| Escenario | Recomendación |
|-----------|---------------|
| Proyecto Angular nuevo | **Angular CLI MFE** — consistencia con el stack |
| Proyecto Angular existente | **Angular CLI MFE** — no migrar a Webpack directo |
| SSR requerido | **Angular CLI MFE** — soporte vía @angular-architects |
| Prototipo / MVP rápido | **Angular CLI MFE** — schematics aceleran setup |
| Migración gradual desde monolito Angular | **Angular CLI MFE** — no mezclar configuración |
| Multi-framework (Angular + React) | **Webpack directo** — mayor flexibilidad cross-framework |

**Patrón híbrido (avanzado):**

Es posible usar Angular CLI para Host y Webpack directo para Remotes de otros frameworks, pero **no es recomendado** salvo casos de migración cross-framework. Los trade-offs incluyen: doble configuración, doble CI, inconsistencia en shared deps y debugging más complejo.

```typescript
// Angular Host consumiendo Webpack Remote (NO recomendado salvo migración cross-framework)
new ModuleFederationPlugin({
  name: 'shell',
  remotes: {
    cases: 'cases@http://localhost:3001/remoteEntry.js',
  },
});
```

> **Regla**: Un proyecto Angular = Angular CLI end-to-end. Si necesitas MFE cross-framework, evalúa Webpack directo pero mantén consistencia dentro de cada proyecto.
