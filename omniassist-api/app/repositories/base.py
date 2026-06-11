"""Generic tenant-scoped async repository (CRUD + pagination)."""
from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class TenantRepository(Generic[ModelT]):
    """All queries are scoped by ``org_id`` to enforce tenant isolation."""

    model: type[ModelT]

    def __init__(self, db: AsyncSession, model: type[ModelT]) -> None:
        self.db = db
        self.model = model

    async def get(self, org_id: uuid.UUID, obj_id: uuid.UUID) -> ModelT | None:
        obj = await self.db.get(self.model, obj_id)
        if obj is not None and getattr(obj, "org_id", None) == org_id:
            return obj
        return None

    async def list(
        self,
        org_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
        filters: list[Any] | None = None,
        order_by: Any = None,
    ) -> tuple[list[ModelT], int]:
        base = select(self.model).where(self.model.org_id == org_id)  # type: ignore[attr-defined]
        if filters:
            base = base.where(*filters)
        total = (
            await self.db.execute(
                select(func.count()).select_from(base.subquery())
            )
        ).scalar_one()
        if order_by is not None:
            base = base.order_by(order_by)
        rows = (await self.db.execute(base.limit(limit).offset(offset))).scalars().all()
        return list(rows), int(total)

    async def create(self, **values: Any) -> ModelT:
        obj = self.model(**values)
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def delete(self, obj: ModelT) -> None:
        await self.db.delete(obj)
