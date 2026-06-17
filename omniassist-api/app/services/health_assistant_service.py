"""AI Health Assistant — friendly general health Q&A.

Hard safety rails: never diagnoses, never prescribes doses, routes emergencies to
professional care, and always nudges users to consult a doctor.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import health_rag, openrouter
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger("health_assistant")

_MAX_TURNS = 12
_MAX_CHARS = 4000

_REFERENCE_PREAMBLE = (
    "\n\nREFERENCE KNOWLEDGE (retrieved from a trusted medical knowledge base — "
    "prefer these facts and weave them into your answer naturally; if they don't "
    "cover the question, use careful general medical knowledge and stay within the "
    "safety rules above. Never cite this block or say 'according to my references'):\n"
)

SYSTEM = (
    "You are a warm, trustworthy AI Health Assistant inside a healthcare app. You "
    "help people understand general health topics, medicines, symptoms, lab tests "
    "and prescriptions in simple, calm language.\n\n"
    "STRICT SAFETY RULES:\n"
    "1. NEVER give a diagnosis. Say things like 'I can't diagnose this, but here is "
    "some general information…'.\n"
    "2. NEVER recommend specific prescription doses. Tell users to follow their "
    "doctor's instructions.\n"
    "3. EMERGENCIES: if the user mentions chest pain, trouble breathing, severe "
    "bleeding, stroke signs, fainting, or thoughts of self-harm, tell them to seek "
    "emergency care or call their local emergency number immediately, first.\n"
    "4. Always remind the user to consult a qualified doctor for personal advice.\n"
    "5. Be concise, kind and clear. Use plain words, short paragraphs or bullet "
    "points. Do not be alarming.\n"
    "6. For a specific medicine, give general info (what it's for, how it works, "
    "common side effects, general timing/food notes) — not personalised dosing."
)


async def answer(messages: list[dict], db: AsyncSession | None = None) -> str:
    """Generate the assistant's reply to a conversation. Raises on provider error.

    When `db` is provided, the latest user question is grounded with RAG context
    retrieved from the curated medical knowledge base before answering.
    """
    if not openrouter.is_configured():
        raise ExternalServiceError(
            "The assistant isn't configured yet (OPENROUTER_API_KEY missing).",
            code="ASSISTANT_NOT_CONFIGURED",
        )
    trimmed = [
        {"role": ("assistant" if m.get("role") == "assistant" else "user"),
         "content": str(m.get("content", ""))[:_MAX_CHARS]}
        for m in messages[-_MAX_TURNS:]
        if m.get("content")
    ]
    if not trimmed:
        return "Hi! I'm your AI Health Assistant. Ask me about a medicine, symptom, or lab result and I'll explain it simply."

    # RAG: ground the answer in retrieved medical knowledge for the last user turn.
    system = SYSTEM
    if db is not None:
        last_user = next(
            (m["content"] for m in reversed(trimmed) if m["role"] == "user" and m["content"]),
            "",
        )
        if last_user:
            try:
                context = await health_rag.retrieve(db, last_user)
            except Exception as exc:  # noqa: BLE001 — never let retrieval break the chat
                logger.warning("health_rag_retrieve_failed", error=str(exc))
                context = ""
            if context:
                system = SYSTEM + _REFERENCE_PREAMBLE + context

    try:
        reply, _, _ = await openrouter.complete(system=system, messages=trimmed, max_tokens=800)
    except Exception as exc:  # noqa: BLE001 — surface a friendly error
        logger.error("health_assistant_failed", error=str(exc))
        raise ExternalServiceError(
            "The assistant is busy right now. Please try again in a moment.",
            code="ASSISTANT_ERROR",
        )
    return reply or "Sorry, I couldn't generate a response. Please try rephrasing."
