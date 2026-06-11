"""AI Executive Insights + Business Impact (ROI) routes for leadership dashboards."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.core.deps import CurrentContext, DbSession, PaginationDep, require_permission
from app.core.permissions import Permission
from app.models.insights import BusinessImpactMetric, ExecutiveInsight
from app.repositories.base import TenantRepository
from app.schemas.common import Page, PageMeta
from app.schemas.ops import (
    BusinessImpactIn,
    BusinessImpactOut,
    ExecutiveInsightIn,
    ExecutiveInsightOut,
)

router = APIRouter(prefix="/insights", tags=["Executive Insights"])


@router.get("", response_model=Page[ExecutiveInsightOut])
async def list_insights(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    kind: str | None = Query(None),
    _: object = Depends(require_permission(Permission.INSIGHTS_READ)),
) -> Page[ExecutiveInsightOut]:
    repo = TenantRepository(db, ExecutiveInsight)
    filters = [ExecutiveInsight.kind == kind] if kind else []
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  filters=filters, order_by=ExecutiveInsight.created_at.desc())
    return Page(
        items=[ExecutiveInsightOut.model_validate(r) for r in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.post("", response_model=ExecutiveInsightOut, status_code=201)
async def create_insight(
    payload: ExecutiveInsightIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.ANALYTICS_EXPORT)),
) -> ExecutiveInsightOut:
    repo = TenantRepository(db, ExecutiveInsight)
    row = await repo.create(org_id=ctx.org_id, generated_by="manual", **payload.model_dump())
    return ExecutiveInsightOut.model_validate(row)


@router.get("/impact", response_model=Page[BusinessImpactOut])
async def list_impact(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    _: object = Depends(require_permission(Permission.IMPACT_READ)),
) -> Page[BusinessImpactOut]:
    repo = TenantRepository(db, BusinessImpactMetric)
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  order_by=BusinessImpactMetric.period_start.desc())
    return Page(
        items=[BusinessImpactOut.model_validate(r) for r in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.post("/impact", response_model=BusinessImpactOut, status_code=201)
async def upsert_impact(
    payload: BusinessImpactIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.ANALYTICS_EXPORT)),
) -> BusinessImpactOut:
    """Insert or update the ROI snapshot for a period (unique per org/period/grain)."""
    existing = (
        await db.execute(
            select(BusinessImpactMetric).where(
                BusinessImpactMetric.org_id == ctx.org_id,
                BusinessImpactMetric.period_start == payload.period_start,
                BusinessImpactMetric.period_end == payload.period_end,
                BusinessImpactMetric.granularity == payload.granularity,
            )
        )
    ).scalar_one_or_none()
    if existing is None:
        existing = BusinessImpactMetric(org_id=ctx.org_id, **payload.model_dump())
        db.add(existing)
    else:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)
    await db.flush()
    return BusinessImpactOut.model_validate(existing)
