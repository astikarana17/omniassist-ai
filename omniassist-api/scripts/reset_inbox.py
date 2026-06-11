"""Clear all old inbox data for the OmniAssist org and seed one fresh, LIVE
AI-handled conversation per channel (Web, WhatsApp, Email, Voice) — the same RAG
brain + knowledge base answers on every channel.

Usage: python -m scripts.reset_inbox
"""
from __future__ import annotations

import asyncio

from sqlalchemy import select, text

from app.core.database import AsyncSessionLocal
from app.models.enums import Channel
from app.models.organization import Organization
from app.services.conversation_service import ConversationService

# (channel, name, email, company, opening message)
SEED = [
    (Channel.WEB, "Priya Sharma", "priya@example.com", "Acme", "Hi! What does OmniAssist do?"),
    (Channel.WHATSAPP, "Rahul Verma", "rahul@example.com", "Nova", "How much is the Growth plan?"),
    (Channel.EMAIL, "John Carter", "john@bigco.com", "BigCo",
     "The May invoice doesn't match our usage report. Can someone check?"),
    (Channel.VOICE, "Sara Lee", "sara@example.com", "Lumen", "How do I set up the WhatsApp agent?"),
]


async def main() -> None:
    async with AsyncSessionLocal() as db:
        org_id = (
            await db.execute(select(Organization.id).where(Organization.slug == "omniassist"))
        ).scalar_one()

        for t in ("tickets", "leads", "conversations", "contacts"):
            await db.execute(text(f"delete from {t} where org_id=:o"), {"o": org_id})
        await db.commit()

        svc = ConversationService(db)
        results = []
        for channel, name, email, company, msg in SEED:
            contact = await svc.resolve_contact(org_id, name=name, email=email)
            contact.company = company
            conv = await svc.resolve_conversation(org_id, contact, channel=channel)
            conv.contact = contact
            _, ai = await svc.handle_inbound(
                org_id=org_id, conversation=conv, text=msg, author_name=name
            )
            results.append((channel, name, ai.content if ai else "(handed off)"))
        await db.commit()

    print("Inbox reset — one live AI conversation per channel:")
    for ch, name, reply in results:
        print(f"  [{ch}] {name}: {reply[:70]}")


if __name__ == "__main__":
    asyncio.run(main())
