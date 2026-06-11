"""End-to-end RAG ingestion: parse → chunk → upsert (Pinecone) → persist chunk rows.

Runs inside a Celery worker. Uses a synchronous SQLAlchemy session because Celery
tasks are synchronous; the FastAPI request path stays async.
"""
from __future__ import annotations

import uuid

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker

from app.ai import pinecone_client
from app.ai.rag import chunker, parser
from app.ai.retriever import namespace_for
from app.core.config import settings
from app.core.logging import get_logger
from app.models.enums import DocStatus
from app.models.knowledge import KbChunk, KbDocument

logger = get_logger("rag.pipeline")

_sync_engine = create_engine(settings.DATABASE_SYNC_URL, pool_pre_ping=True, future=True)
_SyncSession: sessionmaker[Session] = sessionmaker(bind=_sync_engine, expire_on_commit=False)


def ingest_document(document_id: str, content: bytes, content_type: str, filename: str) -> int:
    """Process a document into retrievable chunks. Returns the chunk count."""
    with _SyncSession() as db:
        doc = db.get(KbDocument, uuid.UUID(document_id))
        if doc is None:
            logger.warning("ingest_missing_doc", document_id=document_id)
            return 0
        try:
            text = parser.parse(content, content_type, filename)
            chunks = chunker.chunk_text(text)
            if not chunks:
                doc.status = DocStatus.FAILED
                doc.error = "No extractable text found."
                db.commit()
                return 0

            namespace = namespace_for(doc.org_id)
            records = []
            rows = []
            for ch in chunks:
                pid = f"{doc.id}:{ch.index}"
                records.append(
                    {
                        "_id": pid,
                        "text": ch.text,
                        "document_id": str(doc.id),
                        "title": doc.title,
                        "chunk_index": ch.index,
                    }
                )
                rows.append(
                    KbChunk(
                        org_id=doc.org_id,
                        document_id=doc.id,
                        chunk_index=ch.index,
                        content=ch.text,
                        token_count=ch.token_count,
                        pinecone_id=pid,
                        meta={"title": doc.title},
                    )
                )

            # Replace any previous chunks for this document (idempotent re-ingest).
            db.execute(delete(KbChunk).where(KbChunk.document_id == doc.id))
            pinecone_client.upsert_records(namespace, records)
            db.add_all(rows)

            doc.status = DocStatus.READY
            doc.chunk_count = len(rows)
            doc.error = None
            db.commit()
            logger.info("ingest_ok", document_id=document_id, chunks=len(rows))
            return len(rows)
        except Exception as exc:  # noqa: BLE001
            logger.error("ingest_failed", document_id=document_id, error=str(exc))
            doc.status = DocStatus.FAILED
            doc.error = str(exc)[:500]
            db.commit()
            return 0


def delete_document_vectors(org_id: str, document_id: str) -> None:
    """Remove a document's vectors from Pinecone (chunks rows cascade in Postgres)."""
    with _SyncSession() as db:
        ids = [
            row.pinecone_id
            for row in db.query(KbChunk.pinecone_id)
            .filter(KbChunk.document_id == uuid.UUID(document_id))
            .all()
            if row.pinecone_id
        ]
    if ids:
        pinecone_client.delete_records(namespace_for(org_id), ids)
