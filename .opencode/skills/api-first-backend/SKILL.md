---
name: api-first-backend
description: 'Generate backend code from OpenAPI spec: Database objects, Handlers/Services,
  Endpoints. DB-driven approach: data access first, then API layer. Uses Python FastAPI + SQLAlchemy.
  Trigger: When implementing backend from OpenAPI spec, generating code from endpoints.'
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: mandatory
  depends_on:
  - api-first-spec
  - database-sp
  consumed_by:
  - agent-backend
  - agent-fullstack
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: skill-contract
mcp_usage: none
---

## Workflow
OpenAPI Spec → Parse → DB objects (DB first) → Handler/Service → DTOs → Endpoint

## Method → Pattern Mapping

| HTTP Method | Action | Handler/Service | DB Object Prefix |
|-------------|--------|-----------------|------------------|
| `GET` (list) | List | `list_{entity}` | `list_{entities}` |
| `GET` (single) | Get | `get_{entity}` | `get_{entity}` |
| `POST` | Create | `create_{entity}` | `create_{entity}` |
| `PUT` | Update | `update_{entity}` | `update_{entity}` |
| `DELETE` | Delete | `delete_{entity}` | `delete_{entity}` |
| `POST` (operation) | {Verb} | `{verb}_{entity}` | `{verb}_{entity}` |
| `POST` (remove) | Remove | `remove_{entity}` | `remove_{sub_entity}` |
| `PUT` (reorder) | Reorder | `reorder_{entity}` | `reorder_{sub_entities}` |

## Type Mapping
| OpenAPI Type | Python Type | SQL Type (PostgreSQL) |
|--------------|-------------|----------------------|
| `integer` | `int` | `INTEGER` |
| `integer` (int64) | `int` | `BIGINT` |
| `number` | `Decimal` | `NUMERIC(18,2)` |
| `string` | `str` | `VARCHAR` |
| `string` (date) | `date` | `DATE` |
| `string` (date-time) | `datetime` | `TIMESTAMP` |
| `boolean` | `bool` | `BOOLEAN` |

## Error Pattern (Function → Handler)
DB operations return business errors via result rows (not exceptions):
```sql
-- PL/pgSQL example
IF p_amount <= 0 THEN
    RETURN QUERY SELECT 'VAL_001'::TEXT AS error_code, 'Amount'::TEXT AS field, 'Amount must be greater than 0'::TEXT AS message;
    RETURN;
END IF;
```
Handler/Service maps error result to typed domain exception.

## Endpoint Key Conventions
| Convention | Pattern |
|-----------|---------|
| Validation | Validate POST/PUT before reaching handler |
| Handler injection | Dependency Injection via `Depends()` |
| Current user | From auth context / dependency |
| Success response | `ApiResponse.ok(data)` |
| Created response | 201 with Location header |

## Common Operations
| Operation | Verb | Request Body |
|-----------|------|-------------|
| Submit | submit | `{}` or optional |
| Cancel | cancel | `{ reason? }` |
| Approve | approve | `{ notes? }` |
| Reject | reject | `{ reason }` |

## Checklist
- [ ] DB objects created
- [ ] DB errors handled properly (error result → typed exception)
- [ ] Handler/Service calls DB object
- [ ] Input validation for required/format/length
- [ ] Endpoint wired to handler
- [ ] Module/router registered

## Workflow completo: De spec a endpoint funcional

### 1. Inputs

La skill `api-first-spec` produce un documento de especificación por módulo que es el contrato de entrada. Antes de generar código, el agente de backend debe extraer del spec:

- **ERD**: entidades, atributos, claves primarias/foráneas y relaciones (uno-a-uno, uno-a-muchos, muchos-a-muchos).
- **Catálogos y estados**: tablas de catálogo (`Status`, `Type`, `Category`) y enumeraciones de estado de la entidad.
- **Endpoints**: tabla con `Method`, `Path`, `Path params`, `Query params`, `Request body`, `Response body` y `Roles` permitidos.
- **DB objects**: lista de funciones PL/pgSQL, queries o vistas a crear con su nombre y firma.
- **DTOs**: input/output de cada endpoint, tipados con Pydantic.
- **Reglas de negocio**: validaciones de unicidad, rangos, dependencias, transiciones de estado, fechas permitidas.
- **Códigos de error**: catálogo tipado (`VAL_001`, `BIZ_002`, `NF_001`, `SYS_001`) con mensaje y campo asociado.

El flujo de generación es: **Función → handler → DTOs → endpoint → test → registro en módulo**. Nunca se invierte el orden: la base de datos define el contrato.

### 2. Step 1 — Generar Funciones (PL/pgSQL)

**Convención de nombrado**: `{acción}_{entidad}` en snake_case. Cada función reside en el schema del dominio (e.g. `sales`, `inventory`).

| Operación | Ejemplo |
|-----------|---------|
| Listar | `sales.list_customers` |
| Obtener uno | `sales.get_customer` |
| Crear | `sales.create_customer` |
| Actualizar | `sales.update_customer` |
| Eliminar | `sales.delete_customer` |
| Buscar con filtros | `inventory.search_products` |
| Operación custom | `orders.approve_order`, `invoices.cancel_invoice`, `inventory.reorder_categories` |

**Convención de parámetros**:
- Prefijo `p_` para inputs: `p_name`, `p_email`, `p_phone`.
- `p_creation_user`, `p_update_user` (auditoría).
- `p_record_status` para filtros de soft delete (default `TRUE`).
- Para listados: `p_page_number`, `p_page_size`, `p_sort_by`, `p_sort_direction`.

**Plantilla de función (PL/pgSQL / PostgreSQL)**:

```sql
CREATE OR REPLACE FUNCTION {schema}.{action}_{entity}(
    p_name          VARCHAR(200),
    p_other_field   INTEGER DEFAULT NULL,
    p_creation_user VARCHAR(100),
    p_record_status BOOLEAN DEFAULT TRUE
)
RETURNS TABLE (
    entity_id   BIGINT,
    name        VARCHAR(200)
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- ── Validación de input ──────────────────────────────────
    IF p_name IS NULL OR TRIM(p_name) = '' THEN
        RAISE EXCEPTION 'VAL_001|Name|Name is required';
    END IF;

    -- ── Regla de negocio: unicidad ──────────────────────────
    IF EXISTS (
        SELECT 1
        FROM   {schema}.{entity}
        WHERE  name = p_name
          AND  record_status = TRUE
    ) THEN
        RAISE EXCEPTION 'BIZ_001|Name|Name already exists';
    END IF;

    -- ── Inserción ───────────────────────────────────────────
    RETURN QUERY
        INSERT INTO {schema}.{entity} (
            name, other_field, creation_user, creation_date, record_status
        ) VALUES (
            p_name, p_other_field, p_creation_user, NOW(), TRUE
        )
        RETURNING id, name;
END;
$$;
```

**Convención de error**: Las funciones PostgreSQL usan `RAISE EXCEPTION` con formato `código|campo|mensaje`. El handler parsea la excepción y extrae el `ErrorCode`. Para funciones que retornan tabla de errores (alternativa a RAISE), usar `RETURNS TABLE` y devolver filas con `error_code`, `field`, `message`.

Reglas de función:
- Toda validación de negocio va en la función, no en el handler. El handler solo mapea errores.
- Usar `BEGIN/EXCEPTION WHEN OTHERS` con `GET STACKED DIAGNOSTICS` para errores inesperados (equivalente a TRY/CATCH).
- No usar `RAISE NOTICE` para errores de negocio; usar `RAISE EXCEPTION` con código tipado o `RETURN QUERY SELECT` con `ErrorCode`.
- Devolver siempre al menos un `RETURN NEXT` (incluso en updates/delete), para que el handler pueda inspeccionar el resultado.
- Usar `NOW()` en lugar de `GETDATE()`, `RETURNING` / `RETURN QUERY` en lugar de `SCOPE_IDENTITY()`.

### 3. Step 2 — Crear data-access handler

El handler es el puente entre endpoint y función PL/pgSQL. Recibe request tipado, invoca la función, valida el resultado y devuelve response tipado.

**Python (SQLAlchemy con raw SQL)**:
```python
class CreateCustomerHandler:
    FN_NAME = "sales.create_customer"

    def __init__(self, db: Session):
        self.db = db

    def handle(self, request: CreateCustomerRequest, current_user: str) -> CreateCustomerResponse:
        params = {
            "p_name": request.name,
            "p_email": request.email,
            "p_phone": request.phone,
            "p_creation_user": current_user,
        }
        sql = text(
            "SELECT * FROM sales.create_customer("
            ":p_name, :p_email, :p_phone, :p_creation_user)"
        )
        result = self.db.execute(sql, params).mappings().first()

        SpResultHelper.throw_if_error(result)
        return CreateCustomerResponse(
            customer_id=result["entity_id"],
            name=result["name"],
        )
```

### 4. Step 3 — Definir Request/Response DTOs

Los DTOs son el contrato entre la API y el handler. Viven junto al endpoint.

**Python (Pydantic v2)**:
```python
from pydantic import BaseModel

class CreateCustomerRequest(BaseModel):
    name: str
    email: str
    phone: str | None = None

class CreateCustomerResponse(BaseModel):
    customer_id: int
    name: str

class CreateCustomerSpResult(BaseModel):
    entity_id: int
    name: str | None = None
    error_code: str | None = None
    field: str | None = None
    message: str | None = None
```

Reglas DTO:
- Request y Response son inmutables (Pydantic BaseModel).
- El `SpResult` siempre incluye `error_code`, `field`, `message` para que el handler pueda mapear errores.
- Los nombres de campo del `SpResult` deben coincidir exactamente con los alias del `SELECT` / `RETURNING` de la función (case-sensitive en PostgreSQL).

### 5. Step 4 — Crear endpoint

El endpoint recibe el request HTTP, valida el body, extrae el current user del contexto de auth, llama al handler y envuelve la respuesta en `ApiResponse`.

**FastAPI (Python)**:
```python
@router.post(
    "/customers",
    status_code=201,
    response_model=ApiResponse[CreateCustomerResponse],
)
def create_customer(
    request: CreateCustomerRequest,
    handler: CreateCustomerHandler = Depends(),
    current_user: str = Depends(get_current_user),
) -> ApiResponse[CreateCustomerResponse]:
    response = handler.handle(request, current_user)
    return ApiResponse.ok(
        data=response,
        location=f"/api/v1/customers/{response.customer_id}",
    )
```

### 6. Step 5 — Validaciones y ApiResponse

`ApiResponse` es la envolvente estándar para TODAS las respuestas. Garantiza shape consistente y simplifica el manejo en frontend.

**Shape de referencia**:
```python
class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: ApiError | None = None
    metadata: PaginationMetadata | None = None

class ApiError(BaseModel):
    code: str
    message: str
    field: str | None = None

class PaginationMetadata(BaseModel):
    page_number: int
    page_size: int
    total_records: int
```

**Mapeo de códigos a HTTP status**:

| Caso | ErrorCode prefix | HTTP | Ejemplo |
|------|------------------|------|---------|
| Validación de input fallida | `VAL_*` | 400 | `VAL_001` campo requerido |
| Regla de negocio violada | `BIZ_*` | 422 | `BIZ_001` nombre duplicado |
| Recurso no encontrado | `NF_*` | 404 | `NF_001` |
| No autorizado / token inválido | `AUTH_*` | 401 | — |
| Permiso insuficiente | `AUTHZ_*` | 403 | `AUTHZ_001` |
| Conflicto de concurrencia | `CON_*` | 409 | `CON_001` |
| Error inesperado del sistema | `SYS_*` | 500 | `SYS_001` (loggear stack completo server-side, no exponer al cliente) |

**Reglas de validación**:
- Las validaciones de input se ejecutan ANTES de invocar el handler. Si fallan, nunca se llama a la función.
- Las validaciones de negocio (unicidad, transiciones de estado, fechas) viven en la función PL/pgSQL y se comunican vía `RAISE EXCEPTION` con código tipado.
- El handler traduce el `ErrorCode` a excepción tipada de dominio (`ValidationException`, `BusinessException`, `NotFoundException`).
- Un middleware/exception handler global convierte la excepción a `ApiResponse` con el HTTP status correcto.

### 7. Step 6 — Tests del endpoint

Cada endpoint debe tener al menos: 1 test del happy path, 1 test de validación fallida, 1 test del error de negocio principal.

**pytest + httpx (Python)**:
```python
import pytest
from httpx import ASGITransport, AsyncClient
from main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_customer_with_valid_request_returns_201(client: AsyncClient):
    payload = {"name": "Acme Corp", "email": "test@email.com", "phone": "+15555550100"}
    response = await client.post("/api/v1/customers", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["name"] == "Acme Corp"

@pytest.mark.asyncio
async def test_create_customer_with_empty_name_returns_400(client: AsyncClient):
    response = await client.post("/api/v1/customers", json={"name": "", "email": "test@email.com"})
    assert response.status_code == 400
```

## Checklist de generación

Antes de marcar un endpoint como terminado, verifica que se cumplen TODOS los puntos siguientes.

1. [ ] La función PL/pgSQL existe en la base de datos, reside en el schema correcto y compila sin warnings.
2. [ ] La función sigue la convención de nombrado `{acción}_{entidad}` en snake_case y sus parámetros usan prefijo `p_`.
3. [ ] La función valida TODAS las reglas de negocio declaradas en la spec y emite `RAISE EXCEPTION` con código tipado (`VAL_*`, `BIZ_*`, `NF_*`, `CON_*`).
4. [ ] La función usa `EXCEPTION WHEN OTHERS` con `GET STACKED DIAGNOSTICS` para errores inesperados (equivalente a TRY/CATCH).
5. [ ] La función nunca usa `RAISE NOTICE` para errores de negocio; siempre usa `RAISE EXCEPTION` con `código|campo|mensaje` o `RETURN QUERY SELECT` con `ErrorCode`.
6. [ ] El handler invoca la función con `SELECT * FROM {schema}.{function}(...)` y los parámetros exactos del contrato, propagando `current_user` desde el contexto de auth (no del body).
7. [ ] El handler mapea el `ErrorCode` de la función a excepción tipada de dominio (`ValidationException`, `BusinessException`, `NotFoundException`) vía `SpResultHelper`.
8. [ ] Los DTOs (Request, Response, SpResult) existen en Pydantic y respetan la tabla de mapping de tipos OpenAPI → Python → SQL.
9. [ ] Los nombres de campo del `SpResult` coinciden exactamente con los aliases del `RETURNING` / `SELECT` de la función (case-sensitive en PostgreSQL).
10. [ ] El endpoint valida el body ANTES de invocar el handler y devuelve `ApiResponse` con código `VAL_*` y `field` poblado en caso de fallo.
11. [ ] El endpoint devuelve códigos HTTP correctos: `200`/`201` éxito, `400` validación, `401`/`403` auth, `404` no encontrado, `422` negocio, `409` conflicto, `500` sistema.
12. [ ] El endpoint está protegido por autorización declarativa (`Depends(require_permission(...))`) cuando aplica.
13. [ ] La respuesta está envuelta en `ApiResponse` con shape consistente (`success`, `data`, `error`, `metadata` opcional) en TODOS los casos.
14. [ ] El endpoint está registrado en el router (`app.include_router(entity_router, prefix="/api/v1/{entities}")`).
15. [ ] El endpoint está documentado en OpenAPI/Swagger con summary, descripción, parámetros, request/response schema y códigos de error.
16. [ ] Existe al menos un test del happy path, uno de validación fallida y uno de error de negocio principal.
17. [ ] El endpoint no expone stack traces, queries SQL, ni secretos en respuestas de error; los detalles solo van al log server-side.
18. [ ] La operación respeta multi-tenancy cuando aplica: la función filtra por `tenant_id` y la respuesta nunca fuga datos de otros tenants.
19. [ ] El changelog del módulo registra el endpoint nuevo siguiendo `keepachangelog.com` (Added / Changed / Fixed).
20. [ ] El endpoint pasó code review con la checklist de la skill `code-review` antes de abrir el PR.
