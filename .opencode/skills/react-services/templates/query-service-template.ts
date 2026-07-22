/**
 * @tanstack/react-query Hooks Template
 *
 * Módulo de hooks que encapsula queries y mutaciones usando TanStack Query.
 * Separación clara entre:
 * - Queries (lectura de datos) — useQuery()
 * - Mutations (escritura) — useMutation()
 * - Invalidación de caché — queryClient.invalidateQueries()
 *
 * Convenciones:
 * - Un hook por operación (useItems, useItem, useCreateItem, ...)
 * - Cada query tiene queryKey único y descriptivo
 * - Mutaciones invalidan queries relacionadas en onSuccess
 * - Optimistic updates cuando aplica
 * - Tipos genéricos completos
 * - Error handling a nivel de query/mutation
 *
 * Requisito: instalar @tanstack/react-query en el proyecto
 *   npm install @tanstack/react-query
 *
 * Uso: Copiar este archivo, renombrar los hooks,
 *       reemplazar los placeholders.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiFetch } from '../../core/api/fetch-client';

// --- Tipos (mover a {{model-name}}.types.ts) ---
export interface {{ModelName}} {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'pending';
  createdAt: string;
  updatedAt: string;
}

export interface Create{{ModelName}}Dto {
  name: string;
  status?: 'active' | 'inactive' | 'pending';
}

export interface Update{{ModelName}}Dto {
  name?: string;
  status?: 'active' | 'inactive' | 'pending';
}

export interface {{ModelName}}Filters {
  search?: string;
  status?: string;
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

const BASE_URL = '/{{api-path}}';

function buildSearchParams(filters: {{ModelName}}Filters = {}): string {
  const params = new URLSearchParams();
  if (filters.search) params.set('search', filters.search);
  if (filters.status) params.set('status', filters.status);
  if (filters.page) params.set('page', String(filters.page));
  if (filters.limit) params.set('limit', String(filters.limit));
  return params.toString();
}

// =====================================================================
// Queries (lectura, caché automática, re-fetch en focus/reconnect)
// =====================================================================

/**
 * Lista de {{ModelName}} con paginación y filtros.
 * queryKey: ['{{model-name}}', filters] — se re-fetchea cuando cambian los filtros
 */
export function use{{ModelName}}s(filters?: {{ModelName}}Filters) {
  return useQuery({
    queryKey: ['{{model-name}}', filters ?? {}] as const,
    queryFn: () => apiFetch<PaginatedResponse<{{ModelName}}>>(`${BASE_URL}?${buildSearchParams(filters)}`),
    staleTime: 30_000,   // 30 segundos sin re-fetch
    gcTime: 5 * 60_000,  // 5 minutos en garbage collector
    refetchOnWindowFocus: true,
    retry: 2,
  });
}

/**
 * Detalle de un {{ModelName}} por ID.
 * queryKey: ['{{model-name}}', id] — único por recurso
 */
export function use{{ModelName}}(id: string | undefined) {
  return useQuery({
    queryKey: ['{{model-name}}', id] as const,
    queryFn: () => apiFetch<{{ModelName}}>(`${BASE_URL}/${id}`),
    enabled: !!id,          // Solo ejecuta si hay ID
    staleTime: 60_000,      // 1 minuto
    gcTime: 10 * 60_000,    // 10 minutos
    retry: 1,
  });
}

/**
 * Conteo de {{ModelName}} (ej: para badges, indicadores).
 * queryKey: ['{{model-name}}', 'count']
 */
export function use{{ModelName}}Count(filters?: Omit<{{ModelName}}Filters, 'page' | 'limit'>) {
  return useQuery({
    queryKey: ['{{model-name}}', 'count', filters ?? {}] as const,
    queryFn: () => apiFetch<{ total: number }>(`${BASE_URL}/count?${buildSearchParams(filters)}`),
    staleTime: 60_000,
    gcTime: 10 * 60_000,
  });
}

// =====================================================================
// Mutations (crear, actualizar, eliminar)
// =====================================================================

/**
 * Crear {{ModelName}}.
 * Invalidación: refetch de la lista y del conteo.
 */
export function useCreate{{ModelName}}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Create{{ModelName}}Dto) =>
      apiFetch<{{ModelName}}>(BASE_URL, { method: 'POST', body: JSON.stringify(data) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['{{model-name}}'] });
      queryClient.invalidateQueries({ queryKey: ['{{model-name}}', 'count'] });
    },
    onError: (error) => logError('createItem', error),
  });
}

/**
 * Actualizar {{ModelName}}.
 * Invalidación: refetch del detalle y de la lista.
 */
export function useUpdate{{ModelName}}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Update{{ModelName}}Dto }) =>
      apiFetch<{{ModelName}}>(`${BASE_URL}/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    onSuccess: (_result, variables) => {
      queryClient.invalidateQueries({ queryKey: ['{{model-name}}', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['{{model-name}}'] });
    },
    onError: (error, variables) => logError('updateItem', error, { id: variables.id }),
  });
}

/**
 * Eliminar {{ModelName}}.
 * Optimistic update: elimina del caché inmediatamente, revierte en caso de error.
 */
export function useDelete{{ModelName}}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiFetch<void>(`${BASE_URL}/${id}`, { method: 'DELETE' }),
    onMutate: async (id: string) => {
      await queryClient.cancelQueries({ queryKey: ['{{model-name}}'] });

      const previousList = queryClient.getQueryData<PaginatedResponse<{{ModelName}}>>(['{{model-name}}']);

      if (previousList) {
        queryClient.setQueryData<PaginatedResponse<{{ModelName}}>>(['{{model-name}}'], {
          ...previousList,
          data: previousList.data.filter((item) => item.id !== id),
          total: previousList.total - 1,
        });
      }

      queryClient.removeQueries({ queryKey: ['{{model-name}}', id] });

      return { previousList };
    },
    onError: (error, id, context) => {
      if (context?.previousList) {
        queryClient.setQueryData(['{{model-name}}'], context.previousList);
      }
      logError('deleteItem', error, { id });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['{{model-name}}'] });
      queryClient.invalidateQueries({ queryKey: ['{{model-name}}', 'count'] });
    },
  });
}

// =====================================================================
// Helpers
// =====================================================================

/**
 * Log de errores centralizado.
 * Reemplazar con el servicio de logging/observabilidad del proyecto.
 */
function logError(operation: string, error: unknown, context?: Record<string, unknown>): void {
  console.error(`[{{ModelName}}Hooks] Error en ${operation}:`, { error, context, timestamp: new Date().toISOString() });
  // TODO: Integrar con servicio de telemetría (OpenTelemetry, Sentry, etc.)
}

// =====================================================================
// Ejemplo: componente que consume los hooks
// =====================================================================
//
// export function {{ModelName}}ListPage() {
//   const { data, isLoading, isError, error } = use{{ModelName}}s({ page: 1, limit: 20 });
//   const createMutation = useCreate{{ModelName}}();
//   const deleteMutation = useDelete{{ModelName}}();
//
//   if (isLoading) return <Spinner />;
//   if (isError) return <ErrorState message={error.message} />;
//   if (!data?.data.length) return <EmptyState />;
//
//   return (
//     <>
//       {data.data.map((item) => (
//         <ItemCard key={item.id} item={item} onDelete={() => deleteMutation.mutate(item.id)} />
//       ))}
//     </>
//   );
// }
