"""AI Employee Assistant — internal-only knowledge (HR policies, handbook, SOPs).

Kept separate from the customer-facing knowledge base (`kb_documents`) so internal
content is never retrievable by customer-facing agents. `InternalChunk` mirrors the
`KbChunk` pattern (pgvector tier + Pinecone id).
"""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import (
    ARRAY,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base, TimestampMixin, UUIDMixin
from app.models.enums import DocStatus


class InternalDocument(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "internal_documents"
    __table_args__ = (
        Index("ix_internal_documents_org", "org_id"),
        Index("ix_internal_documents_category", "org_id", "category"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(40), default="general", nullable=False)  # hr|handbook|sop|process|it|finance|general
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=DocStatus.READY, nullable=False)
    visibility: Mapped[str] = mapped_column(String(20), default="all_employees", nullable=False)  # all_employees|managers|admins
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    chunks: Mapped[list["InternalChunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class InternalChunk(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "internal_chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_internal_chunk_document_index"),
        Index("ix_internal_chunks_org", "org_id"),
        Index("ix_internal_chunks_document", "document_id"),
        Index("ix_internal_chunks_pinecone", "pinecone_id"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("internal_documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.EMBEDDING_DIM), nullable=True
    )
    pinecone_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    document: Mapped["InternalDocument"] = relationship(back_populates="chunks")


class HrPolicy(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "hr_policies"
    __table_args__ = (Index("ix_hr_policies_org", "org_id"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(40), default="general", nullable=False)  # leave|benefits|conduct|remote|expense|general
    body: Mapped[str] = mapped_column(Text, nullable=False)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    applies_to: Mapped[str] = mapped_column(String(40), default="all", nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
