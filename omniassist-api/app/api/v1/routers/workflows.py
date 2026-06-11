"""No-code Workflow Automation Engine routes — define, trigger and inspect runs."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentContext, DbSession, PaginationDep, require_permission
from app.core.exceptions import NotFoundError, ValidationError
from app.core.permissions import Permission
from app.models.enums import WorkflowStatus
from app.models.workflow import Workflow, WorkflowRun
from app.repositories.base import TenantRepository
from app.schemas.common import Page, PageMeta
from app.schemas.ops import (
    TriggerWorkflowRequest,
    WorkflowIn,
    WorkflowOut,
    WorkflowRunDetail,
    WorkflowRunOut,
)
from app.services.ops_service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("", response_model=Page[WorkflowOut])
async def list_workflows(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    _: object = Depends(require_permission(Permission.WORKFLOW_READ)),
) -> Page[WorkflowOut]:
    repo = TenantRepository(db, Workflow)
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  order_by=Workflow.created_at.desc())
    return Page(
        items=[WorkflowOut.model_validate(r) for r in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.post("", response_model=WorkflowOut, status_code=201)
async def create_workflow(
    payload: WorkflowIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.WORKFLOW_WRITE)),
) -> WorkflowOut:
    repo = TenantRepository(db, Workflow)
    row = await repo.create(org_id=ctx.org_id, created_by=ctx.user.id, **payload.model_dump())
    return WorkflowOut.model_validate(row)


@router.post("/{workflow_id}/trigger", response_model=WorkflowRunDetail, status_code=201)
async def trigger_workflow(
    workflow_id: uuid.UUID, payload: TriggerWorkflowRequest, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.WORKFLOW_WRITE)),
) -> WorkflowRunDetail:
    workflow = await TenantRepository(db, Workflow).get(ctx.org_id, workflow_id)
    if workflow is None:
        raise NotFoundError("Workflow not found.")
    if workflow.status == WorkflowStatus.ARCHIVED:
        raise ValidationError("Cannot run an archived workflow.")
    run = await WorkflowService(db).run(
        ctx.org_id, workflow, context=payload.context,
        triggered_by=ctx.user.id, trigger_source=payload.trigger_source or "manual",
    )
    # Reload with steps for the response.
    run = (
        await db.execute(
            select(WorkflowRun).options(selectinload(WorkflowRun.steps))
            .where(WorkflowRun.id == run.id)
        )
    ).scalar_one()
    return WorkflowRunDetail.model_validate(run)


@router.get("/{workflow_id}/runs", response_model=Page[WorkflowRunOut])
async def list_runs(
    workflow_id: uuid.UUID, ctx: CurrentContext, db: DbSession, page: PaginationDep,
    _: object = Depends(require_permission(Permission.WORKFLOW_READ)),
) -> Page[WorkflowRunOut]:
    repo = TenantRepository(db, WorkflowRun)
    rows, total = await repo.list(
        ctx.org_id, limit=page.limit, offset=page.offset,
        filters=[WorkflowRun.workflow_id == workflow_id],
        order_by=WorkflowRun.created_at.desc(),
    )
    return Page(
        items=[WorkflowRunOut.model_validate(r) for r in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )
