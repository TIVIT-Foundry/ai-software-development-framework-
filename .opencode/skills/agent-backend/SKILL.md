---
name: agent-backend
description: 'Meta-skill: activates all backend skills in sequence for backend-only
  work. Trigger: When implementing a backend feature end-to-end (DB → API → endpoints).'
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: optional
  depends_on:
  - database-modeling
  - backend-api
  consumed_by:
  - agent-fullstack
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: skill-contract
  mcp_usage: governed
---

## Tabla de contenidos

- Purpose
- Backend Workflow
- Sequence Diagram
- How to Use
- Quality Gates
- Rollback Scenarios
- Common Mistakes
- Quality Gates
- Flujo de ejecución detallado
  - Nivel 17 — database-modeling
  - Nivel 18 — database-sp
  - Nivel 19 — database-migrations
  - Nivel 20 — database-seeding
  - Nivel 21 — data-access
  - Nivel 22 — backend-api
  - Nivel 23 — api-integration
  - Nivel 24 — api-versioning
  - Nivel 25 — api-resilience
  - Nivel 26 — openapi-docs
- Prompt templates por nivel
  - Nivel 17 — database-modeling
  - Nivel 18 — database-sp
  - Nivel 19 — database-migrations
  - Nivel 20 — database-seeding
  - Nivel 21 — data-access
  - Nivel 22 — backend-api
  - Nivel 23 — api-integration
  - Nivel 24 — api-versioning
  - Nivel 25 — api-resilience
  - Nivel 26 — openapi-docs
- Verificaciones entre niveles
  - database-modeling → database-sp
  - database-sp → database-migrations
  - database-migrations → database-seeding
  - database-seeding → data-access
  - data-access → backend-api
  - backend-api → api-integration
  - api-integration → api-versioning
  - api-versioning → api-resilience
  - api-resilience → openapi-docs
  - Validación transversal (todos los niveles)

## Purpose
This meta-skill activates all backend skills in the correct sequence for backend feature development.
Load each skill in order before generating artifacts.

## Backend Workflow

| Step | Skill | Artifacts |
|------|-------|-----------|
| 1 | `database-modeling` | SQL conventions review |
| 2 | `database-modeling` | Table design |
| 3 | `database-sp` | Stored procedures / queries |
| 4 | `database-audit` | Audit columns, soft delete |
| 5 | `data-access` | Handler pattern |
| 6 | `backend-api` | Module structure, endpoints |
| 7 | `api-integration` | DB → API wiring |
| 8 | `error-handling` | Error propagation |
| 9 | `shared-libs` | Shared response types |
| 10 | `openapi-docs` | OpenAPI documentation |

## Sequence Diagram
```
[DB Schema] → [SPs/Queries] → [Handler] → [Endpoint] → [Response] → [Swagger]
```

## How to Use
1. Activate this meta-skill
2. Load each referenced skill in the workflow table order
3. Generate each artifact in sequence
4. Validate before moving to next step

## Quality Gates
After completing each step, verify:
- [ ] Step 1-4 (DB): Tables, SPs tested, error codes documented
- [ ] Step 5-7 (Backend): Handler maps SP results, validation errors translated
- [ ] Step 8-9 (Quality): Error codes consistent, shared types used
- [ ] Step 10 (Docs): All endpoints documented in OpenAPI

## Rollback Scenarios

| Situation | Action |
|-----------|--------|
| SP returns unexpected error | Rollback step 4, verify column types match expected schema |
| Handler mapping breaks existing endpoint | Rollback to step 5, verify return types match SP output |
| OpenAPI spec diverges from implementation | Regenerate spec from actual response types, do not hand-edit spec |
| Breaking DB change needed mid-flow | Rollback to step 2, document migration plan, notify downstream consumers |

## Common Mistakes

- **Skipping database-audit**: Audit columns (created_at, updated_at, deleted_at) must exist in every table. Never skip step 4.
- **Handlers with business logic**: Handlers must only map SP results → API responses. Business logic belongs in stored procedures or a service layer.
- **Missing error codes**: Every SP must return a success/error code. Validate error code coverage before step 8.
- **Mixed response types**: All endpoints in a module must use the same response wrapper. Verify in step 10.

## Quality Gates

Los siguientes gates deben verificarse antes de considerar la meta-skill completada:

| Gate | Título | Descripción |
|------|--------|-------------|
| 1 | SPs/queries sin errores | Todas las SPs/queries ejecutan sin errores en la base de datos de desarrollo |
| 2 | Mapeo completo de handlers | Los data-access handlers mapean correctamente todos los campos (sin campos huérfanos) |
| 3 | Respuesta ApiResponse<T> consistente | Los endpoints responden con estructura ApiResponse<T> consistente |
| 4 | Autenticación y autorización válida | La autenticación y autorización bloquean accesos no autorizados |
| 5 | Traducción de errores DB→HTTP | Los errores de DB se traducen a códigos de error HTTP apropiados |
| 6 | OpenAPI generada y completa | La documentación OpenAPI está generada y refleja todos los endpoints |

## Flujo de ejecución detallado

Este meta-skill ejecuta 10 niveles backend en secuencia estricta. Cada nivel consume el artefacto del anterior y produce un artefacto para el siguiente. Saltarse un nivel o ejecutarlo incompleto rompe toda la cadena.

### Nivel 17 — database-modeling

**Qué produce**: Modelo de datos completo del módulo: tablas con columnas, tipos de datos, constraints (PK, FK, UNIQUE, CHECK, DEFAULT), índices, esquema de base de datos, funciones y vistas si aplican.

**Input necesario**: API spec del módulo (api-first-spec, nivel 16). Debe contener: ERD conceptual, descripción de entidades, atributos, relaciones, reglas de negocio que impactan el modelo (unicidad, obligatoriedad, cascada).

**Validación previa a siguiente nivel**:
- [ ] Cada tabla tiene PK definida (identity o UUID según convención del proyecto)
- [ ] Cada FK tiene índice asociado
- [ ] Tipos de datos correctos (VARCHAR con longitud, DECIMAL con precisión, fechas con timezone si aplica)
- [ ] Columnas audit estándar incluidas (created_at, updated_at, created_by, updated_by)
- [ ] Soft delete si aplica (deleted_at, deleted_by o RecordStatus)
- [ ] Nombres en plural para tablas, singular para columnas (según convención)
- [ ] Esquema correcto (no usar public por defecto)
- [ ] CHECK constraints documentadas para dominios cerrados
- [ ] Relaciones many-to-many resueltas con tabla puente

**Tiempo estimado**: 45-90 minutos para un módulo de 3-5 entidades.

**Pitfalls comunes**:
- Usar tipos de datos incorrectos (VARCHAR(MAX) sin necesidad, TIMESTAMP sin timezone en vez de TIMESTAMPTZ)
- Olvidar índices en columnas de búsqueda frecuente
- No definir UNIQUE constraints donde la regla de negocio lo exige
- Modelar herencia sin evaluar performance (joined table vs single table)
- No considerar el volumen de datos futuro (falta de particionamiento o indexación)

### Nivel 18 — database-sp

**Qué produce**: Stored procedures para cada operación CRUD de cada entidad del módulo. Incluye: List (paginado con filtros), Get (por ID), Create, Update, Delete (físico o lógico), Search (búsqueda textual si aplica), Merge (upsert) para catálogos.

**Input necesario**: Modelo de datos del nivel anterior (database-modeling). Cada tabla definida debe tener sus SPs correspondientes.

**Validación previa a siguiente nivel**:
- [ ] Cada tabla tiene al menos SPs List, Get, Create, Update, Delete
- [ ] Todos los SPs ejecutan sin errores sintácticos en BD local
- [ ] Parámetros de entrada usan tipos correctos y coinciden con columnas de la tabla
- [ ] SPs List tienen paginación (OFFSET/FETCH) con parámetros p_page_number, p_page_size
- [ ] SPs List tienen ordenamiento dinámico con columna y dirección seguras (whitelist)
- [ ] SPs Create devuelven el ID generado con RETURNING id
- [ ] SPs Update verifican existencia del registro antes de actualizar
- [ ] SPs Delete (lógico) actualizan RecordStatus sin borrar físicamente
- [ ] Manejo de errores con EXCEPTION y código de error estandarizado
- [ ] Naming consistente: usp_{Esquema}_{Entidad}_{Accion}
- [ ] Parámetros con el mismo nombre y tipo que la columna correspondiente

**Tiempo estimado**: 60-120 minutos por módulo de 3-5 entidades.

**Pitfalls comunes**:
- SPs sin paginación que devuelven miles de registros
- No manejar duplicados en Create (falta validación de unicidad)
- Olvidar el RETURNING del ID generado en Create
- Parámetros con nombres distintos a las columnas (confunde al handler)
- No usar esquema en nombres de SPs

### Nivel 19 — database-migrations

**Qué produce**: Scripts de migración versionados que crean, modifican o eliminan objetos de base de datos. Incluye: Create Table, ALTER TABLE, índices, restricciones, y scripts de rollback. Los scripts deben ser idempotentes (ejecutables múltiples veces sin error).

**Input necesario**: SQL completo del módulo del nivel anterior (database-sp + database-modeling). Tablas, SPs, funciones y vistas listos para versionar.

**Validación previa a siguiente nivel**:
- [ ] Scripts de migración enumerados en orden de ejecución (V1__, V2__, etc.)
- [ ] Cada migración tiene su script de rollback correspondiente
- [ ] Migraciones aplicadas en BD de desarrollo sin errores
- [ ] Idempotencia verificada (ejecutar migración dos veces no produce error)
- [ ] No hay ALTER TABLE antes del CREATE TABLE correspondiente
- [ ] SPs incluidos en migraciones posteriores a la creación de tablas
- [ ] Rollback probado y funcional

**Tiempo estimado**: 30-60 minutos.

**Pitfalls comunes**:
- Scripts no idempotentes (fallan en segunda ejecución)
- Mezclar cambios de schema con datos seed en la misma migración
- No probar rollback antes de avanzar
- Nombres de archivo sin orden secuencial claro
- Migraciones que modifican objetos que aún no existen

### Nivel 20 — database-seeding

**Qué produce**: Scripts de seed para datos maestros, catálogos y fixtures de prueba. Usan MERGE (UPSERT) para ser idempotentes. Separados por tipo: catálogos fijos (siempre iguales), datos de referencia (entorno específico), fixtures de prueba (desarrollo).

**Input necesario**: Migraciones aplicadas del nivel anterior. Tablas creadas y listas para recibir datos.

**Validación previa a siguiente nivel**:
- [ ] Todos los catálogos del módulo tienen seed (estados, tipos, categorías)
- [ ] Scripts usan MERGE, no DELETE+INSERT (para mantener IDs)
- [ ] Seeds ejecutados en BD de desarrollo sin errores
- [ ] Datos de catálogo existen y son correctos
- [ ] Fixtures de prueba no contaminan datos maestros
- [ ] Seeds separados por archivo (uno por catálogo o entidad)
- [ ] No hay dependencias circulares entre seeds

**Tiempo estimado**: 30-60 minutos.

**Pitfalls comunes**:
- Usar DELETE+INSERT que rompe IDs referenciados
- No separar datos maestros de datos de prueba
- Dependencias entre seeds no resueltas (FK violation)
- Hardcodear IDs que chocan con producción
- Olvidar seed de tablas catálogo nuevas

### Nivel 21 — data-access

**Qué produce**: Handlers de acceso a datos (repositories o data access objects) que encapsulan las llamadas a SPs. Cada handler expone métodos tipados que reciben parámetros, ejecutan el SP, mapean resultados a modelos y traducen errores de BD.

**Input necesario**: SPs del nivel 18 (database-sp) y migraciones del nivel 19. Cada método del handler corresponde a un SP.

**Validación previa a siguiente nivel**:
- [ ] Cada SP tiene un método handler correspondiente
- [ ] Parámetros del handler coinciden 1:1 con parámetros del SP (nombre y tipo)
- [ ] Mapeo de resultados cubre todas las columnas devueltas (sin columnas huérfanas)
- [ ] Tipos de retorno correctos (List vs single item vs paginated result)
- [ ] Paginación expuesta con modelo PaginatedResult<T>
- [ ] Errores de BD traducidos a excepciones de dominio (NotFoundException, ValidationException, etc.)
- [ ] Handlers agnósticos al framework HTTP (no dependen de HttpContext, Request, etc.)
- [ ] Conexiones abiertas y cerradas correctamente (context managers / async with)
- [ ] Transacciones manejadas explícitamente cuando aplica

**Tiempo estimado**: 60-120 minutos.

**Pitfalls comunes**:
- Handlers que filtran datos en memoria en vez de en BD
- No cerrar conexiones (connection leak)
- Mapeo manual propenso a errores (usar SQLAlchemy o similar)
- Handlers con lógica de negocio (violación de separación de capas)
- No manejar DBNull en columnas nulables

### Nivel 22 — backend-api

**Qué produce**: Endpoints de API (controllers o Minimal API) que exponen los handlers como servicios HTTP. Incluye: validación de requests, routing, inyección de dependencias, responses con estructura ApiResponse<T>.

**Input necesario**: Handlers del nivel anterior (data-access) y la especificación del módulo (api-first-spec). Cada endpoint corresponde a un handler y a un endpoint definido en la spec.

**Validación previa a siguiente nivel**:
- [ ] Cada endpoint definido en api-first-spec tiene su implementación
- [ ] Requests validados con Pydantic o Zod
- [ ] Responses envueltos en ApiResponse<T> consistente
- [ ] Endpoints agrupados por módulo (grupos de rutas)
- [ ] Método HTTP correcto (GET para list/get, POST para create, PUT/PATCH para update, DELETE)
- [ ] URLs siguen convención RESTful (/api/v1/{modulo}/{id})
- [ ] Dependency injection registrada para handlers y servicios
- [ ] Status codes HTTP correctos (200, 201, 204, 400, 404, 500)
- [ ] Documentación de endpoint (Summary, Tags, ResponseType)

**Tiempo estimado**: 90-150 minutos.

**Pitfalls comunes**:
- Endpoints con lógica de negocio (debe estar en handler o servicio)
- Respuestas inconsistentes (distinto formato según endpoint)
- No validar input antes de llamar al handler
- Status codes incorrectos (200 para create en vez de 201)
- Olvidar registrar dependencias en DI container
- No manejar errores de validación con estructura consistente

### Nivel 23 — api-integration

**Qué produce**: Capa de integración que conecta los endpoints con los handlers. Traduce errores de BD a errores HTTP, implementa paginación estándar, normaliza respuestas y aplica transformaciones DTO.

**Input necesario**: Endpoints del nivel anterior (backend-api) y SPs/handlers de niveles previos. El puente entre la capa HTTP y la capa de datos debe ser sólido.

**Validación previa a siguiente nivel**:
- [ ] Errores de BD traducidos a errores HTTP con estructura ApiErrorResponse
- [ ] Paginación implementada con modelo estándar (PageNumber, PageSize, TotalCount, TotalPages, HasNext, HasPrevious)
- [ ] Fechas en formato ISO 8601 consistente
- [ ] Enums serializados como strings (no integers)
- [ ] Null handling: propiedades null se excluyen del response (exclude_none en Pydantic)
- [ ] CORS configurado para dominios permitidos
- [ ] Content-Type consistente (application/json)
- [ ] Errores de validación con estructura de campo + mensaje

**Tiempo estimado**: 45-90 minutos.

**Pitfalls comunes**:
- Fechas en formato local (deben ser UTC + ISO 8601)
- Paginación no consistente entre endpoints
- Enums como números enteros (rompe el contrato del frontend)
- Errores de validación sin estructura (solo mensaje de texto)
- No estandarizar el formato de errores antes del versionado

### Nivel 24 — api-versioning

**Qué produce**: Estrategia de versionado de API implementada. URLs versionadas (/api/v1/, /api/v2/), handlers por versión, compatibilidad hacia atrás, deprecation con sunset headers y migración de consumidores documentada.

**Input necesario**: API completa del nivel anterior (api-integration). La versión 1 (v1) es la implementación actual; versiones futuras añadirán v2, v3, etc.

**Validación previa a siguiente nivel**:
- [ ] URLs versionadas (ej: /api/v1/incidentes)
- [ ] Versión por defecto configurada (v1)
- [ ] Endpoints de v1 funcionales sin cambios
- [ ] Sunset header configurado para versiones deprecadas
- [ ] Deprecation policy documentada en OpenAPI
- [ ] Breaking changes identificados y documentados para próxima versión
- [ ] Estrategia elegida (URI vs header vs media-type) y aplicada consistentemente

**Tiempo estimado**: 30-60 minutos para configuración inicial.

**Pitfalls comunes**:
- Versionado por URI cuando el resto del equipo espera header versioning
- No planificar la migración de consumidores existentes
- No incluir la versión en los logs ni en métricas
- Deprecar endpoints sin aviso ni sunset header
- Copiar controladores enteros para cada versión (código duplicado)

### Nivel 25 — api-resilience

**Qué produce**: Patrones de resiliencia aplicados: circuit breaker para dependencias externas, retry policies con exponential backoff, rate limiting por cliente o tenant, timeouts configurados, bulkheads para aislar recursos críticos.

**Input necesario**: API versionada del nivel anterior (api-versioning). La capa de resiliencia envuelve las llamadas a dependencias externas (BD, otros servicios, APIs de terceros).

**Validación previa a siguiente nivel**:
- [ ] Circuit breaker configurado para cada dependencia externa
- [ ] Retry policy con exponential backoff y jitter
- [ ] Número máximo de retries definido (3-5)
- [ ] Rate limiting configurado por cliente o tenant
- [ ] Timeouts por operación definidos y documentados
- [ ] Fallback responses implementadas para degradación graceful
- [ ] Métricas de resiliencia (circuit state, retry count, rate limit hits) expuestas
- [ ] Bulkheads aislados por recurso crítico (no compartir pool de conexiones)

**Tiempo estimado**: 60-120 minutos.

**Pitfalls comunes**:
- Circuit breaker sin reset (semiconnected state no implementado)
- Retry policy sin jitter (thundering herd problem)
- Rate limiting sin diferenciar por cliente/tenant (afecta a todos por igual)
- No exponer métricas de resiliencia para diagnóstico
- Fallback que retorna datos incorrectos sin logging

### Nivel 26 — openapi-docs

**Qué produce**: Documentación OpenAPI 3.0 completa del módulo. Incluye: endpoints con request/response schemas, ejemplos, códigos de error, tags de agrupación, security schemes, versionado documentado.

**Input necesario**: API completa con integración, versionado y resiliencia de niveles anteriores (backend-api + api-integration + api-versioning + api-resilience). La documentación se genera desde el código (FastAPI built-in OpenAPI / Swagger), no se escribe a mano.

**Validación previa a siguiente nivel**:
- [ ] Todos los endpoints documentados en Swagger UI
- [ ] Schemas de request y response completos con tipos correctos
- [ ] Ejemplos de request/response incluidos
- [ ] Códigos de error documentados (400, 401, 403, 404, 422, 500)
- [ ] Security schemes documentados (Bearer JWT)
- [ ] Tags de agrupación por módulo
- [ ] Versión de API en spec
- [ ] Servers configurados (dev, staging, prod)
- [ ] Spec OpenAPI navegable y válida (sin errores de schema)
- [ ] Endpoints deprecados marcados como deprecated

**Tiempo estimado**: 30-60 minutos.

**Pitfalls comunes**:
- Spec generada con schemas incompletos (faltan propiedades)
- No incluir ejemplos de error (solo de éxito)
- No documentar security schemes (Swagger UI no muestra el botón Authorize)
- Tags inconsistentes (cada endpoint usa un tag distinto)
- Spec con errores de validación que rompen herramientas cliente

## Prompt templates por nivel

Cada prompt activa la skill correspondiente. El agente debe cargar la skill ANTES de ejecutar el prompt usando la herramienta `skill` con el nombre indicado.

### Nivel 17 — database-modeling

**Skill a cargar**: `database-modeling`

**Input**: API spec del módulo (api-first-spec)

**Prompt template**:
```
Basado en la especificación del módulo {modulo}, crea el modelo de datos completo.

Entidad principal: {entidad_principal}
Entidades relacionadas: {entidades_relacionadas}
Esquema de base de datos: {schema}

Requerimientos:
1. Crea las tablas con columnas, tipos, constraints (PK, FK, UNIQUE, CHECK, DEFAULT)
2. Incluye columnas de auditoría: created_at, created_by, updated_at, updated_by
3. Soft delete con columna RecordStatus (A=Activo, I=Inactivo) o deleted_at
4. Índices para todas las FKs y columnas de búsqueda frecuente
5. CHECK constraints para campos con dominio cerrado (estados, tipos)
6. Tablas en plural, columnas en singular
7. Usa el esquema {schema}, no public por defecto
8. Relaciones many-to-many resueltas con tabla puente

Reglas de negocio que impactan el modelo:
- {regla_1}
- {regla_2}
- {regla_3}

Validaciones post-generación:
- [ ] Cada tabla tiene PK
- [ ] Cada FK tiene índice
- [ ] Tipos correctos (VARCHAR con longitud, DECIMAL con precisión)
- [ ] CHECK constraints documentadas
```

### Nivel 18 — database-sp

**Skill a cargar**: `database-sp`

**Input**: Modelo de datos del nivel anterior

**Prompt template**:
```
Basado en el modelo de datos del módulo {modulo}, crea los stored procedures para las siguientes tablas: {lista_tablas}.

Para cada tabla, genera:

1. usp_{schema}_{Entidad}_List — Listado paginado con filtros
    - Parámetros: p_page_number INT, p_page_size INT, p_sort_column VARCHAR, p_sort_direction VARCHAR, p_{filtro1} TYPE, p_{filtro2} TYPE
   - OFFSET/FETCH pagination
   - Ordenamiento dinámico seguro (whitelist de columnas)
   - RETURN SELECT con TotalCount

2. usp_{schema}_{Entidad}_Get — Obtener por ID
    - Parámetro: p_id TYPE
   - RETURN SELECT con todas las columnas

3. usp_{schema}_{Entidad}_Create — Crear registro
   - Parámetros para todas las columnas NO auto-generadas
    - RETURNING id
   - Validar unicidad si aplica

4. usp_{schema}_{Entidad}_Update — Actualizar registro
   - Parámetros para todas las columnas editables
   - Verificar existencia antes de actualizar (IF NOT EXISTS RETURN error)
   - Validar unicidad si aplica

5. usp_{schema}_{Entidad}_Delete — Eliminar registro
   - Si soft delete: UPDATE RecordStatus = 'I', updated_at, updated_by
   - Si físico: DELETE con verificación de existencia
   - RETURN éxito/fracaso con código de error

6. usp_{schema}_{Entidad}_Search — Búsqueda (solo si aplica)
    - Parámetro p_search_term VARCHAR
   - Búsqueda con LIKE o Full-Text Search

Convenciones:
- EXCEPTION en todos los SPs
- Códigos de error estandarizados: 0=éxito, 1=no encontrado, 2=duplicado, 3=error genérico
- Nombres de parámetros iguales a nombres de columnas
- Usar BEGIN; ... COMMIT; en operaciones multi-tabla
```

### Nivel 19 — database-migrations

**Skill a cargar**: `database-migrations`

**Input**: SQL completo del módulo (tablas + SPs)

**Prompt template**:
```
Basado en el modelo de datos y SPs del módulo {modulo}, genera los scripts de migración versionados.

Estructura de archivos:
- V1__Create_{modulo}_Tables.sql — Creación de tablas
- V1__Create_{modulo}_Tables_rollback.sql — Drop de tablas (orden inverso)
- V2__Create_{modulo}_SPs.sql — Creación de SPs
- V2__Create_{modulo}_SPs_rollback.sql — Drop de SPs
- V3__Create_{modulo}_Indexes.sql — Índices adicionales
- V3__Create_{modulo}_Indexes_rollback.sql — Drop de índices

Requisitos:
1. Cada migración debe ser idempotente (IF NOT EXISTS / IF EXISTS)
2. Migraciones en orden secuencial estricto
3. Rollback funcional y probado
4. Separar DDL de datos (no mezclar CREATE con INSERT)
5. Migraciones de SPs después de migraciones de tablas
6. Usar ; para separar statements (PostgreSQL)
```

### Nivel 20 — database-seeding

**Skill a cargar**: `database-seeding`

**Input**: Migraciones aplicadas

**Prompt template**:
```
Basado en las tablas del módulo {modulo}, genera los scripts de seed para los catálogos y datos maestros.

Tablas a seedear: {tablas_catalogo}

Para cada catálogo:
1. Usa MERGE (UPSERT) para idempotencia
2. Incluye todas las columnas no auto-generadas
3. IDs explícitos (no auto-increment) para referencias estables
4. Archivo separado por catálogo: Seed_{Catalogo}.sql

Ejemplo MERGE:
```sql
MERGE INTO {schema}.{Tabla} AS target
USING (VALUES (1, 'Valor', 'Descripción')) AS source (Id, Nombre, Descripcion)
ON target.Id = source.Id
WHEN MATCHED THEN UPDATE SET Nombre = source.Nombre, Descripcion = source.Descripcion
WHEN NOT MATCHED THEN INSERT (Id, Nombre, Descripcion) VALUES (source.Id, source.Nombre, source.Descripcion);
```

Orden de seeds respetando dependencias de FK:
{orden_seeds}

Si se requieren fixtures de prueba, crearlos en archivo aparte: Seed_{modulo}_TestData.sql
```

### Nivel 21 — data-access

**Skill a cargar**: `data-access`

**Input**: SPs del módulo

**Prompt template**:
```
Basado en los stored procedures del módulo {modulo}, crea los handlers de acceso a datos.

Para cada SP del módulo, crea un método en el handler {Entidad}Handler:

1. ListAsync(ListRequest request) → llama a usp_{schema}_{Entidad}_List
   - Parámetros: PageNumber, PageSize, SortColumn, SortDirection, filtros
   - Retorno: PaginatedResult<{Entidad}Dto>

2. GetAsync(int id) → llama a usp_{schema}_{Entidad}_Get
   - Parámetros: Id
   - Retorno: {Entidad}Dto o null

3. CreateAsync(Create{Entidad}Request request) → llama a usp_{schema}_{Entidad}_Create
   - Parámetros: mapeados del request
   - Retorno: int (Id creado)

4. UpdateAsync(int id, Update{Entidad}Request request) → llama a usp_{schema}_{Entidad}_Update
   - Verificar existencia antes de actualizar
   - Retorno: bool

5. DeleteAsync(int id) → llama a usp_{schema}_{Entidad}_Delete
   - Retorno: bool

Requisitos:
- Usar SQLAlchemy para ejecución de consultas
- Mapeo de columnas con SQLAlchemy (no manual)
- Traducción de errores de BD a excepciones de dominio
- PaginatedResult<T> con TotalCount, PageNumber, PageSize, Items
- SQL connection inyectada (no crear nuevas conexiones)
- Métodos asíncronos (async def)
- Comentarios con descripción de parámetros y tipo de retorno
- Transacciones explícitas para operaciones multi-tabla
```

### Nivel 22 — backend-api

**Skill a cargar**: `backend-api`

**Input**: Handlers del nivel anterior + api-first-spec

**Prompt template**:
```
Basado en los handlers del módulo {modulo} y la especificación api-first-spec, crea los endpoints de API.

Endpoint group: /api/v1/{modulo}

Endpoints a implementar:

1. GET /api/v1/{modulo}
   → Handler: ListAsync
   → Response: ApiResponse<PaginatedResult<{Entidad}Dto>>
   → Query params: PageNumber, PageSize, SortColumn, SortDirection, filtros

2. GET /api/v1/{modulo}/{id}
   → Handler: GetAsync
   → Response: ApiResponse<{Entidad}Dto>
   → Si null: 404 NotFound

3. POST /api/v1/{modulo}
   → Handler: CreateAsync
   → Request: Create{Entidad}Request (validado con Pydantic)
   → Response: ApiResponse<int> (201 Created con Location header)
   → Si error validación: 400 BadRequest

4. PUT /api/v1/{modulo}/{id}
   → Handler: UpdateAsync
   → Request: Update{Entidad}Request (validado)
   → Response: ApiResponse<bool> (200 OK)
   → Si no existe: 404 NotFound

5. DELETE /api/v1/{modulo}/{id}
   → Handler: DeleteAsync
   → Response: ApiResponse<bool> (200 OK)
   → Si no existe: 404 NotFound

Requisitos:
- ApiResponse<T> como wrapper único de respuesta
- Pydantic para request validation
- Status codes correctos (201 para create, 204 para delete exitoso sin body)
- Dependency injection de handlers
- Route groups por módulo
- Docstrings / descripciones en cada endpoint
- Tags de Swagger agrupados por módulo
- Endpoints protegidos con Depends(auth_required) si aplica
```

### Nivel 23 — api-integration

**Skill a cargar**: `api-integration`

**Input**: Endpoints del nivel anterior + SPs/handlers

**Prompt template**:
```
Basado en los endpoints del módulo {modulo} y los handlers existentes, implementa la capa de integración DB→API.

Requerimientos:

1. Mapeo de errores DB→HTTP:
   - NotFoundException → 404
   - DuplicateException → 409 Conflict
   - ValidationException → 422 Unprocessable Entity
   - UnauthorizedException → 403 Forbidden
    - DatabaseError / IntegrityError → 500 con error genérico (no exponer detalles internos)

2. Paginación estandarizada:
   - PaginatedResult<T> con: Items, TotalCount, PageNumber, PageSize, TotalPages
    - Calcular TotalPages = math.ceil(TotalCount / PageSize)
   - Incluir HasNext, HasPrevious en response

3. Normalización de respuestas:
   - Fechas en formato ISO 8601 UTC
   - Enums serializados como strings
    - Propiedades null excluidas del JSON (exclude_none=True / exclude_unset=True en Pydantic)
   - Nombres de propiedades en camelCase

4. Transformaciones DTO:
   - Entity → DTO en handler (no en endpoint)
   - Request → SP params en handler (no en endpoint)
   - No exponer entidades de BD directamente en API

Validaciones:
- [ ] Todos los errores de BD tienen traducción HTTP
- [ ] Paginación consistente entre endpoints
- [ ] Fechas en UTC ISO 8601
- [ ] Enums como strings
- [ ] Null handling configurado
```

### Nivel 24 — api-versioning

**Skill a cargar**: `api-versioning`

**Input**: API completa del nivel anterior

**Prompt template**:
```
Basado en la API del módulo {modulo}, implementa el versionado de endpoints.

Estrategia elegida: {URI / Header / Media-type}

Para URI versioning:
1. Configura el route prefix: /api/v{{version}}/{modulo}
2. Endpoints actuales pasan a ser v1
3. Crea un endpoint de versión que devuelva las versiones disponibles

Configuración:
- Default version: 1.0
- Version reader: FromUrlSegment o FromHeader o FromMediaType
- ReportApiVersions = true (incluir api-supported-versions header)
- Deprecated version en endpoint: marcar con deprecated=True en el decorador de ruta

Ejemplo de headers de respuesta:
```
api-supported-versions: 1.0, 2.0
api-deprecated-versions: 1.0
sunset: Sun, 01 Jan 2028 23:59:59 GMT
```

Documentación de deprecation para incluir en OpenAPI:
- Endpoints deprecados marcados como deprecated: true
- Descripción con fecha de sunset y versión recomendada
```

### Nivel 25 — api-resilience

**Skill a cargar**: `api-resilience`

**Input**: API versionada del nivel anterior

**Prompt template**:
```
Basado en la API versionada del módulo {modulo}, implementa los patrones de resiliencia.

Dependencias externas identificadas:
- {dependencia_1} (BD)
- {dependencia_2} (API externa)
- {dependencia_3} (servicio interno)

Para cada dependencia, configura:

1. Circuit Breaker:
   - Failure threshold: 50% de requests fallidas en ventana de 30 segundos
   - Sampling duration: 30 segundos
   - Minimum throughput: 10 requests
   - Break duration: 60 segundos
   - Half-open: permitir 1 request para probar recuperación

2. Retry Policy:
   - Max retries: 3
   - Delay: 200ms, 400ms, 800ms (exponential backoff)
   - Jitter: añadir random 0-100ms
   - Retry on: timeout, transient failures (500, 503)

3. Timeout:
   - BD queries: 30 segundos
   - API externas: 10 segundos
   - Operaciones batch: 120 segundos

4. Rate Limiting:
   - Fixed window: 100 requests / minuto por tenant
   - Concurrency limit: 20 requests simultáneas
   - Queue limit: 10 (con rejection policy)

5. Fallback:
   - Response con datos cacheados si disponibles
   - Mensaje degradado si no hay fallback
   - Logging de fallback activado

Métricas a exponer:
- Circuit state (open/closed/half-open) por dependencia
- Retry count por operación
- Rate limit hits por tenant
- Timeout count por operación
```
### Nivel 26 — openapi-docs

**Skill a cargar**: `openapi-docs` (o `swagger`)

**Input**: API completa de todos los niveles anteriores

**Prompt template**:
```
Basado en los endpoints del módulo {modulo}, genera la documentación OpenAPI 3.0 completa.

Configuración de FastAPI / Swagger:

1. Info:
   - Title: "{modulo} API"
   - Description: "API de {modulo} - {descripcion_modulo}"
   - Version: "v1" (o la versión actual)

2. Security:
   - Scheme: Bearer JWT
   - Description: "JWT Authorization header using the Bearer scheme"

3. Endpoint documentation:
   - Summary descriptivo para cada endpoint
   - Tags = "{modulo}" (consistente entre endpoints)

4. Schema examples:
   - ApiResponse<T> genérico documentado
   - PaginatedResult<T> documentado
   - Cada DTO con ejemplo de valores

5. Error responses:
   - 400: ValidationErrorResponse (campo + mensaje)
   - 401: ApiResponse (no autorizado)
   - 403: ApiResponse (sin permisos)
   - 404: ApiResponse (no encontrado)
   - 422: ValidationErrorResponse
   - 500: ApiResponse (error interno, sin detalles)

Validación final:
- [ ] Spec válida sin errores (verificar con validador OpenAPI)
- [ ] Todos los schemas tienen tipos correctos
- [ ] Todos los endpoints tienen summary y tags
- [ ] Security scheme configurado
- [ ] Ejemplos de error incluidos
- [ ] Servers configurados (localhost, dev, staging)
```

## Verificaciones entre niveles

Cada handoff entre niveles debe validarse con la siguiente checklist. Si alguna verificación falla, NO avanzar al siguiente nivel hasta corregir.

### database-modeling → database-sp

- [ ] Cada columna de cada tabla tiene un SP que la referencia
- [ ] Tipos de datos en SPs coinciden con tipos de columnas (VARCHAR(n) → VARCHAR(n), INT → INT)
- [ ] Longitudes de VARCHAR coinciden (VARCHAR(50) en tabla = VARCHAR(50) en SP)
- [ ] Precisión de DECIMAL coincide (DECIMAL(18,2) en tabla = DECIMAL(18,2) en SP)
- [ ] Columnas NOT NULL en tabla tienen parámetros NOT NULL en SP (o valor por defecto)
- [ ] Columnas con DEFAULT en tabla no son obligatorias en SP Create
- [ ] FK references existen en tablas referenciadas
- [ ] Índices de FK cubren todas las columnas de FK
- [ ] CHECK constraints están reflejadas en validaciones de SPs
- [ ] Columnas audit (created_at, updated_at) no son parámetros de SPs Create/Update (se asignan automáticamente con NOW())

### database-sp → database-migrations

- [ ] Todos los SPs están incluidos en scripts de migración (ninguno manual en BD)
- [ ] Migración de tablas (V1) ejecuta antes de migración de SPs (V2+)
- [ ] Migraciones incluyen tanto CREATE como sus correspondientes DROP (rollback)
- [ ] SPs con dependencias entre sí (un SP llama a otro) están en orden correcto
- [ ] No hay SPs hardcodeados en migraciones sin verificar idempotencia
- [ ] Scripts de migración no contienen datos (solo DDL y SPs)
- [ ] Nombres de SPs consistentes entre migración y definición original

### database-migrations → database-seeding

- [ ] Tablas referenciadas en seeds existen en migraciones ejecutadas
- [ ] Columnas usadas en seeds coinciden con columnas de las tablas
- [ ] IDs de seeds no chocan con secuencias auto-incrementales
- [ ] Orden de seeds respeta dependencias de FK
- [ ] Seeds de catálogos referenciados por FKs existen ANTES de los datos transaccionales
- [ ] MERGE usa columnas que existen en la tabla (verificar nombres exactos)
- [ ] Si se insertan IDs explícitos en columnas serial/identity, usar OVERRIDING SYSTEM VALUE

### database-seeding → data-access

- [ ] Handlers referencian nombres de SPs exactos (incluyendo esquema)
- [ ] Número de parámetros del handler coincide con número de parámetros del SP
- [ ] Tipos de parámetros del handler coinciden con tipos de SP (Python int → SQL INT, Python str → SQL VARCHAR)
- [ ] Parámetros opcionales del SP tienen valor por defecto en handler
- [ ] Columnas devueltas por SP List coinciden con propiedades del DTO
- [ ] Columnas devueltas por el SP (RETURNS TABLE) se mapean en handler
- [ ] Paginación: SP devuelve TotalCount y handler lo mapea correctamente
- [ ] Tipos de retorno: SP devuelve INT y handler retorna int (async)

### data-access → backend-api

- [ ] Cada método del handler expuesto tiene un endpoint correspondiente
- [ ] Tipos de request del endpoint coinciden con parámetros del handler
- [ ] Tipos de response del endpoint coinciden con tipos de retorno del handler
- [ ] Validaciones de request no contradicen constraints de BD (ej: Required en campo NOT NULL)
- [ ] Registros de DI: handler registrado como dependencia (per-request o singleton según corresponda)
- [ ] Status codes HTTP alineados con resultados del handler (null→404, exception→500)
- [ ] ApiResponse<T> envuelve el tipo de retorno correcto
- [ ] Parámetros de ruta del endpoint coinciden con parámetros del handler (id→id)

### backend-api → api-integration

- [ ] Traducción de errores cubre todas las excepciones que puede lanzar el handler
- [ ] Paginación expuesta en endpoint coincide con paginación del handler (mismos nombres de parámetros)
- [ ] Formato ISO 8601 aplicado a todas las fechas en responses
- [ ] CamelCase configurado para serialización JSON
- [ ] Enums con serialización como string (use_enum_values en Pydantic)
- [ ] Null handling: propiedades null excluidas o incluidas según convención
- [ ] CORS permite orígenes correctos (no permitir * en producción)
- [ ] Content-Type application/json en todos los responses
- [ ] Errores de validación tienen estructura ApiErrorResponse (no solo mensaje)

### api-integration → api-versioning

- [ ] Versión actual (v1) funcional y testeada ANTES de versionar
- [ ] Endpoints envueltos en grupo de ruta versionado (/api/v1/{modulo})
- [ ] No hay breaking changes entre la implementación actual y la v1
- [ ] Si hay cambios en ruta, hay redirección 301/308 de ruta antigua a nueva
- [ ] Version reader configurado (URL, header o media-type)
- [ ] API Explorer configurado para descubrir versiones

### api-versioning → api-resilience

- [ ] Endpoints versionados funcionan correctamente sin resiliencia aplicada (baseline)
- [ ] Timeouts configurados antes de retry/circuit breaker (para no enmascarar lentitud)
- [ ] Rate limits no afectan endpoints de health check / version info
- [ ] Fallback responses no rompen contratos de versión (mismo schema ApiResponse<T>)
- [ ] Métricas de resiliencia no afectan performance en ruta crítica

### api-resilience → openapi-docs

- [ ] Todos los endpoints (incluyendo fallback) documentados en OpenAPI
- [ ] Rate limit headers documentados (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
- [ ] Timeout documentado como posible error (504 Gateway Timeout)
- [ ] Circuit breaker documentado como posible error (503 Service Unavailable)
- [ ] Versiones deprecadas marcadas como deprecated=true en spec
- [ ] Sunset headers documentados en spec
- [ ] Security scheme documentado (Bearer JWT)
- [ ] Servers configurados para todos los entornos

### Validación transversal (todos los niveles)

- [ ] No hay secretos hardcodeados en ningún archivo
- [ ] Nombres consistentes en todo el flujo (entidad, columna, SP, handler, endpoint)
- [ ] Convenciones de código del proyecto seguidas en todos los archivos
- [ ] Todos los archivos nuevos tienen copyright/header según convención
- [ ] Logging implementado en puntos críticos (handlers, endpoints, fallback)
- [ ] Tests unitarios creados para lógica no trivial (validaciones, transformaciones)
- [ ] Scripts de BD, handlers y endpoints agregan al repo en el mismo commit (atomicidad)
- [ ] No hay errores de linting (ruff/flake8) en backend
- [ ] La API responde correctamente desde Swagger UI
