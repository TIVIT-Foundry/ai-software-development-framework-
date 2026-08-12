---
name: data-access
description: 'Data access handler patterns: calling stored procedures/queries, mapping
  results, error handling. Uses Python SQLAlchemy. Trigger: When implementing data access handlers, calling
  stored procedures, or mapping results.'
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: mandatory
  depends_on:
  - database-sp
  - backend-api
  consumed_by:
  - api-first-backend
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
| Call error helper after reading SP result | ALWAYS | Proper error handling |
| Use async queries for lists | ALWAYS | Non-blocking IO |
| Return paginated tuple `(Data, Pagination)` for lists | ALWAYS | Consistent pattern |
| Set sort defaults in Service | ALWAYS | Single source of truth |
| Pass `currentUser` for audit trail | ALWAYS | Auditability |
| Use parameterized queries always | ALWAYS | SQL injection prevention |

## Python SQLAlchemy Equivalent
```python
async def get_entity(db: AsyncSession, entity_id: int) -> EntityModel:
    result = await db.execute(
        text("EXEC Schema.GetEntity @ParamIId = :id"),
        {"id": entity_id}
    )
    row = result.fetchone()
    if not row:
        raise NotFoundException("Entity not found")
    return EntityModel(**row._mapping)
```

## Handler Types Quick Reference
| Type | SQLAlchemy Method | Returns |
|------|---------------|---------|
| List | `session.execute(select(...)).scalars().all()` | `(Response, PaginationResult)` |
| Get | `session.execute(select(...)).scalar_one_or_none()` | `Response` |
| Create | `session.add(entity)` → `session.commit()` | `Response` |
| Update | `session.merge(entity)` → `session.commit()` | `Response` |
| Delete | `session.delete(entity)` → `session.commit()` | `Response` (ID confirmation) |

## SP Error Mapping
| SP Code | Exception | HTTP |
|---------|-----------|------|
| `VAL_*` | ValidationException | 400 |
| `{MOD}_001` | NotFoundException | 404 |
| `{MOD}_002` | ConflictException | 409 |
| `{MOD}_003+` | BusinessRuleException | 422 |
| `AUTH_*` | ForbiddenException | 403 |
| `SYS_*` | InternalException | 500 |

## Patrones de handler

### Python SQLAlchemy — Repositorio completo

```python
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, text, select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, joinedload
from sqlalchemy.exc import IntegrityError, DatabaseError, TimeoutError
from typing import Optional, List, Tuple
from datetime import datetime

Base = declarative_base()


class ProductoModel(Base):
    __tablename__ = "Producto"
    __table_args__ = {"schema": "ventas"}

    producto_id = Column("ProductoId", Integer, primary_key=True, autoincrement=True)
    nombre = Column("Nombre", String(100), nullable=False)
    precio = Column("Precio", Numeric(18, 2), nullable=False)
    categoria_id = Column("CategoriaId", Integer, nullable=False)
    fecha_creacion = Column("FechaCreacion", DateTime)
    activo = Column("Activo", Boolean, default=True)


class ProductoRepository:
    """Repositorio asíncrono con SQLAlchemy 2.0 style queries."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def list(
        self,
        nombre: Optional[str] = None,
        pagina: int = 1,
        tamano: int = 20,
        ordenar_por: str = "ProductoId",
        orden_dir: str = "ASC",
    ) -> Tuple[List[ProductoDto], PaginationResult]:
        async with self._session_factory() as session:
            try:
                stmt = select(ProductoModel).where(ProductoModel.activo == True)

                if nombre:
                    stmt = stmt.where(ProductoModel.nombre.ilike(f"%{nombre}%"))

                # Total count
                count_stmt = select(func.count()).select_from(stmt.subquery())
                total = await session.scalar(count_stmt) or 0

                # Ordenamiento dinámico validado
                columna = getattr(ProductoModel, ordenar_por, ProductoModel.producto_id)
                order = columna.asc() if orden_dir.upper() == "ASC" else columna.desc()
                stmt = stmt.order_by(order).offset((pagina - 1) * tamano).limit(tamano)

                result = await session.execute(stmt)
                entities = result.scalars().all()

                dtos = [self._to_dto(e) for e in entities]
                pagination = PaginationResult(
                    pagina=pagina,
                    tamano_pagina=tamano,
                    total_count=total or 0,
                    total_pages=max(1, (total or 0) // tamano + (1 if (total or 0) % tamano else 0)),
                )
                return dtos, pagination

            except TimeoutError:
                raise DataAccessException("Timeout en listado de productos")
            except DatabaseError as ex:
                raise DataAccessException(f"Error de BD: {ex}")

    async def get_by_id(self, producto_id: int) -> ProductoDto:
        async with self._session_factory() as session:
            try:
                stmt = select(ProductoModel).where(ProductoModel.producto_id == producto_id)
                result = await session.execute(stmt)
                entity = result.scalar_one_or_none()

                if not entity:
                    raise NotFoundException(f"Producto {producto_id} no encontrado")
                return self._to_dto(entity)
            except DatabaseError as ex:
                raise DataAccessException(f"Error al consultar producto {producto_id}", ex)

    async def create(self, request: CreateProductoRequest, current_user: str) -> ProductoDto:
        async with self._session_factory() as session:
            try:
                entity = ProductoModel(
                    nombre=request.nombre,
                    precio=request.precio,
                    categoria_id=request.categoria_id,
                    fecha_creacion=datetime.utcnow(),
                )
                session.add(entity)
                await session.commit()
                # Obligatorio si el modelo tiene columnas computadas por la DB
                # (DEFAULT NOW() / onupdate=func.now()): el commit deja el atributo
                # expired y, en sesión async, accederlo sin refresh lanza
                # MissingGreenlet (ver database-modeling).
                await session.refresh(entity)
                return self._to_dto(entity)
            except IntegrityError as ex:
                await session.rollback()
                if "UQ_Producto_Nombre" in str(ex):
                    raise ConflictException("Ya existe un producto con ese nombre", ex)
                raise DataAccessException("Error de integridad al crear producto", ex)
            except DatabaseError as ex:
                await session.rollback()
                raise DataAccessException("Error al crear producto", ex)

    async def update(self, producto_id: int, request: UpdateProductoRequest) -> ProductoDto:
        async with self._session_factory() as session:
            try:
                stmt = select(ProductoModel).where(ProductoModel.producto_id == producto_id)
                result = await session.execute(stmt)
                entity = result.scalar_one_or_none()

                if not entity:
                    raise NotFoundException(f"Producto {producto_id} no encontrado")

                if request.nombre is not None:
                    entity.nombre = request.nombre
                if request.precio is not None:
                    entity.precio = request.precio

                await session.commit()
                # Refresh post-commit: mismo motivo que en create — atributos
                # computados por la DB quedan expired (ver database-modeling).
                await session.refresh(entity)
                return self._to_dto(entity)
            except DatabaseError as ex:
                await session.rollback()
                raise DataAccessException(f"Error al actualizar producto {producto_id}", ex)

    async def delete(self, producto_id: int) -> None:
        async with self._session_factory() as session:
            try:
                stmt = select(ProductoModel).where(ProductoModel.producto_id == producto_id)
                result = await session.execute(stmt)
                entity = result.scalar_one_or_none()

                if not entity:
                    raise NotFoundException(f"Producto {producto_id} no encontrado")

                entity.activo = False  # soft delete
                await session.commit()
            except DatabaseError as ex:
                await session.rollback()
                raise DataAccessException(f"Error al eliminar producto {producto_id}", ex)

    def _to_dto(self, entity: ProductoModel) -> ProductoDto:
        return ProductoDto(
            producto_id=entity.producto_id,
            nombre=entity.nombre or "",
            precio=float(entity.precio),
            categoria_id=entity.categoria_id,
            fecha_creacion=entity.fecha_creacion,
        )


# Versión síncrona (para scripts o cargas batch)
class ProductoRepositorySync:
    """Repositorio síncrono, útil para ETL y migraciones."""

    def __init__(self, session_factory):
        self._session_factory = session_factory

    def list_all(self) -> List[ProductoDto]:
        with self._session_factory() as session:
            stmt = select(ProductoModel).where(ProductoModel.activo == True)
            entities = session.execute(stmt).scalars().all()
            return [self._to_dto(e) for e in entities]

    def _to_dto(self, entity: ProductoModel) -> ProductoDto:
        return ProductoDto(
            producto_id=entity.producto_id,
            nombre=entity.nombre or "",
            precio=float(entity.precio),
            categoria_id=entity.categoria_id,
            fecha_creacion=entity.fecha_creacion,
        )
```

## Mapeo de resultados

### Manual vs auto-mapping

| Aspecto | Auto-mapping (ORM) | Manual (dict → DTO) |
|---------|---------------------------------|----------------------|
| Velocidad de desarrollo | Alta — el ORM hace coincidir columnas con props | Baja — hay que mapear campo por campo |
| Performance | Buena, con overhead de ORM | Óptima — solo lo necesario |
| Control de tipos | Limitado — conversiones implícitas | Total — cada conversión se declara |
| NULL handling | Depende del ORM | Explícito |
| Debugging | Más difícil si la proyección falla | Cada línea es verificable |

**Cuándo usar cada uno:**
- **Auto-mapping**: CRUD simple, DTOs planos donde las columnas del SP/query coinciden 1:1 con las propiedades.
- **Manual mapping**: SPs con prefijos en columnas, lógica de conversión, joins complejos, o cuando se necesita rendimiento máximo.

### Convenciones de nomenclatura columna → DTO

```
# BD: ProductoId → Python: producto_id (estilo snake_case en modelos)
# BD: Nombre → Python: nombre
# BD: FechaCreacion → Python: fecha_creacion
# BD: CategoriaId → Python: categoria_id
```

### Manejo de valores NULL

```python
# Python — manejo de NULL con Optional
from typing import Optional
from pydantic import BaseModel

class ProductoDto(BaseModel):
    producto_id: int
    nombre: str = ""
    email: Optional[str] = None
    descuento: Optional[float] = None

# En mapeo manual
def row_to_dto(row) -> ProductoDto:
    return ProductoDto(
        producto_id=row["ProductoId"],
        nombre=row.get("Nombre") or "",
        email=row.get("Email"),       # None si es NULL
        descuento=float(row["Descuento"]) if row.get("Descuento") else None,
    )
```

### Multi-resultset: paginación + total count

```python
# Python SQLAlchemy — count separado + query paginada
async def list_with_count(
    session: AsyncSession,
    stmt: Select,
    pagina: int,
    tamano: int,
) -> Tuple[List[Any], int]:
    # Obtener total (sin paginación)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await session.scalar(count_stmt) or 0

    # Aplicar paginación
    stmt = stmt.offset((pagina - 1) * tamano).limit(tamano)
    result = await session.execute(stmt)
    items = result.scalars().all()

    return items, total
```

## Buenas prácticas de caché en data access

### ¿Cuándo cachear a nivel de data access?

| Situación | Cachear | No cachear |
|-----------|---------|------------|
| Catálogos estáticos (ej. tipos de producto) | Siempre — cambian poco | — |
| Listados con alta concurrencia de lectura | Sí — reduce presión en BD | — |
| Datos de sesión/usuario | No — riesgo de datos obsoletos | Usar caché de auth |
| Operaciones de escritura frecuente | No — invalidación constante | Caché en capa superior |
| Consultas agregadas (reportes) | Sí — TTL largo (minutos/horas) | — |
| Datos con permisos por fila | No — complejidad de invalidación | Caché por usuario |
| Resultados de búsqueda | Sí — TTL corto (segundos) | — |

### Redis vs in-memory

| Aspecto | Redis | In-memory |
|---------|-------|----------|
| Persistencia | Sí (RDB/AOF) | No — se pierde al reiniciar |
| Distribuido | Sí — todos los nodos ven la misma caché | No — cada instancia tiene su copia |
| Latencia | ~1-5ms (red) | ~0.01ms (local) |
| Capacidad | GB/TB (memoria externa) | Limitado a RAM del proceso |
| Costo operativo | Infraestructura separada | Gratis (incluido en el proceso) |
| Ideal para | Catálogos compartidos, sesiones distribuidas, rate limiting | Datos de un solo nodo, cálculos repetitivos |

**Regla general:** Usar in-memory para datos que solo usa una instancia (cálculos locales, datos de warm-up) y Redis para datos compartidos entre réplicas o entre servicios.

### Estrategias de invalidación

```python
# Python — decorador de caché Redis
from functools import wraps
import json
import hashlib

def cache_redis(ttl_seconds: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            redis = get_redis_client()
            # Generar key a partir de función + argumentos
            key = f"{func.__name__}:{hashlib.md5(str(args).encode()).hexdigest()}"
            cached = await redis.get(key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            await redis.setex(key, ttl_seconds, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator

class ProductoRepository:
    @cache_redis(ttl_seconds=60)
    async def list(self, nombre: Optional[str] = None):
        # consulta a BD
        ...
```
