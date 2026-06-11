"""Customer Success Agent + Customer Health Score Engine.

`CustomerAccount` is the monitored end-customer (the account being served). Usage
signal (`UsageEvent`) + support history feed periodic `CustomerHealthScore` snapshots;
the CS agent surfaces `EngagementAction` follow-ups for at-risk accounts.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
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
from app.models.enums import HealthCategory, Priority


class CustomerAccount(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "customer_accounts"
    __table_args__ = (
        Index("ix_customer_accounts_org_status", "org_id", "status"),
        Index("ix_customer_accounts_owner", "owner_id"),
        Index("ix_customer_accounts_active", "org_id", "last_active_at"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    primary_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # CSM
    plan: Mapped[str | None] = mapped_column(String(40), nullable=True)
    mrr: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True
    )
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    onboarded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    health_scores: Mapped[list["CustomerHealthScore"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )
    engagement_actions: Mapped[list["EngagementAction"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )


class UsageEvent(UUIDMixin, TimestampMixin, Base):
    """Raw product-usage signal (login, feature use, api call, ...)."""

    __tablename__ = "usage_events"
    __table_args__ = (
        Index("ix_usage_events_org", "org_id", "occurred_at"),
        Index("ix_usage_events_customer", "customer_id", "occurred_at"),
        Index("ix_usage_events_type", "org_id", "event_type"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("customer_accounts.id", ondelete="CASCADE"), nullable=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    feature: Mapped[str | None] = mapped_column(String(120), nullable=True)
    quantity: Mapped[float] = mapped_column(Numeric(12, 2), default=1, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class CustomerHealthScore(UUIDMixin, TimestampMixin, Base):
    """A health-score snapshot. Latest row per customer = current health."""

    __tablename__ = "customer_health_scores"
    __table_args__ = (
        Index("ix_customer_health_org", "org_id", "computed_at"),
        Index("ix_customer_health_customer", "customer_id", "computed_at"),
        Index("ix_customer_health_category", "org_id", "category"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("customer_accounts.id", ondelete="CASCADE"), nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0..100
    category: Mapped[str] = mapped_column(String(20), nullable=False, default=HealthCategory.HEALTHY)
    churn_risk: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0..1
    usage_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    engagement_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    support_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    satisfaction_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    adoption_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    drivers: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)  # explainability
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    customer: Mapped["CustomerAccount"] = relationship(back_populates="health_scores")


class EngagementAction(UUIDMixin, TimestampMixin, Base):
    """A recommended follow-up surfaced by the Customer Success agent."""

    __tablename__ = "engagement_actions"
    __table_args__ = (
        Index("ix_engagement_actions_org", "org_id"),
        Index("ix_engagement_actions_customer", "customer_id"),
        Index("ix_engagement_actions_status", "org_id", "status"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("customer_accounts.id", ondelete="CASCADE"), nullable=False
    )
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[str] = mapped_column(String(40), nullable=False)  # email|call|checkin|offer|nudge
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default=Priority.MEDIUM, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="suggested", nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    customer: Mapped["CustomerAccount"] = relationship(back_populates="engagement_actions")
