"""Audit log routes (read-only; logs are append-only)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.deps import CurrentContext, DbSession, PaginationDep, require_permission
from app.core.permissions import Permission
from app.models.ops import AuditLog
from app.repositories.base import TenantRepository
from app.schemas.common import Page, PageMeta
from app.schemas.domain import AuditOut

router = APIRouter(prefix="/audit-logs", tags=["Audit"])


@router.get("", response_model=Page[AuditOut])
async def list_audit(
    ctx: CurrentContext,
    db: DbSession,
    page: PaginationDep,
    resource_type: str | None = Query(None),
    _: object = Depends(require_permission(Permission.AUDIT_READ)),
) -> Page[AuditOut]:
    repo = TenantRepository(db, AuditLog)
    filters = [AuditLog.resource_type == resource_type] if resource_type else []
    rows, total = await repo.list(
        ctx.org_id, limit=page.limit, offset=page.offset, filters=filters,
        order_by=AuditLog.created_at.desc(),
    )
    return Page(
        items=[AuditOut.model_validate(a) for a in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )
