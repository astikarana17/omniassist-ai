"""AI Employee Assistant routes — internal docs & HR policies (internal-only)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query

from app.ai.graphs import ops_agents
from app.core.deps import CurrentContext, DbSession, PaginationDep, require_permission
from app.core.exceptions import NotFoundError
from app.core.permissions import Permission
from app.models.internal import HrPolicy, InternalDocument
from app.repositories.base import TenantRepository
from app.schemas.common import MessageResponse, Page, PageMeta
from app.schemas.ops import (
    AskRequest,
    AskResponse,
    HrPolicyIn,
    HrPolicyOut,
    InternalDocIn,
    InternalDocOut,
)

router = APIRouter(prefix="/employee", tags=["Employee Assistant"])


@router.post("/ask", response_model=AskResponse)
async def ask_employee_assistant(
    payload: AskRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.EMPLOYEE_READ)),
) -> AskResponse:
    """Ask the internal AI Employee Assistant — grounded only in internal docs / HR policies."""
    result = await ops_agents.run_employee_assistant(db, ctx.org_id, payload.question)
    return AskResponse(
        answer=result.reply, confidence=result.confidence, sources=result.sources,
    )


@router.get("/documents", response_model=Page[InternalDocOut])
async def list_documents(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    category: str | None = Query(None),
    _: object = Depends(require_permission(Permission.EMPLOYEE_READ)),
) -> Page[InternalDocOut]:
    repo = TenantRepository(db, InternalDocument)
    filters = [InternalDocument.category == category] if category else []
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  filters=filters, order_by=InternalDocument.created_at.desc())
    return Page(
        items=[InternalDocOut.model_validate(r) for r in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.post("/documents", response_model=InternalDocOut, status_code=201)
async def create_document(
    payload: InternalDocIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.EMPLOYEE_WRITE)),
) -> InternalDocOut:
    repo = TenantRepository(db, InternalDocument)
    row = await repo.create(org_id=ctx.org_id, owner_id=ctx.user.id, **payload.model_dump())
    return InternalDocOut.model_validate(row)


@router.delete("/documents/{doc_id}", response_model=MessageResponse)
async def delete_document(
    doc_id: uuid.UUID, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.EMPLOYEE_WRITE)),
) -> MessageResponse:
    repo = TenantRepository(db, InternalDocument)
    row = await repo.get(ctx.org_id, doc_id)
    if row is None:
        raise NotFoundError("Internal document not found.")
    await repo.delete(row)
    return MessageResponse(message="Document deleted.")


@router.get("/hr-policies", response_model=Page[HrPolicyOut])
async def list_hr_policies(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    _: object = Depends(require_permission(Permission.EMPLOYEE_READ)),
) -> Page[HrPolicyOut]:
    repo = TenantRepository(db, HrPolicy)
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  order_by=HrPolicy.created_at.desc())
    return Page(
        items=[HrPolicyOut.model_validate(r) for r in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.post("/hr-policies", response_model=HrPolicyOut, status_code=201)
async def create_hr_policy(
    payload: HrPolicyIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.EMPLOYEE_WRITE)),
) -> HrPolicyOut:
    repo = TenantRepository(db, HrPolicy)
    row = await repo.create(org_id=ctx.org_id, **payload.model_dump())
    return HrPolicyOut.model_validate(row)
