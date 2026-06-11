"""Twilio integration: WhatsApp/SMS sending, Voice TwiML, webhook signature validation."""
from __future__ import annotations

from twilio.request_validator import RequestValidator
from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("twilio")

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    return _client


def validate_signature(url: str, params: dict, signature: str) -> bool:
    """Verify an inbound Twilio webhook signature (anti-spoofing)."""
    if not settings.TWILIO_AUTH_TOKEN:
        return False
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    return validator.validate(url, params, signature or "")


def send_whatsapp(to: str, body: str, media_url: str | None = None) -> str:
    """Send an outbound WhatsApp message. ``to`` is a bare number or whatsapp:+E164."""
    dest = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
    kwargs = {"from_": settings.TWILIO_WHATSAPP_NUMBER, "to": dest, "body": body}
    if media_url:
        kwargs["media_url"] = [media_url]
    msg = get_client().messages.create(**kwargs)
    logger.info("whatsapp_sent", to=dest, sid=msg.sid)
    return msg.sid


def send_sms(to: str, body: str) -> str:
    msg = get_client().messages.create(
        from_=settings.TWILIO_VOICE_NUMBER, to=to, body=body
    )
    return msg.sid


def voice_greeting_twiml(prompt: str, action_url: str) -> str:
    """Build TwiML that speaks a prompt and gathers the caller's speech."""
    response = VoiceResponse()
    gather = Gather(
        input="speech", action=action_url, method="POST", speech_timeout="auto",
        language="en-US",
    )
    gather.say(prompt, voice="Polly.Joanna")
    response.append(gather)
    response.say("I didn't catch that. Goodbye.", voice="Polly.Joanna")
    return str(response)


def voice_reply_twiml(text: str, action_url: str, hangup: bool = False) -> str:
    """Speak an AI reply, then either gather more speech or hang up."""
    response = VoiceResponse()
    response.say(text, voice="Polly.Joanna")
    if hangup:
        response.hangup()
    else:
        gather = Gather(
            input="speech", action=action_url, method="POST", speech_timeout="auto",
            language="en-US",
        )
        response.append(gather)
    return str(response)
