"""Seed realistic inbox conversations for the `tcs` org across channels, with real
AI replies (KB-grounded) + handoff — so the Inbox shows live data, not mock.

Usage:  python -m scripts.seed_conversations
"""
from __future__ import annotations

import asyncio

from sqlalchemy import select, text

from app.core.database import AsyncSessionLocal
from app.models.enums import Channel
from app.models.organization import Organization
from app.services.conversation_service import ConversationService

# (channel, contact name, email, opening customer message)
CONVOS = [
    (Channel.WEB, "Anita Desai", "anita.desai@example.com", "Hi, what is OmniAssist AI?"),
    (Channel.WHATSAPP, "Rakesh Kumar", "rakesh.k@example.com", "How much does the Growth plan cost?"),
    (Channel.EMAIL, "Meera Iyer", "meera.iyer@example.com",
     "I was double charged on my invoice and need a refund."),
    (Channel.VOICE, "John Mathew", "john.m@example.com", "How do I set up the WhatsApp agent?"),
    (Channel.WEB, "Sara Khan", "sara.khan@example.com", "I'd like to speak to a human agent please."),
    (Channel.WHATSAPP, "David Park", "david.park@example.com", "Do you support voice calls and email?"),
]


async def main() -> None:
    async with AsyncSessionLocal() as db:
        org_id = (
            await db.execute(select(Organization.id).where(Organization.slug == "omniassist"))
        ).scalar_one()

        # Idempotent: clear prior seeded conversations + contacts.
        await db.execute(text("delete from conversations where org_id=:o"), {"o": org_id})
        await db.execute(text("delete from contacts where org_id=:o"), {"o": org_id})
        await db.commit()

        svc = ConversationService(db)
        results = []
        for channel, name, email, msg in CONVOS:
            contact = await svc.resolve_contact(org_id, name=name, email=email)
            conv = await svc.resolve_conversation(org_id, contact, channel=channel)
            conv.contact = contact
            inbound, ai = await svc.handle_inbound(
                org_id=org_id, conversation=conv, text=msg, author_name=name
            )
            results.append((channel, name, ai.content if ai else "(handed off)",
                            conv.status, round((ai.confidence or 0)) if ai else 0))
        await db.commit()

    print("=== Seeded conversations ===")
    for ch, name, reply, status, conf in results:
        print(f"\n[{ch}] {name}  (status: {status})")
        print(f"  AI: {reply[:110]}  ({conf}%)")


if __name__ == "__main__":
    asyncio.run(main())
