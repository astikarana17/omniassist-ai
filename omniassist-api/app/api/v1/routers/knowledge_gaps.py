"""Knowledge Gap Detector routes — record low-confidence answers, review & resolve.

When an AI agent answers with confidence below its threshold (no good source),
it calls ``record`` which clusters near-duplicate questions onto a single gap.
The dashboard surfaces the most frequent gaps for documentation improvement.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.core.deps import CurrentContext, DbSession, PaginationDep, require_permission
from app.core.exceptions import NotFoundError
from app.core.permissions import Permission
from app.models.enums import GapStatus
from app.models.insights import KnowledgeGap
from app.repositories.base import TenantRepository
from app.schemas.common import Page, PageMeta
from app.schemas.ops import (
    GapDashboard,
    KnowledgeGapOut,
    RecordGapRequest,
    ResolveGapRequest,
)
from app.services.ops_service import KnowledgeGapService

router = APIRouter(prefix="/knowledge-gaps", tags=["Knowledge Gaps"])


@router.post("", response_model=KnowledgeGapOut, status_code=201)
async def record_gap(
    payload: RecordGapRequest, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.KNOWLEDGE_GAP_WRITE)),
) -> KnowledgeGapOut:
    row = await KnowledgeGapService(db).record(
        ctx.org_id, question=payload.question, confidence=payload.confidence,
        conversation_id=payload.conversation_id, agent_run_id=payload.agent_run_id,
    )
    return KnowledgeGapOut.model_validate(row)


@router.get("", response_model=Page[KnowledgeGapOut])
async def list_gaps(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    status: str | None = Query(None),
    _: object = Depends(require_permission(Permission.KNOWLEDGE_GAP_READ)),
) -> Page[KnowledgeGapOut]:
    repo = TenantRepository(db, KnowledgeGap)
    filters = [KnowledgeGap.status == status] if status else []
    rows, total = await repo.list(
        ctx.org_id, limit=page.limit, offset=page.offset, filters=filters,
        order_by=KnowledgeGap.occurrences.desc(),
    )
    return Page(
        items=[KnowledgeGapOut.model_validate(r) for r in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.get("/dashboard", response_model=GapDashboard)
async def dashboard(
    ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.KNOWLEDGE_GAP_READ)),
) -> GapDashboard:
    counts = await KnowledgeGapService(db).counts_by_status(ctx.org_id)
    top = (
        await db.execute(
            select(KnowledgeGap)
            .where(KnowledgeGap.org_id == ctx.org_id, KnowledgeGap.status == GapStatus.OPEN)
            .order_by(KnowledgeGap.occurrences.desc())
            .limit(10)
        )
    ).scalars().all()
    return GapDashboard(
        open=counts[GapStatus.OPEN.value],
        in_review=counts[GapStatus.IN_REVIEW.value],
        resolved=counts[GapStatus.RESOLVED.value],
        dismissed=counts[GapStatus.DISMISSED.value],
        top_gaps=[KnowledgeGapOut.model_validate(g) for g in top],
    )


@router.post("/{gap_id}/resolve", response_model=KnowledgeGapOut)
async def resolve_gap(
    gap_id: uuid.UUID, payload: ResolveGapRequest, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.KNOWLEDGE_GAP_WRITE)),
) -> KnowledgeGapOut:
    repo = TenantRepository(db, KnowledgeGap)
    gap = await repo.get(ctx.org_id, gap_id)
    if gap is None:
        raise NotFoundError("Knowledge gap not found.")
    gap.status = payload.status
    gap.suggested_answer = payload.suggested_answer
    gap.document_id = payload.document_id
    gap.resolved_by = ctx.user.id
    gap.resolved_at = datetime.utcnow()
    await db.flush()
    return KnowledgeGapOut.model_validate(gap)
