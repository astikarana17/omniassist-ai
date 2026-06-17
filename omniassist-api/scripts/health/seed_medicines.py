"""Seed the medicine knowledge base + (optionally) its pgvector embeddings.

Idempotent — safe to re-run. Two phases:
  1. Upsert structured medicine rows (works WITHOUT a Gemini key — powers exact
     name-match retrieval immediately).
  2. If GEMINI_API_KEY is set, embed each medicine and upsert into
     `medicine_embeddings` (powers semantic / fuzzy retrieval).

Usage:
    python -m scripts.health.seed_medicines           # rows + embeddings (if key)
    python -m scripts.health.seed_medicines --no-embed # rows only
"""
from __future__ import annotations

import argparse
import asyncio

from sqlalchemy import select

from app.ai import gemini
from app.core.database import AsyncSessionLocal
from app.models.health import Medicine, MedicineEmbedding
from scripts.health.medicines_data import MEDICINES

SOURCE = "starter-curated"


def _embed_text(m: Medicine) -> str:
    """The text we embed — everything a semantic query might match on."""
    return (
        f"{m.name} ({m.generic_name or ''}). Purpose: {m.purpose or ''} "
        f"How it works: {m.how_it_works or ''} Side effects: {m.side_effects or ''} "
        f"Warnings: {m.warnings or ''} Food: {m.food_instructions or ''} "
        f"Timing: {m.timing or ''}"
    ).strip()


async def _upsert_rows() -> list[Medicine]:
    """Insert new medicines / update existing ones (matched by name). Returns all rows."""
    created = updated = 0
    async with AsyncSessionLocal() as db:
        for data in MEDICINES:
            existing = (
                await db.execute(select(Medicine).where(Medicine.name == data["name"]))
            ).scalar_one_or_none()
            if existing is None:
                db.add(Medicine(source=SOURCE, **data))
                created += 1
            else:
                for k, v in data.items():
                    setattr(existing, k, v)
                existing.source = SOURCE
                updated += 1
        await db.commit()
        rows = list((await db.execute(select(Medicine))).scalars().all())
    print(f"[rows] {created} created, {updated} updated, {len(rows)} total")
    return rows


async def _embed_rows() -> None:
    """Embed medicines that don't yet have an up-to-date embedding row."""
    if not gemini.is_configured():
        print("[embed] skipped — GEMINI_API_KEY not set (name-match retrieval still works).")
        return

    async with AsyncSessionLocal() as db:
        rows = list((await db.execute(select(Medicine))).scalars().all())
        have = {
            e.medicine_id
            for e in (await db.execute(select(MedicineEmbedding))).scalars().all()
        }
        todo = [m for m in rows if m.id not in have]
        if not todo:
            print(f"[embed] up to date — {len(rows)} medicines already embedded.")
            return

        print(f"[embed] embedding {len(todo)} medicines via Gemini…")
        done = 0
        for m in todo:
            content = _embed_text(m)
            vector = await gemini.embed(content, task_type="RETRIEVAL_DOCUMENT")
            db.add(MedicineEmbedding(medicine_id=m.id, content=content, embedding=vector))
            done += 1
            if done % 10 == 0:
                await db.commit()
                print(f"  …{done}/{len(todo)}")
        await db.commit()
        print(f"[embed] done — {done} embeddings written.")


async def main(embed: bool) -> None:
    await _upsert_rows()
    if embed:
        await _embed_rows()
    print("[OK] medicine knowledge base seeded.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-embed", action="store_true", help="seed rows only, skip embeddings")
    args = parser.parse_args()
    asyncio.run(main(embed=not args.no_embed))
