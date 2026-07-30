/**
 * Angular Service Template
 *
 * Servicio inyectable con HttpClient para comunicación con API REST.
 * Incluye patrón de store con signals para estado compartido.
 *
 * Convenciones:
 * - @Injectable({ providedIn: 'root' }) — singleton automático
 * - inject(HttpClient) — nunca usar fetch() directamente
 * - Métodos devuelven Observable<T> — no Promises
 * - catchError en cada llamada HTTP — manejo obligatorio de errores
 * - Tipado genérico completo — sin any
 * - HttpParams para query strings — evita concatenación manual
 * - Store con signals para estado local compartido
 *
 * Uso: Copiar este archivo, renombrar clase y selector,
 *       reemplazar los placeholders ({{ClassName}}, {{ModelName}}, etc.)
 */

import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, tap, throwError, map } from 'rxjs';

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

export interface {{ModelName}}ListParams {
  page?: number;
  limit?: number;
  search?: string;
  status?: string;
  sortBy?: string;
  sortDir?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// --- Error tipado de la API ---
export interface ApiError {
  statusCode: number;
  message: string;
  errors?: Record<string, string[]>;
  timestamp: string;
}

// =====================================================================
// Store — Estado compartido con signals
// =====================================================================
@Injectable({ providedIn: 'root' })
export class {{ClassName}}Store {
  // --- Estado ---
  private items = signal<{{ModelName}}[]>([]);
  private selectedId = signal<string | null>(null);
  private loadingState = signal(false);
  private errorState = signal<string | null>(null);
  private paginationState = signal({
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0,
  });

  // --- Selectores (readonly para consumidores) ---
  readonly itemList = this.items.asReadonly();
  readonly isLoading = this.loadingState.asReadonly();
  readonly error = this.errorState.asReadonly();
  readonly pagination = this.paginationState.asReadonly();

  readonly selectedItem = computed(() => {
    const id = this.selectedId();
    if (!id) return null;
    return this.items().find(item => item.id === id) ?? null;
  });

  readonly hasItems = computed(() => this.items().length > 0);
  readonly totalCount = computed(() => this.paginationState().total);

  // --- Mutaciones ---
  setItems(items: {{ModelName}}[]): void {
    this.items.set(items);
  }

  addItem(item: {{ModelName}}): void {
    this.items.update(current => [item, ...current]);
    this.paginationState.update(p => ({ ...p, total: p.total + 1 }));
  }

  updateItem(updated: {{ModelName}}): void {
    this.items.update(current =>
      current.map(item => (item.id === updated.id ? updated : item))
    );
  }

  removeItem(id: string): void {
    this.items.update(current => current.filter(item => item.id !== id));
    this.paginationState.update(p => ({ ...p, total: p.total - 1 }));
  }

  selectItem(id: string | null): void {
    this.selectedId.set(id);
  }

  setLoading(loading: boolean): void {
    this.loadingState.set(loading);
  }

  setError(error: string | null): void {
    this.errorState.set(error);
  }

  setPagination(page: number, limit: number, total: number): void {
    this.paginationState.set({
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
    });
  }

  // --- Reset ---
  reset(): void {
    this.items.set([]);
    this.selectedId.set(null);
    this.loadingState.set(false);
    this.errorState.set(null);
    this.paginationState.set({ page: 1, limit: 10, total: 0, totalPages: 0 });
  }
}

// =====================================================================
// Service — Capa de acceso a datos HTTP
// =====================================================================
@Injectable({ providedIn: 'root' })
export class {{ClassName}}Service {
  private http = inject(HttpClient);
  private store = inject({{ClassName}}Store);
  private readonly baseUrl = '/api/{{api-path}}';

  // --- Queries (GET) ---

  /**
   * Obtiene lista paginada de {{ModelName}}.
   * Actualiza el store automáticamente en éxito.
   */
  getItems(params?: {{ModelName}}ListParams): Observable<PaginatedResponse<{{ModelName}}>> {
    this.store.setLoading(true);
    this.store.setError(null);

    let httpParams = new HttpParams();
    if (params) {
      if (params.page) httpParams = httpParams.set('page', params.page.toString());
      if (params.limit) httpParams = httpParams.set('limit', params.limit.toString());
      if (params.search) httpParams = httpParams.set('search', params.search);
      if (params.status) httpParams = httpParams.set('status', params.status);
      if (params.sortBy) httpParams = httpParams.set('sortBy', params.sortBy);
      if (params.sortDir) httpParams = httpParams.set('sortDir', params.sortDir);
    }

    return this.http.get<PaginatedResponse<{{ModelName}}>>(this.baseUrl, { params: httpParams }).pipe(
      tap(response => {
        this.store.setItems(response.data);
        this.store.setPagination(response.page, response.limit, response.total);
        this.store.setLoading(false);
      }),
      catchError(error => {
        this.store.setLoading(false);
        this.store.setError(this.extractErrorMessage(error));
        return throwError(() => error);
      })
    );
  }

  /**
   * Obtiene un {{ModelName}} por ID.
   */
  getItem(id: string): Observable<{{ModelName}}> {
    this.store.setError(null);

    return this.http.get<{{ModelName}}>(`${this.baseUrl}/${id}`).pipe(
      tap(item => {
        this.store.selectItem(item.id);
      }),
      catchError(error => {
        this.store.setError(this.extractErrorMessage(error));
        return throwError(() => error);
      })
    );
  }

  // --- Mutations (POST, PUT, PATCH, DELETE) ---

  /**
   * Crea un nuevo {{ModelName}}.
   * Optimistic update: lo añade al store antes de la respuesta del servidor.
   */
  createItem(data: Create{{ModelName}}Dto): Observable<{{ModelName}}> {
    this.store.setError(null);

    return this.http.post<{{ModelName}}>(this.baseUrl, data).pipe(
      tap(created => {
        this.store.addItem(created);
      }),
      catchError(error => {
        this.store.setError(this.extractErrorMessage(error));
        return throwError(() => error);
      })
    );
  }

  /**
   * Actualiza un {{ModelName}} existente.
   */
  updateItem(id: string, data: Update{{ModelName}}Dto): Observable<{{ModelName}}> {
    this.store.setError(null);

    return this.http.put<{{ModelName}}>(`${this.baseUrl}/${id}`, data).pipe(
      tap(updated => {
        this.store.updateItem(updated);
      }),
      catchError(error => {
        this.store.setError(this.extractErrorMessage(error));
        return throwError(() => error);
      })
    );
  }

  /**
   * Actualización parcial (PATCH).
   */
  patchItem(id: string, data: Partial<Update{{ModelName}}Dto>): Observable<{{ModelName}}> {
    this.store.setError(null);

    return this.http.patch<{{ModelName}}>(`${this.baseUrl}/${id}`, data).pipe(
      tap(updated => {
        this.store.updateItem(updated);
      }),
      catchError(error => {
        this.store.setError(this.extractErrorMessage(error));
        return throwError(() => error);
      })
    );
  }

  /**
   * Elimina un {{ModelName}}.
   * Optimistic delete: lo quita del store inmediatamente.
   */
  deleteItem(id: string): Observable<void> {
    this.store.setError(null);

    return this.http.delete<void>(`${this.baseUrl}/${id}`).pipe(
      tap(() => {
        this.store.removeItem(id);
      }),
      catchError(error => {
        this.store.setError(this.extractErrorMessage(error));
        return throwError(() => error);
      })
    );
  }

  // --- Bulk operations ---

  /**
   * Eliminación masiva.
   */
  deleteItems(ids: string[]): Observable<void> {
    this.store.setError(null);

    return this.http.delete<void>(this.baseUrl, {
      body: { ids },
    }).pipe(
      tap(() => {
        ids.forEach(id => this.store.removeItem(id));
      }),
      catchError(error => {
        this.store.setError(this.extractErrorMessage(error));
        return throwError(() => error);
      })
    );
  }

  /**
   * Exporta datos (ej: Excel, CSV).
   */
  exportItems(params?: {{ModelName}}ListParams): Observable<Blob> {
    let httpParams = new HttpParams();
    if (params?.status) httpParams = httpParams.set('status', params.status);

    return this.http.get(`${this.baseUrl}/export`, {
      params: httpParams,
      responseType: 'blob',
    }).pipe(
      catchError(error => {
        this.store.setError(this.extractErrorMessage(error));
        return throwError(() => error);
      })
    );
  }

  // --- Helpers ---

  /**
   * Extrae un mensaje de error legible de la respuesta HTTP.
   */
  private extractErrorMessage(error: unknown): string {
    if (error instanceof HttpErrorResponse) {
      const apiError = error.error as ApiError | undefined;

      if (apiError?.message) {
        // Si hay errores de validación, los concatenamos
        const validationErrors = apiError.errors
          ? Object.values(apiError.errors).flat().join('; ')
          : '';
        return validationErrors || apiError.message;
      }

      // Errores HTTP estándar
      const statusMessages: Record<number, string> = {
        400: 'Datos inválidos. Verifica los campos.',
        401: 'Sesión expirada. Inicia sesión nuevamente.',
        403: 'No tienes permisos para realizar esta acción.',
        404: 'El recurso solicitado no existe.',
        409: 'Conflicto. El recurso ya existe o fue modificado.',
        422: 'Error de validación. Revisa los datos enviados.',
        429: 'Demasiadas solicitudes. Intenta de nuevo en unos segundos.',
        500: 'Error interno del servidor. Intenta más tarde.',
        503: 'Servicio no disponible. Intenta más tarde.',
      };

      return statusMessages[error.status] ?? `Error inesperado (${error.status})`;
    }

    if (error instanceof Error) {
      return error.message;
    }

    return 'Error desconocido. Contacta a soporte.';
  }

  /**
   * Construye HttpParams tipados a partir de un objeto de filtros.
   * Útil para queries con múltiples filtros opcionales.
   */
  private buildHttpParams(filters: Record<string, string | number | boolean | undefined | null>): HttpParams {
    let params = new HttpParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, String(value));
      }
    });
    return params;
  }
}
