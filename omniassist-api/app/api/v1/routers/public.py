"""Public widget routes (no JWT) — the embeddable website chat endpoint.

Identified by the organization slug. Heavily rate-limited by the global middleware.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import DbSession
from app.core.exceptions import ExternalServiceError, NotFoundError
from app.core.logging import get_logger
from app.models.enums import Channel
from app.models.organization import Organization
from app.schemas.domain import WidgetMessageRequest
from app.schemas.health import HealthChatRequest
from app.services import health_assistant_service
from app.services.conversation_service import ConversationService

logger = get_logger("public")

router = APIRouter(prefix="/public", tags=["Public Widget"])


@router.post("/health-demo/chat")
async def health_demo_chat(payload: HealthChatRequest, db: DbSession) -> dict:
    """Public, unauthenticated health Q&A for the landing-page demo.

    Reuses the REAL safety-railed, RAG-grounded Health Assistant brain (same model
    the signed-in /health-assistant page uses), so visitors get genuine, correct
    answers — not a canned human-handoff. Stateless: the client sends the running
    transcript. Degrades to a friendly message on provider error so the demo never
    hard-fails.
    """
    try:
        reply = await health_assistant_service.answer(
            [m.model_dump() for m in payload.messages], db=db
        )
    except ExternalServiceError as exc:
        logger.warning("health_demo_unavailable", error=str(exc))
        reply = (
            "I'm just waking up — please try again in a moment. You can also sign up "
            "to use the full Health Assistant."
        )
    return {"data": {"reply": reply}, "error": None}


@router.post("/widget/{org_slug}/message")
async def widget_message(org_slug: str, payload: WidgetMessageRequest) -> dict:
    async for db in get_db():
        org = (
            await db.execute(select(Organization).where(Organization.slug == org_slug))
        ).scalar_one_or_none()
        if not org or not org.is_active:
            raise NotFoundError("Workspace not found.")

        svc = ConversationService(db)
        contact = await svc.resolve_contact(
            org.id, name=payload.contact_name, email=payload.contact_email
        )
        if payload.conversation_id:
            from app.models.conversation import Conversation

            conv = await db.get(Conversation, payload.conversation_id)
            if not conv or conv.org_id != org.id:
                raise NotFoundError("Conversation not found.")
            conv.contact = contact
        else:
            conv = await svc.resolve_conversation(
                org.id, contact, Channel.WEB, external_ref=f"widget:{uuid.uuid4()}"
            )

        _, ai_message = await svc.handle_inbound(
            org_id=org.id, conversation=conv, text=payload.content,
            author_name=payload.contact_name,
        )
        return {
            "data": {
                "conversation_id": str(conv.id),
                "reply": ai_message.content if ai_message else None,
                "confidence": ai_message.confidence if ai_message else None,
                "sources": ai_message.sources if ai_message else [],
                "handed_off": conv.status == "pending",
            },
            "error": None,
        }
    raise NotFoundError("Database unavailable.")
