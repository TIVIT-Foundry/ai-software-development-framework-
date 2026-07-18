---
name: api-integration
description: 'DB-to-API integration patterns: error mapping, pagination, validation,
  response structure. Uses Python FastAPI + SQLAlchemy. Trigger: When connecting stored procedures/queries to APIs,
  handling DB errors, or implementing pagination.'
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: mandatory
  depends_on:
  - data-access
  - backend-api
  - database-sp
  consumed_by:
  - agent-backend
  - agent-fullstack
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: architecture-consistency
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Map DB errors to typed domain exceptions | ALWAYS | Consistent error handling |
| Use typed response wrappers (`ApiResponse`) | ALWAYS | Never use untyped/generic |
| Validate format/required at API layer | ALWAYS | Fast fail before DB |
| Validate duplicates/FK/business rules at DB layer | ALWAYS | Data integrity |
| Cap pageSize at a maximum (e.g., 50 or 100) | ALWAYS | Prevent memory issues |

## ApiResponse Data Structure
| Endpoint Type | Data Structure |
|---------------|----------------|
| GET detail | `{ item: {...} }` |
| GET list | `{ items: [...] }` |
| POST create | `{ item: {...} }` |
| PUT update | `{ item: {...} }` |
| DELETE | `{ {entity}Id: int }` |

## Pagination Defaults Behavior
| Parameter | Validation | Normalization |
|-----------|------------|---------------|
| `page` | Required (400 if <= 0) | — |
| `pageSize` | Required (400 if <= 0) | Cap at maxPageSize |
| `sortOrder` | Optional | Default "DESC", uppercase |

## Validation Error Codes
| Code | Description | Validate in |
|------|-------------|-------------|
| `VAL_001` | Required field | API |
| `VAL_002` | Invalid format | API |
| `VAL_003` | Duplicate value | DB |
| `VAL_004` | FK not exists | DB |
| `VAL_006` | Invalid JSON syntax | Middleware |
| `VAL_007` | Out of range | API |
| `VAL_008` | Length exceeded | API |

## Python Pydantic Validation
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

## JSON Response Examples
```json
// List: { "success": true, "data": { "items": [...] }, "pagination": { "page":1, "totalRecords":25 } }
// Detail: { "success": true, "data": { "item": {...} }, "message": "Item retrieved" }
// Error: { "success": false, "errors": [{ "code": "VAL_001", "message": "...", "field": "Name" }] }
```

## Conexión DB→API: Python FastAPI

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/productos", tags=["Productos"])

class ProductoDto(BaseModel):
    id: int
    nombre: str
    precio: float
    categoria: str

class PagedResult(BaseModel):
    items: list[ProductoDto]
    total: int
    page: int
    pageSize: int
    totalPages: int

@router.get("/{producto_id}", response_model=ApiResponse[ProductoDto])
async def obtener_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    prod = await db.get(Producto, producto_id)
    if not prod:
        raise HTTPException(status_code=404, detail={
            "code": "PROD_001", "message": "Producto no encontrado"
        })
    return ApiResponse.ok(ProductoDto(
        id=prod.id, nombre=prod.nombre,
        precio=prod.precio, categoria=prod.categoria.nombre
    ))

@router.get("", response_model=ApiResponse[PagedResult])
async def listar_productos(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Producto)
    if search:
        query = query.where(Producto.nombre.ilike(f"%{search}%"))
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    items = (await db.execute(
        query.offset((page - 1) * pageSize).limit(pageSize)
    )).scalars().all()
    return ApiResponse.ok(PagedResult(
        items=[ProductoDto(id=p.id, nombre=p.nombre, precio=p.precio, categoria=p.categoria.nombre) for p in items],
        total=total, page=page, pageSize=pageSize,
        totalPages=(total + pageSize - 1) // pageSize
    ))

# Error handler
@app.exception_handler(SQLAlchemyError)
async def db_error_handler(request, exc: SQLAlchemyError):
    if "duplicate key" in str(exc):
        raise HTTPException(status_code=409, detail={"code": "DB_003", "message": "Registro duplicado"})
    raise HTTPException(status_code=500, detail={"code": "INT_001", "message": "Error de base de datos"})
```

## Paginación

### Formato de request

```
GET /api/v1/productos?page=1&pageSize=20&search=term&sortBy=nombre&sortOrder=ASC
```

| Parámetro | Tipo | Default | Validación |
|-----------|------|---------|------------|
| `page` | int | 1 | ≥ 1 |
| `pageSize` | int | 20 | 1 – maxPageSize (100) |
| `search` | string | null | Opcional, sanitizado |
| `sortBy` | string | null | Opcional, columna válida |
| `sortOrder` | string | DESC | ASC o DESC |

### Función PL/pgSQL paginada con total count

```sql
CREATE OR REPLACE FUNCTION sp_entity_list(
    p_page       INT DEFAULT 1,
    p_page_size  INT DEFAULT 20,
    p_search     TEXT DEFAULT NULL,
    p_sort_by    TEXT DEFAULT 'id',
    p_sort_order TEXT DEFAULT 'DESC'
)
RETURNS TABLE (
    id            INT,
    nombre        VARCHAR,
    descripcion   TEXT,
    estado        VARCHAR,
    fecha_creacion TIMESTAMPTZ,
    total_count   BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_offset   INT := (p_page - 1) * p_page_size;
    v_order    TEXT;
BEGIN
    -- Construir ORDER BY de forma segura
    v_order := CASE
        WHEN p_sort_by IN ('nombre','estado','fecha_creacion')
        THEN p_sort_by
        ELSE 'id'
    END || ' ' || CASE WHEN UPPER(p_sort_order) = 'ASC' THEN 'ASC' ELSE 'DESC' END;

    RETURN QUERY EXECUTE format(
        'SELECT e.id, e.nombre, e.descripcion, e.estado, e.fecha_creacion,
                COUNT(*) OVER() AS total_count
         FROM {Entity} e
         WHERE ($1 IS NULL OR e.nombre ILIKE ''%%'' || $1 || ''%%'')
         ORDER BY %s
         LIMIT $2 OFFSET $3',
        v_order
    ) USING p_search, p_page_size, v_offset;
END;
$$;
```

### Alternativa: LIMIT/OFFSET con SQLAlchemy (patrón preferido)

La mayoría de los casos no requieren PL/pgSQL. Se resuelve directo en Python:

```python
query = select(Entity)
if search:
    query = query.where(Entity.nombre.ilike(f"%{search}%"))
total = await db.scalar(select(func.count()).select_from(query.subquery()))
items = (await db.execute(
    query.order_by(Entity.nombre.desc())
         .offset((page - 1) * page_size)
         .limit(page_size)
)).scalars().all()
```

### Formato de respuesta

```json
{
  "success": true,
  "data": {
    "items": [
      { "id": 1, "nombre": "Producto A", "precio": 150.00 }
    ]
  },
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 57,
    "totalPages": 3
  }
}
```

### Python / SQLAlchemy — Paginación

```python
def listar_paginado(page: int, page_size: int, search: str | None):
    offset = (page - 1) * page_size
    query = select(Producto)
    if search:
        query = query.where(Producto.nombre.ilike(f"%{search}%"))
    total = db.session.scalar(select(func.count()).select_from(query.subquery()))
    items = db.session.execute(query.offset(offset).limit(page_size)).scalars().all()
    return PagedResult(items=[p.to_dto() for p in items], total=total, page=page, page_size=page_size)
```

### Frontend: uso con @ngneat/query y signals (Angular)

```typescript
// Servicio: src/app/products/services/productos.service.ts
import { injectQuery } from '@ngneat/query';
import { signal } from '@angular/core';
import { inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

export function toQueryString(params: PagedRequest): string {
  return new HttpParams({ fromObject: params as Record<string, unknown> }).toString();
}

export class ProductosService {
  private readonly http = inject(HttpClient);
  private readonly query = injectQuery();

  getProductos(params: PagedRequest) {
    return this.query({
      queryKey: ['productos', params],
      queryFn: () =>
        this.http
          .get<ApiResponse<PagedResult>>(`/api/v1/productos?${toQueryString(params)}`)
          .toPromise(),
    });
  }
}

// Componente: src/app/products/pages/productos-listado/productos-listado.component.ts
import { Component, inject, signal } from '@angular/core';
import { ProductosService } from '../../services/productos.service';

@Component({
  selector: 'app-productos-listado',
  template: `
    @if (query.isLoading()) {
      <app-skeleton />
    } @else {
      <app-tabla [items]="query.data()?.data?.items ?? []" />
      <app-paginador
        [currentPage]="query.data()?.pagination?.page ?? 1"
        [totalPages]="query.data()?.pagination?.totalPages ?? 1"
        (pageChange)="page.set($event); refetch()"
      />
      <span>Total: {{ query.data()?.pagination?.total }} registros</span>
    }
  `,
})
export class ProductosListadoComponent {
  private readonly productosService = inject(ProductosService);

  readonly page = signal(1);
  readonly pageSize = 20;

  readonly query = this.productosService.getProductos({
    page: this.page(),
    pageSize: this.pageSize,
  });

  refetch() {
    this.query.updateQueryKey(['productos', { page: this.page(), pageSize: this.pageSize }]);
  }
}
```

## Mapeo de errores DB → HTTP

### Tabla completa de traducción (PostgreSQL)

| Código SQLSTATE | Condición | HTTP | Código Error | Mensaje para el usuario |
|-----------------|-----------|------|-------------|------------------------|
| `23505` | Unique violation (PK / unique index) | 409 | `DB_003` | El registro ya existe (valor duplicado) |
| `23503` | FK constraint violation | 409 | `DB_004` | Violación de integridad referencial |
| `23502` | NOT NULL violation | 400 | `VAL_001` | El campo {columna} es obligatorio |
| `42P01` | Undefined table / relation | 500 | `INT_001` | Error interno de configuración |
| `40P01` | Deadlock detected | 409 | `DB_002` | Conflicto de concurrencia, reintente |

### Python — Traducción de SQLAlchemyError

```python
from sqlalchemy.exc import IntegrityError, DataError, OperationalError

DB_ERROR_MAP = {
    "duplicate key": (409, "DB_003", "El registro ya existe"),
    "foreign key": (409, "DB_004", "Violación de integridad referencial"),
    "null": (400, "VAL_001", "El campo es obligatorio"),
    "truncation": (400, "VAL_008", "El valor excede la longitud máxima"),
    "deadlock": (409, "DB_002", "Conflicto de concurrencia, reintente"),
}

@app.exception_handler(IntegrityError)
async def integrity_error(request, exc: IntegrityError):
    msg = str(exc.orig)
    for key, (status, code, friendly) in DB_ERROR_MAP.items():
        if key in msg.lower():
            raise HTTPException(status_code=status, detail={"code": code, "message": friendly})
    raise HTTPException(status_code=500, detail={"code": "INT_001", "message": "Error de integridad"})

@app.exception_handler(DataError)
async def data_error(request, exc: DataError):
    raise HTTPException(status_code=400, detail={"code": "VAL_008", "message": "Dato inválido o truncado"})

@app.exception_handler(OperationalError)
async def operational_error(request, exc: OperationalError):
    raise HTTPException(status_code=500, detail={"code": "INT_001", "message": "Error de operación en base de datos"})
```
