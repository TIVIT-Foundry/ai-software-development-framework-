---
name: project-architecture
description: 'Application architecture patterns: Vertical Slice, Modular Monolith,
  Microservices. Covers Python/FastAPI, Bun (TypeScript) backend and Angular frontend
  conventions, naming, and response shapes. Trigger: When designing project architecture
  or onboarding a new project structure.'
version: 1.1
metadata:
  phase:
  - inception
  layer:
  - backend
  - frontend
  enforcement: mandatory
  depends_on:
  - repo-structure
  consumed_by:
  - backend-api
  - angular
  - agent-backend
  - agent-frontend
  - agent-fullstack
  agent_roles:
  - design-agent
  - orchestrator-agent
  validation_profile: architecture-consistency
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Choose ONE architecture style per service | ALWAYS | Avoid mixed concerns |
| Document architecture decisions in ARCHITECTURE.md | ALWAYS | Team alignment |
| Use consistent module naming across layers | ALWAYS | Discoverability |
| Use standardized ApiResponse wrapper | ALWAYS | API consistency |
| Don't mix Modular Monolith and Microservices without clear boundaries | NEVER | Operational complexity |

## Architecture Styles

| Style | Best For | When NOT to use |
|-------|----------|-----------------|
| Modular Monolith | Small–medium teams, single deployment | When you need independent scaling |
| Vertical Slice | Feature-centric apps, CQRS workflows | Heavily shared domain logic |
| Microservices | Large teams, independent scaling/deployment | Early-stage MVPs |
| Monolith | Quick POC, single developer | Production at scale |

## Vertical Slice Structure (Recommended)
Each feature (slice) is self-contained. Example for a Bun (TypeScript) backend:
```
{Project}/
├── src/
│   ├── features/
│   │   └── {entity}/
│   │       ├── create/
│   │       │   ├── create-{entity}.controller.ts   # Route handler / endpoint
│   │       │   ├── create-{entity}.service.ts      # Use case / business logic
│   │       │   ├── create-{entity}.schema.ts       # Zod / Valibot validation
│   │       │   └── create-{entity}.dto.ts          # Request/Response types
│   │       ├── update/
│   │       ├── delete/
│   │       ├── get-by-id/
│   │       └── list/
│   ├── shared/
│   │   ├── infrastructure/  (db clients, http clients)
│   │   ├── middleware/
│   │   └── extensions/
│   └── index.ts                                  # App entrypoint (Elysia/Hono)
└── tests/
```

## Modular Monolith Structure
```
{Solution}/
├── src/
│   ├── {Module1}/
│   │   ├── API/           (Controllers or Endpoints)
│   │   ├── Application/   (Use cases, Handlers)
│   │   ├── Domain/        (Entities, Value Objects)
│   │   └── Infrastructure/(Data access, External calls)
│   ├── {Module2}/
│   └── Shared/
└── tests/
```

## Microservices Naming

| Type | Pattern | Example |
|------|---------|---------|
| API Service | `{Domain}-api` | `orders-api` |
| Worker/Consumer | `{Domain}-worker` | `orders-worker` |
| Gateway | `{Project}-gateway` | `ecommerce-gateway` |
| BFF | `{Client}-bff` | `mobile-bff` |

## URL Patterns

| Method | URL | Usage |
|--------|-----|-------|
| GET | `/api/{module}/{entity}s` | List |
| GET | `/api/{module}/{entity}s/{id}` | Get by ID |
| POST | `/api/{module}/{entity}s` | Create |
| PUT | `/api/{module}/{entity}s/{id}` | Update |
| DELETE | `/api/{module}/{entity}s/{id}` | Delete |
| GET | `/api/{module}/{entity}s/export` | Export |
| POST | `/api/{module}/{entity}s/search` | Complex search |

## Standard API Response Shape
```json
{
  "success": true,
  "data": { ... },
  "message": null,
  "errors": null,
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalRecords": 150,
    "totalPages": 8,
    "hasNext": true,
    "hasPrevious": false
  },
  "metadata": null
}
```

## Error Response Shape
```json
{
  "success": false,
  "data": null,
  "message": "Validation failed",
  "errors": [
    { "code": "VAL_001", "field": "Name", "message": "Name is required" }
  ],
  "pagination": null,
  "metadata": null
}
```

## Module Naming Conventions

### Backend (Bun / TypeScript)

| Element | Convention | Example |
|---------|------------|---------|
| Module | kebab-case folder, PascalCase type | `orders/`, `OrdersModule` |
| Feature folder | kebab-case verb | `create-order/`, `list-orders/` |
| Controller / Handler | `{action}-{entity}.controller.ts` | `create-order.controller.ts` |
| Service | `{entity}.service.ts` | `order.service.ts` |
| Schema (validation) | `{action}-{entity}.schema.ts` | `create-order.schema.ts` |
| DTO / Types | `{action}-{entity}.dto.ts` | `create-order.dto.ts` |
| Repository | `{entity}.repository.ts` | `order.repository.ts` |
| Route registration | `{entity}.routes.ts` | `order.routes.ts` |

### Backend (Python / FastAPI)

| Element | Convention | Example |
|---------|------------|---------|
| Module | snake_case folder | `orders/` |
| Router | `router.py` | `presentation/router.py` |
| Service | `{entity}_service.py` | `order_service.py` |
| Schema (Pydantic) | `schemas.py` | `presentation/schemas.py` |
| Repository | `repository.py` | `infrastructure/database/repository.py` |

### Frontend (Angular)

| Element | Convention | Example |
|---------|------------|---------|
| Feature module folder | kebab-case | `orders/`, `order-detail/` |
| Standalone component | `{name}.component.ts` | `order-list.component.ts` |
| Service | `{name}.service.ts` | `order.service.ts` |
| Route file | `{feature}.routes.ts` | `orders.routes.ts` |
| Guard | `{name}.guard.ts` | `auth.guard.ts` |
| Directive | `{name}.directive.ts` | `highlight.directive.ts` |
| Pipe | `{name}.pipe.ts` | `order-status.pipe.ts` |
| Model / Interface | `{name}.model.ts` | `order.model.ts` |

## Angular Frontend Architecture

Angular 17+ con **standalone components**, **signals** y **lazy loading** por ruta. Cada feature es un módulo autocontenido con sus propias rutas, componentes, servicios y modelos.

```
src/
├── app/
│   ├── core/                              # Singleton: layout, guards, interceptors, error handlers
│   │   ├── layout/
│   │   │   ├── shell.component.ts         # Main layout (header + router-outlet + footer)
│   │   │   └── shell.routes.ts
│   │   ├── guards/
│   │   │   └── auth.guard.ts
│   │   ├── interceptors/
│   │   │   ├── auth.interceptor.ts        # Attach JWT
│   │   │   ├── error.interceptor.ts       # Global error mapping
│   │   │   └── loading.interceptor.ts
│   │   └── services/
│   │       └── notification.service.ts
│   │
│   ├── features/                          # Vertical slices by domain
│   │   └── orders/
│   │       ├── orders.routes.ts           # loadChildren → standalone routes
│   │       ├── orders-list/
│   │       │   ├── orders-list.component.ts
│   │       │   ├── orders-list.component.html
│   │       │   └── orders-list.component.css
│   │       ├── order-detail/
│   │       │   └── order-detail.component.ts
│   │       ├── order-form/
│   │       │   └── order-form.component.ts
│   │       ├── services/
│   │       │   └── orders.service.ts      # @Injectable({ providedIn: 'root' })
│   │       └── models/
│   │           └── order.model.ts
│   │
│   ├── shared/                            # Reusable: dumb components, pipes, directives
│   │   ├── components/
│   │   │   ├── data-table/
│   │   │   ├── confirm-dialog/
│   │   │   └── loading-spinner/
│   │   ├── directives/
│   │   └── pipes/
│   │
│   ├── app.component.ts                   # Root standalone component
│   ├── app.config.ts                      # provideRouter, provideHttpClient, provideAnimations
│   └── app.routes.ts                      # Top-level routes with lazy loading
│
├── assets/
├── environments/
│   ├── environment.ts
│   └── environment.prod.ts
├── main.ts                                # bootstrapApplication(AppComponent, appConfig)
└── styles.css                             # Global styles + design tokens
```

**Convenciones Angular:**

| Convención | Regla |
|------------|-------|
| Standalone components | Todos los componentes son `standalone: true` (sin NgModules) |
| Signals | Estado reactivo con `signal()`, `computed()`, `effect()` |
| Lazy loading | `loadChildren: () => import('./features/orders/orders.routes')` |
| DI | `@Injectable({ providedIn: 'root' })` para servicios singleton |
| HTTP | `provideHttpClient(withInterceptors([...]))` en `app.config.ts` |
| Routing | Un archivo `{feature}.routes.ts` por feature con `Routes[]` |
| Change detection | `OnPush` por defecto en componentes standalone |
| Data fetching | `@ngneat/query` (TanStack Query) o signals + `toSignal()` |

**Ejemplo de lazy route (app.routes.ts):**
```typescript
export const routes: Routes = [
  { path: '', component: ShellComponent, children: [
    { path: 'orders', loadChildren: () => import('./features/orders/orders.routes').then(m => m.ORDERS_ROUTES) },
    { path: 'billing', loadChildren: () => import('./features/billing/billing.routes').then(m => m.BILLING_ROUTES) },
  ]},
  { path: 'login', loadComponent: () => import('./features/auth/login.component').then(m => m.LoginComponent) },
];
```

## Bun (TypeScript) Backend Architecture

Backend con **Bun** como runtime y **Elysia** (o **Hono**) como framework. Estructura modular con separación presentation / application / infrastructure.

```
src/
├── app/
│   ├── index.ts                           # Elysia/Hono app instance + plugin registration
│   ├── config/
│   │   ├── env.ts                         # Typed env vars (Zod / t.process.env)
│   │   ├── database.ts                    # Drizzle / Kysely client (PostgreSQL)
│   │   └── redis.ts                       # ioredis client
│   │
│   ├── common/
│   │   ├── dto/
│   │   │   ├── api-response.ts            # ApiResponse<T> envelope
│   │   │   └── pagination.ts              # PagedResponse<T>, PageParams
│   │   ├── exceptions/
│   │   │   ├── business-error.ts          # BusinessException class
│   │   │   └── error-catalog.ts           # Error code catalog
│   │   ├── middleware/
│   │   │   ├── correlation-id.ts          # Correlation ID plugin
│   │   │   ├── request-logging.ts         # Structured logging
│   │   │   ├── error-handler.ts           # Global onError handler
│   │   │   └── auth.ts                    # JWT verification plugin
│   │   └── utils/
│   │       └── pagination.ts
│   │
│   ├── modules/                           # Feature modules (self-contained)
│   │   └── orders/
│   │       ├── infrastructure/
│   │       │   ├── database/
│   │       │   │   ├── schema.ts          # Drizzle table definitions
│   │       │   │   └── order.repository.ts
│   │       │   └── external/
│   │       │       └── payment-gateway.ts # External HTTP client (Bun.fetch)
│   │       │
│   │       ├── domain/
│   │       │   ├── order.model.ts         # Domain entity (type / class)
│   │       │   ├── value-objects.ts       # Money, OrderStatus
│   │       │   └── events.ts              # Domain events
│   │       │
│   │       ├── application/
│   │       │   ├── order.repository.interface.ts  # Port (abstract)
│   │       │   ├── order.service.ts              # Business logic
│   │       │   └── order.validator.ts           # Zod schema validation
│   │       │
│   │       ├── presentation/
│   │       │   ├── order.routes.ts        # Elysia/Hono route registration
│   │       │   ├── order.controller.ts    # Request → service → response
│   │       │   └── order.dto.ts           # Request/Response types
│   │       │
│   │       └── tests/
│   │           ├── order.controller.test.ts
│   │           └── order.service.test.ts
│   │
│   └── shared/
│       ├── auth/
│       │   ├── jwt-handler.ts
│       │   └── auth-context.ts            # Derive current user from request
│       ├── cache/
│       │   └── cache.service.ts           # Redis wrapper
│       └── events/
│           └── event-bus.ts               # Redis pub/sub / Kafka producer
│
├── drizzle/                               # Database migrations (Drizzle Kit)
│   ├── 0001_create_orders.ts
│   └── meta/
│
├── tests/                                 # Global integration tests
│   └── api.test.ts
│
├── .env.example
├── package.json
├── tsconfig.json
├── Dockerfile
└── docker-compose.yml
```

**Convenciones Bun backend:**

| Convencia | Regla |
|-----------|-------|
| Runtime | Bun (no Node.js) |
| Framework | Elysia (preferido) o Hono |
| Validación | Zod o Valibot en `{entity}.validator.ts` |
| ORM | Drizzle ORM o Kysely (PostgreSQL, type-safe) |
| HTTP client | `Bun.fetch` nativo (no axios) |
| Tipado | TypeScript strict mode (`"strict": true`) |
| ESM | Solo ES Modules (`"type": "module"`) |
| Tests | `bun test` (Bun nativo) o Vitest |
| Env | `Bun.env` con validación Zod al startup |
| Response envelope | `ApiResponse<T>` en todas las rutas |

**Ejemplo de controller Elysia:**
```typescript
// presentation/order.controller.ts
import { Elysia, t } from 'elysia';
import { orderService } from '../application/order.service';
import { createOrderSchema } from '../application/order.validator';
import { ApiResponse } from '../../common/dto/api-response';

export const orderController = new Elysia()
  .post('/orders', async ({ body, set }) => {
    const dto = createOrderSchema.parse(body);
    const order = await orderService.create(dto);
    set.status = 201;
    return ApiResponse.ok(order);
  }, { body: t.Object({ /* ... */ }) })
  .get('/orders/:id', async ({ params }) => {
    const order = await orderService.getById(params.id);
    return ApiResponse.ok(order);
  });
```

## ARCHITECTURE.md Required Sections
1. Architecture style chosen and rationale
2. Module/service boundaries
3. Data flow diagram (ASCII or linked image)
4. Tech stack decisions
5. External dependencies / integrations
6. Open decisions (ADRs)

## Estructuras de proyecto por stack

Cada stack tiene una estructura de directorios canónica que refleja el estilo arquitectónico elegido. A continuación se presentan las cuatro variantes más comunes con árboles completos y descripción de cada directorio.

### Python FastAPI — Module-oriented con routers, services, repositories

```
src/
├── app/
│   ├── __init__.py
│   ├── main.py                                   # FastAPI application, lifespan, middleware
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py                           # Pydantic Settings (BaseSettings)
│   │   ├── database.py                           # SQLAlchemy async engine + session
│   │   └── redis.py                              # Redis client setup
│   │
│   ├── common/
│   │   ├── __init__.py
│   │   ├── dto/
│   │   │   ├── __init__.py
│   │   │   ├── api_response.py                   # Respuesta estándar genérica
│   │   │   └── pagination.py                     # PagedResponse, PageParams
│   │   ├── exceptions/
│   │   │   ├── __init__.py
│   │   │   ├── business_error.py                 # BusinessException base
│   │   │   └── error_catalog.py                  # Catálogo de errores (códigos)
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── correlation_id.py                 # Correlation ID middleware
│   │   │   ├── request_logging.py                # Logging estructurado
│   │   │   └── error_handler.py                  # Global exception handler
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── pagination.py                     # Pagination helper
│   │
│   ├── modules/                                  # Feature modules
│   │   └── orders/                               # Cada módulo es autocontenido
│   │       ├── __init__.py
│   │       │
│   │       ├── infrastructure/                   # Adaptadores de salida
│   │       │   ├── __init__.py
│   │       │   ├── database/
│   │       │   │   ├── __init__.py
│   │       │   │   ├── models.py                 # SQLAlchemy ORM models
│   │       │   │   └── repository.py             # Repositorio (SQLAlchemy queries)
│   │       │   └── external/
│   │       │       ├── __init__.py
│   │       │       └── payment_gateway.py        # Cliente HTTP externo (httpx)
│   │       │
│   │       ├── domain/                           # Modelo de dominio puro
│   │       │   ├── __init__.py
│   │       │   ├── entities.py                   # Dataclasses / Pydantic domain models
│   │       │   ├── value_objects.py              # Value objects (Money, Status)
│   │       │   └── events.py                     # Domain events
│   │       │
│   │       ├── application/                      # Casos de uso / servicios
│   │       │   ├── __init__.py
│   │       │   ├── interfaces/                   # Puerto de repositorio (abstract)
│   │       │   │   ├── __init__.py
│   │       │   │   └── order_repository.py       # Protocol / ABC
│   │       │   └── services/
│   │       │       ├── __init__.py
│   │       │       ├── order_service.py          # Lógica de negocio
│   │       │       └── order_validator.py        # Validación de dominio
│   │       │
│   │       ├── presentation/                     # Adaptadores de entrada
│   │       │   ├── __init__.py
│   │       │   ├── router.py                     # APIRouter con endpoints
│   │       │   ├── schemas.py                    # Pydantic request/response schemas
│   │       │   └── dependencies.py               # FastAPI dependencies (Depends)
│   │       │
│   │       └── tests/                            # Tests del módulo
│   │           ├── __init__.py
│   │           ├── test_router.py                # TestClient endpoint tests
│   │           ├── test_service.py               # Test de servicio con mocks
│   │           └── test_repository.py            # Test de repositorio (test DB)
│   │
│   └── shared/                                   # Código reusable entre módulos
│       ├── __init__.py
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── jwt_handler.py                    # JWT encode/decode
│       │   └── auth_deps.py                      # get_current_user dependency
│       ├── cache/
│       │   ├── __init__.py
│       │   └── cache_service.py                  # Redis cache wrapper
│       └── events/
│           ├── __init__.py
│           └── event_bus.py                      # Event dispatcher (Redis pub/sub)
│
├── alembic/                                      # Database migrations
│   ├── env.py
│   ├── versions/
│   │   └── 0001_create_orders_table.py
│   └── alembic.ini
│
├── tests/                                        # Tests de integración globales
│   ├── __init__.py
│   ├── conftest.py                               # Fixtures globales (test DB, client)
│   └── test_api.py                               # End-to-end API tests
│
├── .env.example
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

**Explicación de directorios clave:**

| Directorio | Propósito |
|------------|-----------|
| `modules/{modulo}/presentation/` | Capa de presentación: routers FastAPI, Pydantic schemas de entrada/salida, dependencias de inyección. |
| `modules/{modulo}/application/` | Servicios de aplicación con la lógica de negocio. Define interfaces abstractas (Protocol) que la infraestructura implementa. |
| `modules/{modulo}/domain/` | Entidades del negocio como dataclasses puras, value objects y eventos. Sin dependencias de FastAPI ni SQLAlchemy. |
| `modules/{modulo}/infrastructure/` | Implementaciones concretas: modelos SQLAlchemy, repositorios, clientes HTTP externos. |
| `modules/{modulo}/tests/` | Tests del módulo que pueden ejecutarse de forma aislada. Cada módulo es testeable independientemente. |
| `common/middleware/` | Middleware global de FastAPI: correlation ID, logging, manejo de errores. |
| `config/` | Configuración con Pydantic Settings (type-safe, validada al inicio). |

## Decision framework: V-Slice vs Modular Monolith vs Microservices

### Árbol de decisión

```
¿Equipo pequeño (< 5 personas)?
├── Sí → ¿Dominio complejo con subdominios claros?
│       ├── Sí → Modular Monolith (módulos con límites definidos)
│       └── No → Vertical Slice (mínima fricción, rápido time-to-market)
└── No → ¿Equipo grande (> 10 personas) y despliegues independientes?
        ├── Sí → Microservices (cada equipo dueño de 1+ servicios)
        └── No → Modular Monolith con posible extracción futura

¿Proyecto nuevo sin validación de mercado?
├── Vertical Slice (cambio barato, refactorizable después)
└── No empezar con Microservices (costo cognitivo alto)

¿Necesitas escalar equipos después del MVP?
├── Modular Monolith con módulos en carpetas separadas
└── Extraer a Microservices cuando un módulo requiere deploy independiente
```

### Tabla comparativa

| Criterio | Vertical Slice | Modular Monolith | Microservices |
|---|---|---|---|
| **Tamaño de equipo** | 1–3 personas | 3–10 personas | 8+ personas (por servicio 2–5) |
| **Frecuencia de deploy** | Varias veces al día | 1–5 veces por semana | Independiente por servicio |
| **Complejidad de dominio** | Baja a media | Media a alta | Alta (subdominios delimitados) |
| **Velocidad inicial** | Máxima (cero overhead) | Alta (overhead mínimo) | Baja (contratos, infraestructura) |
| **Acoplamiento entre features** | Bajo (por diseño) | Medio (módulos independientes) | Bajo (contratos explícitos) |
| **Pruebas** | Unitarias + integración | Unitarias + integración + contract | Contract tests + integración + E2E |
| **Costo operativo** | Mínimo | Bajo | Alto (orquestación, monitoreo, redes) |
| **Escalabilidad** | Vertical (todo junto) | Vertical por módulo | Horizontal independiente |
| **Tiempo de build** | Minutos | Minutos | Segundos–minutos |
| **Rollback** | Un solo deploy | Un solo deploy | Coordinado entre servicios |
| **Observabilidad** | Un solo proceso | Un solo proceso | Distribuida (trazado, logs agregados) |

### Cuándo empezar con cuál

| Escenario | Recomendación | Razón |
|-----------|---------------|-------|
| MVP / Startup sin validación | Vertical Slice | Cambiar de dirección es barato. El overhead de módulos o microservicios frena el aprendizaje. |
| Proyecto corporativo con dominio conocido | Modular Monolith | Se conocen los límites del dominio. Los módulos dan orden sin la complejidad operativa de microservicios. |
| SaaS multi-tenant con módulos bien definidos | Modular Monolith | Cada módulo puede escalarse y desplegarse de forma independiente cuando sea necesario. |
| Plataforma con equipos independientes | Microservices | Cada equipo necesita autonomía total en deploy y escalado. |
| Migración de monolitho legacy | Modular Monolith primero, luego extracción | Extraer módulos uno por uno a microservicios reduce el riesgo. |

### Ruta de migración: Monolith → Modular Monolith → Microservices

```
Fase 1: Monolith (código espagueti)
  ├── Todo en un solo proyecto sin separación clara
  └── Acción: Identificar bounded contexts y crear carpetas de módulos

Fase 2: Modular Monolith (módulos con interfaces)
  ├── Cada módulo tiene API pública y privada
  ├── Los módulos se comunican por interfaces, no por clases concretas
  └── Acción: Extraer módulo candidato a servicio independiente

Fase 3: Microservices híbrido
  ├── Módulo extraído como servicio nuevo (con API contract)
  ├── Monolith consume el nuevo servicio por HTTP / mensajería
  └── Acción: Migrar consumidores uno por uno

Fase 4: Microservices puro
  ├── Todos los módulos son servicios independientes
  ├── API Gateway / BFF como entry point
  └── Estado: Cada equipo dueño de 1+ servicios
```

**Patrón estrangulador (Strangler Fig):** La estrategia recomendada para migrar de monolith a microservicios. Consiste en crear un nuevo servicio que gradualmente reemplaza funcionalidad del monolith. El router/envía tráfico al nuevo servicio o al monolith según la funcionalidad solicitada. Cuando el nuevo servicio cubre toda la funcionalidad, el monolith se retira.

### Anti-patrones

| Anti-patrón | Problema | Solución |
|-------------|----------|----------|
| **Distributed Monolith** | Microservicios que se llaman sincrónicamente en cadena (A → B → C → D). Latencia alta, fallos en cascada. | Usar mensajería asíncrona (eventos, colas). Cada servicio debe ser autónomo. |
| **Microservicios para MVP** | Overhead de infraestructura, contratos, deploy coordinado. El producto nunca llega a mercado. | Empezar con Vertical Slice o Modular Monolith. Extraer después. |
| **Shared Database entre servicios** | Dos servicios que escriben en la misma tabla de BD. Los límites del dominio se rompen. | Cada servicio debe tener su propia base de datos (database per service). |
| **Service per table** | Un microservicio por tabla de BD. Sin lógica de negocio real. Cientos de servicios minúsculos. | Agrupar por bounded context. Un servicio debe abarcar un agregado completo. |
| **Modulorama falso** | Carpetas de módulos en el código pero sin interfaces ni límites claros. Los módulos se importan entre sí directamente. | Aplicar principios de arquitectura limpia: las interfaces definen los contratos entre módulos. |
| **Orquestación excesiva** | Un servicio orquestador que coordina 10+ servicios en cada request. Punto único de fallo y acoplamiento. | Preferir coreografía con eventos. Cada servicio reacciona a eventos sin un coordinador central. |
| **Microservicios sin observabilidad** | 20+ servicios sin tracing distribuido, logs agregados ni métricas unificadas. Imposible diagnosticar fallos. | Implementar OpenTelemetry desde el día 1. Logs estructurados, métricas y tracing obligatorios. |
| **Versionado de base de datos compartida** | Dos microservicios que comparten esquema de BD y hacen migraciones simultáneas. | Database per service + migraciones independientes. Los cambios de esquema nunca deben coordinar servicios. |

### Patrones de comunicación entre servicios

| Patrón | Cuándo usarlo | Tecnologías |
|--------|---------------|-------------|
| **HTTP/REST síncrono** | Consultas que requieren respuesta inmediata (Q&A queries). | RestTemplate, WebClient, Feign, axios, httpx |
| **gRPC** | Alta frecuencia de llamadas, baja latencia, contratos fuertes. | gRPC, Protobuf, buf |
| **Eventos asíncronos** | Notificaciones, propagación de cambios, desacoplamiento total. | Kafka, RabbitMQ, NATS, Redis Streams |
| **Cola de trabajos** | Tareas pesadas sin respuesta inmediata (emails, reportes, procesamiento batch). | BullMQ, Sidekiq, Celery, AWS SQS |
| **CQRS + Event Sourcing** | Sistemas donde el historial de cambios es obligatorio (auditoría, proyecciones múltiples). | Event Store, Kafka + proyecciones |

### Checklist para elegir arquitectura

- [ ] ¿El equipo puede mantener N servicios en producción? (costo operativo)
- [ ] ¿El dominio tiene bounded contexts claramente identificables?
- [ ] ¿Se necesitan deploys independientes por funcionalidad?
- [ ] ¿Hay requisitos de escalado diferentes por funcionalidad?
- [ ] ¿La organización está alineada con los límites de los servicios?
- [ ] ¿Existe el presupuesto para infraestructura de microservicios (service mesh, tracing, CI/CD)?
- [ ] ¿Se tiene experiencia previa con la arquitectura elegida?

Si respondes "No" a 3 o más preguntas, empieza con Vertical Slice o Modular Monolith.
