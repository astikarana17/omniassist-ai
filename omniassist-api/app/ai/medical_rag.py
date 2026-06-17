"""Medical knowledge-base retrieval for the Prescription Intelligence Engine.

Given a medicine name read off a prescription, find the best-matching reference
row. SQL-based so it scales to the full Indian medicine catalogue (250k+ rows).
Strategy (cheapest → richest), first hit wins:
  1. Exact name / generic match (prefers rows with rich patient-education data).
  2. Prefix match — handles brand+form names ("Azithral" → "Azithral 500 Tablet").
  3. Containment — KB name inside the query, or query inside the composition.
  4. pgvector semantic match over the curated (embedded) set.
"""
from __future__ import annotations

from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import gemini
from app.core.logging import get_logger
from app.models.health import Medicine, MedicineEmbedding

logger = get_logger("medical_rag")

# Prefer reference rows that actually carry explanation data when several match.
_RICH_FIRST = (Medicine.purpose.isnot(None)).desc()


def _clean(q: str) -> str:
    return q.strip().lower().replace("%", "").replace("_", "")


async def _exact(db: AsyncSession, q: str) -> Medicine | None:
    stmt = (
        select(Medicine)
        .where(or_(func.lower(Medicine.name) == q, func.lower(Medicine.generic_name) == q))
        .order_by(_RICH_FIRST)
        .limit(1)
    )
    return (await db.execute(stmt)).scalars().first()


async def _prefix(db: AsyncSession, q: str) -> Medicine | None:
    """The query is the start of a longer catalogue name (brand + strength + form)."""
    stmt = (
        select(Medicine)
        .where(func.lower(Medicine.name).like(f"{q}%"))
        .order_by(_RICH_FIRST, func.length(Medicine.name).asc())  # shortest = closest
        .limit(1)
    )
    return (await db.execute(stmt)).scalars().first()


async def _contains(db: AsyncSession, q: str) -> Medicine | None:
    """Query appears inside a catalogue name or composition. Forward-LIKE so the
    pg_trgm GIN indexes on lower(name)/lower(generic_name) accelerate it."""
    like = f"%{q}%"
    stmt = (
        select(Medicine)
        .where(or_(func.lower(Medicine.name).like(like), func.lower(Medicine.generic_name).like(like)))
        .order_by(_RICH_FIRST, func.length(Medicine.name).asc())
        .limit(1)
    )
    return (await db.execute(stmt)).scalars().first()


async def _semantic(db: AsyncSession, q: str) -> Medicine | None:
    if not gemini.is_configured():
        return None
    if not (await db.execute(select(MedicineEmbedding.id).limit(1))).first():
        return None  # nothing embedded yet
    try:
        vec = await gemini.embed(q, task_type="RETRIEVAL_QUERY")
    except Exception as exc:  # network / quota — degrade gracefully
        logger.warning("medical_rag_embed_failed", error=str(exc))
        return None
    stmt = (
        select(Medicine)
        .join(MedicineEmbedding, MedicineEmbedding.medicine_id == Medicine.id)
        .order_by(MedicineEmbedding.embedding.cosine_distance(vec))
        .limit(1)
    )
    return (await db.execute(stmt)).scalars().first()


async def match_medicine(db: AsyncSession, query: str) -> Medicine | None:
    """Return the best KB match for an extracted medicine name, or None."""
    q = _clean(query or "")
    if not q:
        return None
    return (
        await _exact(db, q)
        or await _prefix(db, q)
        or await _contains(db, q)
        or await _semantic(db, q)
    )
