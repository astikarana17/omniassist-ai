"""AI agent configuration and per-turn run records."""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin
from app.models.enums import AgentType


class AiAgent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ai_agents"
    __table_args__ = (Index("ix_ai_agents_org_type", "org_id", "type"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False, default=AgentType.SUPPORT)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(60), default="claude-opus-4-8", nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0.3, nullable=False)
    tone: Mapped[str] = mapped_column(String(40), default="friendly", nullable=False)
    confidence_threshold: Mapped[int] = mapped_column(Integer, default=70, nullable=False)
    tools: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    languages: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    runs: Mapped[list["AgentRun"]] = relationship(back_populates="agent")


class AgentRun(UUIDMixin, TimestampMixin, Base):
    """One execution of an agent graph for a conversation turn (for replay/audit/cost)."""

    __tablename__ = "agent_runs"
    __table_args__ = (
        Index("ix_agent_runs_org", "org_id", "created_at"),
        Index("ix_agent_runs_conversation", "conversation_id"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("ai_agents.id", ondelete="SET NULL"), nullable=True
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True
    )
    intent: Mapped[str | None] = mapped_column(String(80), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    handed_off: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    graph_state: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    tools_used: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    agent: Mapped["AiAgent | None"] = relationship(back_populates="runs")
