/**
 * React Route Configuration Template (react-router-dom, Vite variant)
 *
 * Define las rutas de un feature con code-splitting obligatorio.
 * Cada página se carga mediante React.lazy().
 *
 * Convenciones:
 * - Todas las rutas usan lazy(() => import(...))
 * - Guards como elementos wrapper (<RequireAuth>) o loaders
 * - Loaders (RouteObject.loader) para precarga de datos
 * - Path parameters con :id
 * - Title por ruta seteado en el propio page component (useEffect)
 * - Rutas hijas anidadas para sub-páginas dentro del mismo feature
 *
 * Uso: Copiar este archivo en la raíz del feature (ej: users/users.routes.ts),
 *       reemplazar placeholders, importar en el router raíz con las rutas hijas.
 *
 * Nota (Next.js): en el variante App Router esto no aplica — las rutas se
 * definen por convención de archivos en app/{{feature-path}}/**\/page.tsx.
 */

import { lazy } from 'react';
import { Navigate } from 'react-router-dom';
import type { RouteObject } from 'react-router-dom';

// --- Guards (crear en core/guards/) ---
// import { RequireAuth } from '../../core/guards/RequireAuth';
// import { RequireRole } from '../../core/guards/RequireRole';

// --- Loaders (crear en el feature o core/loaders/) ---
// import { {{modelName}}Loader } from './loaders/{{model-name}}.loader';

const {{ModelName}}ListPage = lazy(() => import('./pages/{{ModelName}}ListPage'));
const {{ModelName}}FormPage = lazy(() => import('./pages/{{ModelName}}FormPage'));
const {{ModelName}}DetailPage = lazy(() => import('./pages/{{ModelName}}DetailPage'));

/**
 * Rutas del feature {{FeatureName}}.
 *
 * Para integrar en el router raíz:
 * {
 *   path: '{{feature-path}}',
 *   children: {{FEATURE_NAME}}_ROUTES,
 * }
 */
export const {{FEATURE_NAME}}_ROUTES: RouteObject[] = [
  // --- Ruta raíz: listado (página principal del feature) ---
  {
    index: true,
    element: <{{ModelName}}ListPage />,
    // element: <RequireAuth><{{ModelName}}ListPage /></RequireAuth>,
    // loader: {{modelName}}Loader,
  },

  // --- Ruta de creación (debe ir antes de :id para no colisionar) ---
  {
    path: 'new',
    element: <{{ModelName}}FormPage />,
    // element: <RequireAuth><RequireRole roles={['admin', 'editor']}><{{ModelName}}FormPage /></RequireRole></RequireAuth>,
  },

  // --- Ruta de detalle ---
  {
    path: ':id',
    element: <{{ModelName}}DetailPage />,
    // loader: {{modelName}}ItemLoader,
    // children: [
    //   // Sub-rutas dentro del detalle (ej: pestañas)
    //   { index: true, element: <Navigate to="overview" replace /> },
    //   { path: 'overview', element: <{{ModelName}}Overview /> },
    //   { path: 'history', element: <{{ModelName}}History /> },
    // ],
  },

  // --- Ruta de edición ---
  {
    path: ':id/edit',
    element: <{{ModelName}}FormPage mode="edit" />,
    // element: <RequireAuth><RequireRole roles={['admin', 'editor']}><{{ModelName}}FormPage mode="edit" /></RequireRole></RequireAuth>,
  },

  // --- Ruta wildcard para rutas no encontradas dentro del feature ---
  {
    path: '*',
    element: <Navigate to="." replace />,
  },
];

// --- Ejemplos adicionales de patrones útiles ---

/**
 * Ejemplo: loader para precargar datos antes de renderizar la ruta
 *
 * export const {{modelName}}Loader: LoaderFunction = async () => {
 *   return apiFetch<{{ModelName}}[]>('/{{api-path}}');
 * };
 */

/**
 * Ejemplo: loader con parámetros de ruta
 *
 * export const {{modelName}}ItemLoader: LoaderFunction = async ({ params }) => {
 *   if (!params.id) throw new Response('Not Found', { status: 404 });
 *   return apiFetch<{{ModelName}}>(`/{{api-path}}/${params.id}`);
 * };
 */

/**
 * Ejemplo: guard funcional que verifica roles
 *
 * export function RequireRole({ roles, children }: { roles: string[]; children: React.ReactNode }) {
 *   const userRoles = useAuthStore((s) => s.currentUser?.roles ?? []);
 *   const hasRole = roles.some((role) => userRoles.includes(role));
 *   return hasRole ? <>{children}</> : <Navigate to="/forbidden" replace />;
 * }
 */
