# Module Structure: {ModuleName}

## Folder Layout (Python FastAPI)

```
src/{module}/
├── __init__.py
├── router.py           # FastAPI router with endpoints
├── service.py          # Business logic
├── repository.py       # Data access (calls SPs)
├── schemas.py          # Pydantic models (request/response)
├── dependencies.py     # Dependency injection factories
├── models.py           # SQLAlchemy models (if needed)
└── constants.py        # SP name constants
```

## File Responsibilities

| File | Responsibility |
|------|----------------|
| `router.py` | FastAPI `APIRouter` — route definitions, HTTP verbs, status codes |
| `service.py` | Business logic — orchestrates repository calls, validation rules |
| `repository.py` | Data access — calls stored procedures, maps results to schemas |
| `schemas.py` | Pydantic models — `BaseModel` for request/response DTOs, validation |
| `dependencies.py` | DI factories — `get_*_service()`, `get_*_repository()` for `Depends()` |
| `constants.py` | SP name constants — single source of truth for procedure names |

## Example Module (Python FastAPI)

### router.py

```python
from fastapi import APIRouter, Depends, status
from .schemas import {Entity}Create, {Entity}Update, {Entity}Out, ApiResponse
from .service import {Entity}Service
from .dependencies import get_{entity}_service

router = APIRouter(prefix="/api/v1/{entities}", tags=["{Entity}"])


@router.get("/", response_model=ApiResponse[list[{Entity}Out]])
async def list_{entities}(
    page: int = 1,
    page_size: int = 20,
    service: {Entity}Service = Depends(get_{entity}_service),
) -> ApiResponse[list[{Entity}Out]]:
    items, total = service.list(page=page, page_size=page_size)
    return ApiResponse.ok_list(items, total=total, page=page, page_size=page_size)


@router.get("/{{id}}", response_model=ApiResponse[{Entity}Out])
async def get_{entity}(
    id: int,
    service: {Entity}Service = Depends(get_{entity}_service),
) -> ApiResponse[{Entity}Out]:
    return ApiResponse.ok(service.get_by_id(id))


@router.post("/", response_model=ApiResponse[{Entity}Out], status_code=status.HTTP_201_CREATED)
async def create_{entity}(
    payload: {Entity}Create,
    service: {Entity}Service = Depends(get_{entity}_service),
) -> ApiResponse[{Entity}Out]:
    return ApiResponse.ok(service.create(payload))


@router.put("/{{id}}", response_model=ApiResponse[{Entity}Out])
async def update_{entity}(
    id: int,
    payload: {Entity}Update,
    service: {Entity}Service = Depends(get_{entity}_service),
) -> ApiResponse[{Entity}Out]:
    return ApiResponse.ok(service.update(id, payload))


@router.delete("/{{id}}", response_model=ApiResponse[None])
async def delete_{entity}(
    id: int,
    service: {Entity}Service = Depends(get_{entity}_service),
) -> ApiResponse[None]:
    service.delete(id)
    return ApiResponse.ok(None)
```

### service.py

```python
from .repository import {Entity}Repository
from .schemas import {Entity}Create, {Entity}Update


class {Entity}Service:
    def __init__(self, repo: {Entity}Repository):
        self.repo = repo

    def list(self, page: int = 1, page_size: int = 20):
        return self.repo.list(page=page, page_size=page_size)

    def get_by_id(self, id: int):
        return self.repo.get_by_id(id)

    def create(self, payload: {Entity}Create):
        return self.repo.create(payload)

    def update(self, id: int, payload: {Entity}Update):
        return self.repo.update(id, payload)

    def delete(self, id: int):
        self.repo.delete(id)
```

### repository.py

```python
from ..database import get_session
from .constants import SP
from .schemas import {Entity}Create, {Entity}Update


class {Entity}Repository:
    def list(self, page: int = 1, page_size: int = 20):
        with get_session() as session:
            result = session.execute(
                f"SELECT * FROM {SP.LIST_{ENTITY}}(p_page => :page, p_page_size => :page_size)",
                {"page": page, "page_size": page_size},
            )
            items = [dict(row) for row in result.fetchall()]
            total = session.execute(f"SELECT {SP.COUNT_{ENTITY}}()").scalar()
            return items, total

    def get_by_id(self, id: int):
        with get_session() as session:
            result = session.execute(
                f"SELECT * FROM {SP.GET_{ENTITY}}(p_id => :id)",
                {"id": id},
            )
            return result.mappings().first()

    def create(self, payload: {Entity}Create):
        with get_session() as session:
            result = session.execute(
                f"SELECT * FROM {SP.CREATE_{ENTITY}}({', '.join(f'p_{k} => :{k}' for k in payload.model_fields)})",
                payload.model_dump(),
            )
            session.commit()
            return result.mappings().first()

    def update(self, id: int, payload: {Entity}Update):
        with get_session() as session:
            data = {k: v for k, v in payload.model_dump().items() if v is not None}
            data["id"] = id
            result = session.execute(
                f"SELECT * FROM {SP.UPDATE_{ENTITY}}({', '.join(f'p_{k} => :{k}' for k in data)})",
                data,
            )
            session.commit()
            return result.mappings().first()

    def delete(self, id: int):
        with get_session() as session:
            session.execute(f"SELECT {SP.DELETE_{ENTITY}}(p_id => :id)", {"id": id})
            session.commit()
```

### schemas.py

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class {Entity}Create(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class {Entity}Update(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class {Entity}Out(BaseModel):
    id: int
    name: str
    created_at: datetime
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    record_status: str
```

### dependencies.py

```python
from functools import lru_cache
from .repository import {Entity}Repository
from .service import {Entity}Service


@lru_cache
def get_{entity}_repository() -> {Entity}Repository:
    return {Entity}Repository()


def get_{entity}_service() -> {Entity}Service:
    return {Entity}Service(repo=get_{entity}_repository())
```

### constants.py

```python
class SP:
    LIST_{ENTITY} = "sp_{entities}_list"
    GET_{ENTITY} = "sp_{entities}_get"
    CREATE_{ENTITY} = "sp_{entities}_create"
    UPDATE_{ENTITY} = "sp_{entities}_update"
    DELETE_{ENTITY} = "sp_{entities}_delete"
    COUNT_{ENTITY} = "sp_{entities}_count"
```
