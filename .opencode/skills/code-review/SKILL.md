---
name: code-review
description: 'Code review checklist before creating PRs. Applies to Angular frontend,
  Bun (TypeScript) backend, and PostgreSQL database layer. Includes Keycloak/OAuth2
  security checks and OpenTelemetry observability. Trigger: Before committing code,
  creating PRs, or when asked to review.'
version: 2.0
metadata:
  phase:
  - construction
  layer:
  - process
  enforcement: mandatory
  depends_on: []
  consumed_by:
  - pull-request
  agent_roles:
  - control-agent
  - delivery-agent
  validation_profile: skill-contract
mcp_usage: none
---

## Critical Rules

| Rule | Type | Rationale |
|------|------|-----------|
| Run this checklist before EVERY PR | ALWAYS | Catch issues early |
| Fix all blockers before commit | ALWAYS | Don't merge broken code |
| Document skipped checks with reason | ALWAYS | Transparency |

## Quick Checklist

### Blockers (MUST fix)
- Build passes / No type errors / No linter errors / Tests pass
- No secrets in code / No console.log or debug output / No commented-out code

### Warnings (Should fix)
- No loosely typed variables (`any`, `Object` without reason) / No magic numbers / No duplicate code
- Error handling / Loading states / Empty states

### Best Practices
- Meaningful names / Small functions / Consistent patterns with the rest of the codebase

## Layer-Specific Checks

### Database (PostgreSQL)
| Check | Look For |
|-------|----------|
| Error format | Standardized error code + message + field |
| Transaction | `BEGIN ... EXCEPTION ... ROLLBACK; RAISE; END;` with proper exception handling |
| Parameters | All inputs are parameters, no string concatenation in queries |
| Pagination | List queries have `LIMIT/OFFSET` or cursor-based pagination |
| Locking | `FOR UPDATE SKIP LOCKED` for concurrent workers, no `WITH(NOLOCK)` antipattern |

### Backend (Bun / TypeScript)
| Check | Look For |
|-------|----------|
| Types | Strict TypeScript, no `any`, Result types for fallible operations |
| Async | `await` on all async calls, no `.then()` chains mixing patterns |
| Error handling | Result types (`Ok`/`Err`) or typed exceptions, no naked `try/catch` swallowing |
| Validation | Zod schemas for input validation at API boundary |
| Logging | Structured logging, no sensitive data, correlation IDs |
| Security | Keycloak JWT validation, RBAC enforcement, CORS configured |

### Frontend (Angular)
| Check | Look For |
|-------|----------|
| Components | Standalone components, proper lifecycle hooks (`OnInit`, `OnDestroy`, `OnChanges`) |
| Signals | Use signals for reactive state, avoid manual `ChangeDetectionStrategy.OnPush` boilerplate |
| RxJS | Proper subscription management (`takeUntil`, `DestroyRef`), no memory leaks |
| Templates | Async pipe for observables, `@if`/`@for` control flow, no ngDoCheck overuse |
| Accessibility | Labels, ARIA attributes, keyboard navigation |

## Common Issues to Catch

| Issue | Example | Fix |
|-------|---------|-----|
| Missing error handling | `await api.post()` without try/catch | Use Result types or typed exceptions |
| Hardcoded values | `if (status === 1)` | Use constants/enums |
| Missing loading state | Button doesn't show loading | Add loading indicator with signals |
| N+1 queries | Loop with DB call inside | Batch or join |
| Memory leak | Subscription without `takeUntil` or `DestroyRef` | Auto-unsubscribe pattern |

## Checklist por capa

### Database — Análisis detallado (PostgreSQL)

| Categoría | Check | Detalle |
|-----------|-------|---------|
| **Índices** | ¿Hay index para cada columna en WHERE/ORDER BY/JOIN? | Revisar query plan con `EXPLAIN ANALYZE`. Faltas de index = sequential scan = degradación |
| **Índices** | ¿Evita over-indexing? | Más de 5 índices por tabla en tablas transaccionales es sospechoso |
| **Índices** | ¿Los índices compuestos siguen el orden correcto? | Columnas de mayor selectividad primero |
| **Índices** | ¿Usa índices parciales cuando aplica? | `CREATE INDEX ... WHERE status = 'active'` reduce tamaño del índice |
| **Queries** | ¿Usa parámetros tipados? | `$1::int` no `$1::text` si la columna es INTEGER. Evita conversiones implícitas |
| **Queries** | ¿Evita SELECT *? | Siempre columnas explícitas, especialmente en JOINs |
| **Queries** | ¿Las funciones en WHERE están en columnas indexadas? | `WHERE EXTRACT(YEAR FROM fecha) = 2024` no usa index. Usar `fecha >= '2024-01-01' AND fecha < '2025-01-01'` |
| **Queries** | ¿Hay paginación consistente? | `LIMIT/OFFSET` con `ORDER BY` determinista, o cursor-based. Misma paginación en todos los List |
| **Queries** | ¿CTE vs subquery? | Preferir CTE para legibilidad. CTEs son optimizados desde PG 12 |
| **Queries** | ¿FOR UPDATE cuando aplica? | `SELECT ... FOR UPDATE` para filas que serán modificadas. `SKIP LOCKED` para workers concurrentes |
| **Stored Procedures** | ¿Maneja transacciones correctamente? | `BEGIN ... EXCEPTION WHEN ... THEN ROLLBACK; RAISE; END;` con manejo explícito |
| **Stored Procedures** | ¿Errores estandarizados? | `RAISE EXCEPTION` con código, mensaje, y campo en formato consistente |
| **Stored Procedures** | ¿Permisos mínimos? | Funciones con `SECURITY DEFINER` o permisos granular. No dar acceso directo a tablas |
| **Funciones** | ¿Return type correcto? | `RETURNS TABLE`, `RETURNS SETOF`, o `RETURNS SETOF record` según el caso |
| **Funciones** | ¿Idempotente? | `CREATE OR REPLACE FUNCTION` siempre. `IF EXISTS` en DROP |
| **Migraciones** | ¿Rollback definido? | Toda migración UP tiene su DOWN correspondiente |
| **Migraciones** | ¿Idempotente? | `IF NOT EXISTS`, `ON CONFLICT DO NOTHING`, o condicionales. Doble ejecución no debe fallar |
| **Migraciones** | ¿ALTER TABLE sin bloqueos? | `ADD COLUMN ... DEFAULT` en PG 11+ es rápido. `NOT NULL` en tablas grandes sin plan es riesgoso |
| **Migraciones** | ¿Concurrent index creation? | `CREATE INDEX CONCURRENTLY` en tablas en producción para evitar locks |
| **Seguridad** | ¿SQL Injection? | Todos los inputs son parametrizados. Cero concatenación en dinámicos |
| **Seguridad** | ¿Dynamic SQL controlado? | Si usa `EXECUTE`, verificar que los parámetros vienen de una lista blanca |
| **Seguridad** | ¿Row Level Security? | Políticas RLS activas en tablas multi-tenant |
| **Auditoría** | ¿Columnas de auditoría presentes? | `created_at`, `created_by`, `updated_at`, `updated_by`, `record_status` en tablas de datos |
| **Auditoría** | ¿Log de cambios? | Tablas críticas tienen trigger o log table para cambios (UPDATE/DELETE) |

### Backend — Análisis detallado (Bun / TypeScript)

| Categoría | Check | Detalle |
|-----------|-------|---------|
| **Tipos** | ¿TypeScript strict mode habilitado? | `tsconfig.json` con `strict: true`, `noImplicitAny`, `strictNullChecks` |
| **Tipos** | ¿Sin `any`? | `any` requiere justificación documentada. Usar `unknown` y narrowing |
| **Tipos** | ¿Result types para operaciones fallibles? | `Result<T, E>` o `E.Either` en vez de exceptions para errores esperados |
| **Tipos** | ¿Discriminated unions? | Para estados de error/éxito, usar uniones discriminadas con `kind` o `tag` |
| **Validación** | ¿Zod schemas en boundary? | Todo input de API validado con Zod. `z.infer<typeof schema>` para tipos |
| **Validación** | ¿Validación en capa correcta? | Validación de formato en API boundary, validación de negocio en service/handler |
| **Validación** | ¿Sanitización de strings? | XSS: sanitizar HTML si se renderiza. Strip whitespace en campos de texto |
| **Manejo de errores** | ¿Result types en lógica de negocio? | `Result<User, DomainError>` en vez de `throw`. Exceptions solo para errores inesperados |
| **Manejo de errores** | ¿Error response consistente? | `{ "code": "USER_NOT_FOUND", "message": "...", "field": "id" }` — mismo formato siempre |
| **Manejo de errores** | ¿Sin excepciones silenciosas? | `catch { }` vacío está prohibido. Mínimo loguear y propagar error genérico |
| **Manejo de errores** | ¿Error middleware global? | Middleware que captura excepciones no manejadas y las mapea a respuestas HTTP |
| **Async** | ¿Async all the way? | Métodos async se llaman con `await`. Sin `.then()` mixing con `await` |
| **Async** | ¿Promise.all para paralelismo? | Llamadas independientes se ejecutan en paralelo con `Promise.all()` o `Promise.allSettled()` |
| **Async** | ¿Timeout en llamadas externas? | `AbortController` con timeout para llamadas HTTP. Evitar hanging promises |
| **Seguridad** | ¿JWT validation con Keycloak? | Verificar token, issuer, audience, expiry. Usar JWKS endpoint de Keycloak |
| **Seguridad** | ¿RBAC enforcement? | Roles extraídos del JWT. Decorator o middleware que valida permisos por endpoint |
| **Seguridad** | ¿CORS configurado? | Orígenes específicos en config, no `*` en producción |
| **Seguridad** | ¿Rate limiting configurado? | Endpoints expuestos tienen rate limiting. Usar middleware de Bun |
| **Seguridad** | ¿Secrets management? | No hardcodear. Usar variables de entorno o vault. Keycloak client secrets fuera del repo |
| **Logging** | ¿Structured logging? | JSON format con `correlationId`, `tenantId`, `userId`. No strings libres |
| **Logging** | ¿Sin PII en logs? | No loguear emails, passwords, tokens, IPs, tarjetas. Usar estructura de log |
| **Logging** | ¿Correlation ID propagado? | Desde request header `X-Correlation-ID` a través de toda la cadena |
| **Observabilidad** | ¿OpenTelemetry traces? | Span en cada operación de negocio. Propagar context entre servicios |
| **Observabilidad** | ¿Prometheus metrics? | Contadores de requests, histogramas de latencia, gauges de negocio |
| **Observabilidad** | ¿Health checks? | `/health/live` y `/health/ready` expuestos. Verificar dependencias en ready |
| **Rendimiento** | ¿Connection pooling? | Pool de conexiones a PostgreSQL configurado. No abrir/cerrar por request |
| **Rendimiento** | ¿Paginación en todos los list? | Sin paginación = riesgo de OOM o timeout. `page` / `pageSize` requeridos |
| **Rendimiento** | ¿Cache strategy? | Datos de lectura frecuente (catálogos, config) con cache y TTL razonable |
| **Testing** | ¿Test por handler/endpoint? | Cada endpoint público tiene test de integración |
| **Testing** | ¿Mocks en capa correcta? | Mock en la interfaz inmediata. No mockear BD, mockear repositorio |
| **Testing** | ¿Bun test runner? | Usar `bun test` nativo. Tests rápidos con `describe`/`it`/`expect` |

### Frontend — Análisis detallado (Angular)

| Categoría | Check | Detalle |
|-----------|-------|---------|
| **Componentes** | ¿Standalone components? | Components con `standalone: true`. Evitar NgModules innecesarios |
| **Componentes** | ¿Lifecycle hooks correctos? | `OnInit` para setup, `OnDestroy` para cleanup, `OnChanges` para inputs reactivos |
| **Componentes** | ¿DestroyRef para cleanup? | `inject(DestroyRef).onDestroy(...)` o `takeUntilDestroyed()` para auto-unsubscribe |
| **Componentes** | ¿Signals para estado reactivo? | `signal()`, `computed()`, `effect()` en vez de BehaviorSubjects manuales |
| **Componentes** | ¿Change detection eficiente? | `OnPush` o signals. Evitar `ngDoCheck` costoso |
| **Templates** | ¿Control flow moderno? | `@if`, `@for`, `@switch` en vez de `*ngIf`, `*ngFor`, `ngSwitch` |
| **Templates** | ¿Async pipe? | Siempre `async` pipe en vez de `.subscribe()` manual en templates |
| **Templates** | ¿Track functions en @for? | `@for (item of items; track item.id)` para performance |
| **Templates** | ¿Input signals? | `input()`, `input.required()` para inputs tipados y reactivos |
| **Templates** | ¿Output functions? | `output()` en vez de `@Output()` decorator |
| **Tipos** | ¿Sin `any`? | TypeScript strict mode. `any` requiere justificación documentada |
| **Tipos** | ¿Interfaces para modelos? | Modelos de datos como interfaces exportadas. No clases para DTOs |
| **RxJS** | ¿Suscripciones manejadas? | `takeUntilDestroyed()`, `takeUntil(destroy$)`, o `toSignal()` |
| **RxJS** | ¿Operadores correctos? | `switchMap` para búsquedas, `mergeMap` para paralelo, `concatMap` para secuencial |
| **RxJS** | ¿Sin subscribe anidado? | Combinar con `switchMap`, `combineLatest`, `forkJoin` en vez de nesting |
| **RxJS** | ¿Signals vs RxJS? | Estado simple = signals. Streams complejos = RxJS. No mezclar sin razón |
| **Estado** | ¿Estado levantado correctamente? | Estado compartido en el ancestro común más bajo. Services para estado global |
| **Estado** | ¿Loading states? | `toSignal()` con estado de loading. Spinner/skeleton mientras carga |
| **Estado** | ¿Error states? | Error interceptor global. Toast/manejo de error por operación |
| **Estado** | ¿Empty states? | "No hay datos" + ilustración + CTA relevante cuando lista vacía |
| **Routing** | ¿Lazy loading? | `loadComponent` o `loadChildren` en rutas. No importar todo en módulo raíz |
| **Routing** | ¿Guards funcionales? | `canActivate` con funciones, no clases |
| **Routing** | ¿Resolvers cuando aplica? | Datos precargados antes de activar ruta. No loading en componente |
| **Forms** | ¿Reactive forms? | `FormGroup`, `FormControl`, `FormBuilder`. Validación con validators |
| **Forms** | ¿Validación inline? | Errores mostrados bajo cada campo. No solo al submit |
| **Forms** | ¿Typed forms? | `FormGroup<{ name: FormControl<string> }>`. No forms genéricos |
| **Rendimiento** | ¿OnPush strategy? | Componentes con `changeDetection: OnPush` o signals |
| **Rendimiento** │ ¿Track functions? | `@for` con `track` para evitar re-renders innecesarios |
| **Rendimiento** | ¿Imágenes optimizadas? | WebP, lazy loading (`loading="lazy"`), dimensiones explícitas |
| **Accesibilidad** | ¿Labels? | Todo input tiene `<label>` o `aria-label`. No placeholder como label |
| **Accesibilidad** | ¿Roles ARIA correctos? | `role="button"` en botones, `role="navigation"` en nav. No sobrecargar |
| **Accesibilidad** | ¿Contraste? | 4.5:1 texto normal, 3:1 texto grande. Verificar con herramienta |
| **Accesibilidad** | ¿Teclado? | Todas las acciones disponibles con Tab, Enter, Escape. Focus visible |
| **Testing** | ¿Test por componente? | Componente principal tiene test de render, interacción, estados |
| **Testing** | ¿Testing module? | `TestBed.configureTestingModule` con imports necesarios |
| **Testing** | ¿Signal testing? | Probar computed values y effects con `fixture.detectChanges()` |
| **Testing** | │ ¿Test de acceso? | Pantallas protegidas redirigen a login sin token |

### Seguridad — Análisis detallado (Keycloak / OAuth2)

| Categoría | Check | Detalle |
|-----------|-------|---------|
| **Token validation** | ¿JWT verificado correctamente? | Verificar firma (JWKS), `iss`, `aud`, `exp`, `nbf`. No confiar solo en payload |
| **Token validation** | ¿Refresh token handling? | Refresh token con rotación. Almacenar securemente, no en localStorage |
| **RBAC** | ¿Roles extraídos del JWT? | Leer roles del token, no de DB en cada request |
| **RBAC** | ¿Permissions granular? | `realm_access.roles` y `resource_access.client_roles`. No solo "is_admin" |
| **RBAC** | ¿Endpoint protection? | Cada endpoint tiene role/permission requirement. Endpoints públicos son excepción explícita |
| **CORS** | ¿Orígenes configurados? | Lista explícita de dominios permitidos. No `*` nunca |
| **CORS** | ¿Headers permitidos? | `Authorization`, `Content-Type`, `X-Correlation-ID`. No permitir headers sensibles |
| **Secrets** | ¿Client secrets fuera del código? | Variables de entorno o vault. Nunca en repositorio |
| **Secrets** | ¿Keycloak realm configurado? | Realm propio, no Master. Client dedicado por servicio |
| **Multi-tenancy** | ¿Tenant isolation? | Tenant ID en JWT claims. Queries filtradas por tenant. RLS en DB |
| **Multi-tenancy** | ¿Cross-tenant access bloqueado? | Validación explícita que usuario no accede a datos de otro tenant |
| **Session** | ¿Token expiry razonable? | Access token < 15min. Refresh token < 24h. No tokens de larga duración |
| **Session** | ¿Logout completo? | Logout de Keycloak + limpieza de tokens locales. No solo cerrar sesión local |

### Observabilidad — Análisis detallado (OpenTelemetry / Prometheus)

| Categoría | Check | Detalle |
|-----------|-------|---------|
| **Tracing** | ¿Spans en operaciones de negocio? | Cada operación significativa es un span. Nombre descriptivo: `user.create`, `order.process` |
| **Tracing** | ¿Context propagation? | Propagar `traceparent` header entre servicios. Usar propagadores de OpenTelemetry |
| **Tracing** | ¿Span attributes útiles? | `user.id`, `tenant.id`, `order.id` como attributes. No solo el nombre del span |
| **Tracing** | ¿Error recording? | `span.recordException(error)` en catch. Set `span.setStatus(StatusCode.ERROR)` |
| **Metrics** | │¿Contadores de requests? | `http_requests_total` con labels `method`, `path`, `status`. Usar histogramas para latencia |
| **Metrics** | │¿Business metrics? | Contadores de dominio: `orders.created`, `users.registered`. Gauges de estado activo |
| **Metrics** | │¿Exposición Prometheus? | Endpoint `/metrics` accesible. Formato estándar Prometheus |
| **Metrics** | │¿Labels controladas? | No cardinalidad infinita. User ID como attribute, no como label de metric |
| **Logs** | │¿Structured logging? | JSON con `timestamp`, `level`, `message`, `correlationId`, `service`, `traceId` |
| **Logs** | │¿Correlation con traces? | `traceId` y `spanId` en cada log entry para correlacionar con distributed tracing |
| **Logs** | │¿Nivel correcto? | `TRACE` = debug fino, `DEBUG` = desarrollo, `INFO` = flujo normal, `WARN` = recuperable, `ERROR` = fallo |
| **Health** | │¿Health endpoints? | `/health/live` (proceso vivo) y `/health/ready` (acepta tráfico). Verificar dependencias en ready |
| **Health** | │¿Dependencies check? | Ready check verifica DB connectivity, cache availability, downstream services |
| **Dashboards** | │¿Grafana dashboards? | Dashboard por servicio: requests, latencia, errors, saturation. SLOs visibles |
| **Alerts** | │¿Alert rules definidas? | Error rate > 1% = P1. Latency p99 > 5s = P2. Disk > 80% = P3 |

## Anti-patterns comunes

### Database (PostgreSQL)

| Anti-patrón | Ejemplo | Problema | Solución |
|-------------|---------|----------|----------|
| **SELECT *** | `SELECT * FROM users` | Trae columnas innecesarias, rompe si cambia el schema | Columnas explícitas |
| **Sin FOR UPDATE en workers** | `SELECT * FROM jobs WHERE status = 'pending'` | Race condition entre workers | `FOR UPDATE SKIP LOCKED` |
| **BEGIN TRY/CATCH de SQL Server** | `BEGIN TRY ... BEGIN CATCH ... END TRY ... END CATCH` | Sintaxis incorrecta en PostgreSQL | `BEGIN ... EXCEPTION WHEN ... THEN ... END;` |
| **Dynamic SQL sin validación** | `EXECUTE('SELECT * FROM ' || table_name)` | SQL Injection, no hay plan cache | `EXECUTE format(...)` con whitelist, o `pg_notify` para eventos |
| **String concatenation en WHERE** | `WHERE name LIKE '%' || term || '%'` | No usa índices, performance O(n) | Full-text search con `tsvector`, o trigram indexes con `pg_trgm` |
| **Transacción larga** | BEGIN antes de llamadas HTTP | Bloquea recursos por minutos | Transacciones cortas, solo operaciones DB |
| **Trigger complejo** | Trigger de 100 líneas con lógica de negocio | Debugging imposible, efectos colaterales | Log table + proceso separado con LISTEN/NOTIFY |
| **Sin paginación** | `SELECT * FROM products` sin límite | OOM en tablas grandes | `LIMIT/OFFSET` o cursor-based pagination |
| **Índice en cada columna** | Index individual en 8 columnas | Wasted space, INSERT/UPDATE lentos | Índices compuestos según queries reales |
| **Sin CONCURRENTLY** | `CREATE INDEX idx ON users(email)` | Lock exclusivo en tabla durante creación | `CREATE INDEX CONCURRENTLY` en producción |
| **Sin RLS** | Queries sin filtrar por tenant | Cross-tenant data exposure | Row Level Security policies activas |

### Backend (Bun / TypeScript)

| Anti-patrón | Ejemplo | Problema | Solución |
|-------------|---------|----------|----------|
| **God class** | `UserService` con 30 métodos | Difícil de testear, mantener, extender | Separar por dominio (`AuthService`, `ProfileService`, `AdminService`) |
| **Shotgun surgery** | Cambiar 15 archivos para una validación | Alta cohesión, difícil de revisar | Encapsular en middleware o validator único |
| **Copy-paste de errores** | 20 catch blocks con `return 500` | Inconsistente, no informativo | Middleware global de errores con mapeo centralizado |
| **`any` por todos lados** | `const data: any = await api.get(...)` | Sin tipos, errores en runtime | Tipar response de API, usar `unknown` si es necesario |
| **Sync over async** | `Bun.spawnSync` en hot path | Bloquea el event loop | `await Bun.spawn` con async |
| **Magic strings** | `if (role == "admin")` | Error typo, difícil de refactorizar | Enum o constantes tipadas |
| **DTO anémico** | Misma interfaz para request, response, entity | Acoplamiento, breaking changes | DTO separado por capa (Request, Response, Entity) |
| **No idempotencia** | POST /orders crea orden duplicada | Doble click = doble cobro | Idempotency key en POST |
| **Logging excesivo** | `console.log()` en cada línea | Ruido, costo, información útil diluida | Loggear eventos de negocio, no cada instrucción |
| **Missing timeout** | `fetch()` sin AbortController | Hanging requests consumen resources | `AbortSignal.timeout(ms)` en todas las llamadas externas |
| **No structured logging** | `console.log("User created")` | Imposible filtrar/correlacionar | Logger estructurado: `logger.info({ userId, tenantId }, "User created")` |

### Frontend (Angular)

| Anti-patrón | Ejemplo | Problema | Solución |
|-------------|---------|----------|----------|
| **NgModules innecesarios** | Módulo para cada componente | Boilerplate excesivo, tree-shaking imposible | Standalone components |
| **Subscribe sin unsubscribe** | `this.api.get().subscribe(data => ...)` | Memory leak | `toSignal()`, `takeUntilDestroyed()`, o `async` pipe |
| **ngDoCheck costoso** | Cálculo pesado en `ngDoCheck` | Performance degradation | Signals con `computed()` o `OnPush` manual |
| **Manejo de errores en catch genérico** | `catch (err) { this.error = "Error" }` | Usuario no sabe qué pasó | Mapear errores por código HTTP + mensaje contextual |
| **Estado derivado en state** | `this.filteredItems = this.items.filter(...)` en setter | Dos fuentes de verdad | `computed(() => this.items().filter(...))` |
| **No lazy load** | Import de componente pesado en módulo raíz | Bundle grande, First Paint lento | `loadComponent` en rutas |
| **Form sin validación inline** | Validar al submit, no al escribir | UX pobre | Validación reactiva + errores inline |
| **Cualquier en templates** | `{{ user?.address?.city }}` sin null check real | Template errors silenciosos | `@if` con null checks explícitos |
| ** RxJS sin operador de error** | `this.api.get().subscribe({ next: ..., error: ... })` sin complete | Posibles leaks | Manejar complete o usar `finalize` |

### Testing

| Anti-patrón | Ejemplo | Problema | Solución |
|-------------|---------|----------|----------|
| **Test de implementación** | Test llama a método privado | Tests frágiles, no refactor-friendly | Testear comportamiento público, no implementación |
| **Mock excesivo** | Mockear 5 dependencias para un test unitario | Tests frágiles, no detectan regresiones reales | Mockear solo interfaz inmediata |
| **Test con sleeps** | `await new Promise(r => setTimeout(r, 1000))` | Test lento, flaky (varía por máquina) | Usar `fakeAsync`, `tick()`, o `waitForAsync` |
| **Test que depende de otro** | Test B necesita datos de Test A | Flaky, no se puede ejecutar en paralelo | `beforeEach` con setup completo |
| **No testear errores** | Solo happy path | 90% de bugs están en edge cases | Test de: 400, 401, 403, 404, 409, 500, timeout |
| **Assert vago** | `expect(result).toBeDefined()` | No verifica nada relevante | Assert específico: valor, tipo, estructura |
| **Test sin cleanup** | Crear datos sin eliminar después | DB contaminada, otros tests fallan | Rollback transacción, truncate, o teardown |
| **Cobertura por métrica** | 90% coverage pero solo getters/setters | Falsa sensación de seguridad | Coverage en lógica de negocio. Excluir getters/DTOs triviales |

## Review workflow

### 1. Preparación (5 min antes del review)

```
1. Abrir el PR en GitHub / GitLab
2. Leer título y descripción del PR → entender qué cambia y por qué
3. Identificar el issue/ticket asociado
4. Determinar alcance: ¿cuántos archivos? ¿qué capas afecta?
5. Si el PR > 400 líneas, pedir al autor que lo divida en PRs más pequeños
```

### 2. Primera pasada — Arquitectura y diseño (10 min)

Enfocarse en el panorama general, no en detalles:

```
Preguntas guía:
- ¿La solución resuelve el problema planteado en la descripción?
- ¿El diseño es consistente con la arquitectura existente?
- ¿Sigue los patrones del proyecto (Standalone Components, Signals, Result types)?
- ¿Respeta los principios SOLID? (especialmente SRP y OCP)
- ¿Hay acoplamiento innecesario entre capas?
- ¿La solución introduce deuda técnica?
- ¿Los nombres de archivos/módulos siguen la convención del proyecto?
```

**Salida:** Comentarios de alto nivel sobre diseño. Si hay issues graves, detener el review aquí y discutir con el autor antes de continuar.

### 3. Segunda pasada — Cada archivo en detalle (20-30 min)

Revisar archivo por archivo siguiendo la checklist por capa:

```
Orden recomendado:
1. DB → Backend → Frontend → Tests
   (porque los cambios en capas inferiores afectan a las superiores)

Por archivo:
1. ¿El archivo debe existir? (¿duplica funcionalidad?)
2. ¿Nombres de clases/funciones/variables son descriptivos?
3. ¿Tests cubren este archivo?
4. ¿Maneja errores correctamente?
5. ¿Performance: hay loops innecesarios, N+1, sin paginación?
6. ¿Seguridad: inputs validados, auth presente?
7. ¿Cumple la checklist por capa de esta skill?
```

**Salida:** Comentarios específicos en línea. Para cada comentario:
- **Blocker**: Debe arreglarse antes de mergear
- **Warning**: Debe discutirse, ideal arreglar
- **Suggestion**: Mejora opcional

### 4. Tercera pasada — Tests (5 min)

```
- ¿Hay tests para este cambio? (si no, preguntar por qué)
- ¿Los tests son legibles? (siguen AAA)
- ¿Los tests prueban comportamiento, no implementación?
- ¿Cubren casos de error además de happy path?
- ¿Los mocks están en la capa correcta?
- ¿Los tests usan Bun test runner correctamente?
- ¿Los tests son independientes?
```

### 5. Resumen del review (2 min)

```
Formato de resumen:

## Review: [PR Title]
**Overall:** Approve / Needs Changes / Blocked
**Severity:** Trivial / Minor / Major / Critical

### Resumen
- {1-2 oraciones de impresión general}
- {Fortalezas del PR}
- {Áreas de mejora}

### Blockers
- {Lista de issues que deben arreglarse}

### Warnings
- {Issues que deben discutirse}

### Suggestions
- {Mejoras opcionales}

### Notas adicionales
- {Contexto, referencias, learning para el equipo}
```

### 6. Post-review

```
- Aprobar con comentarios si solo hay suggestions/warnings y el autor puede responder
- Solicitar cambios si hay blockers
- NO aprobar y esperar que el autor adivine que debe cambiar algo
- Dar seguimiento a los blockers resueltos
- Lograr consenso: el review no es una competencia, es colaboración
```

### Reglas de oro del code review

| Regla | Explicación |
|-------|-------------|
| **Sé constructivo** | Enfócate en el código, no en la persona. "Este método puede optimizarse" no "Esto está mal hecho" |
| **Explica el por qué** | No solo "cambia esto". Explica: "cambia esto porque causa X problema de seguridad" |
| **Respeta el contexto** | No impongas preferencias personales. Si el proyecto usa Angular signals, no pidas BehaviorSubjects |
| **Sé oportuno** | Review en < 24h. PRs pequeños < 200 líneas revisados en horas |
| **PRs pequeños** | < 400 líneas por PR. Bloquea en CI si supera el límite |
| **Dos pares de ojos** | Cada PR necesita al menos 1 approval. PRs críticos (seguridad, infra) necesitan 2 |
| **Automatiza lo repetitivo** | Linting, formato, type checks en CI. No gastes review en lo que puede hacer una máquina |
| **Acepta que te equivoques** | Si el autor demuestra que tu comentario no aplica, reconócelo y sigue |
