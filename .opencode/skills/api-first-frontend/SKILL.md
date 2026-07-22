---
name: api-first-frontend
description: 'Generate frontend code from OpenAPI spec: TypeScript types, data-fetching
  hooks, base components. Trigger: When implementing frontend from OpenAPI spec, generating
  types from endpoints.'
version: 2.0
metadata:
  phase:
  - construction
  layer:
  - frontend
  enforcement: mandatory
  depends_on:
  - api-first-spec
  - react
  - react-services
  - typescript
  consumed_by:
  - agent-frontend
  - agent-fullstack
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: skill-contract
mcp_usage: none
---

## Workflow
OpenAPI Spec → Parse → Generate Types → Generate API Client → Generate Query/Mutation Hooks → Generate Components → Generate Page

## TypeScript Type Mapping
| OpenAPI Type | TypeScript Type |
|--------------|-----------------|
| `integer` | `number` |
| `string` | `string` |
| `string` (date-time) | `string` |
| `boolean` | `boolean` |
| `array` | `T[]` |
| `object` | `interface` |

**Note:** All nullable fields use `Type | null` (not optional `Type?`). Request types must extend `Record<string, unknown>` when using factory patterns.

## Service IDs (in `models/constants.ts`)
```typescript
export const {Feature}Service = {
  Get{Entity}s: 100,
  Get{Entity}ById: 101,
  PostCreate{Entity}: 102,
  PutUpdate{Entity}: 103,
  Delete{Entity}: 104,
  Post{Verb}{Entity}: 110,  // State transitions
} as const;
```

## Query Hook Pattern (React + @tanstack/react-query)
```typescript
import { useQuery } from '@tanstack/react-query';
import { UsersApi } from '../api/users.api';

export function useUsersList(params?: UsersQueryParams) {
  return useQuery({
    queryKey: ['users', 'list', params],
    queryFn: () => UsersApi.list(params),
  });
}
```

## Mutation Hook Pattern
```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { UsersApi } from '../api/users.api';

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateUserRequest) => UsersApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', 'list'] });
    },
  });
}
```

## Operation Hook Naming Convention
| Operation | Hook Name | Action Returned |
|-----------|-------------|-----------------|
| Submit | `useSubmit{Entity}` | `mutate` |
| Cancel | `useCancel{Entity}` | `mutate` |
| Approve | `useApprove{Entity}` | `mutate` |
| Reject | `useReject{Entity}` | `mutate` |
| Remove | `useRemove{SubEntity}` | `mutate` |

## File Structure
```
features/{feature-name}/
├── components/
│   ├── {FeatureList}.tsx
│   └── {FeatureForm}.tsx
├── hooks/
│   ├── use-{entity}s.query.ts       # Query hook (useQuery)
│   ├── use-create-{entity}.mutation.ts  # Mutation hook (useMutation)
│   └── use-{feature}.ts             # Orchestrator hook (queries + mutations + local state)
├── api/
│   └── {feature}.api.ts             # Typed HTTP calls
├── models/
│   ├── constants.ts                  # Service IDs, enums
│   ├── {feature}.types.ts           # Form value types
│   └── index.ts                     # Re-exports
└── {feature}.routes.tsx             # Route definitions (react-router-dom)
```

## Generation Order
1. Service IDs / constants first
2. Types inline with API client
3. Query hooks (GET endpoints)
4. Mutation hooks (POST/PUT/DELETE/Operation)
5. Feature hook (orchestrates queries + mutations + local state)
6. Page component

## Critical Checklist
- [ ] Request types extend `Record<string, unknown>` (if using factory pattern)
- [ ] Query hooks have proper cache keys
- [ ] Mutation hooks do NOT show toast (toast in orchestrator hook/page layer)
- [ ] Blob mutation generates file download
- [ ] All nullable fields use `Type | null`
- [ ] All components have explicit typed props (no `any`)

## Workflow completo: De spec a componente React funcional

Esta sección describe el flujo end-to-end para transformar una especificación OpenAPI (producida por `api-first-spec`) en una pantalla React totalmente funcional, tipada y traducida. El ejemplo guía es el módulo `users` con CRUD + paginación.

### Inputs

La skill `api-first-spec` debe entregar como mínimo:

| Artefacto | Ubicación esperada | Contenido |
|-----------|--------------------|-----------|
| `openapi.yaml` | `docs/api/{module}/openapi.yaml` | Definición OpenAPI 3.1 con `paths`, `components.schemas`, `securitySchemes` |
| `catalog.md` | `docs/api/{module}/catalog.md` | Tabla `DB Object → Endpoint → Service ID → Screen → Route` |
| `error-codes.md` | `docs/api/{module}/error-codes.md` | Catálogo de códigos de error con HTTP status, mensaje i18n key |
| `business-rules.md` | `docs/api/{module}/business-rules.md` | Reglas de negocio (validaciones, transiciones de estado) |

El frontend consume estos artefactos para generar tipos, hooks y componentes sin inventar contratos. Si algo no está en el spec, se devuelve al equipo de diseño.

### Step 1 — Generar TypeScript types

Cada `schema` del bloque `components.schemas` del OpenAPI se mapea a una interface TypeScript en `src/features/users/models/users.types.ts`. Los enums se materializan como `const` objects (no `enum` de TS) para evitar problemas de tree-shaking.

```typescript
export interface UserResponse {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  status: UserStatus;
  roleId: number;
  roleName: string;
  createdAt: string;
  updatedAt: string | null;
  lastLoginAt: string | null;
}

export interface CreateUserRequest extends Record<string, unknown> {
  email: string;
  firstName: string;
  lastName: string;
  password: string;
  roleId: number;
}

export interface UpdateUserRequest extends Record<string, unknown> {
  firstName: string;
  lastName: string;
  roleId: number;
  status: UserStatus;
}

export interface PaginatedResponse<T> {
  items: T[];
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
}

export const UserStatus = {
  Active: 'ACTIVE',
  Inactive: 'INACTIVE',
  Suspended: 'SUSPENDED',
} as const;
export type UserStatus = (typeof UserStatus)[keyof typeof UserStatus];

export interface UsersQueryParams {
  page?: number;
  pageSize?: number;
  search?: string;
  status?: UserStatus;
  roleId?: number;
}
```

Y los Service IDs (constantes numéricas que mapean cada endpoint a un identificador único, usado para trazabilidad, permisos y logging):

```typescript
export const UsersService = {
  GetUsers: 1001,
  GetUserById: 1002,
  PostCreateUser: 1003,
  PutUpdateUser: 1004,
  DeleteUser: 1005,
  PostActivateUser: 1010,
  PostSuspendUser: 1011,
} as const;
export type UsersServiceId = (typeof UsersService)[keyof typeof UsersService];
```

### Step 2 — Crear API client

El cliente HTTP centraliza autenticación, headers, manejo de errores y wrap del `ApiResponse<T>`. Se ubica en `src/core/api/api-client.ts` como funciones puras (sin DI — un objeto exportado).

```typescript
import type { ApiResponse, ApiError } from '../types/api';
import { useAuthStore } from '../auth/auth.store';

const BASE_URL = '/api';

async function request<T>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE',
  path: string,
  options: { body?: unknown; params?: Record<string, unknown>; serviceId?: number } = {},
): Promise<ApiResponse<T>> {
  const headers = new Headers({ 'Content-Type': 'application/json', Accept: 'application/json' });
  if (options.serviceId) headers.set('X-Service-Id', String(options.serviceId));

  const token = useAuthStore.getState().token;
  if (token) headers.set('Authorization', `Bearer ${token}`);

  const search = new URLSearchParams();
  if (options.params) {
    for (const [key, value] of Object.entries(options.params)) {
      if (value !== undefined && value !== null) search.set(key, String(value));
    }
  }

  const url = `${BASE_URL}${path}${search.toString() ? `?${search}` : ''}`;
  const res = await fetch(url, { method, headers, body: options.body ? JSON.stringify(options.body) : undefined });

  if (!res.ok) {
    const error = (await res.json().catch(() => null)) as ApiError | null;
    throw {
      status: res.status,
      code: error?.error?.code ?? 'UNKNOWN',
      message: error?.error?.message ?? res.statusText,
      details: error?.error?.details,
    };
  }

  return res.json() as Promise<ApiResponse<T>>;
}

export const apiClient = {
  get: <T>(path: string, options?: { params?: Record<string, unknown>; serviceId?: number }) =>
    request<T>('GET', path, options),
  post: <T>(path: string, body: unknown, options?: { serviceId?: number }) =>
    request<T>('POST', path, { body, ...options }),
  put: <T>(path: string, body: unknown, options?: { serviceId?: number }) =>
    request<T>('PUT', path, { body, ...options }),
  delete: <T>(path: string, options?: { serviceId?: number }) =>
    request<T>('DELETE', path, options),
};
```

Las funciones tipadas por módulo viven en `src/features/users/api/users.api.ts`:

```typescript
import { apiClient } from '../../../core/api/api-client';
import { UsersService } from '../models/constants';
import type {
  UserResponse,
  CreateUserRequest,
  UpdateUserRequest,
  UsersQueryParams,
  PaginatedResponse,
} from '../models';
import type { ApiResponse } from '../../../core/types/api';

export const UsersApi = {
  list: (params?: UsersQueryParams): Promise<ApiResponse<PaginatedResponse<UserResponse>>> =>
    apiClient.get('/users', { params: params as Record<string, unknown>, serviceId: UsersService.GetUsers }),

  getById: (id: string): Promise<ApiResponse<UserResponse>> =>
    apiClient.get(`/users/${id}`, { serviceId: UsersService.GetUserById }),

  create: (data: CreateUserRequest): Promise<ApiResponse<UserResponse>> =>
    apiClient.post('/users', data, { serviceId: UsersService.PostCreateUser }),

  update: (id: string, data: UpdateUserRequest): Promise<ApiResponse<UserResponse>> =>
    apiClient.put(`/users/${id}`, data, { serviceId: UsersService.PutUpdateUser }),

  remove: (id: string): Promise<ApiResponse<void>> =>
    apiClient.delete(`/users/${id}`, { serviceId: UsersService.DeleteUser }),
};
```

### Step 3 — Crear hooks de @tanstack/react-query

Un archivo por hook en `src/features/users/hooks/`. Las query keys siguen el patrón `['users', ...]` para invalidación granular.

```typescript
// use-users-list.query.ts
import { useQuery } from '@tanstack/react-query';
import { UsersApi } from '../api/users.api';
import type { UsersQueryParams } from '../models';

export function useUsersList(params: UsersQueryParams) {
  return useQuery({
    queryKey: ['users', 'list', params],
    queryFn: () => UsersApi.list(params),
  });
}
```

```typescript
// use-user-detail.query.ts
import { useQuery } from '@tanstack/react-query';
import { UsersApi } from '../api/users.api';

export function useUserDetail(id: string | undefined) {
  return useQuery({
    queryKey: ['users', 'detail', id],
    queryFn: () => UsersApi.getById(id!),
    enabled: Boolean(id),
  });
}
```

```typescript
// use-create-user.mutation.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { UsersApi } from '../api/users.api';
import type { CreateUserRequest } from '../models';

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateUserRequest) => UsersApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', 'list'] });
    },
  });
}
```

```typescript
// use-update-user.mutation.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { UsersApi } from '../api/users.api';
import type { UpdateUserRequest } from '../models';

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateUserRequest }) => UsersApi.update(id, data),
    onSuccess: (_result, variables) => {
      queryClient.invalidateQueries({ queryKey: ['users', 'list'] });
      queryClient.invalidateQueries({ queryKey: ['users', 'detail', variables.id] });
    },
  });
}
```

```typescript
// use-delete-user.mutation.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { UsersApi } from '../api/users.api';

export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => UsersApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', 'list'] });
    },
  });
}
```

### Step 4 — Componente base (UsersList)

Componente de lista con estados loading/error/empty, paginación y acciones por fila. Vive en `src/features/users/components/UsersList.tsx`.

```tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useUsersList } from '../hooks/use-users-list.query';
import { useDeleteUser } from '../hooks/use-delete-user.mutation';
import { Spinner } from '../../../shared/components/Spinner';
import { ErrorBanner } from '../../../shared/components/ErrorBanner';
import { EmptyState } from '../../../shared/components/EmptyState';
import { Pagination } from '../../../shared/components/Pagination';

export function UsersList() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [page, setPage] = useState(1);

  const query = useUsersList({ page, pageSize: 20 });
  const deleteMutation = useDeleteUser();

  const items = query.data?.data?.items ?? [];
  const totalPages = query.data?.data?.totalPages ?? 0;

  const navigateToCreate = () => navigate('/users/new');
  const navigateToEdit = (id: string) => navigate(`/users/${id}/edit`);
  const handleDelete = (id: string) => {
    if (!window.confirm(t('list.confirmDelete'))) return;
    deleteMutation.mutate(id);
  };

  return (
    <section aria-labelledby="users-title">
      <header>
        <h1 id="users-title">{t('list.title')}</h1>
        <button onClick={navigateToCreate}>{t('list.createCta')}</button>
      </header>

      {query.isLoading ? (
        <Spinner label={t('list.loading')} />
      ) : query.isError ? (
        <ErrorBanner title={t('list.errorTitle')} message={query.error?.message ?? ''} onRetry={() => query.refetch()} />
      ) : items.length === 0 ? (
        <EmptyState title={t('list.emptyTitle')} description={t('list.emptyDescription')}>
          <button onClick={navigateToCreate}>{t('list.createCta')}</button>
        </EmptyState>
      ) : (
        <>
          <table>
            <thead>
              <tr>
                <th>{t('list.columns.name')}</th>
                <th>{t('list.columns.email')}</th>
                <th>{t('list.columns.role')}</th>
                <th>{t('list.columns.status')}</th>
                <th>{t('list.columns.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {items.map((user) => (
                <tr key={user.id}>
                  <td>{user.firstName} {user.lastName}</td>
                  <td>{user.email}</td>
                  <td>{user.roleName}</td>
                  <td>{t(`status.${user.status}`)}</td>
                  <td>
                    <button onClick={() => navigateToEdit(user.id)}>{t('list.actions.edit')}</button>
                    <button disabled={deleteMutation.isPending} onClick={() => handleDelete(user.id)}>
                      {t('list.actions.delete')}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />
        </>
      )}
    </section>
  );
}
```

### Step 5 — Form component (UsersForm)

Formulario reutilizable para crear/editar con validación cliente (`react-hook-form` + `zod`), manejo de errores del servidor y submit tipado.

```tsx
import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useTranslation } from 'react-i18next';
import { UserStatus } from '../models';
import type { CreateUserRequest, UserResponse } from '../models';

const userFormSchema = (mode: 'create' | 'edit') =>
  z.object({
    firstName: z.string().min(1).max(50),
    lastName: z.string().min(1).max(50),
    email: z.string().email(),
    password: mode === 'create' ? z.string().min(8) : z.string().optional(),
    roleId: z.coerce.number().min(1),
    status: z.nativeEnum(UserStatus).default(UserStatus.Active),
  });

type UserFormValues = z.infer<ReturnType<typeof userFormSchema>>;

interface UsersFormProps {
  initialValues?: UserResponse;
  mode?: 'create' | 'edit';
  isSubmitting?: boolean;
  serverError?: string | null;
  onSubmitForm: (values: CreateUserRequest) => void;
}

export function UsersForm({ initialValues, mode = 'create', isSubmitting = false, serverError = null, onSubmitForm }: UsersFormProps) {
  const { t } = useTranslation();
  const { register, handleSubmit, reset, formState: { errors } } = useForm<UserFormValues>({
    resolver: zodResolver(userFormSchema(mode)),
    defaultValues: { status: UserStatus.Active },
  });

  useEffect(() => {
    if (initialValues) {
      reset({
        firstName: initialValues.firstName,
        lastName: initialValues.lastName,
        email: initialValues.email,
        roleId: initialValues.roleId,
        status: initialValues.status,
      });
    }
  }, [initialValues, reset]);

  return (
    <form onSubmit={handleSubmit((values) => onSubmitForm(values as CreateUserRequest))} noValidate>
      {serverError && <div role="alert" className="error-banner">{serverError}</div>}

      <label>
        {t('form.firstName')}
        <input {...register('firstName')} aria-invalid={!!errors.firstName} />
        {errors.firstName && <span className="field-error">{t('validation.required')}</span>}
      </label>

      <label>
        {t('form.lastName')}
        <input {...register('lastName')} aria-invalid={!!errors.lastName} />
        {errors.lastName && <span className="field-error">{t('validation.required')}</span>}
      </label>

      <label>
        {t('form.email')}
        <input type="email" {...register('email')} aria-invalid={!!errors.email} />
        {errors.email && <span className="field-error">{t('validation.email')}</span>}
      </label>

      {mode === 'create' && (
        <label>
          {t('form.password')}
          <input type="password" {...register('password')} aria-invalid={!!errors.password} />
          {errors.password && <span className="field-error">{t('validation.passwordMin')}</span>}
        </label>
      )}

      <label>
        {t('form.roleId')}
        <input type="number" {...register('roleId')} aria-invalid={!!errors.roleId} />
      </label>

      {mode === 'edit' && (
        <label>
          {t('form.status')}
          <select {...register('status')}>
            {Object.values(UserStatus).map((s) => (
              <option key={s} value={s}>{t(`status.${s}`)}</option>
            ))}
          </select>
        </label>
      )}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? t('form.submitting') : t(`form.submit.${mode}`)}
      </button>
    </form>
  );
}
```

### Step 6 — i18n integration

Las claves se agrupan por namespace por feature en `src/assets/i18n/{lang}/users.json`. Esto permite lazy loading por módulo con `react-i18next` + `i18next-http-backend`.

```json
{
  "list": {
    "title": "Usuarios",
    "loading": "Cargando usuarios...",
    "errorTitle": "No se pudieron cargar los usuarios",
    "emptyTitle": "No hay usuarios todavía",
    "emptyDescription": "Crea el primer usuario para empezar.",
    "createCta": "Nuevo usuario",
    "confirmDelete": "¿Eliminar este usuario? Esta acción no se puede deshacer.",
    "columns": {
      "name": "Nombre",
      "email": "Correo",
      "role": "Rol",
      "status": "Estado",
      "actions": "Acciones"
    },
    "actions": { "edit": "Editar", "delete": "Eliminar" }
  },
  "form": {
    "firstName": "Nombre",
    "lastName": "Apellido",
    "email": "Correo electrónico",
    "password": "Contraseña",
    "roleId": "Rol",
    "status": "Estado",
    "submitting": "Guardando...",
    "submit": { "create": "Crear usuario", "edit": "Guardar cambios" }
  },
  "status": { "ACTIVE": "Activo", "INACTIVE": "Inactivo", "SUSPENDED": "Suspendido" },
  "validation": {
    "required": "Este campo es obligatorio",
    "email": "Correo inválido",
    "maxLength": "Máximo de caracteres excedido",
    "passwordMin": "Mínimo 8 caracteres"
  }
}
```

Uso en componentes (ya mostrado arriba con `t('key')`). El namespace `users` se registra en la configuración de `i18next` con `i18next-http-backend` y se carga bajo demanda al entrar a la ruta `/users`.

```typescript
// Configuración en src/core/i18n/i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpBackend from 'i18next-http-backend';

i18n
  .use(HttpBackend)
  .use(initReactI18next)
  .init({
    lng: 'es',
    fallbackLng: 'es',
    ns: ['common'],
    backend: { loadPath: '/assets/i18n/{{lng}}/{{ns}}.json' },
  });

export default i18n;
```

## Service IDs y constantes

### Patrón

Cada endpoint del módulo recibe un identificador numérico único (Service ID) que se propaga del frontend al backend en el header `X-Service-Id`. Sirve para:

- Trazabilidad end-to-end en logs y traces distribuidos.
- Autorización por servicio (permisos granulares por endpoint, no por rol).
- Métricas y rate limiting por servicio en el API Gateway.
- Auditoría: cada request queda registrado con su Service ID en la tabla de logs.

La numeración es por módulo, con rangos asignados en el spec (`api-first-spec`):

| Rango | Módulo |
|-------|--------|
| 1000–1099 | users |
| 1100–1199 | roles |
| 1200–1299 | permissions |
| 2000–2099 | orders |

Dentro del rango, la convención es:

| Sufijo | Operación |
|--------|-----------|
| `x00` | List / Search |
| `x01` | GetById |
| `x02` | Create |
| `x03` | Update |
| `x04` | Delete |
| `x10+` | Operaciones de estado (Activate, Suspend, Approve...) |

### Ubicación de las constantes

Estructura recomendada:

```
src/
├── core/
│   ├── api/
│   │   └── api-client.ts            # apiClient (fetch wrapper)
│   └── types/
│       └── api.ts                   # ApiResponse, ApiError
├── shared/
│   └── components/                  # Componentes reutilizables
└── features/
    └── users/
        ├── api/
        │   └── users.api.ts         # UsersApi (typed HTTP calls)
        ├── hooks/
        │   ├── use-users-list.query.ts
        │   ├── use-create-user.mutation.ts
        │   └── use-users.ts         # Orchestrator hook
        ├── components/
        │   ├── UsersList.tsx
        │   └── UsersForm.tsx
        ├── models/
        │   ├── constants.ts         # UsersService (Service IDs del módulo)
        │   ├── index.ts             # Re-exports
        │   └── users.types.ts       # Interfaces del módulo
        └── users.routes.tsx         # react-router-dom route config
```

`src/features/users/models/constants.ts`:

```typescript
export const UsersService = {
  GetUsers: 1001,
  GetUserById: 1002,
  PostCreateUser: 1003,
  PutUpdateUser: 1004,
  DeleteUser: 1005,
  PostActivateUser: 1010,
  PostSuspendUser: 1011,
} as const;
export type UsersServiceId = (typeof UsersService)[keyof typeof UsersService];

export const UsersRoutes = {
  List: '/users',
  Detail: (id: string) => `/users/${id}`,
  New: '/users/new',
  Edit: (id: string) => `/users/${id}/edit`,
} as const;
```

### Importación en hooks y componentes

```typescript
import { UsersService, UsersRoutes } from '../models/constants';

// En un hook/API call
UsersApi.list({ serviceId: UsersService.GetUsers });

// En un componente
navigate(UsersRoutes.Edit(user.id));
```

Nunca hardcodear strings de rutas ni números de Service ID dentro de componentes; siempre importar desde `constants.ts`.

### Relación entre Service IDs y route paths

El catálogo entregado por `api-first-spec` mantiene la correspondencia 1:1:

| Service ID | HTTP Method | API Path | Frontend Route | Componente |
|------------|-------------|----------|----------------|------------|
| 1001 | GET | `/api/users` | `/users` | `UsersList` |
| 1002 | GET | `/api/users/{id}` | `/users/:id` | `UserDetail` |
| 1003 | POST | `/api/users` | `/users/new` | `UsersForm` (create) |
| 1004 | PUT | `/api/users/{id}` | `/users/:id/edit` | `UsersForm` (edit) |
| 1005 | DELETE | `/api/users/{id}` | (acción inline) | `UsersList` |
| 1010 | POST | `/api/users/{id}/activate` | (acción inline) | `UserDetail` |
| 1011 | POST | `/api/users/{id}/suspend` | (acción inline) | `UserDetail` |

Esta tabla se valida automáticamente en CI con el script `scripts/validate-service-ids.ts`, que cruza `openapi.yaml` contra los archivos `constants.ts` de todos los features y falla el build si hay desalineación.
