"""Knowledge base documents and embedded chunks (pgvector + Pinecone join)."""
from __future__ import annotations

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base, TimestampMixin, UUIDMixin
from app.models.enums import DocSource, DocStatus


class KbDocument(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "kb_documents"
    __table_args__ = (Index("ix_kb_documents_org_status", "org_id", "status"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False, default=DocSource.UPLOAD)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=DocStatus.PROCESSING)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    chunks: Mapped[list["KbChunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class KbChunk(UUIDMixin, TimestampMixin, Base):
    """A retrievable chunk. `embedding` is the pgvector fallback tier; `pinecone_id`
    references the same chunk in Pinecone (namespace = org_id)."""

    __tablename__ = "kb_chunks"
    __table_args__ = (
        Index("ix_kb_chunks_org", "org_id"),
        Index("ix_kb_chunks_document", "document_id"),
        Index("ix_kb_chunks_pinecone", "pinecone_id"),
        # HNSW vector index is created in the migration (cosine ops).
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("kb_documents.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.EMBEDDING_DIM), nullable=True
    )
    pinecone_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    document: Mapped["KbDocument"] = relationship(back_populates="chunks")
