"""Verify the AI Product Expert can answer 100 realistic customer questions using
the knowledge base (structured company knowledge + the Pinecone RAG KB).

Runs each question through the REAL agent (run_product_expert, use_kb=True) against
live Supabase + Pinecone, and reports accuracy (answered confidently vs gaps).

Usage:  python -m scripts.verify_100
"""
from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.ai.graphs import ops_agents
from app.core.database import AsyncSessionLocal
from app.models.organization import Organization

# 100 realistic customer-support questions across the KB categories.
QUESTIONS: list[tuple[str, str]] = [
    # --- Company / overview (12) ---
    ("company", "What is TCS?"),
    ("company", "Tell me about your company"),
    ("company", "When was TCS founded?"),
    ("company", "Where is TCS headquartered?"),
    ("company", "Who owns TCS?"),
    ("company", "Is TCS part of the Tata Group?"),
    ("company", "How big is TCS?"),
    ("company", "How many employees does TCS have?"),
    ("company", "In how many countries does TCS operate?"),
    ("company", "What is TCS's revenue?"),
    ("company", "What is your company mission?"),
    ("company", "What does Building on Belief mean?"),
    # --- Leadership (5) ---
    ("leadership", "Who is the CEO of TCS?"),
    ("leadership", "Who leads TCS?"),
    ("leadership", "Who is the chairman of TCS?"),
    ("leadership", "Who is the managing director?"),
    ("leadership", "When did K. Krithivasan become CEO?"),
    # --- Services (14) ---
    ("services", "What services does TCS offer?"),
    ("services", "Do you provide consulting?"),
    ("services", "Do you offer cloud services?"),
    ("services", "Can you help with cloud migration?"),
    ("services", "Do you do AI and generative AI?"),
    ("services", "Do you offer cybersecurity services?"),
    ("services", "Do you provide managed detection and response?"),
    ("services", "What about data and analytics?"),
    ("services", "Do you work with SAP?"),
    ("services", "Do you offer enterprise application services?"),
    ("services", "Do you provide IoT and engineering?"),
    ("services", "What is BPS?"),
    ("services", "Do you do application maintenance?"),
    ("services", "How do you deliver projects globally?"),
    # --- Products (14) ---
    ("products", "What products does TCS make?"),
    ("products", "What is TCS BaNCS?"),
    ("products", "Do you have software for banks?"),
    ("products", "Is BaNCS used for insurance?"),
    ("products", "How many institutions use BaNCS?"),
    ("products", "What is ignio?"),
    ("products", "What does ignio do?"),
    ("products", "Who makes ignio?"),
    ("products", "When was ignio launched?"),
    ("products", "What is AIOps?"),
    ("products", "What is TCS iON?"),
    ("products", "Do you have a learning platform?"),
    ("products", "What is TCS MasterCraft?"),
    ("products", "What is Quartz?"),
    # --- Industries (12) ---
    ("industries", "Which industries does TCS serve?"),
    ("industries", "Do you work with banks?"),
    ("industries", "Do you serve the insurance industry?"),
    ("industries", "Do you work in retail?"),
    ("industries", "Do you serve healthcare?"),
    ("industries", "Do you work with life sciences companies?"),
    ("industries", "Do you serve manufacturing?"),
    ("industries", "Do you work in automotive?"),
    ("industries", "Do you serve telecom and media?"),
    ("industries", "Do you work with energy and utilities?"),
    ("industries", "Do you serve government and public sector?"),
    ("industries", "Do you work in education?"),
    # --- Pricing (9) ---
    ("pricing", "How much does it cost to work with TCS?"),
    ("pricing", "What is your pricing?"),
    ("pricing", "Do you have fixed-price contracts?"),
    ("pricing", "Do you offer time and materials?"),
    ("pricing", "What is an outcome-based model?"),
    ("pricing", "How is BaNCS licensed?"),
    ("pricing", "How is TCS iON priced?"),
    ("pricing", "How do I get a quote?"),
    ("pricing", "What engagement models do you offer?"),
    # --- Support / contact (12) ---
    ("contact", "How do I contact TCS support?"),
    ("contact", "What is your support phone number?"),
    ("contact", "What is your support email?"),
    ("contact", "What are your support hours?"),
    ("contact", "How do I reach the global helpdesk?"),
    ("contact", "What is the TCS iON customer care number?"),
    ("contact", "Where is TCS located?"),
    ("contact", "What is your address in Mumbai?"),
    ("contact", "How do I reach sales?"),
    ("contact", "What is your website?"),
    ("contact", "How do I report a fraudulent job offer?"),
    ("contact", "Who do I contact for partnerships?"),
    # --- Support policies / security (10) ---
    ("support", "What are your SLAs?"),
    ("support", "What are your priority levels?"),
    ("support", "What is a P1 issue?"),
    ("support", "How does escalation work?"),
    ("support", "Is my data secure?"),
    ("support", "Do you follow ISO 27001?"),
    ("support", "How do you protect personal data?"),
    ("support", "Are you GDPR compliant?"),
    ("support", "Do you offer 24x7 support?"),
    ("support", "What is your business continuity plan?"),
    # --- Scenarios (7) ---
    ("scenario", "I can't log in to the portal, what do I do?"),
    ("scenario", "We have a production outage, how do you handle it?"),
    ("scenario", "I have a question about my invoice"),
    ("scenario", "I want to add a new service to our contract"),
    ("scenario", "I am worried about a data privacy issue"),
    ("scenario", "Someone asked me to pay for a TCS job offer"),
    ("scenario", "I need help with a TCS iON exam"),
    # --- Competitors (5) ---
    ("competitors", "Who are your competitors?"),
    ("competitors", "How do you compare to Infosys?"),
    ("competitors", "Why choose TCS over Accenture?"),
    ("competitors", "What are your alternatives?"),
    ("competitors", "Is TCS bigger than Infosys?"),
]


async def main() -> None:
    async with AsyncSessionLocal() as db:
        org = (
            await db.execute(select(Organization).where(Organization.slug == "tcs"))
        ).scalar_one()

        total = len(QUESTIONS)
        answered = 0
        by_cat: dict[str, list[int]] = {}
        samples: list[str] = []

        for i, (cat, q) in enumerate(QUESTIONS):
            res = await ops_agents.run_product_expert(db, org.id, q, use_kb=True)
            ok = not res.knowledge_gap and bool(res.reply)
            answered += int(ok)
            by_cat.setdefault(cat, [0, 0])
            by_cat[cat][0] += int(ok)
            by_cat[cat][1] += 1
            if i < 8:
                samples.append(f"  Q: {q}\n  A: {res.reply[:120]}  (conf {res.confidence})")

        print(f"=== 100-question KB verification — {org.name} ===\n")
        print("Sample answers:")
        print("\n".join(samples))
        print("\nPer-category accuracy:")
        for cat, (ok, n) in sorted(by_cat.items()):
            print(f"  {cat:<12} {ok}/{n}")
        print(f"\nOVERALL: {answered}/{total} answered confidently "
              f"({answered / total * 100:.0f}%)")


if __name__ == "__main__":
    asyncio.run(main())
