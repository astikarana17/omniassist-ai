"""Inbound email webhook — parse, classify, AI-draft, optionally auto-send, create ticket.

Accepts a normalized JSON payload (from a Gmail push/Pub-Sub relay or an inbound-parse
provider). Verified by a shared secret header.
"""
from __future__ import annotations

from fastapi import APIRouter, Header, Request, Response
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.integrations import email_client
from app.models.enums import Channel
from app.models.organization import Setting
from app.services.conversation_service import ConversationService

logger = get_logger("webhook.gmail")
router = APIRouter(prefix="/webhooks/gmail", tags=["Webhooks"])


async def _org_for_recipient(db, recipient: str):
    rows = (
        (await db.execute(select(Setting).where(Setting.key == "channel:email"))).scalars().all()
    )
    for s in rows:
        if recipient and recipient in str(s.value.get("address", "")):
            return s.org_id
    return rows[0].org_id if rows else None


@router.post("/inbound")
async def gmail_inbound(
    request: Request, x_webhook_secret: str = Header(default="")
) -> Response:
    # Shared-secret verification (set the same value on your Gmail relay).
    expected = settings.SECRET_KEY[:24]
    if x_webhook_secret != expected:
        logger.warning("gmail_bad_secret")
        return Response(status_code=403)

    payload = await request.json()
    email = email_client.parse_inbound(payload)
    recipient = payload.get("to", "")

    async for db in get_db():
        org_id = await _org_for_recipient(db, recipient)
        if not org_id:
            return Response(status_code=204)

        svc = ConversationService(db)
        contact = await svc.resolve_contact(
            org_id, name=email["from_name"], email=email["from_email"]
        )
        conv = await svc.resolve_conversation(
            org_id, contact, Channel.EMAIL, external_ref=email["thread_id"]
        )
        conv.subject = email["subject"]
        _, ai_message = await svc.handle_inbound(
            org_id=org_id, conversation=conv, text=email["body"], author_name=email["from_name"]
        )

    # Send the AI draft reply back over email (config decides auto vs review).
    if ai_message and ai_message.content and email["from_email"]:
        try:
            email_client.send_email(
                email["from_email"], f"Re: {email['subject']}", ai_message.content
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("gmail_reply_failed", error=str(exc))

    return Response(status_code=200)
