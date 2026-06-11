"""AI Onboarding Agent routes — flows, steps, per-user progress & completion rates."""
from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select

from app.core.deps import CurrentContext, DbSession, PaginationDep, require_permission
from app.core.exceptions import NotFoundError
from app.core.permissions import Permission
from app.models.enums import OnboardingStatus
from app.models.onboarding import (
    OnboardingFlow,
    OnboardingStep,
    UserOnboarding,
    UserOnboardingStep,
)
from app.repositories.base import TenantRepository
from app.schemas.common import MessageResponse, Page, PageMeta
from app.schemas.ops import (
    CompleteStepRequest,
    OnboardingFlowIn,
    OnboardingFlowOut,
    OnboardingStats,
    OnboardingStepIn,
    OnboardingStepOut,
    UserOnboardingOut,
)

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.get("/flows", response_model=Page[OnboardingFlowOut])
async def list_flows(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    _: object = Depends(require_permission(Permission.ONBOARDING_READ)),
) -> Page[OnboardingFlowOut]:
    repo = TenantRepository(db, OnboardingFlow)
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  order_by=OnboardingFlow.created_at.desc())
    return Page(
        items=[OnboardingFlowOut.model_validate(r) for r in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.post("/flows", response_model=OnboardingFlowOut, status_code=201)
async def create_flow(
    payload: OnboardingFlowIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.ONBOARDING_WRITE)),
) -> OnboardingFlowOut:
    repo = TenantRepository(db, OnboardingFlow)
    row = await repo.create(org_id=ctx.org_id, **payload.model_dump())
    return OnboardingFlowOut.model_validate(row)


@router.post("/steps", response_model=OnboardingStepOut, status_code=201)
async def create_step(
    payload: OnboardingStepIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.ONBOARDING_WRITE)),
) -> OnboardingStepOut:
    flow = await TenantRepository(db, OnboardingFlow).get(ctx.org_id, payload.flow_id)
    if flow is None:
        raise NotFoundError("Onboarding flow not found.")
    repo = TenantRepository(db, OnboardingStep)
    row = await repo.create(org_id=ctx.org_id, **payload.model_dump())
    return OnboardingStepOut.model_validate(row)


@router.get("/flows/{flow_id}/steps", response_model=list[OnboardingStepOut])
async def list_steps(
    flow_id: uuid.UUID, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.ONBOARDING_READ)),
) -> list[OnboardingStepOut]:
    rows = (
        await db.execute(
            select(OnboardingStep)
            .where(OnboardingStep.org_id == ctx.org_id, OnboardingStep.flow_id == flow_id)
            .order_by(OnboardingStep.position.asc())
        )
    ).scalars().all()
    return [OnboardingStepOut.model_validate(r) for r in rows]


@router.post("/flows/{flow_id}/start", response_model=UserOnboardingOut, status_code=201)
async def start_onboarding(
    flow_id: uuid.UUID, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.ONBOARDING_READ)),
) -> UserOnboardingOut:
    """Enroll the current user into a flow (idempotent)."""
    flow = await TenantRepository(db, OnboardingFlow).get(ctx.org_id, flow_id)
    if flow is None:
        raise NotFoundError("Onboarding flow not found.")
    existing = (
        await db.execute(
            select(UserOnboarding).where(
                UserOnboarding.user_id == ctx.user.id, UserOnboarding.flow_id == flow_id
            )
        )
    ).scalar_one_or_none()
    if existing:
        return UserOnboardingOut.model_validate(existing)
    row = UserOnboarding(
        org_id=ctx.org_id, user_id=ctx.user.id, flow_id=flow_id,
        status=OnboardingStatus.IN_PROGRESS, started_at=datetime.utcnow(),
        last_activity_at=datetime.utcnow(),
    )
    db.add(row)
    await db.flush()
    return UserOnboardingOut.model_validate(row)


@router.post("/flows/{flow_id}/complete-step", response_model=UserOnboardingOut)
async def complete_step(
    flow_id: uuid.UUID, payload: CompleteStepRequest, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.ONBOARDING_READ)),
) -> UserOnboardingOut:
    """Mark a step complete and recompute the user's completion percentage."""
    enrolment = (
        await db.execute(
            select(UserOnboarding).where(
                UserOnboarding.user_id == ctx.user.id, UserOnboarding.flow_id == flow_id
            )
        )
    ).scalar_one_or_none()
    if enrolment is None:
        raise NotFoundError("Onboarding not started for this flow.")

    step = await TenantRepository(db, OnboardingStep).get(ctx.org_id, payload.step_id)
    if step is None or step.flow_id != flow_id:
        raise NotFoundError("Step not found in this flow.")

    progress = (
        await db.execute(
            select(UserOnboardingStep).where(
                UserOnboardingStep.user_onboarding_id == enrolment.id,
                UserOnboardingStep.step_id == payload.step_id,
            )
        )
    ).scalar_one_or_none()
    if progress is None:
        progress = UserOnboardingStep(
            org_id=ctx.org_id, user_onboarding_id=enrolment.id, step_id=payload.step_id,
        )
        db.add(progress)
    progress.is_completed = not payload.skipped
    progress.skipped = payload.skipped
    progress.completed_at = datetime.utcnow()

    total_steps = (
        await db.execute(
            select(func.count()).select_from(OnboardingStep).where(
                OnboardingStep.flow_id == flow_id
            )
        )
    ).scalar_one()
    done_steps = (
        await db.execute(
            select(func.count()).select_from(UserOnboardingStep).where(
                UserOnboardingStep.user_onboarding_id == enrolment.id,
                UserOnboardingStep.is_completed.is_(True),
            )
        )
    ).scalar_one()
    # +1 accounts for the step just completed if it wasn't counted yet.
    completed = int(done_steps) + (1 if (progress.is_completed) else 0)
    completed = min(completed, int(total_steps) or 1)
    pct = round(completed / (int(total_steps) or 1) * 100)
    enrolment.completion_pct = min(pct, 100)
    enrolment.last_activity_at = datetime.utcnow()
    if enrolment.completion_pct >= 100:
        enrolment.status = OnboardingStatus.COMPLETED
        enrolment.completed_at = datetime.utcnow()
    await db.flush()
    return UserOnboardingOut.model_validate(enrolment)


@router.get("/stats", response_model=OnboardingStats)
async def completion_stats(
    ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.ONBOARDING_READ)),
) -> OnboardingStats:
    rows = (
        await db.execute(
            select(UserOnboarding.status, func.count())
            .where(UserOnboarding.org_id == ctx.org_id)
            .group_by(UserOnboarding.status)
        )
    ).all()
    by_status = {s.value: 0 for s in OnboardingStatus}
    for status, count in rows:
        by_status[status] = int(count)
    total = sum(by_status.values())
    completed = by_status[OnboardingStatus.COMPLETED.value]
    return OnboardingStats(
        total_users=total,
        completed=completed,
        in_progress=by_status[OnboardingStatus.IN_PROGRESS.value],
        not_started=by_status[OnboardingStatus.NOT_STARTED.value],
        completion_rate=round(completed / total * 100, 1) if total else 0.0,
    )
