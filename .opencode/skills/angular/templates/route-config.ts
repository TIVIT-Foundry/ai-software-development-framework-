/**
 * Angular Route Configuration Template
 *
 * Define las rutas de un feature module con lazy loading obligatorio.
 * Cada página se carga mediante loadComponent (standalone).
 *
 * Convenciones:
 * - Todas las rutas usan loadComponent: () => import(...)
 * - Guards como CanActivateFn inyectables con inject()
 * - Resolvers como ResolveFn para precarga de datos
 * - Path parameters con :id, query params como queryParams
 * - Title por ruta para SEO/accesibilidad
 * - Children para rutas anidadas (sub-páginas dentro del mismo feature)
 *
 * Uso: Copiar este archivo en la raíz del feature (ej: users/users.routes.ts),
 *       reemplazar placeholders, importar en app.routes.ts con loadChildren.
 */

import { Routes } from '@angular/router';

// --- Guards funcionales (crear en core/guards/) ---
// import { authGuard } from '../../core/guards/auth.guard';
// import { roleGuard } from '../../core/guards/role.guard';
// import { unsavedChangesGuard } from '../../core/guards/unsaved-changes.guard';

// --- Resolvers funcionales (crear en el feature o core/resolvers/) ---
// import { {{modelName}}Resolver } from './resolvers/{{model-name}}.resolver';

/**
 * Rutas del feature {{FeatureName}}.
 *
 * Para integrar en app.routes.ts:
 * {
 *   path: '{{feature-path}}',
 *   loadChildren: () => import('./features/{{feature-name}}/{{feature-name}}.routes')
 *     .then(m => m.{{FEATURE_NAME}}_ROUTES),
 * }
 */
export const {{FEATURE_NAME}}_ROUTES: Routes = [
  // --- Ruta raíz: listado (página principal del feature) ---
  {
    path: '',
    loadComponent: () =>
      import('./pages/{{model-name}}-list/{{model-name}}-list-page.component').then(
        m => m.{{ModelName}}ListPageComponent
      ),
    title: '{{FeatureTitle}} | App',
    // canActivate: [authGuard],
    // resolve: { items: {{modelName}}Resolver },
  },

  // --- Ruta de creación (debe ir antes de :id para no colisionar) ---
  {
    path: 'new',
    loadComponent: () =>
      import('./pages/{{model-name}}-form/{{model-name}}-form-page.component').then(
        m => m.{{ModelName}}FormPageComponent
      ),
    title: 'Nuevo {{ModelName}} | App',
    // canActivate: [authGuard, roleGuard(['admin', 'editor'])],
  },

  // --- Ruta de detalle ---
  {
    path: ':id',
    loadComponent: () =>
      import('./pages/{{model-name}}-detail/{{model-name}}-detail-page.component').then(
        m => m.{{ModelName}}DetailPageComponent
      ),
    title: 'Detalle de {{ModelName}} | App',
    // canActivate: [authGuard],
    // resolve: { item: {{modelName}}ItemResolver },
    // children: [
    //   // Sub-rutas dentro del detalle (ej: pestañas)
    //   {
    //     path: '',
    //     pathMatch: 'full',
    //     redirectTo: 'overview',
    //   },
    //   {
    //     path: 'overview',
    //     loadComponent: () =>
    //       import('./pages/{{model-name}}-detail/{{model-name}}-overview.component').then(
    //         m => m.{{ModelName}}OverviewComponent
    //       ),
    //   },
    //   {
    //     path: 'history',
    //     loadComponent: () =>
    //       import('./pages/{{model-name}}-detail/{{model-name}}-history.component').then(
    //         m => m.{{ModelName}}HistoryComponent
    //       ),
    //   },
    // ],
  },

  // --- Ruta de edición ---
  {
    path: ':id/edit',
    loadComponent: () =>
      import('./pages/{{model-name}}-form/{{model-name}}-form-page.component').then(
        m => m.{{ModelName}}FormPageComponent
      ),
    title: 'Editar {{ModelName}} | App',
    // canActivate: [authGuard, roleGuard(['admin', 'editor'])],
    // canDeactivate: [unsavedChangesGuard],
    // resolve: { item: {{modelName}}ItemResolver },
    data: { mode: 'edit' as const },
  },

  // --- Ruta wildcard para rutas no encontradas dentro del feature ---
  {
    path: '**',
    redirectTo: '',
    pathMatch: 'full',
  },
];

// --- Ejemplos adicionales de patrones útiles ---

/**
 * Ejemplo: Resolver funcional para precargar datos antes de activar la ruta
 *
 * export const {{modelName}}Resolver: ResolveFn<{{ModelName}}[]> = (
 *   route: ActivatedRouteSnapshot,
 *   state: RouterStateSnapshot
 * ) => {
 *   const service = inject({{ModelName}}Service);
 *   return service.getItems();
 * };
 */

/**
 * Ejemplo: Resolver con parámetros de ruta
 *
 * export const {{modelName}}ItemResolver: ResolveFn<{{ModelName}} | null> = (
 *   route: ActivatedRouteSnapshot
 * ) => {
 *   const id = route.paramMap.get('id');
 *   if (!id) return of(null);
 *   const service = inject({{ModelName}}Service);
 *   return service.getItem(id);
 * };
 */

/**
 * Ejemplo: Guard funcional que verifica roles
 *
 * export const roleGuard = (allowedRoles: string[]): CanActivateFn => {
 *   return () => {
 *     const authService = inject(AuthService);
 *     const router = inject(Router);
 *     const userRoles = authService.currentUser()?.roles ?? [];
 *
 *     const hasRole = allowedRoles.some(role => userRoles.includes(role));
 *     return hasRole ? true : router.createUrlTree(['/forbidden']);
 *   };
 * };
 */
