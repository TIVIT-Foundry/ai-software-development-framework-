from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from {package}.{module}.schemas import (
    {Entity}ListResponse,
    {Entity}DetailResponse,
    Create{Entity}Request,
    Update{Entity}Request,
    PaginatedResponse,
    ApiResponse,
)
from {package}.{module}.repository import (
    list_{entity},
    get_{entity},
    create_{entity},
    update_{entity},
    delete_{entity},
)
from {package}.database import get_db
from {package}.auth import get_current_user

router = APIRouter(prefix="/api/v1/{entities}", tags=["{Entity}"])


@router.get("/", response_model=ApiResponse[PaginatedResponse[{Entity}ListResponse]])
async def list_{entities}(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query("CreatedDate"),
    sort_order: Optional[str] = Query("DESC"),
    search_filter: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    items, pagination = await list_{entity}(
        db, page, page_size, sort_by, sort_order, search_filter
    )
    return ApiResponse.ok(
        PaginatedResponse(items=items, pagination=pagination)
    )


@router.get("/{entity_id}", response_model=ApiResponse[{Entity}DetailResponse])
async def get_{entity}(
    entity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await get_{entity}(db, entity_id)
    if not result:
        raise HTTPException(status_code=404, detail="{Entity} not found")
    return ApiResponse.ok(result)


@router.post(
    "/",
    response_model=ApiResponse[{Entity}DetailResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_{entity}(
    request: Create{Entity}Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await create_{entity}(
        db, request.name, request.code, request.status, current_user["id"]
    )
    return ApiResponse.ok(result)


@router.put("/{entity_id}", response_model=ApiResponse[{Entity}DetailResponse])
async def update_{entity}(
    entity_id: int,
    request: Update{Entity}Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await update_{entity}(
        db, entity_id, request.name, request.code, request.status, current_user["id"]
    )
    return ApiResponse.ok(result)


@router.delete("/{entity_id}", response_model=ApiResponse[bool])
async def delete_{entity}(
    entity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await delete_{entity}(db, entity_id, current_user["id"])
    return ApiResponse.ok(result)
