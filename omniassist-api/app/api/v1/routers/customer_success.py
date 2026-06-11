"""AI Customer Success Agent routes — accounts, health scores, engagement actions."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.core.deps import CurrentContext, DbSession, PaginationDep, require_permission
from app.core.exceptions import NotFoundError
from app.core.permissions import Permission
from app.models.success import CustomerAccount, CustomerHealthScore, EngagementAction
from app.repositories.base import TenantRepository
from app.schemas.common import Page, PageMeta
from app.schemas.ops import (
    CustomerAccountIn,
    CustomerAccountOut,
    EngagementActionIn,
    EngagementActionOut,
    HealthInputs,
    HealthScoreOut,
)
from app.services.ops_service import CustomerSuccessService

router = APIRouter(prefix="/customer-success", tags=["Customer Success"])


@router.get("/accounts", response_model=Page[CustomerAccountOut])
async def list_accounts(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    status: str | None = Query(None),
    _: object = Depends(require_permission(Permission.CUSTOMER_SUCCESS_READ)),
) -> Page[CustomerAccountOut]:
    repo = TenantRepository(db, CustomerAccount)
    filters = [CustomerAccount.status == status] if status else []
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  filters=filters, order_by=CustomerAccount.created_at.desc())
    return Page(
        items=[CustomerAccountOut.model_validate(r) for r in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.post("/accounts", response_model=CustomerAccountOut, status_code=201)
async def create_account(
    payload: CustomerAccountIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.CUSTOMER_SUCCESS_WRITE)),
) -> CustomerAccountOut:
    repo = TenantRepository(db, CustomerAccount)
    row = await repo.create(org_id=ctx.org_id, **payload.model_dump())
    return CustomerAccountOut.model_validate(row)


@router.post("/accounts/{customer_id}/health", response_model=HealthScoreOut, status_code=201)
async def compute_health(
    customer_id: uuid.UUID, payload: HealthInputs, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.CUSTOMER_SUCCESS_WRITE)),
) -> HealthScoreOut:
    """Compute and persist a health-score snapshot for the account."""
    account = await TenantRepository(db, CustomerAccount).get(ctx.org_id, customer_id)
    if account is None:
        raise NotFoundError("Customer account not found.")
    row = await CustomerSuccessService(db).record_health(
        ctx.org_id, customer_id,
        usage_score=payload.usage_score, engagement_score=payload.engagement_score,
        support_score=payload.support_score, satisfaction_score=payload.satisfaction_score,
        adoption_score=payload.adoption_score,
    )
    return HealthScoreOut.model_validate(row)


@router.get("/accounts/{customer_id}/health", response_model=HealthScoreOut | None)
async def latest_health(
    customer_id: uuid.UUID, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.CUSTOMER_SUCCESS_READ)),
) -> HealthScoreOut | None:
    row = (
        await db.execute(
            select(CustomerHealthScore)
            .where(CustomerHealthScore.org_id == ctx.org_id,
                   CustomerHealthScore.customer_id == customer_id)
            .order_by(CustomerHealthScore.computed_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    return HealthScoreOut.model_validate(row) if row else None


@router.get("/at-risk", response_model=list[HealthScoreOut])
async def at_risk_accounts(
    ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.CUSTOMER_SUCCESS_READ)),
) -> list[HealthScoreOut]:
    """Latest health snapshot for accounts flagged at_risk or critical."""
    rows = (
        await db.execute(
            select(CustomerHealthScore)
            .where(CustomerHealthScore.org_id == ctx.org_id,
                   CustomerHealthScore.category.in_(["at_risk", "critical"]))
            .order_by(CustomerHealthScore.churn_risk.desc())
            .limit(100)
        )
    ).scalars().all()
    return [HealthScoreOut.model_validate(r) for r in rows]


@router.get("/actions", response_model=Page[EngagementActionOut])
async def list_actions(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    status: str | None = Query(None),
    _: object = Depends(require_permission(Permission.CUSTOMER_SUCCESS_READ)),
) -> Page[EngagementActionOut]:
    repo = TenantRepository(db, EngagementAction)
    filters = [EngagementAction.status == status] if status else []
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  filters=filters, order_by=EngagementAction.created_at.desc())
    return Page(
        items=[EngagementActionOut.model_validate(r) for r in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.post("/actions", response_model=EngagementActionOut, status_code=201)
async def create_action(
    payload: EngagementActionIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.CUSTOMER_SUCCESS_WRITE)),
) -> EngagementActionOut:
    account = await TenantRepository(db, CustomerAccount).get(ctx.org_id, payload.customer_id)
    if account is None:
        raise NotFoundError("Customer account not found.")
    repo = TenantRepository(db, EngagementAction)
    row = await repo.create(
        org_id=ctx.org_id, assignee_id=ctx.user.id, ai_generated=False, **payload.model_dump()
    )
    return EngagementActionOut.model_validate(row)
