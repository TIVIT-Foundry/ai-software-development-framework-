from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import Depends, HTTPException
from pydantic import BaseModel


class {Entity}ListItem(BaseModel):
    id: int
    name: str
    code: str
    status: str
    created_date: str


class {Entity}Detail(BaseModel):
    id: int
    name: str
    code: str
    status: str
    created_by: int
    created_date: str
    updated_by: Optional[int] = None
    updated_date: Optional[str] = None


class PaginationResult(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int


async def list_{entity}(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "CreatedDate",
    sort_order: str = "DESC",
    search_filter: Optional[str] = None,
) -> tuple[list[{Entity}ListItem], PaginationResult]:
    result = await db.execute(
        text("""
            EXEC {Schema}.List{Entity}
                @ParamIPage = :page,
                @ParamIPageSize = :page_size,
                @ParamISortBy = :sort_by,
                @ParamISortOrder = :sort_order,
                @ParamISearchFilter = :search_filter
        """),
        {
            "page": page,
            "page_size": page_size,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "search_filter": search_filter,
        },
    )
    rows = result.fetchall()
    if not rows:
        return [], PaginationResult(page=page, page_size=page_size, total_records=0, total_pages=0)

    items = [
        {Entity}ListItem(
            id=row.{entity}_id,
            name=row.name,
            code=row.code,
            status=row.status,
            created_date=str(row.created_date),
        )
        for row in rows
    ]
    total_count = rows[0].total_count if hasattr(rows[0], "total_count") else 0
    total_pages = (total_count + page_size - 1) // page_size

    return items, PaginationResult(
        page=page,
        page_size=page_size,
        total_records=total_count,
        total_pages=total_pages,
    )


async def get_{entity}(
    db: AsyncSession,
    entity_id: int,
) -> Optional[{Entity}Detail]:
    result = await db.execute(
        text("EXEC {Schema}.Get{Entity} @ParamIId = :id"),
        {"id": entity_id},
    )
    row = result.fetchone()
    if not row:
        return None
    return {Entity}Detail(
        id=row.{entity}_id,
        name=row.name,
        code=row.code,
        status=row.status,
        created_by=row.created_by,
        created_date=str(row.created_date),
        updated_by=getattr(row, "updated_by", None),
        updated_date=str(row.updated_date) if hasattr(row, "updated_date") else None,
    )


async def create_{entity}(
    db: AsyncSession,
    name: str,
    code: str,
    status: str,
    current_user_id: int,
) -> {Entity}Detail:
    result = await db.execute(
        text("""
            EXEC {Schema}.Create{Entity}
                @ParamIName = :name,
                @ParamICode = :code,
                @ParamIStatus = :status,
                @ParamICurrentUserId = :current_user_id
        """),
        {
            "name": name,
            "code": code,
            "status": status,
            "current_user_id": current_user_id,
        },
    )
    await db.commit()
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create {entity}")
    return {Entity}Detail(
        id=row.{entity}_id,
        name=row.name,
        code=row.code,
        status=row.status,
        created_by=row.created_by,
        created_date=str(row.created_date),
        updated_by=None,
        updated_date=None,
    )


async def update_{entity}(
    db: AsyncSession,
    entity_id: int,
    name: Optional[str] = None,
    code: Optional[str] = None,
    status: Optional[str] = None,
    current_user_id: int = None,
) -> {Entity}Detail:
    result = await db.execute(
        text("""
            EXEC {Schema}.Update{Entity}
                @ParamIId = :id,
                @ParamIName = :name,
                @ParamICode = :code,
                @ParamIStatus = :status,
                @ParamICurrentUserId = :current_user_id
        """),
        {
            "id": entity_id,
            "name": name,
            "code": code,
            "status": status,
            "current_user_id": current_user_id,
        },
    )
    await db.commit()
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="{Entity} not found")
    return {Entity}Detail(
        id=row.{entity}_id,
        name=row.name,
        code=row.code,
        status=row.status,
        created_by=row.created_by,
        created_date=str(row.created_date),
        updated_by=getattr(row, "updated_by", None),
        updated_date=str(row.updated_date) if hasattr(row, "updated_date") else None,
    )


async def delete_{entity}(
    db: AsyncSession,
    entity_id: int,
    current_user_id: int,
) -> bool:
    result = await db.execute(
        text("""
            EXEC {Schema}.Delete{Entity}
                @ParamIId = :id,
                @ParamICurrentUserId = :current_user_id
        """),
        {"id": entity_id, "current_user_id": current_user_id},
    )
    await db.commit()
    return True
