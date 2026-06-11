"""Seed a demo organization with an owner, agents and sample data.

Usage:  python -m scripts.seed
Idempotent: skips creation if the demo org already exists.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.permissions import Role
from app.core.security import hash_password
from app.models.conversation import Contact, Conversation, Message
from app.models.enums import (
    Channel,
    ConversationStatus,
    LeadStage,
    Priority,
    SenderType,
    TicketStatus,
)
from app.models.lead import Lead
from app.models.organization import Membership, Organization
from app.models.ticket import Ticket
from app.models.user import User

DEMO_EMAIL = "demo@acme.com"


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        existing = (
            await db.execute(select(Organization).where(Organization.slug == "acme"))
        ).scalar_one_or_none()
        if existing:
            print("Demo org already exists — skipping.")
            return

        org = Organization(name="Acme Inc", slug="acme", plan="growth")
        db.add(org)
        await db.flush()

        owner = User(
            email=DEMO_EMAIL,
            full_name="Priya Rao",
            hashed_password=hash_password("Password123!"),
            title="Head of Customer Experience",
            is_email_verified=True,
        )
        db.add(owner)
        await db.flush()
        db.add(Membership(org_id=org.id, user_id=owner.id, role=Role.SUPER_ADMIN, status="active"))

        from app.services.auth_service import AuthService

        await AuthService(db)._seed_default_agents(org.id)  # noqa: SLF001

        # Sample contact + conversation.
        contact = Contact(
            org_id=org.id, name="Rahul Sharma", email="rahul@gmail.com",
            phone="+919876543210", company="Individual",
        )
        db.add(contact)
        await db.flush()
        conv = Conversation(
            org_id=org.id, contact_id=contact.id, channel=Channel.WHATSAPP,
            status=ConversationStatus.OPEN, subject="Double charge on order #882",
            language="English", last_message_at=datetime.now(timezone.utc),
        )
        db.add(conv)
        await db.flush()
        db.add_all(
            [
                Message(
                    org_id=org.id, conversation_id=conv.id, sender_type=SenderType.CONTACT,
                    author_name="Rahul Sharma", content="I was charged twice for my order.",
                ),
                Message(
                    org_id=org.id, conversation_id=conv.id, sender_type=SenderType.AI,
                    content="I'm sorry about that! I've initiated a refund of ₹2,499.",
                    confidence=91.0,
                    sources=[{"title": "Billing & Refund Policy"}],
                ),
            ]
        )

        # Sample ticket.
        db.add(
            Ticket(
                org_id=org.id, number=1042, subject="Double charge on order #882",
                status=TicketStatus.IN_PROGRESS, priority=Priority.HIGH,
                channel=Channel.WHATSAPP, conversation_id=conv.id, requester_id=contact.id,
                tags=["billing", "refund"],
                sla_due_at=datetime.now(timezone.utc) + timedelta(minutes=15),
            )
        )

        # Sample lead.
        db.add(
            Lead(
                org_id=org.id, name="Acme Corp", company="Acme Corporation",
                email="ops@acme.co", value=42000, score=92, stage=LeadStage.DEMO,
                owner_id=owner.id, source=Channel.WEB, next_action="Demo call",
            )
        )

        await db.commit()
        print(f"Seeded org '{org.name}' with owner {DEMO_EMAIL} / Password123!")


if __name__ == "__main__":
    asyncio.run(seed())
