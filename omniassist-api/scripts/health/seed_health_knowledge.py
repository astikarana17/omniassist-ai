"""Seed the AI Health Assistant knowledge base + its pgvector embeddings.

Idempotent — safe to re-run. Two phases:
  1. Upsert curated health-knowledge rows (matched by title).
  2. If GEMINI_API_KEY is set, embed rows that don't yet have an embedding so the
     assistant can retrieve them (RAG). Without a key, rows are stored but the
     assistant simply falls back to general knowledge.

Usage:
    python -m scripts.health.seed_health_knowledge            # rows + embeddings
    python -m scripts.health.seed_health_knowledge --no-embed # rows only
"""
from __future__ import annotations

import argparse
import asyncio

from sqlalchemy import select

from app.ai import gemini
from app.core.database import AsyncSessionLocal
from app.models.health import HealthKnowledge
from scripts.health.health_knowledge_data import HEALTH_KNOWLEDGE

SOURCE = "curated-health-kb"


def _embed_text(row: HealthKnowledge) -> str:
    return f"{row.title}. {row.content}".strip()


async def _upsert_rows() -> None:
    created = updated = 0
    async with AsyncSessionLocal() as db:
        for data in HEALTH_KNOWLEDGE:
            existing = (
                await db.execute(select(HealthKnowledge).where(HealthKnowledge.title == data["title"]))
            ).scalar_one_or_none()
            if existing is None:
                db.add(HealthKnowledge(source=SOURCE, **data))
                created += 1
            else:
                changed = existing.content != data["content"] or existing.category != data.get("category")
                existing.content = data["content"]
                existing.category = data.get("category")
                existing.source = SOURCE
                if changed:
                    existing.embedding = None  # content changed → re-embed
                updated += 1
        await db.commit()
    print(f"[rows] {created} created, {updated} updated ({len(HEALTH_KNOWLEDGE)} curated).")


async def _embed_rows() -> None:
    if not gemini.is_configured():
        print("[embed] skipped — GEMINI_API_KEY not set. Assistant falls back to general knowledge.")
        return
    async with AsyncSessionLocal() as db:
        todo = list(
            (await db.execute(select(HealthKnowledge).where(HealthKnowledge.embedding.is_(None)))).scalars().all()
        )
        if not todo:
            print("[embed] up to date — all health-knowledge rows already embedded.")
            return
        print(f"[embed] embedding {len(todo)} rows via Gemini…")
        done = 0
        for row in todo:
            vector = await gemini.embed(_embed_text(row), task_type="RETRIEVAL_DOCUMENT")
            row.embedding = vector
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
    print("[OK] health knowledge base seeded.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-embed", action="store_true", help="seed rows only, skip embeddings")
    args = parser.parse_args()
    asyncio.run(main(embed=not args.no_embed))
