"""No-code Workflow Automation Engine.

A `Workflow` stores a no-code node/edge graph in `definition`. Each execution is a
`WorkflowRun`; per-node execution is logged as `WorkflowRunStep` (for replay/audit).

Example definition (Refund Request → Verification → Ticket → Finance notify → Customer update)
is held as JSON in `definition`; the runtime walks the graph node-by-node.
"""
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
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin
from app.models.enums import RunStatus, WorkflowStatus


class Workflow(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workflows"
    __table_args__ = (
        Index("ix_workflows_org", "org_id"),
        Index("ix_workflows_status", "org_id", "status"),
        Index("ix_workflows_trigger", "org_id", "trigger_type"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=WorkflowStatus.DRAFT, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(20), nullable=False)  # event|schedule|manual|webhook
    trigger_config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    definition: Mapped[dict] = mapped_column(
        JSONB, default=lambda: {"nodes": [], "edges": []}, nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    run_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    runs: Mapped[list["WorkflowRun"]] = relationship(
        back_populates="workflow", cascade="all, delete-orphan"
    )


class WorkflowRun(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workflow_runs"
    __table_args__ = (
        Index("ix_workflow_runs_org", "org_id", "created_at"),
        Index("ix_workflow_runs_workflow", "workflow_id", "created_at"),
        Index("ix_workflow_runs_status", "org_id", "status"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default=RunStatus.PENDING, nullable=False)
    trigger_source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    triggered_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    context: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    result: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    workflow: Mapped["Workflow"] = relationship(back_populates="runs")
    steps: Mapped[list["WorkflowRunStep"]] = relationship(
        back_populates="run", cascade="all, delete-orphan", order_by="WorkflowRunStep.step_order"
    )


class WorkflowRunStep(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workflow_run_steps"
    __table_args__ = (
        Index("ix_workflow_run_steps_run", "run_id", "step_order"),
        Index("ix_workflow_run_steps_org", "org_id"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False
    )
    node_id: Mapped[str] = mapped_column(String(80), nullable=False)
    node_type: Mapped[str] = mapped_column(String(40), nullable=False)  # condition|action|notification|delay|ai
    step_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=RunStatus.PENDING, nullable=False)
    input: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    output: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    run: Mapped["WorkflowRun"] = relationship(back_populates="steps")
