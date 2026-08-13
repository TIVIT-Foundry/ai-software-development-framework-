---
name: error-handling
description: 'Error handling patterns across all layers (Database, Backend, Frontend).
  Uses Python FastAPI. Trigger: When implementing error handling, exceptions, error responses, or error
  UI.'
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: mandatory
  depends_on:
  - data-access
  - database-sp
  - shared-libs
  consumed_by:
  - agent-backend
  - agent-fullstack
  - api-resilience
  - graphql
  - kafka
  agent_roles:
  - control-agent
  - delivery-agent
  - design-agent
  validation_profile: security-review
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Use typed exceptions, not generic `Exception` | ALWAYS | Automatic HTTP mapping |
| Return error codes, not just messages | ALWAYS | Frontend can handle programmatically |
| Log at the boundary, not everywhere | ALWAYS | Avoid duplicate logs |
| Never expose stack traces to clients | NEVER | Security risk |
| Never expose internal system details in error messages | NEVER | Information disclosure |

## Error Flow
```
DB (SELECT ErrorCode) → Handler (ThrowIfError) → Typed Exception → 
Exception Middleware → ApiResponse → Frontend (toast/form error)
```

## Layer-by-Layer Reference

### 1. Database — Función PL/pgSQL con RAISE EXCEPTION
```sql
-- PostgreSQL
CREATE OR REPLACE FUNCTION schema.create_entity(p_amount numeric)
RETURNS TABLE(error_code text, error_field text, error_message text)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_amount <= 0 THEN
        error_code := 'VAL_001';
        error_field := 'Amount';
        error_message := 'Amount must be greater than 0';
        RETURN NEXT;
        RETURN;
    END IF;

    -- Lógica de negocio y retorno exitoso
    -- ...
END;
$$;
```

### 2. Backend Handler — Map errors to typed exceptions
```python
# Python FastAPI
result = await db.execute(text("SELECT * FROM schema.create_entity(:amount)"), {"amount": amount})
row = result.mappings().first()
SpResultHelper.throw_if_error(row)  # raises typed exception if ErrorCode present
return CreateEntityResponse(**row)
```

### 3. Exception Types → HTTP Status
| Exception | HTTP | When |
|-----------|------|------|
| `ValidationException` | 400 | Input invalid |
| `ForbiddenException` | 403 | Authorization failed |
| `NotFoundException` | 404 | Resource not found |
| `ConflictException` | 409 | Duplicate or state conflict |
| `BusinessRuleException` | 422 | Business rule violation |
| `InternalException` | 500 | Unhandled system error |

### 4. Frontend — Toast + Form errors
```typescript
// Logic hook pattern
const handleSubmit = async (data: FormData) => {
    try {
        await createMutation(data, {
            onSuccess: () => toast.success("Created successfully"),
        });
    } catch (err) {
        if (err.errors) {
            // Set form field errors from err.errors array
            err.errors.forEach(e => form.setError(e.field, { message: e.message }));
        } else {
            toast.error(err.message ?? "Unexpected error");
        }
    }
};
```

## Contrato de Respuestas API (canónico — ver también `api-contracts`)

**Convención única del framework:** el envelope se usa SIEMPRE, tanto en éxito como en error. El cliente generado (`api.ts.j2` / Angular `service.ts.j2`) devuelve `data` desenvuelto y lanza `ApiError` en `!ok` **o** en `2xx + success:false` (nunca tratar un error como éxito).

- **Éxito (2xx):** `{ "success": true, "data": {...}, "message": null }`
- **Error (4xx/5xx, o 2xx con success:false):**
```json
{
  "success": false,
  "error": {
    "code": "VAL_001",
    "message": "Validation failed",
    "details": [ { "code": "VAL_001", "field": "Name", "message": "Name is required" } ]
  },
  "data": null,
  "meta": { "trace_id": "550e8400-...", "timestamp": "2026-08-12T10:00:00Z" }
}
```
- `error.code` y `error.message` son obligatorios; `error.details` es opcional (array de `{code, field, message}` para errores de validación de campos, o payload libre para otros errores).
- `meta.trace_id` = `X-Correlation-ID` (ver sección de correlación); `meta.timestamp` = ISO 8601 UTC.
- **Regla para clientes frontend:** si el backend responde HTTP 2xx con `success:false`, es un error de negocio/API y debe propagarse como error, jamás como éxito.

## Python FastAPI Exception Handling

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from uuid import uuid4
from datetime import datetime, timezone

class AppException(HTTPException):
    def __init__(self, status_code: int, code: str, message: str, field: str | None = None):
        self.code = code
        self.field = field
        super().__init__(status_code=status_code, detail=message)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.detail,
                "details": [{"code": exc.code, "field": exc.field, "message": exc.detail}]
                if exc.field else None,
            },
            "data": None,
            "meta": {
                "trace_id": getattr(request.state, "correlation_id", str(uuid4())),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        },
    )
```

## Frontend — Consumo de errores (contrato unificado)

El cliente generado lanza `ApiError { status, code, message, details }` (ver `api.ts.j2`). Consumir así:

```typescript
// Logic hook pattern
const handleSubmit = async (data: FormData) => {
    try {
        await createMutation(data, {
            onSuccess: () => toast.success("Created successfully"),
        });
    } catch (err) {
        if (err instanceof ApiError && Array.isArray(err.details)) {
            // Set form field errors from err.details array {code, field, message}
            err.details.forEach(e => form.setError(e.field, { message: e.message }));
        } else {
            toast.error(err instanceof ApiError ? err.message : "Unexpected error");
        }
    }
};
```

## Security Considerations
- Log full error details server-side only
- Return only error code + user-friendly message to client
- Include a `Ref:` ID in SYS_ errors so clients can report it
- Never include SQL error messages in responses

## Patrones avanzados de manejo de errores

### IDs de correlación de errores (X-Correlation-ID)

Cada solicitud entrante recibe un identificador único de correlación que se propaga a lo largo de toda la cadena de llamada: desde el gateway hasta la base de datos y los servicios descendentes.

```python
# FastAPI — Middleware de correlación
from uuid import uuid4

@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response
```

**Reglas de propagación:**
- Si el header `X-Correlation-ID` llega vacío o no llega, generar uno nuevo (UUID).
- Incluir el `correlationId` en todos los logs estructurados de la solicitud.
- Propagar el ID a llamadas HTTP descendentes via header `X-Correlation-ID`.
- Propagar el ID a la base de datos como parámetro `p_correlation_id` en funciones PL/pgSQL.
- El cliente puede enviar el ID de vuelta al reportar un error para trazabilidad completa.

### Versionado del catálogo de errores por versión de API

Los códigos de error deben estar versionados junto con la API. Una versión nueva puede agregar, deprecar o cambiar códigos, pero nunca eliminarlos sin un proceso de sunset.

```json
{
  "success": false,
  "errors": [
    {
      "code": "VAL_001",
      "field": "Email",
      "message": "Email is required",
      "docUrl": "https://api.example.com/docs/v2/errors/VAL_001",
      "deprecated": false,
      "sunsetOn": null
    }
  ]
}
```

**Convenciones:**
- Cada versión de API publica su catálogo de errores en `{baseUrl}/docs/v{version}/errors`.
- Códigos deprecados incluyen `deprecated: true` y `sunsetOn` con la fecha de remoción.
- Nuevos códigos se agregan con la versión mínima en la que aparecen: `"since": "v2"`.
- Los clientes deben ignorar campos desconocidos en la respuesta de error (regla de extensibilidad).

### Respuestas de error estructuradas

#### FastAPI — HTTPException con formato estandarizado

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

class AppException(HTTPException):
    def __init__(self, status_code: int, code: str, message: str, field: str | None = None):
        self.code = code
        self.field = field
        super().__init__(status_code=status_code, detail=message)

class ValidationException(AppException):
    def __init__(self, code: str, message: str, field: str | None = None):
        super().__init__(status_code=400, code=code, message=message, field=field)

class NotFoundException(AppException):
    def __init__(self, code: str = "NF_001", message: str = "Resource not found"):
        super().__init__(status_code=404, code=code, message=message)

class BusinessRuleException(AppException):
    def __init__(self, code: str, message: str, field: str | None = None):
        super().__init__(status_code=422, code=code, message=message, field=field)

class ForbiddenException(AppException):
    def __init__(self, code: str = "AUTH_001", message: str = "Forbidden"):
        super().__init__(status_code=403, code=code, message=message)

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "errors": [{
                    "code": exc.code,
                    "field": exc.field,
                    "message": exc.detail,
                }],
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        import logging
        logger = logging.getLogger(__name__)
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "errors": [{
                    "code": "SYS_001",
                    "message": "Internal server error",
                }],
            },
        )
```

### Agregación de errores (deduplicación, muestreo y rate limiting)

En entornos de alta concurrencia, el mismo error puede repetirse miles de veces por segundo. La agregación evita saturar el sistema de logs y alertas.

**Deduplicación:**
- Agrupar errores por `{code, field, endpoint}` como clave de deduplicación.
- Si el mismo error ocurre múltiples veces en la misma ventana (ej. 1 minuto), registrar solo el primer evento y contar las ocurrencias.
- Incluir `occurrenceCount` y `firstSeenAt` / `lastSeenAt` en el registro agregado.

**Muestreo (sampling):**
- Aplicar sampling adaptativo: registrar el 100% de los errores de tipo `SYS_*` (críticos), pero solo el 10-20% de errores `VAL_*` repetidos.
- Nunca aplicar sampling a errores nuevos (primera ocurrencia siempre se registra completa).

**Rate limiting de reportes:**
- Implementar circuit breaker en el pipeline de errors: si se excede un umbral de errores/segundo hacia el sistema de observabilidad, aplicar backoff.
- Los errores excedentes se almacenan en un buffer de anillo (ring buffer) y se envían en batch al sistema de observabilidad.
- Idealmente usar una métrica de tipo `error_rate{code, endpoint}` en Prometheus/OTel y alertar sobre picos, no sobre eventos individuales.
