---
name: typescript
description: 'TypeScript strict patterns and best practices for frontend projects.
  Trigger: When implementing or refactoring TypeScript in .ts files.'
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - frontend
  enforcement: mandatory
  depends_on:
  - openapi-docs
  consumed_by:
  - angular
  - angular-services
  - api-first-frontend
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: skill-contract
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Use `const` object + extract type, not direct union | ALWAYS | Single source of truth |
| Use flat interfaces (one level deep) | ALWAYS | Avoid deeply nested types |
| Never use `any` | NEVER | Type safety |
| Use `Type | null` not `Type?` for nullable API fields | ALWAYS | API returns null, not undefined |
| Use `import type` for type-only imports | ALWAYS | Build optimization |

## Const Types Pattern (REQUIRED)
```typescript
// ALWAYS: const object first, then extract type
const STATUS = { ACTIVE: "active", INACTIVE: "inactive" } as const;
type Status = (typeof STATUS)[keyof typeof STATUS];

// NEVER: Direct union types
type Status = "active" | "inactive";
```

## Flat Interfaces (REQUIRED)
```typescript
// One level deep — nested objects get their own interface
interface UserDetail {
  userId: number;
  name: string;
  status: StatusItem;        // nested → own interface
  address: AddressDetail;    // nested → own interface
}

// NEVER inline nested objects
interface UserDetail {
  status: { id: number; name: string; };  // wrong!
}
```

## Never Use `any`
```typescript
// Use unknown for truly unknown types
function parse(input: unknown): User { ... }

// Use generics for flexible types
function wrap<T>(value: T): Response<T> { ... }

// NEVER
const data: any = fetchData();
```

## Utility Types to Prefer
| Utility | Usage |
|---------|-------|
| `Pick<T, K>` | Extract subset of properties |
| `Omit<T, K>` | Exclude properties |
| `Partial<T>` | Make all properties optional |
| `Required<T>` | Make all properties required |
| `Readonly<T>` | Immutable type |
| `Record<K, V>` | Dictionary / map type |
| `ReturnType<F>` | Extract return type |
| `Parameters<F>` | Extract parameter types |

## Type Guards
```typescript
function isUser(value: unknown): value is User {
  return typeof value === 'object' && value !== null && 'userId' in value;
}
```

## Standard API Response Type
```typescript
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string | null;
  errors: Array<{
    code: string | null;
    field: string | null;
    message: string | null;
  }> | null;
  pagination: {
    page: number;
    pageSize: number;
    totalRecords: number;
    totalPages: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
  metadata: Record<string, unknown> | null;
}
```

## Request Types (Mutation factory pattern)
```typescript
// Request types must extend Record<string, unknown> when using factory patterns
export interface CreateEntityRequest extends Record<string, unknown> {
  name: string;
  amount: number;
  statusId: number | null;
}
```

## Nullable Fields Convention
```typescript
// API fields that can be null:
export interface EntityDetail {
  entityId: number;
  name: string;        // always string
  email: string | null;  // nullable
  closedAt: string | null; // nullable date
}
// NOT: email?: string  — this is undefined, not null
```

## Module Declarations (env.d.ts for microfrontends)
```typescript
declare module 'host/factories' {
  export const createServiceQuery: (...args: unknown[]) => unknown;
  export const createServiceMutation: (...args: unknown[]) => unknown;
}
declare module 'host/toast' { ... }
declare module 'host/session' { ... }
```

## Enum Pattern (String Enums)
```typescript
// Use string enums for status values and catalogs
enum EntityStatus {
  Draft = 'DRAFT',
  Active = 'ACTIVE',
  Closed = 'CLOSED',
}
```

## Component Input Types
```typescript
// Use @Input() with explicit type for Angular component inputs
@Component({ ... })
export class EntityDetailComponent {
  @Input({ required: true }) entityId!: number;
  @Input({ required: true }) onClose!: () => void;
  @Input() data: EntityDetail | null = null;
}
```

## Patrones modernos de TypeScript (4.9+)

### 1. Operador `satisfies` — Objetos de configuración con seguridad de tipo sin widening

`satisfies` valida que un valor cumple un tipo sin modificar el tipo inferido. Esto preserva tipos literales y evita el widening que causa `as T` o `: T`.

```typescript
interface RouteConfig {
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  public: boolean;
}

// ❌ SIN satisfies: el tipo se widen a string, perdemos literales
const routes: Record<string, RouteConfig> = {
  getUsers: { path: '/users', method: 'GET', public: true },
  createUser: { path: '/users', method: 'POST', public: false },
};
// routes.getUsers.method → string (perdimos 'GET' | 'POST')

// ✅ CON satisfies: validación + tipos literales preservados
const routes = {
  getUsers: { path: '/users', method: 'GET', public: true },
  createUser: { path: '/users', method: 'POST', public: false },
} satisfies Record<string, RouteConfig>;
// routes.getUsers.method → 'GET' (literal preservado)
// routes.createUser.method → 'POST' (literal preservado)

// Caso práctico: configuración de features por módulo
const featureConfig = {
  dashboard: { enabled: true, requiredRole: 'admin' as const },
  reports: { enabled: false, requiredRole: 'viewer' as const },
} satisfies Record<string, { enabled: boolean; requiredRole: string }>;
// featureConfig.dashboard.requiredRole → 'admin' (literal, no string)
```

### 2. Template Literal Types — Patrones de string tipados

Los template literal types permiten crear tipos a partir de combinaciones de strings literales, ideal para keys compuestas, rutas, eventos y convenciones de naming.

```typescript
// Prefijos de eventos por dominio
type Domain = 'user' | 'order' | 'product';
type EventAction = 'created' | 'updated' | 'deleted';
type DomainEvent = `${Domain}.${EventAction}`;
// 'user.created' | 'user.updated' | 'user.deleted' | 'order.created' | ...

// Uso en un bus de eventos tipado
type EventHandler<T extends DomainEvent> = (payload: EventPayload<T>) => void;

function subscribe<T extends DomainEvent>(event: T, handler: EventHandler<T>): void {
  // ...
}

subscribe('user.created', handler);      // ✅
subscribe('user.invalid', handler);       // ❌ Error de tipo

// Cambio de casing: camelCase → snake_case para nombres de columna
type CamelToSnake<S extends string> =
  S extends `${infer Head}${infer Tail}`
    ? Head extends Lowercase<Head>
      ? `${Head}${CamelToSnake<Tail>}`
      : `_${Lowercase<Head>}${CamelToSnake<Tail>}`
    : S;

type ColumnName = CamelToSnake<'userId'>;       // 'user_id'
type TableName = CamelToSnake<'createdAt'>;      // 'created_at'

// Permisos como combinación de acción + recurso
type Action = 'read' | 'write' | 'delete';
type Resource = 'users' | 'orders' | 'products';
type Permission = `${Action}:${Resource}`;
// 'read:users' | 'write:users' | 'delete:users' | 'read:orders' | ...
```

### 3. `Awaited<>` — Desenvolver tipos Promise anidados

`Awaited<>` extrae el tipo interior de un `Promise`, incluyendo promesas anidadas. Útil para inferir el retorno de funciones async sin duplicar la definición del tipo.

```typescript
// Function auxiliar para obtener tipo de retorno de artilugios async
type AsyncResult<T extends (...args: unknown[]) => Promise<unknown>> =
  Awaited<ReturnType<T>>;

// Ejemplo: servicio de API
async function fetchUsers(): Promise<ApiResponse<UserDetail[]>> { /* ... */ }
async function fetchOrders(): Promise<ApiResponse<OrderDetail[]>> { /* ... */ }

type UsersResult = AsyncResult<typeof fetchUsers>;
// → ApiResponse<UserDetail[]> (no Promise<ApiResponse<UserDetail[]>>)

// Uso en servicios Angular con signals: inferir el tipo de data sin repetirlo
function createQueryStore<T extends (...args: unknown[]) => Promise<unknown>>(
  queryFn: T,
) {
  // signal() con el tipo desenvuelto por Awaited, sin Promise wrapper
  const data = signal<Awaited<ReturnType<T>> | null>(null);
  const loading = signal(false);

  async function load(...args: Parameters<T>): Promise<void> {
    loading.set(true);
    try {
      const result = await queryFn(...(args as unknown[]));
      data.set(result as Awaited<ReturnType<T>>);
    } finally {
      loading.set(false);
    }
  }

  return { data: data.asReadonly(), loading: loading.asReadonly(), load };
}

// Promesas anidadas: Awaited las desenvuelve todas
type Nested = Awaited<Promise<Promise<string>>>;
// → string (no Promise<string>)
```

### 4. `as const` objects vs enums — Por qué muchos equipos prefieren const objects

Los `as const` objects ofrecen las mismas garantías que los enums, con ventajas: son tree-shakeables, no generan código JS adicional, y evitan los problemas de enums numéricos y reverse mappings.

```typescript
// ❌ Enum: genera código JS + reverse mapping para numéricos
enum HttpStatus {
  Ok = 200,
  NotFound = 404,
  ServerError = 500,
}
// Genera objeto en JS con { 200: 'Ok', 404: 'NotFound', ... }

// ❌ Enum con string: mejor, pero aún genera IIFE en JS
enum Status {
  Active = 'ACTIVE',
  Inactive = 'INACTIVE',
}

// ✅ Const object: zero runtime overhead, tree-shakeable, inferred types
const HTTP_STATUS = {
  Ok: 200,
  NotFound: 404,
  ServerError: 500,
} as const;

type HttpStatus = (typeof HTTP_STATUS)[keyof typeof HTTP_STATUS];
// 200 | 404 | 500

type HttpStatusKey = keyof typeof HTTP_STATUS;
// 'Ok' | 'NotFound' | 'ServerError'

// Iteración directa (no posible con enums sin Object.keys hack)
Object.entries(HTTP_STATUS).forEach(([key, value]) => {
  console.log(`${key}: ${value}`);
});

// Combinación con satisfies para validación adicional
const ROLE_PERMISSIONS = {
  viewer: { canRead: true, canWrite: false },
  editor: { canRead: true, canWrite: true },
  admin: { canRead: true, canWrite: true },
} satisfies Record<string, { canRead: boolean; canWrite: boolean }>;

type Role = keyof typeof ROLE_PERMISSIONS;
// 'viewer' | 'editor' | 'admin'
```

**Cuándo sí usar enums**: cuando el dominio requiere un namespace agrupado explícito (ej: codes de error de un protocolo externo) y el backend ya los define como enum.

### 5. Zod para validación en runtime — Integración con TypeScript e inferencia de schemas

Zod permite definir schemas que validan datos en runtime y al mismo tiempo producen tipos TypeScript, eliminando la fuente única de verdad duplicada.

```typescript
import { z } from 'zod';

// Definir schema = definición + validación + tipo, todo en uno
const UserSchema = z.object({
  userId: z.number().int().positive(),
  name: z.string().min(1).max(200),
  email: z.string().email(),
  role: z.enum(['viewer', 'editor', 'admin']),
  statusId: z.number().int().nullable(),
  createdAt: z.string().datetime().optional(),
});

// Inferir tipo TypeScript desde el schema (sin duplicar definición)
type UserDetail = z.infer<typeof UserSchema>;
// {
//   userId: number;
//   name: string;
//   email: string;
//   role: 'viewer' | 'editor' | 'admin';
//   statusId: number | null;
//   createdAt?: string;
// }

// Validación en boundaries (API response, form input, localStorage)
function handleApiResponse(raw: unknown): UserDetail {
  return UserSchema.parse(raw); // throw ZodError si no cumple
}

function safeParse(raw: unknown): UserDetail | null {
  const result = UserSchema.safeParse(raw);
  if (!result.success) {
    console.error('Validation failed:', result.error.flatten());
    return null;
  }
  return result.data;
}

// Composición: reutilizar schemas parciales
const CreateUserSchema = UserSchema.omit({ userId: true, createdAt: true });
type CreateUserRequest = z.infer<typeof CreateUserSchema>;

const UpdateUserSchema = UserSchema.partial().omit({ userId: true });
type UpdateUserRequest = z.infer<typeof UpdateUserSchema>;

// Discriminated union con Zod
const ApiResponseSchema = z.discriminatedUnion('success', [
  z.object({ success: z.literal(true), data: UserSchema }),
  z.object({ success: z.literal(false), error: z.string() }),
]);
type ApiResponse = z.infer<typeof ApiResponseSchema>;

// Integración con formularios Angular
const LoginFormSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(8, 'Mínimo 8 caracteres'),
});
type LoginForm = z.infer<typeof LoginFormSchema>;
```

### 6. Discriminated Unions para máquinas de estado

Las discriminated unions modelan estados mutuamente excluyentes con type-safe narrowing, ideal para flujos de UI (loading/success/error), workflows y state machines.

```typescript
// Estado de una solicitud con discriminated union
type RequestState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: string; retryCount: number };

// Type narrowing automático por la propiedad discriminante
function renderState<T>(state: RequestState<T>): string {
  switch (state.status) {
    case 'idle':
      return 'Sin iniciar';
    case 'loading':
      return 'Cargando...';
    case 'success':
      return `Datos: ${JSON.stringify(state.data)}`; // TS sabe que data existe
    case 'error':
      return `Error: ${state.error} (intento ${state.retryCount})`;
  }
}

// State machine para un proceso de aprobación
type ApprovalStep =
  | { step: 'draft'; editable: true }
  | { step: 'pending_review'; reviewerId: number; submittedAt: string }
  | { step: 'approved'; approvedBy: number; approvedAt: string }
  | { step: 'rejected'; rejectedBy: number; reason: string };

function canEdit(step: ApprovalStep): boolean {
  return step.step === 'draft' && step.editable; // TS infiere .editable solo en 'draft'
}

// Transiciones válidas tipadas
type TransitionMap = {
  draft: 'pending_review';
  pending_review: 'approved' | 'rejected';
  approved: never;
  rejected: 'draft'; // puede reenviar
};

function transition<S extends ApprovalStep['step']>(
  current: S,
): TransitionMap[S] {
  const map: TransitionMap = {
    draft: 'pending_review',
    pending_review: 'approved',
    approved: never,
    rejected: 'draft',
  };
  return map[current] as TransitionMap[S];
}

// Uso en Angular: estado de carga con signals
type QueryState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T; timestamp: number }
  | { status: 'error'; message: string; code: number };

function createTypedSignal<T>() {
  const state = signal<QueryState<T>>({ status: 'idle' });
  // state.set({ status: 'success', data: result, timestamp: Date.now() })
  // TS obliga a incluir data y timestamp cuando status es 'success'
  return state;
}
```
