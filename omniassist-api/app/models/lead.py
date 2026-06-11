"""Sales leads, CRM pipeline state and activity timeline."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin
from app.models.enums import Channel, LeadStage


class Lead(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "leads"
    __table_args__ = (
        Index("ix_leads_org_stage", "org_id", "stage"),
        Index("ix_leads_org_score", "org_id", "score"),
        Index("ix_leads_owner", "owner_id"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    contact_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    company: Mapped[str | None] = mapped_column(String(160), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    stage: Mapped[str] = mapped_column(String(20), nullable=False, default=LeadStage.NEW)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    value: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default=Channel.WEB)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    next_action: Mapped[str | None] = mapped_column(String(255), nullable=True)
    next_action_due: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # BANT qualification captured by the sales agent
    qualification: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    activities: Mapped[list["Activity"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan", order_by="Activity.created_at.desc()"
    )


class Activity(UUIDMixin, TimestampMixin, Base):
    """Timeline entry for a lead (call, email, note, stage change, AI action)."""

    __tablename__ = "activities"
    __table_args__ = (Index("ix_activities_lead", "lead_id", "created_at"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    lead_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(40), nullable=False)  # note|call|email|stage|ai
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    lead: Mapped["Lead"] = relationship(back_populates="activities")
