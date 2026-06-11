"""AI Onboarding Agent — flow templates, steps and per-user progress tracking."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin
from app.models.enums import OnboardingStatus


class OnboardingFlow(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "onboarding_flows"
    __table_args__ = (Index("ix_onboarding_flows_org", "org_id"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    audience: Mapped[str] = mapped_column(String(20), default="customer", nullable=False)  # customer|employee
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    steps: Mapped[list["OnboardingStep"]] = relationship(
        back_populates="flow", cascade="all, delete-orphan", order_by="OnboardingStep.position"
    )


class OnboardingStep(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "onboarding_steps"
    __table_args__ = (
        UniqueConstraint("flow_id", "position", name="uq_onboarding_step_flow_position"),
        Index("ix_onboarding_steps_flow", "flow_id", "position"),
        Index("ix_onboarding_steps_org", "org_id"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    flow_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("onboarding_flows.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_type: Mapped[str | None] = mapped_column(String(40), nullable=True)  # visit|configure|invite|connect|watch
    action_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    flow: Mapped["OnboardingFlow"] = relationship(back_populates="steps")


class UserOnboarding(UUIDMixin, TimestampMixin, Base):
    """Per-user progress through a flow; `completion_pct` powers completion-rate analytics."""

    __tablename__ = "user_onboarding"
    __table_args__ = (
        UniqueConstraint("user_id", "flow_id", name="uq_user_onboarding_user_flow"),
        Index("ix_user_onboarding_org_status", "org_id", "status"),
        Index("ix_user_onboarding_user", "user_id"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    flow_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("onboarding_flows.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default=OnboardingStatus.NOT_STARTED, nullable=False
    )
    completion_pct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    step_progress: Mapped[list["UserOnboardingStep"]] = relationship(
        back_populates="user_onboarding", cascade="all, delete-orphan"
    )


class UserOnboardingStep(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "user_onboarding_steps"
    __table_args__ = (
        UniqueConstraint(
            "user_onboarding_id", "step_id", name="uq_user_onboarding_step_parent_step"
        ),
        Index("ix_user_onboarding_steps_parent", "user_onboarding_id"),
        Index("ix_user_onboarding_steps_org", "org_id"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_onboarding_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_onboarding.id", ondelete="CASCADE"), nullable=False
    )
    step_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("onboarding_steps.id", ondelete="CASCADE"), nullable=False
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    skipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user_onboarding: Mapped["UserOnboarding"] = relationship(back_populates="step_progress")
