"""RAG retrieval for the AI Health Assistant.

Embeds the user's question and pulls the most relevant curated health-knowledge
references (conditions, symptoms, lab tests, first aid, medication classes, …)
from pgvector, plus a direct medicine match when the question names a drug. The
assistant injects these as grounding context before answering, so replies are
backed by a real knowledge base rather than the model's memory alone.

Degrades gracefully: with no Gemini key, no embedded rows, or a retrieval error,
it returns "" and the assistant answers from general medical knowledge.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import gemini
from app.ai.medical_rag import match_medicine
from app.core.logging import get_logger
from app.models.health import HealthKnowledge

logger = get_logger("health_rag")

# Cosine distance (0 = identical) above which a knowledge hit is too weak to use.
_MAX_DISTANCE = 0.55


def _format_medicine(m) -> str:
    parts = [f"Medicine — {m.name}" + (f" ({m.generic_name})" if m.generic_name else "")]
    if m.purpose:
        parts.append(f"Used for: {m.purpose}")
    if m.how_it_works:
        parts.append(f"How it works: {m.how_it_works}")
    if m.side_effects:
        parts.append(f"Common side effects: {m.side_effects}")
    if m.timing or m.food_instructions:
        parts.append(f"Timing/food: {m.timing or ''} {m.food_instructions or ''}".strip())
    if m.warnings:
        parts.append(f"Warnings: {m.warnings}")
    return " | ".join(parts)


async def retrieve(db: AsyncSession, query: str, *, k: int = 5) -> str:
    """Return a formatted reference-context block for `query`, or "" if none."""
    q = (query or "").strip()
    if not q or not gemini.is_configured():
        return ""

    chunks: list[str] = []

    # 1) Semantic search over the curated health-knowledge base.
    has_kb = (
        await db.execute(
            select(HealthKnowledge.id).where(HealthKnowledge.embedding.isnot(None)).limit(1)
        )
    ).first()
    if has_kb:
        try:
            vec = await gemini.embed(q, task_type="RETRIEVAL_QUERY")
        except Exception as exc:  # network / quota — degrade gracefully
            logger.warning("health_rag_embed_failed", error=str(exc))
            return ""
        dist = HealthKnowledge.embedding.cosine_distance(vec)
        rows = (
            await db.execute(
                select(HealthKnowledge, dist.label("d"))
                .where(HealthKnowledge.embedding.isnot(None))
                .order_by(dist)
                .limit(k)
            )
        ).all()
        for row, d in rows:
            if d is not None and d <= _MAX_DISTANCE:
                chunks.append(f"{row.title}: {row.content}")

    # 2) Direct medicine match when the question names a drug (exact/prefix/contains
    #    inside match_medicine; only include a rich row to avoid noise).
    try:
        med = await match_medicine(db, q)
        if med and med.purpose:
            chunks.append(_format_medicine(med))
    except Exception as exc:  # noqa: BLE001 — retrieval must never break the chat
        logger.warning("health_rag_medicine_failed", error=str(exc))

    if not chunks:
        return ""
    return "\n".join(f"- {c}" for c in chunks)
