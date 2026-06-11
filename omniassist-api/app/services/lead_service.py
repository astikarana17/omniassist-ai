"""Sales lead management: scoring, pipeline, qualification, follow-ups, activities."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.conversation import Contact, Conversation
from app.models.enums import Channel, LeadStage, NotificationChannel
from app.models.lead import Activity, Lead
from app.services.notification_service import notify

logger = get_logger("leads")


class LeadService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def upsert_from_conversation(
        self, *, org_id: uuid.UUID, contact: Contact, conversation: Conversation,
        qualification: dict,
    ) -> Lead:
        """Create or update a lead from an AI sales qualification."""
        lead = (
            await self.db.execute(
                select(Lead).where(Lead.org_id == org_id, Lead.contact_id == contact.id)
            )
        ).scalar_one_or_none()
        score = int(qualification.get("score", 50))
        stage = self._stage_for_score(score)
        if lead is None:
            lead = Lead(
                org_id=org_id, contact_id=contact.id, name=contact.name,
                company=contact.company, email=contact.email, phone=contact.phone,
                source=Channel(conversation.channel), stage=stage, score=score,
                qualification=qualification,
            )
            self.db.add(lead)
            await self.db.flush()
            await self._log(org_id, lead.id, "ai", "Lead captured by AI sales agent")
        else:
            lead.score = max(lead.score, score)
            lead.stage = stage if LeadStage(stage) != LeadStage.NEW else lead.stage
            lead.qualification = {**lead.qualification, **qualification}
            await self._log(org_id, lead.id, "ai", f"AI re-qualified lead (score {score})")

        if score >= 85:
            await notify(
                self.db, org_id=org_id, type_="lead",
                title="New hot lead",
                body=f"{lead.name} ({lead.company or 'unknown'}) scored {score}. Route to sales.",
                payload={"lead_id": str(lead.id)},
                channels=[NotificationChannel.IN_APP, NotificationChannel.SLACK],
            )
        return lead

    @staticmethod
    def _stage_for_score(score: int) -> str:
        if score >= 85:
            return LeadStage.DEMO
        if score >= 65:
            return LeadStage.QUALIFIED
        return LeadStage.NEW

    async def get(self, org_id: uuid.UUID, lead_id: uuid.UUID) -> Lead:
        lead = await self.db.get(Lead, lead_id)
        if not lead or lead.org_id != org_id:
            raise NotFoundError("Lead not found.")
        return lead

    async def change_stage(
        self, org_id: uuid.UUID, lead_id: uuid.UUID, stage: LeadStage, actor_id: uuid.UUID
    ) -> Lead:
        lead = await self.get(org_id, lead_id)
        previous = lead.stage
        lead.stage = stage
        await self._log(
            org_id, lead.id, "stage", f"Stage {previous} → {stage}", actor_id=actor_id
        )
        return lead

    async def schedule_followup(
        self, org_id: uuid.UUID, lead_id: uuid.UUID, *, when: datetime, action: str,
        actor_id: uuid.UUID | None = None,
    ) -> Lead:
        lead = await self.get(org_id, lead_id)
        lead.next_action = action
        lead.next_action_due = when
        await self._log(org_id, lead.id, "note", f"Follow-up scheduled: {action}", actor_id=actor_id)
        return lead

    async def suggest_followup_time(self) -> datetime:
        return datetime.now(UTC) + timedelta(days=2)

    async def _log(
        self, org_id: uuid.UUID, lead_id: uuid.UUID, type_: str, title: str,
        body: str | None = None, actor_id: uuid.UUID | None = None,
    ) -> None:
        self.db.add(
            Activity(
                org_id=org_id, lead_id=lead_id, type=type_, title=title,
                body=body, actor_id=actor_id,
            )
        )
        await self.db.flush()
