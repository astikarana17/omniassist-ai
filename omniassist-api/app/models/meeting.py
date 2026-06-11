"""AI Demo & Meeting Agent — scheduling, calendar booking, reminders, follow-ups."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin
from app.models.enums import MeetingStatus


class Meeting(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "meetings"
    __table_args__ = (
        Index("ix_meetings_org_start", "org_id", "starts_at"),
        Index("ix_meetings_lead", "lead_id"),
        Index("ix_meetings_status", "org_id", "status"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(20), default="demo", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=MeetingStatus.SCHEDULED, nullable=False)
    organizer_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("customer_accounts.id", ondelete="SET NULL"), nullable=True
    )
    attendee_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    attendee_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    timezone: Mapped[str] = mapped_column(String(60), default="UTC", nullable=False)
    location: Mapped[str | None] = mapped_column(String(512), nullable=True)
    meeting_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    external_event_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    followup_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    reminders: Mapped[list["MeetingReminder"]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )


class MeetingReminder(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "meeting_reminders"
    __table_args__ = (
        Index("ix_meeting_reminders_meeting", "meeting_id"),
        Index("ix_meeting_reminders_org", "org_id"),
        Index("ix_meeting_reminders_due", "remind_at"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False
    )
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), default="email", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    meeting: Mapped["Meeting"] = relationship(back_populates="reminders")
