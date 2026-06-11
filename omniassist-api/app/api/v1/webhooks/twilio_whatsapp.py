"""Inbound WhatsApp webhook (Twilio).

Resolves the org from the Twilio "To" number (configured per-org), runs the AI
support/sales agent through the conversation engine, and replies via WhatsApp.
"""
from __future__ import annotations

from fastapi import APIRouter, Request, Response
from sqlalchemy import select

from app.core.database import get_db
from app.core.logging import get_logger
from app.integrations import twilio_client
from app.models.enums import Channel
from app.models.organization import Setting
from app.services.conversation_service import ConversationService

logger = get_logger("webhook.whatsapp")
router = APIRouter(prefix="/webhooks/twilio", tags=["Webhooks"])


async def _resolve_org_id(db, to_number: str):
    """Map the inbound Twilio number to an org via the channels setting."""
    rows = (
        (
            await db.execute(
                select(Setting).where(Setting.key == "channel:whatsapp")
            )
        )
        .scalars()
        .all()
    )
    for s in rows:
        if to_number.replace("whatsapp:", "") in str(s.value.get("number", "")):
            return s.org_id
    return rows[0].org_id if rows else None


@router.post("/whatsapp")
async def whatsapp_inbound(request: Request) -> Response:
    form = dict(await request.form())
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    if not twilio_client.validate_signature(url, form, signature):
        logger.warning("whatsapp_bad_signature")
        return Response(status_code=403)

    from_number = form.get("From", "")
    to_number = form.get("To", "")
    body = form.get("Body", "")
    profile_name = form.get("ProfileName", "WhatsApp User")

    async for db in get_db():
        org_id = await _resolve_org_id(db, to_number)
        if not org_id:
            logger.warning("whatsapp_no_org", to=to_number)
            return Response(content="<Response/>", media_type="application/xml")

        svc = ConversationService(db)
        contact = await svc.resolve_contact(
            org_id, name=profile_name, phone=from_number.replace("whatsapp:", "")
        )
        conv = await svc.resolve_conversation(
            org_id, contact, Channel.WHATSAPP, external_ref=from_number
        )
        _, ai_message = await svc.handle_inbound(
            org_id=org_id, conversation=conv, text=body, author_name=profile_name
        )

    # Reply asynchronously via the REST API (more reliable than TwiML for AI latency).
    if ai_message and ai_message.content:
        try:
            twilio_client.send_whatsapp(from_number, ai_message.content)
        except Exception as exc:  # noqa: BLE001
            logger.error("whatsapp_send_failed", error=str(exc))

    return Response(content="<Response/>", media_type="application/xml")
