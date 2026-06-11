"""Tickets, comments (internal notes), attachments, summaries."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin
from app.models.enums import Channel, Priority, TicketStatus


class Ticket(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "tickets"
    __table_args__ = (
        Index("ix_tickets_org_status", "org_id", "status", "sla_due_at"),
        Index("ix_tickets_org_number", "org_id", "number", unique=True),
        Index("ix_tickets_assignee", "assignee_id"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False)  # per-org sequential
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=TicketStatus.OPEN)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default=Priority.MEDIUM)
    channel: Mapped[str] = mapped_column(String(20), nullable=False, default=Channel.WEB)
    sentiment: Mapped[str | None] = mapped_column(String(20), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)

    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    requester_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True
    )
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    sla_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_response_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sla_breached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    comments: Mapped[list["TicketComment"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )
    attachments: Mapped[list["TicketAttachment"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )
    summary: Mapped["TicketSummary | None"] = relationship(
        back_populates="ticket", uselist=False, cascade="all, delete-orphan"
    )


class TicketComment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ticket_comments"
    __table_args__ = (Index("ix_ticket_comments_ticket", "ticket_id", "created_at"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    ticket: Mapped["Ticket"] = relationship(back_populates="comments")


class TicketAttachment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ticket_attachments"
    __table_args__ = (Index("ix_ticket_attachments_ticket", "ticket_id"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    ticket: Mapped["Ticket"] = relationship(back_populates="attachments")


class TicketSummary(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ticket_summaries"

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_steps: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    model: Mapped[str | None] = mapped_column(String(60), nullable=True)

    ticket: Mapped["Ticket"] = relationship(back_populates="summary")
