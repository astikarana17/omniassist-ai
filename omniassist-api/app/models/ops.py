"""Operational models: notifications, audit logs, feedback, sentiment, analytics rollups."""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, UUIDMixin
from app.models.enums import NotificationChannel


class Notification(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "notifications"
    __table_args__ = (Index("ix_notifications_org_user", "org_id", "user_id", "read"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    type: Mapped[str] = mapped_column(String(40), nullable=False)  # handoff|sla|mention|lead|...
    channel: Mapped[str] = mapped_column(
        String(20), nullable=False, default=NotificationChannel.IN_APP
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)


class AuditLog(UUIDMixin, TimestampMixin, Base):
    """Append-only audit trail. No updates/deletes (enforced at the service layer)."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_org_created", "org_id", "created_at"),
        Index("ix_audit_logs_actor", "actor_id"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
    )

    org_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    actor_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(60), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    diff: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(400), nullable=True)


class Feedback(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "feedback"
    __table_args__ = (Index("ix_feedback_org", "org_id", "created_at"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # thumbs|csat
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)


class SentimentRecord(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "sentiments"
    __table_args__ = (Index("ix_sentiments_message", "message_id"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=True
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True
    )
    label: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    escalate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class AnalyticsDaily(UUIDMixin, TimestampMixin, Base):
    """Pre-aggregated daily metrics per org/channel (filled by a scheduled rollup)."""

    __tablename__ = "analytics_daily"
    __table_args__ = (
        UniqueConstraint("org_id", "day", "channel", name="uq_analytics_org_day_channel"),
        Index("ix_analytics_org_day", "org_id", "day"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    day: Mapped[date] = mapped_column(Date, nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False, default="all")
    conversations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ai_resolved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    handoffs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tickets_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tickets_resolved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    leads_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    revenue_influenced: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    avg_csat: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_frt_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    sentiment_breakdown: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class VoiceCall(UUIDMixin, TimestampMixin, Base):
    """Voice call record with transcript + AI summary + sentiment."""

    __tablename__ = "voice_calls"
    __table_args__ = (Index("ix_voice_calls_org", "org_id", "created_at"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    call_sid: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    from_number: Mapped[str] = mapped_column(String(40), nullable=False)
    to_number: Mapped[str] = mapped_column(String(40), nullable=False)
    direction: Mapped[str] = mapped_column(String(12), default="inbound", nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    transcript: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    sentiment: Mapped[str | None] = mapped_column(String(20), nullable=True)
    recording_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
