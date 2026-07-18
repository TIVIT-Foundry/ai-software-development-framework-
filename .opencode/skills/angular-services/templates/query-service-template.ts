/**
 * @ngneat/query (TanStack Query for Angular) Service Template
 *
 * Servicio que encapsula queries y mutaciones usando @ngneat/query.
 * Separación clara entre:
 * - Queries (lectura de datos) — injectQuery()
 * - Mutations (escritura) — injectMutation()
 * - Invalidación de caché — injectQueryClient().invalidateQueries()
 *
 * Convenciones:
 * - @Injectable({ providedIn: 'root' })
 * - Cada query tiene queryKey único y descriptivo
 * - Mutaciones invalidan queries relacionadas en onSuccess
 * - Optimistic updates cuando aplica
 * - Tipos genéricos completos
 * - Error handling a nivel de query/mutation
 *
 * Requisito: instalar @ngneat/query en el proyecto
 *   npm install @ngneat/query @tanstack/query-core
 *
 * Uso: Copiar este archivo, renombrar clase,
 *       reemplazar los placeholders.
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { injectQuery, injectMutation, injectQueryClient } from '@ngneat/query';
import { lastValueFrom } from 'rxjs';

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

// =====================================================================
// Queries y Mutations
// =====================================================================
@Injectable({ providedIn: 'root' })
export class {{ClassName}}Queries {
  private http = inject(HttpClient);
  private queryClient = injectQueryClient();
  private readonly baseUrl = '/api/{{api-path}}';

  // ===================================================================
  // Queries (lectura, caché automática, re-fetch en focus/reconnect)
  // ===================================================================

  /**
   * Lista de {{ModelName}} con paginación y filtros.
   * queryKey: ['{{model-name}}', filters] — se re-fetcha cuando cambian los filtros
   */
  items = (filters?: {{ModelName}}Filters) =>
    injectQuery(() => ({
      queryKey: ['{{model-name}}', filters ?? {}] as const,
      queryFn: () => {
        const params = this.buildSearchParams(filters ?? {});
        return lastValueFrom(
          this.http.get<PaginatedResponse<{{ModelName}}>>(this.baseUrl, { params })
        );
      },
      staleTime: 30_000,    // 30 segundos sin re-fetch
      gcTime: 5 * 60_000,   // 5 minutos en garbage collector
      refetchOnWindowFocus: true,
      retry: 2,
    }));

  /**
   * Detalle de un {{ModelName}} por ID.
   * queryKey: ['{{model-name}}', id] — único por recurso
   */
  item = (id: string) =>
    injectQuery(() => ({
      queryKey: ['{{model-name}}', id] as const,
      queryFn: () =>
        lastValueFrom(this.http.get<{{ModelName}}>(`${this.baseUrl}/${id}`)),
      enabled: !!id,           // Solo ejecuta si hay ID
      staleTime: 60_000,       // 1 minuto
      gcTime: 10 * 60_000,     // 10 minutos
      retry: 1,
    }));

  /**
   * Conteo de {{ModelName}} (ej: para badges, indicadores).
   * queryKey: ['{{model-name}}', 'count']
   */
  count = (filters?: Omit<{{ModelName}}Filters, 'page' | 'limit'>) =>
    injectQuery(() => ({
      queryKey: ['{{model-name}}', 'count', filters ?? {}] as const,
      queryFn: () =>
        lastValueFrom(
          this.http.get<{ total: number }>(`${this.baseUrl}/count`, {
            params: this.buildSearchParams(filters ?? {}),
          })
        ),
      staleTime: 60_000,
      gcTime: 10 * 60_000,
    }));

  // ===================================================================
  // Mutations (crear, actualizar, eliminar)
  // ===================================================================

  /**
   * Crear {{ModelName}}.
   * Invalidación: refetch de la lista y del conteo.
   */
  createItem = injectMutation(() => ({
    mutationFn: (data: Create{{ModelName}}Dto) =>
      lastValueFrom(this.http.post<{{ModelName}}>(this.baseUrl, data)),
    onSuccess: () => {
      // Invalidar la lista para que se re-fetchee
      this.queryClient.invalidateQueries({ queryKey: ['{{model-name}}'] });
      // También invalidar el conteo
      this.queryClient.invalidateQueries({ queryKey: ['{{model-name}}', 'count'] });
    },
    onError: (error: unknown) => {
      this.logError('createItem', error);
    },
  }));

  /**
   * Actualizar {{ModelName}}.
   * Invalidación: refetch del detalle y de la lista.
   */
  updateItem = injectMutation(() => ({
    mutationFn: ({ id, data }: { id: string; data: Update{{ModelName}}Dto }) =>
      lastValueFrom(this.http.put<{{ModelName}}>(`${this.baseUrl}/${id}`, data)),
    onSuccess: (_, variables) => {
      // Invalidar el detalle específico
      this.queryClient.invalidateQueries({ queryKey: ['{{model-name}}', variables.id] });
      // Invalidar la lista completa
      this.queryClient.invalidateQueries({ queryKey: ['{{model-name}}'] });
    },
    onError: (error: unknown, variables) => {
      this.logError('updateItem', error, { id: variables.id });
    },
  }));

  /**
   * Actualización parcial (PATCH).
   */
  patchItem = injectMutation(() => ({
    mutationFn: ({ id, data }: { id: string; data: Partial<Update{{ModelName}}Dto> }) =>
      lastValueFrom(this.http.patch<{{ModelName}}>(`${this.baseUrl}/${id}`, data)),
    onSuccess: (_, variables) => {
      this.queryClient.invalidateQueries({ queryKey: ['{{model-name}}', variables.id] });
      this.queryClient.invalidateQueries({ queryKey: ['{{model-name}}'] });
    },
    onError: (error: unknown, variables) => {
      this.logError('patchItem', error, { id: variables.id });
    },
  }));

  /**
   * Eliminar {{ModelName}}.
   * Optimistic update: elimina del caché inmediatamente,
   * revierte en caso de error.
   */
  deleteItem = injectMutation(() => ({
    mutationFn: (id: string) =>
      lastValueFrom(this.http.delete<void>(`${this.baseUrl}/${id}`)),
    onMutate: async (id: string) => {
      // Cancelar queries en vuelo para evitar sobrescritura
      await this.queryClient.cancelQueries({ queryKey: ['{{model-name}}'] });

      // Snapshot del estado anterior (para rollback)
      const previousList = this.queryClient.getQueryData<PaginatedResponse<{{ModelName}}>>([
        '{{model-name}}',
      ]);

      // Optimistic update: quitar el item de la lista actual
      if (previousList) {
        this.queryClient.setQueryData<PaginatedResponse<{{ModelName}}>>(
          ['{{model-name}}'],
          {
            ...previousList,
            data: previousList.data.filter(item => item.id !== id),
            total: previousList.total - 1,
          }
        );
      }

      // También quitar del detalle si está en caché
      this.queryClient.removeQueries({ queryKey: ['{{model-name}}', id] });

      return { previousList };
    },
    onError: (error, id, context) => {
      // Rollback: restaurar datos anteriores
      if (context?.previousList) {
        this.queryClient.setQueryData(['{{model-name}}'], context.previousList);
      }
      this.logError('deleteItem', error, { id });
    },
    onSettled: () => {
      // Refetch para asegurar consistencia
      this.queryClient.invalidateQueries({ queryKey: ['{{model-name}}'] });
      this.queryClient.invalidateQueries({ queryKey: ['{{model-name}}', 'count'] });
    },
  }));

  /**
   * Eliminación masiva.
   * Misma estrategia de optimistic update que deleteItem.
   */
  deleteItems = injectMutation(() => ({
    mutationFn: (ids: string[]) =>
      lastValueFrom(
        this.http.delete<void>(this.baseUrl, { body: { ids } })
      ),
    onMutate: async (ids: string[]) => {
      await this.queryClient.cancelQueries({ queryKey: ['{{model-name}}'] });

      const previousList = this.queryClient.getQueryData<PaginatedResponse<{{ModelName}}>>([
        '{{model-name}}',
      ]);

      if (previousList) {
        const idSet = new Set(ids);
        this.queryClient.setQueryData<PaginatedResponse<{{ModelName}}>>(
          ['{{model-name}}'],
          {
            ...previousList,
            data: previousList.data.filter(item => !idSet.has(item.id)),
            total: previousList.total - ids.length,
          }
        );
      }

      ids.forEach(id => {
        this.queryClient.removeQueries({ queryKey: ['{{model-name}}', id] });
      });

      return { previousList };
    },
    onError: (error, ids, context) => {
      if (context?.previousList) {
        this.queryClient.setQueryData(['{{model-name}}'], context.previousList);
      }
      this.logError('deleteItems', error, { ids });
    },
    onSettled: () => {
      this.queryClient.invalidateQueries({ queryKey: ['{{model-name}}'] });
      this.queryClient.invalidateQueries({ queryKey: ['{{model-name}}', 'count'] });
    },
  }));

  // ===================================================================
  // Helpers
  // ===================================================================

  /**
   * Construye HttpParams a partir de filtros.
   */
  private buildSearchParams(filters: {{ModelName}}Filters): { [param: string]: string } {
    const params: Record<string, string> = {};
    if (filters.search) params['search'] = filters.search;
    if (filters.status) params['status'] = filters.status;
    if (filters.page) params['page'] = String(filters.page);
    if (filters.limit) params['limit'] = String(filters.limit);
    return params;
  }

  /**
   * Log de errores centralizado.
   * Reemplazar con el servicio de logging/observabilidad del proyecto.
   */
  private logError(operation: string, error: unknown, context?: Record<string, unknown>): void {
    console.error(`[${this.constructor.name}] Error en ${operation}:`, {
      error,
      context,
      timestamp: new Date().toISOString(),
    });

    // TODO: Integrar con servicio de telemetría (OpenTelemetry, Sentry, etc.)
    // this.telemetryService.captureException(error, { operation, ...context });
  }

  /**
   * Precarga datos en el caché (útil para navegación predictiva).
   */
  prefetchItem(id: string): void {
    this.queryClient.prefetchQuery({
      queryKey: ['{{model-name}}', id],
      queryFn: () =>
        lastValueFrom(this.http.get<{{ModelName}}>(`${this.baseUrl}/${id}`)),
      staleTime: 60_000,
    });
  }

  /**
   * Precarga la lista de {{ModelName}}.
   */
  prefetchItems(filters?: {{ModelName}}Filters): void {
    this.queryClient.prefetchQuery({
      queryKey: ['{{model-name}}', filters ?? {}],
      queryFn: () => {
        const params = this.buildSearchParams(filters ?? {});
        return lastValueFrom(
          this.http.get<PaginatedResponse<{{ModelName}}>>(this.baseUrl, { params })
        );
      },
      staleTime: 30_000,
    });
  }

  /**
   * Invalida todas las queries de {{ModelName}}.
   * Usar después de operaciones que afectan múltiples recursos.
   */
  invalidateAll(): void {
    this.queryClient.invalidateQueries({ queryKey: ['{{model-name}}'] });
  }

  /**
   * Resetea el caché completamente.
   * Útil en logout o cambio de tenant.
   */
  resetCache(): void {
    this.queryClient.removeQueries({ queryKey: ['{{model-name}}'] });
  }
}

// =====================================================================
// Ejemplo: Componente que consume las queries
// =====================================================================
//
// @Component({
//   selector: 'app-{{model-name}}-list',
//   standalone: true,
//   imports: [CommonModule, RouterLink],
//   templateUrl: './{{model-name}}-list.component.html',
//   changeDetection: ChangeDetectionStrategy.OnPush,
// })
// export class {{ModelName}}ListComponent {
//   private queries = inject({{ClassName}}Queries);
//
//   // Queries
//   itemsQuery = this.queries.items({ page: 1, limit: 20 });
//
//   // Mutations
//   createMutation = this.queries.createItem;
//   deleteMutation = this.queries.deleteItem;
//
//   onCreate(data: Create{{ModelName}}Dto): void {
//     this.createMutation.mutate(data, {
//       onSuccess: (result) => {
//         this.router.navigate(['..', result.id], { relativeTo: this.route });
//       },
//     });
//   }
//
//   onDelete(id: string): void {
//     if (confirm('¿Eliminar este elemento?')) {
//       this.deleteMutation.mutate(id);
//     }
//   }
// }
//
// <!-- Template -->
// <!--
// @if (itemsQuery(); as result) {
//   @if (result.isLoading) {
//     <app-spinner />
//   } @else if (result.isError) {
//     <app-error-state [message]="result.error.message" (retry)="result.refetch()" />
//   } @else if (!result.data?.data.length) {
//     <app-empty-state />
//   } @else {
//     @for (item of result.data.data; track item.id) {
//       <app-item-card [item]="item" (delete)="onDelete(item.id)" />
//     }
//   }
// }
// -->
