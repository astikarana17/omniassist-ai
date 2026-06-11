"""Live end-to-end demo: run the real Product Expert agent against the live
Supabase data for the seeded TCS org. Uses the actual app code paths
(run_product_expert + KnowledgeGapService), no HTTP/auth needed.

Usage:  python -m scripts.demo_expert
"""
from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.ai.graphs import ops_agents
from app.core.database import AsyncSessionLocal
from app.models.organization import Organization
from app.services.ops_service import KnowledgeGapService

QUESTIONS = [
    "Who is the CEO of the company?",
    "What does ignio do?",
    "How much does it cost to engage you?",
    "Who are your main competitors?",
    "Tell me about TCS BaNCS",
    "How many employees are there?",
    "What is TCS iON?",
    "When was the company founded?",
    "Do you sell pizza in Antarctica?",  # no coverage → should flag a knowledge gap
]


async def main() -> None:
    async with AsyncSessionLocal() as db:
        org = (
            await db.execute(select(Organization).where(Organization.slug == "tcs"))
        ).scalar_one()
        print(f"=== AI Product Expert — {org.name} (live Supabase) ===\n")

        for q in QUESTIONS:
            res = await ops_agents.run_product_expert(db, org.id, q, use_kb=False)
            # Mirror the /company/ask endpoint: record a gap on low confidence.
            tag = ""
            if res.knowledge_gap:
                await KnowledgeGapService(db).record(
                    org.id, question=q, confidence=res.confidence
                )
                tag = "  [knowledge gap recorded]"
            print(f"Q: {q}")
            print(f"A: {res.reply}")
            print(f"   (confidence {res.confidence}{tag})\n")

        await db.commit()

        counts = await KnowledgeGapService(db).counts_by_status(org.id)
        print(f"=== Knowledge Gap dashboard (self-improvement) === {counts}")


if __name__ == "__main__":
    asyncio.run(main())
