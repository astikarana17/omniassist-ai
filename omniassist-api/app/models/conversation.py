"""Contacts, conversations and messages."""
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
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin
from app.models.enums import Channel, ConversationStatus, SenderType


class Contact(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "contacts"
    __table_args__ = (
        UniqueConstraint("org_id", "email", name="uq_contact_org_email"),
        Index("ix_contacts_org_phone", "org_id", "phone"),
        Index("ix_contacts_org_name", "org_id", "name"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    external_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    company: Mapped[str | None] = mapped_column(String(160), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    locale: Mapped[str | None] = mapped_column(String(12), nullable=True)
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    conversations: Mapped[list["Conversation"]] = relationship(back_populates="contact")


class Conversation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "conversations"
    __table_args__ = (
        Index("ix_conversations_org_status", "org_id", "status", "last_message_at"),
        Index("ix_conversations_org_channel", "org_id", "channel"),
        Index("ix_conversations_assignee", "assignee_id"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    contact_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False, default=Channel.WEB)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ConversationStatus.OPEN
    )
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(40), default="English", nullable=False)
    ai_handled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sentiment: Mapped[str | None] = mapped_column(String(20), nullable=True)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    external_ref: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    unread_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    contact: Mapped["Contact"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at"
    )


class Message(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_conversation", "conversation_id", "created_at"),
        Index("ix_messages_org", "org_id"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    sender_type: Mapped[str] = mapped_column(String(20), nullable=False, default=SenderType.CONTACT)
    sender_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    author_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str | None] = mapped_column(String(12), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    sources: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    attachments: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    delivery_status: Mapped[str | None] = mapped_column(String(20), nullable=True)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
