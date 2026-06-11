"""Lead / CRM pipeline routes."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.core.deps import CurrentContext, DbSession, PaginationDep, require_permission
from app.core.permissions import Permission
from app.models.lead import Lead
from app.repositories.base import TenantRepository
from app.schemas.common import MessageResponse, Page, PageMeta
from app.schemas.domain import (
    FollowupRequest,
    LeadCreateRequest,
    LeadOut,
    LeadStageRequest,
)
from app.services.lead_service import LeadService

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("", response_model=Page[LeadOut])
async def list_leads(
    ctx: CurrentContext,
    db: DbSession,
    page: PaginationDep,
    stage: str | None = Query(None),
    _: object = Depends(require_permission(Permission.LEAD_READ)),
) -> Page[LeadOut]:
    repo = TenantRepository(db, Lead)
    filters = [Lead.stage == stage] if stage else []
    rows, total = await repo.list(
        ctx.org_id, limit=page.limit, offset=page.offset, filters=filters,
        order_by=Lead.score.desc(),
    )
    return Page(
        items=[LeadOut.model_validate(lead) for lead in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.get("/pipeline")
async def pipeline(
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.LEAD_READ)),
) -> dict:
    rows = (
        (await db.execute(select(Lead).where(Lead.org_id == ctx.org_id))).scalars().all()
    )
    board: dict[str, list[dict]] = {}
    for lead in rows:
        board.setdefault(lead.stage, []).append(
            LeadOut.model_validate(lead).model_dump(mode="json")
        )
    return {"data": board, "error": None}


@router.post("", response_model=LeadOut, status_code=201)
async def create_lead(
    payload: LeadCreateRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.LEAD_WRITE)),
) -> LeadOut:
    repo = TenantRepository(db, Lead)
    lead = await repo.create(
        org_id=ctx.org_id, name=payload.name, company=payload.company, email=payload.email,
        phone=payload.phone, value=payload.value, source=payload.source, stage=payload.stage,
        owner_id=ctx.user.id,
    )
    return LeadOut.model_validate(lead)


@router.post("/{lead_id}/stage", response_model=LeadOut)
async def change_stage(
    lead_id: uuid.UUID,
    payload: LeadStageRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.LEAD_WRITE)),
) -> LeadOut:
    lead = await LeadService(db).change_stage(ctx.org_id, lead_id, payload.stage, ctx.user.id)
    return LeadOut.model_validate(lead)


@router.post("/{lead_id}/followup", response_model=MessageResponse)
async def schedule_followup(
    lead_id: uuid.UUID,
    payload: FollowupRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.LEAD_WRITE)),
) -> MessageResponse:
    await LeadService(db).schedule_followup(
        ctx.org_id, lead_id, when=payload.when, action=payload.action, actor_id=ctx.user.id
    )
    return MessageResponse(message="Follow-up scheduled.")
