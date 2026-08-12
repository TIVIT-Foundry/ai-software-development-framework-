---
name: backend-api
description: 'Backend API structure: modules, features, requests, responses, endpoints/controllers.
  Uses Python FastAPI. Trigger: When creating API endpoints, requests, responses, or project structure.'
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: mandatory
  depends_on:
  - database-sp
  consumed_by:
  - agent-backend
  - agent-fullstack
  - api-first-backend
  - api-gateway
  - api-integration
  - api-resilience
  - api-versioning
  - app-bootstrap
  - costos-llm
  - data-access
  - file-upload
  - graphql
  - notifications
  - openapi-docs
  - performance
  - real-time
  - redis
  - unit-testing
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: architecture-consistency
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Use typed response wrappers | ALWAYS | Type safety |
| Validate all inputs before reaching business logic | ALWAYS | Fast fail |
| Put sort defaults in Service, not Request | ALWAYS | Single source of truth |
| Use auth context for current user identity | ALWAYS | Never trust client-sent user ID |
| Endpoints are thin — no business logic | ALWAYS | Separation of concerns |

## Project Structure (Python FastAPI)
```
{module}/
├── router.py
├── service.py
├── repository.py
├── schemas.py
├── dependencies.py
└── models.py
```

## HTTP Method → Status Code Mapping
| Method | Success Code | Pattern |
|--------|-------------|---------|
| GET (single) | 200 | `ApiResponse.ok(data)` |
| GET (list) | 200 | `ApiResponse.ok_list(items, pagination)` |
| POST | 201 | `status.HTTP_201_CREATED` |
| PUT | 200 | `ApiResponse.ok(data)` |
| DELETE | 200 | `ApiResponse.ok(data)` |

## Patrones por stack tecnológico

### Python FastAPI

#### 1. Endpoint con @router
```python
# ordenes/router.py
from fastapi import APIRouter, Depends, status
from ..schemas import OrdenCreate, OrdenOut, ApiResponse
from ..services import OrdenService

router = APIRouter(prefix="/api/v1/ordenes", tags=["Ordenes"])

@router.get("/{orden_id}", response_model=ApiResponse[OrdenOut])
async def get_orden(
    orden_id: int,
    service: OrdenService = Depends()
) -> ApiResponse[OrdenOut]:
    return ApiResponse.ok(service.get_by_id(orden_id))

@router.post("/", response_model=ApiResponse[OrdenOut], status_code=status.HTTP_201_CREATED)
async def create_orden(
    payload: OrdenCreate,
    service: OrdenService = Depends()
) -> ApiResponse[OrdenOut]:
    return ApiResponse.ok(service.create(payload))
```
> **Cuándo usarlo:** APIs rápidas de prototipado o producción en Python. El `APIRouter` permite modularidad. Combinar con `Depends()` para inyección automática del servicio.

#### 2. Inyección de dependencias con Depends
```python
# ordenes/dependencies.py
from functools import lru_cache
from ..repository import OrdenRepository
from ..services import OrdenService

@lru_cache
def get_orden_repository() -> OrdenRepository:
    return OrdenRepository()

def get_orden_service() -> OrdenService:
    return OrdenService(repo=get_orden_repository())

# En router:
@router.get("/{orden_id}")
async def get_orden(
    orden_id: int,
    service: OrdenService = Depends(get_orden_service)
):
    ...
```
> **Cuándo usarlo:** FastAPI resuelve dependencias en cada request con `Depends()`. Usar factory functions para configurar el grafo de dependencias. Para singletons (conexiones DB, configuración), usar `@lru_cache` o `dependency-injector`.

#### 3. Modelos Pydantic
```python
# ordenes/schemas.py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Generic, TypeVar

T = TypeVar("T")

class OrdenCreate(BaseModel):
    cliente_id: int = Field(..., gt=0, description="ID del cliente")
    items: list[OrdenItemCreate] = Field(..., min_length=1)
    notas: Optional[str] = Field(None, max_length=500)

    @field_validator("notas")
    @classmethod
    def sanitize_notas(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v

class OrdenOut(BaseModel):
    id: int
    cliente_id: int
    estado: str
    creado_en: datetime

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    errors: Optional[list[dict]] = None

    @classmethod
    def ok(cls, data: T, message: str = "Success") -> "ApiResponse[T]":
        return cls(success=True, data=data, message=message)

    @classmethod
    def fail(cls, message: str, errors: list[dict] = None) -> "ApiResponse":
        return cls(success=False, message=message, errors=errors)
```
> **Cuándo usarlo:** Pydantic valida tipos, rangos y longitudes con `Field()`, y lógica custom con `@field_validator`. Los modelos también generan el schema OpenAPI automáticamente — una sola fuente de verdad.

#### 4. Validación con Pydantic
| Code | Validate in |
|------|-------------|
| VAL_001 (Required) | Pydantic Field |
| VAL_002 (Format) | Pydantic Field / @field_validator |
| VAL_003 (Duplicate) | DB/SP |
| VAL_007 (Out of range) | Pydantic Field |
| VAL_008 (Length exceeded) | Pydantic Field |

```python
from pydantic import BaseModel, Field

class UpdateEntityRequest(BaseModel):
    contact_phone: str = Field(
        ...,
        min_length=9,
        max_length=15,
        pattern=r'^\d{9,15}$'
    )
```
