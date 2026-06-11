"""In-app notification routes."""
from __future__ import annotations

import uuid

from fastapi import APIRouter
from sqlalchemy import select, update

from app.core.deps import CurrentContext, DbSession, PaginationDep
from app.core.exceptions import NotFoundError
from app.models.ops import Notification
from app.schemas.common import MessageResponse, Page, PageMeta
from app.schemas.domain import NotificationOut

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=Page[NotificationOut])
async def list_notifications(
    ctx: CurrentContext, db: DbSession, page: PaginationDep, unread_only: bool = False
) -> Page[NotificationOut]:
    conditions = [
        Notification.org_id == ctx.org_id,
        (Notification.user_id == ctx.user.id) | (Notification.user_id.is_(None)),
    ]
    if unread_only:
        conditions.append(Notification.read.is_(False))
    rows = (
        (
            await db.execute(
                select(Notification)
                .where(*conditions)
                .order_by(Notification.created_at.desc())
                .limit(page.limit)
                .offset(page.offset)
            )
        )
        .scalars()
        .all()
    )
    return Page(
        items=[NotificationOut.model_validate(n) for n in rows],
        meta=PageMeta(total=len(rows), limit=page.limit, offset=page.offset,
                      has_more=len(rows) == page.limit),
    )


@router.post("/{notification_id}/read", response_model=MessageResponse)
async def mark_read(notification_id: uuid.UUID, ctx: CurrentContext, db: DbSession) -> MessageResponse:
    notif = await db.get(Notification, notification_id)
    if not notif or notif.org_id != ctx.org_id:
        raise NotFoundError("Notification not found.")
    notif.read = True
    return MessageResponse(message="Marked read.")


@router.post("/read-all", response_model=MessageResponse)
async def mark_all_read(ctx: CurrentContext, db: DbSession) -> MessageResponse:
    await db.execute(
        update(Notification)
        .where(
            Notification.org_id == ctx.org_id,
            (Notification.user_id == ctx.user.id) | (Notification.user_id.is_(None)),
            Notification.read.is_(False),
        )
        .values(read=True)
    )
    return MessageResponse(message="All notifications marked read.")
