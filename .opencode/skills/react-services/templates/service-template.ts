/**
 * React Fetch Client + Zustand Store Template
 *
 * Cliente HTTP centralizado (apiFetch) y store Zustand para estado
 * compartido — el equivalente al par HttpClient service + signal Store
 * de Angular.
 *
 * Convenciones:
 * - apiFetch() — nunca usar fetch() directamente desde un componente
 * - Métodos devuelven Promise<T> tipada
 * - Errores normalizados vía ApiError
 * - Store Zustand con selectors granulares (evita re-renders innecesarios)
 *
 * Uso: Copiar este archivo, renombrar el store y los tipos,
 *       reemplazar los placeholders ({{ModelName}}, etc.)
 */

import { create } from 'zustand';

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

export interface ApiError {
  statusCode: number;
  message: string;
  errors?: Record<string, string[]>;
}

const BASE_URL = '/api/{{api-path}}';

// --- Mensajes de error estándar por status HTTP ---
const STATUS_MESSAGES: Record<number, string> = {
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

async function extractErrorMessage(res: Response): Promise<string> {
  const body = (await res.json().catch(() => null)) as ApiError | null;
  if (body?.message) {
    const validationErrors = body.errors ? Object.values(body.errors).flat().join('; ') : '';
    return validationErrors || body.message;
  }
  return STATUS_MESSAGES[res.status] ?? `Error inesperado (${res.status})`;
}

function buildQueryString(params: Record<string, string | number | boolean | undefined | null>): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value));
  });
  return search.toString();
}

// =====================================================================
// Store — Estado compartido con Zustand (equivalente al signal store)
// =====================================================================
interface {{ModelName}}StoreState {
  items: {{ModelName}}[];
  selectedId: string | null;
  isLoading: boolean;
  error: string | null;
  pagination: { page: number; limit: number; total: number; totalPages: number };

  setItems: (items: {{ModelName}}[]) => void;
  addItem: (item: {{ModelName}}) => void;
  updateItem: (item: {{ModelName}}) => void;
  removeItem: (id: string) => void;
  selectItem: (id: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setPagination: (page: number, limit: number, total: number) => void;
  reset: () => void;
}

const initialPagination = { page: 1, limit: 10, total: 0, totalPages: 0 };

export const use{{ModelName}}Store = create<{{ModelName}}StoreState>((set, get) => ({
  items: [],
  selectedId: null,
  isLoading: false,
  error: null,
  pagination: initialPagination,

  setItems: (items) => set({ items }),
  addItem: (item) =>
    set((s) => ({ items: [item, ...s.items], pagination: { ...s.pagination, total: s.pagination.total + 1 } })),
  updateItem: (updated) =>
    set((s) => ({ items: s.items.map((item) => (item.id === updated.id ? updated : item)) })),
  removeItem: (id) =>
    set((s) => ({
      items: s.items.filter((item) => item.id !== id),
      pagination: { ...s.pagination, total: s.pagination.total - 1 },
    })),
  selectItem: (id) => set({ selectedId: id }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setPagination: (page, limit, total) => set({ pagination: { page, limit, total, totalPages: Math.ceil(total / limit) } }),
  reset: () => set({ items: [], selectedId: null, isLoading: false, error: null, pagination: initialPagination }),
}));

// Selectors sugeridos (importar y usar en componentes, no leer el store completo):
// const items = use{{ModelName}}Store((s) => s.items);
// const selectedItem = use{{ModelName}}Store((s) => s.items.find((i) => i.id === s.selectedId) ?? null);

// =====================================================================
// apiFetch — Capa de acceso a datos HTTP
// =====================================================================

/**
 * Obtiene lista paginada de {{ModelName}} y sincroniza el store.
 */
export async function fetch{{ModelName}}s(params?: {{ModelName}}ListParams): Promise<PaginatedResponse<{{ModelName}}>> {
  const store = use{{ModelName}}Store.getState();
  store.setLoading(true);
  store.setError(null);

  const res = await fetch(`${BASE_URL}?${buildQueryString(params ?? {})}`);
  if (!res.ok) {
    const message = await extractErrorMessage(res);
    store.setLoading(false);
    store.setError(message);
    throw new Error(message);
  }

  const response = (await res.json()) as PaginatedResponse<{{ModelName}}>;
  store.setItems(response.data);
  store.setPagination(response.page, response.limit, response.total);
  store.setLoading(false);
  return response;
}

/**
 * Obtiene un {{ModelName}} por ID.
 */
export async function fetch{{ModelName}}(id: string): Promise<{{ModelName}}> {
  const store = use{{ModelName}}Store.getState();
  store.setError(null);

  const res = await fetch(`${BASE_URL}/${id}`);
  if (!res.ok) {
    const message = await extractErrorMessage(res);
    store.setError(message);
    throw new Error(message);
  }

  const item = (await res.json()) as {{ModelName}};
  store.selectItem(item.id);
  return item;
}

/**
 * Crea un nuevo {{ModelName}} y lo añade al store.
 */
export async function create{{ModelName}}(data: Create{{ModelName}}Dto): Promise<{{ModelName}}> {
  const store = use{{ModelName}}Store.getState();
  store.setError(null);

  const res = await fetch(BASE_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
  if (!res.ok) {
    const message = await extractErrorMessage(res);
    store.setError(message);
    throw new Error(message);
  }

  const created = (await res.json()) as {{ModelName}};
  store.addItem(created);
  return created;
}

/**
 * Actualiza un {{ModelName}} existente.
 */
export async function update{{ModelName}}(id: string, data: Update{{ModelName}}Dto): Promise<{{ModelName}}> {
  const store = use{{ModelName}}Store.getState();
  store.setError(null);

  const res = await fetch(`${BASE_URL}/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
  if (!res.ok) {
    const message = await extractErrorMessage(res);
    store.setError(message);
    throw new Error(message);
  }

  const updated = (await res.json()) as {{ModelName}};
  store.updateItem(updated);
  return updated;
}

/**
 * Elimina un {{ModelName}}. Optimistic delete: lo quita del store inmediatamente.
 */
export async function delete{{ModelName}}(id: string): Promise<void> {
  const store = use{{ModelName}}Store.getState();
  store.setError(null);
  store.removeItem(id);

  const res = await fetch(`${BASE_URL}/${id}`, { method: 'DELETE' });
  if (!res.ok) {
    const message = await extractErrorMessage(res);
    store.setError(message);
    throw new Error(message);
  }
}

/**
 * Exporta datos (ej: Excel, CSV).
 */
export async function export{{ModelName}}s(params?: {{ModelName}}ListParams): Promise<Blob> {
  const res = await fetch(`${BASE_URL}/export?${buildQueryString({ status: params?.status })}`);
  if (!res.ok) {
    const store = use{{ModelName}}Store.getState();
    const message = await extractErrorMessage(res);
    store.setError(message);
    throw new Error(message);
  }
  return res.blob();
}
