"""Knowledge Gap Detector + Executive Insights + Business Impact (ROI) analytics."""
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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, UUIDMixin
from app.models.enums import GapStatus, InsightKind


class KnowledgeGap(UUIDMixin, TimestampMixin, Base):
    """Logged when an AI agent answers with low confidence / no source found.
    Duplicate questions are clustered onto one row via `normalized_q` (occurrences++)."""

    __tablename__ = "knowledge_gaps"
    __table_args__ = (
        Index("ix_knowledge_gaps_org_status", "org_id", "status"),
        Index("ix_knowledge_gaps_occurrences", "org_id", "occurrences"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_q: Mapped[str | None] = mapped_column(Text, nullable=True)
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="SET NULL"), nullable=True
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("kb_documents.id", ondelete="SET NULL"), nullable=True
    )  # resolving document
    occurrences: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    avg_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=GapStatus.OPEN, nullable=False)
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class ExecutiveInsight(UUIDMixin, TimestampMixin, Base):
    """AI-generated narrative + recommendation for leadership dashboards."""

    __tablename__ = "executive_insights"
    __table_args__ = (
        Index("ix_executive_insights_org", "org_id", "created_at"),
        Index("ix_executive_insights_kind", "org_id", "kind"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(20), nullable=False, default=InsightKind.RECOMMENDATION)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="info", nullable=False)
    metrics: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    generated_by: Mapped[str] = mapped_column(String(20), default="ai", nullable=False)


class BusinessImpactMetric(UUIDMixin, TimestampMixin, Base):
    """Periodic ROI snapshot — the numbers behind the Business Impact dashboard."""

    __tablename__ = "business_impact_metrics"
    __table_args__ = (
        UniqueConstraint(
            "org_id", "period_start", "period_end", "granularity",
            name="uq_business_impact_org_period",
        ),
        Index("ix_business_impact_org", "org_id", "period_start"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    granularity: Mapped[str] = mapped_column(String(12), default="month", nullable=False)
    ai_resolution_rate: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    cost_savings_usd: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    revenue_influenced_usd: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    churn_reduction_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    agent_productivity: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    customer_retention_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    tickets_handled: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tickets_ai_resolved: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_first_response_min: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    csat_avg: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    details: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
