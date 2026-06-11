"""Notification fan-out across in-app, email and Slack channels."""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.enums import NotificationChannel
from app.models.ops import Notification

logger = get_logger("notifications")


async def notify(
    db: AsyncSession,
    *,
    org_id: uuid.UUID,
    type_: str,
    title: str,
    body: str | None = None,
    user_id: uuid.UUID | None = None,
    payload: dict[str, Any] | None = None,
    channels: list[NotificationChannel] | None = None,
) -> Notification:
    """Persist an in-app notification and enqueue external delivery (Slack/email)."""
    channels = channels or [NotificationChannel.IN_APP]
    record = Notification(
        org_id=org_id,
        user_id=user_id,
        type=type_,
        channel=NotificationChannel.IN_APP,
        title=title,
        body=body,
        payload=payload or {},
        delivery_status="sent",
    )
    db.add(record)
    await db.flush()

    # External channels are delivered asynchronously by the worker.
    if NotificationChannel.SLACK in channels:
        _enqueue_slack(org_id, title, body)
    if NotificationChannel.EMAIL in channels and payload and payload.get("email"):
        _enqueue_email(payload["email"], title, body or "")

    return record


def _enqueue_slack(org_id: uuid.UUID, title: str, body: str | None) -> None:
    try:
        from app.workers.tasks import send_slack_notification

        send_slack_notification.delay(str(org_id), f"*{title}*\n{body or ''}")
    except Exception as exc:  # noqa: BLE001
        logger.warning("slack_enqueue_failed", error=str(exc))


def _enqueue_email(to: str, subject: str, body: str) -> None:
    try:
        from app.workers.tasks import send_email

        send_email.delay(to, subject, body)
    except Exception as exc:  # noqa: BLE001
        logger.warning("email_enqueue_failed", error=str(exc))
