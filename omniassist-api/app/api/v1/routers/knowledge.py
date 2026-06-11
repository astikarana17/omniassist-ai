"""Knowledge base routes: upload, crawl, list, delete, retrieval test."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, UploadFile

from app.ai import retriever
from app.core.config import settings
from app.core.deps import CurrentContext, DbSession, PaginationDep, require_permission
from app.core.exceptions import NotFoundError, ValidationError
from app.core.permissions import Permission
from app.models.enums import DocSource, DocStatus
from app.models.knowledge import KbDocument
from app.repositories.base import TenantRepository
from app.schemas.common import MessageResponse, Page, PageMeta
from app.schemas.domain import (
    CrawlRequest,
    KbDocumentOut,
    RetrievalTestRequest,
    RetrievedChunkOut,
)

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])


@router.get("/documents", response_model=Page[KbDocumentOut])
async def list_documents(
    ctx: CurrentContext,
    db: DbSession,
    page: PaginationDep,
    _: object = Depends(require_permission(Permission.KB_READ)),
) -> Page[KbDocumentOut]:
    repo = TenantRepository(db, KbDocument)
    rows, total = await repo.list(
        ctx.org_id, limit=page.limit, offset=page.offset,
        order_by=KbDocument.created_at.desc(),
    )
    return Page(
        items=[KbDocumentOut.model_validate(d) for d in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.post("/documents", response_model=KbDocumentOut, status_code=201)
async def upload_document(
    ctx: CurrentContext,
    db: DbSession,
    file: UploadFile = File(...),
    _: object = Depends(require_permission(Permission.KB_WRITE)),
) -> KbDocumentOut:
    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise ValidationError(
            f"File exceeds {settings.MAX_UPLOAD_MB}MB limit.", code="FILE_TOO_LARGE"
        )
    if not content:
        raise ValidationError("Empty file.", code="EMPTY_FILE")

    doc = KbDocument(
        org_id=ctx.org_id, title=file.filename or "Untitled",
        source_type=DocSource.UPLOAD, content_type=file.content_type,
        status=DocStatus.PROCESSING, size_bytes=len(content), created_by=ctx.user.id,
    )
    db.add(doc)
    await db.flush()

    # Persist the raw file, then hand off heavy parsing/embedding to the worker
    # (avoids shipping bytes through the broker).
    from app.core import storage

    key = f"{ctx.org_id}/{doc.id}/{file.filename or 'document'}"
    doc.storage_path = storage.save(key, content)
    await db.flush()

    from app.workers.tasks import ingest_kb_document

    ingest_kb_document.delay(str(doc.id), doc.storage_path, file.content_type or "", file.filename or "")
    return KbDocumentOut.model_validate(doc)


@router.post("/crawl", response_model=KbDocumentOut, status_code=201)
async def crawl_site(
    payload: CrawlRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.KB_WRITE)),
) -> KbDocumentOut:
    doc = KbDocument(
        org_id=ctx.org_id, title=payload.title or payload.url, source_type=DocSource.CRAWL,
        source_url=payload.url, status=DocStatus.PROCESSING, created_by=ctx.user.id,
    )
    db.add(doc)
    await db.flush()
    from app.workers.tasks import crawl_url

    crawl_url.delay(str(doc.id), payload.url)
    return KbDocumentOut.model_validate(doc)


@router.delete("/documents/{document_id}", response_model=MessageResponse)
async def delete_document(
    document_id: uuid.UUID,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.KB_DELETE)),
) -> MessageResponse:
    repo = TenantRepository(db, KbDocument)
    doc = await repo.get(ctx.org_id, document_id)
    if not doc:
        raise NotFoundError("Document not found.")
    from app.workers.tasks import delete_kb_document_vectors

    delete_kb_document_vectors.delay(str(ctx.org_id), str(document_id))
    await repo.delete(doc)
    return MessageResponse(message="Document deleted.")


@router.post("/search", response_model=list[RetrievedChunkOut])
async def retrieval_test(
    payload: RetrievalTestRequest,
    ctx: CurrentContext,
    _: object = Depends(require_permission(Permission.KB_READ)),
) -> list[RetrievedChunkOut]:
    chunks = await retriever.retrieve(ctx.org_id, payload.query, top_k=payload.top_k)
    return [
        RetrievedChunkOut(title=c.title, text=c.text, score=round(c.score, 3)) for c in chunks
    ]
