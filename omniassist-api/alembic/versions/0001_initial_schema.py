"""Initial schema — extensions, all tables, vector HNSW index.

This bootstrap migration enables the required PostgreSQL extensions, creates the
full schema from the SQLAlchemy metadata, and adds the pgvector HNSW index used
by the RAG fallback tier. Subsequent schema changes use ``alembic revision
--autogenerate``.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-08
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

from app.models import Base

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # Required extensions (available on Supabase).
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create all tables, constraints and (non-vector) indexes from metadata.
    Base.metadata.create_all(bind=bind)

    # Vector similarity index (cosine) for the pgvector fallback retrieval tier.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_kb_chunks_embedding_hnsw "
        "ON kb_chunks USING hnsw (embedding vector_cosine_ops)"
    )

    # Trigram index for fast contact search by name/email.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_contacts_name_trgm "
        "ON contacts USING gin (name gin_trgm_ops)"
    )


def downgrade() -> None:
    bind = op.get_bind()
    op.execute("DROP INDEX IF EXISTS ix_contacts_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_kb_chunks_embedding_hnsw")
    Base.metadata.drop_all(bind=bind)
