"""Generate raw PostgreSQL DDL from the SQLAlchemy models.

Used to apply the schema via the Supabase MCP / SQL editor when Alembic can't be
run directly. Output is deterministic and ordered by FK dependency.

Usage:  python -m scripts.dump_ddl > infra/schema.sql
"""
from __future__ import annotations

import os

# Dummy settings so config import succeeds without a real environment.
os.environ.setdefault("SECRET_KEY", "ddl-dump-placeholder-key-000000")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
os.environ.setdefault("DATABASE_SYNC_URL", "postgresql+psycopg2://u:p@localhost/db")

from sqlalchemy.dialects import postgresql  # noqa: E402
from sqlalchemy.schema import CreateIndex, CreateTable  # noqa: E402

from app.models import Base  # noqa: E402

DIALECT = postgresql.dialect()
EXTENSIONS = ["uuid-ossp", "pgcrypto", "pg_trgm", "vector"]


def main() -> None:
    lines: list[str] = ["-- OmniAssist AI — schema DDL (generated from models)", ""]
    for ext in EXTENSIONS:
        lines.append(f'CREATE EXTENSION IF NOT EXISTS "{ext}";')
    lines.append("")

    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=DIALECT)).strip()
        lines.append(ddl.rstrip() + ";")
        for index in table.indexes:
            idx = str(CreateIndex(index).compile(dialect=DIALECT)).strip()
            if idx:
                lines.append(idx.rstrip() + ";")
        lines.append("")

    # Vector + trigram indexes that the ORM doesn't emit directly.
    lines.append(
        "CREATE INDEX IF NOT EXISTS ix_kb_chunks_embedding_hnsw "
        "ON kb_chunks USING hnsw (embedding vector_cosine_ops);"
    )
    lines.append(
        "CREATE INDEX IF NOT EXISTS ix_contacts_name_trgm "
        "ON contacts USING gin (name gin_trgm_ops);"
    )
    # Business-Operations expansion (0002) manual indexes.
    lines.append(
        "CREATE INDEX IF NOT EXISTS ix_internal_chunks_embedding_hnsw "
        "ON internal_chunks USING hnsw (embedding vector_cosine_ops);"
    )
    lines.append(
        "CREATE INDEX IF NOT EXISTS ix_faqs_question_trgm "
        "ON faqs USING gin (question gin_trgm_ops);"
    )
    lines.append(
        "CREATE INDEX IF NOT EXISTS ix_knowledge_gaps_question_trgm "
        "ON knowledge_gaps USING gin (question gin_trgm_ops);"
    )
    lines.append(
        "CREATE INDEX IF NOT EXISTS ix_internal_documents_title_trgm "
        "ON internal_documents USING gin (title gin_trgm_ops);"
    )
    print("\n".join(lines))


if __name__ == "__main__":
    main()
