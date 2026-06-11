"""AI Demo & Meeting Agent routes — scheduling, reminders, follow-up."""
from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.core.deps import CurrentContext, DbSession, PaginationDep, require_permission
from app.core.exceptions import NotFoundError
from app.core.permissions import Permission
from app.models.enums import MeetingStatus
from app.models.meeting import Meeting, MeetingReminder
from app.repositories.base import TenantRepository
from app.schemas.common import MessageResponse, Page, PageMeta
from app.schemas.ops import MeetingIn, MeetingOut, ReminderIn, ReminderOut

router = APIRouter(prefix="/meetings", tags=["Meetings"])


@router.get("", response_model=Page[MeetingOut])
async def list_meetings(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    status: str | None = Query(None),
    _: object = Depends(require_permission(Permission.MEETING_READ)),
) -> Page[MeetingOut]:
    repo = TenantRepository(db, Meeting)
    filters = [Meeting.status == status] if status else []
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  filters=filters, order_by=Meeting.starts_at.desc())
    return Page(
        items=[MeetingOut.model_validate(r) for r in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.post("", response_model=MeetingOut, status_code=201)
async def schedule_meeting(
    payload: MeetingIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.MEETING_WRITE)),
) -> MeetingOut:
    repo = TenantRepository(db, Meeting)
    row = await repo.create(org_id=ctx.org_id, organizer_id=ctx.user.id, **payload.model_dump())
    return MeetingOut.model_validate(row)


@router.post("/{meeting_id}/reminders", response_model=ReminderOut, status_code=201)
async def add_reminder(
    meeting_id: uuid.UUID, payload: ReminderIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.MEETING_WRITE)),
) -> ReminderOut:
    meeting = await TenantRepository(db, Meeting).get(ctx.org_id, meeting_id)
    if meeting is None:
        raise NotFoundError("Meeting not found.")
    repo = TenantRepository(db, MeetingReminder)
    row = await repo.create(org_id=ctx.org_id, meeting_id=meeting_id, **payload.model_dump())
    return ReminderOut.model_validate(row)


@router.post("/{meeting_id}/status", response_model=MeetingOut)
async def update_status(
    meeting_id: uuid.UUID, ctx: CurrentContext, db: DbSession,
    value: MeetingStatus = Query(...),
    _: object = Depends(require_permission(Permission.MEETING_WRITE)),
) -> MeetingOut:
    repo = TenantRepository(db, Meeting)
    meeting = await repo.get(ctx.org_id, meeting_id)
    if meeting is None:
        raise NotFoundError("Meeting not found.")
    meeting.status = value.value
    await db.flush()
    return MeetingOut.model_validate(meeting)


@router.post("/{meeting_id}/followup", response_model=MessageResponse)
async def mark_followup_sent(
    meeting_id: uuid.UUID, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.MEETING_WRITE)),
) -> MessageResponse:
    repo = TenantRepository(db, Meeting)
    meeting = await repo.get(ctx.org_id, meeting_id)
    if meeting is None:
        raise NotFoundError("Meeting not found.")
    meeting.followup_sent = True
    await db.flush()
    return MessageResponse(message="Follow-up marked as sent.")
