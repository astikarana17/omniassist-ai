"""Inbound Voice webhooks (Twilio) — IVR → speech-to-text → AI → text-to-speech.

Twilio handles STT (Gather input=speech) and TTS (Say). We bridge the transcribed
speech to the AI agent and return TwiML with the spoken reply.
"""
from __future__ import annotations

from fastapi import APIRouter, Request, Response
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.integrations import twilio_client
from app.models.enums import Channel
from app.models.ops import VoiceCall
from app.models.organization import Setting
from app.services.conversation_service import ConversationService

logger = get_logger("webhook.voice")
router = APIRouter(prefix="/webhooks/twilio", tags=["Webhooks"])

_GREETING = "Hi, you've reached OmniAssist support. How can I help you today?"


def _action_url(base: str) -> str:
    return f"{base}{settings.API_V1_PREFIX}/webhooks/twilio/voice/gather"


async def _org_for_number(db, to_number: str):
    rows = (
        (await db.execute(select(Setting).where(Setting.key == "channel:voice"))).scalars().all()
    )
    for s in rows:
        if to_number in str(s.value.get("number", "")):
            return s.org_id
    return rows[0].org_id if rows else None


@router.post("/voice")
async def voice_inbound(request: Request) -> Response:
    form = dict(await request.form())
    signature = request.headers.get("X-Twilio-Signature", "")
    if not twilio_client.validate_signature(str(request.url), form, signature):
        return Response(status_code=403)

    call_sid = form.get("CallSid", "")
    from_number = form.get("From", "")
    to_number = form.get("To", "")
    base = f"{request.url.scheme}://{request.url.netloc}"

    async for db in get_db():
        org_id = await _org_for_number(db, to_number)
        if org_id:
            db.add(
                VoiceCall(
                    org_id=org_id, call_sid=call_sid, from_number=from_number,
                    to_number=to_number, direction="inbound",
                )
            )
    twiml = twilio_client.voice_greeting_twiml(_GREETING, _action_url(base))
    return Response(content=twiml, media_type="application/xml")


@router.post("/voice/gather")
async def voice_gather(request: Request) -> Response:
    form = dict(await request.form())
    speech = form.get("SpeechResult", "")
    call_sid = form.get("CallSid", "")
    from_number = form.get("From", "")
    to_number = form.get("To", "")
    base = f"{request.url.scheme}://{request.url.netloc}"

    if not speech:
        twiml = twilio_client.voice_reply_twiml(
            "Sorry, I didn't catch that. Could you repeat?", _action_url(base)
        )
        return Response(content=twiml, media_type="application/xml")

    reply_text = "Let me connect you with a teammate."
    async for db in get_db():
        org_id = await _org_for_number(db, to_number)
        if org_id:
            svc = ConversationService(db)
            contact = await svc.resolve_contact(org_id, name="Caller", phone=from_number)
            conv = await svc.resolve_conversation(
                org_id, contact, Channel.VOICE, external_ref=call_sid
            )
            _, ai_message = await svc.handle_inbound(
                org_id=org_id, conversation=conv, text=speech, author_name="Caller"
            )
            # Append to the call transcript.
            call = (
                await db.execute(select(VoiceCall).where(VoiceCall.call_sid == call_sid))
            ).scalar_one_or_none()
            if call is not None:
                call.transcript = [
                    *call.transcript,
                    {"speaker": "customer", "text": speech},
                    {"speaker": "ai", "text": ai_message.content if ai_message else ""},
                ]
            if ai_message:
                reply_text = ai_message.content

    twiml = twilio_client.voice_reply_twiml(reply_text, _action_url(base))
    return Response(content=twiml, media_type="application/xml")
