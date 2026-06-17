"""AI Health Assistant API — stateless medical Q&A chat."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.deps import CurrentContext, DbSession
from app.schemas.health import HealthChatRequest, HealthChatResponse
from app.services import health_assistant_service

router = APIRouter(prefix="/health-assistant", tags=["AI Health Assistant"])


@router.post("/chat", response_model=HealthChatResponse)
async def chat(payload: HealthChatRequest, ctx: CurrentContext, db: DbSession) -> HealthChatResponse:
    """Answer a health question. The client sends the running conversation; the
    server is stateless. RAG-grounded via the medical knowledge base. Never
    diagnoses — see the service's safety rules."""
    reply = await health_assistant_service.answer(
        [m.model_dump() for m in payload.messages], db=db
    )
    return HealthChatResponse(reply=reply)
