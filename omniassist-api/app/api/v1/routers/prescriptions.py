"""Prescription Intelligence Engine API — upload, analyse, list, detail."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, File, UploadFile

from app.core.config import settings
from app.core.deps import CurrentContext, DbSession, PaginationDep
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.models.health import Prescription
from app.repositories.base import TenantRepository
from app.schemas.common import MessageResponse, Page, PageMeta
from app.schemas.health import PrescriptionListItem, PrescriptionOut
from app.services import prescription_service

logger = get_logger("prescriptions")

router = APIRouter(prefix="/prescriptions", tags=["Prescription Intelligence"])

_ALLOWED = {"image/jpeg", "image/jpg", "image/png", "image/webp", "application/pdf"}


@router.post("", response_model=PrescriptionOut, status_code=201)
async def upload_prescription(
    ctx: CurrentContext,
    db: DbSession,
    file: UploadFile = File(...),
    patient_id: uuid.UUID | None = None,
) -> PrescriptionOut:
    """Upload a prescription image/PDF and get an AI explanation of every medicine."""
    mime = (file.content_type or "").lower()
    if mime not in _ALLOWED:
        raise ValidationError(
            "Please upload a JPG, PNG, WEBP or PDF prescription.", code="UNSUPPORTED_FILE"
        )
    content = await file.read()
    if not content:
        raise ValidationError("Empty file.", code="EMPTY_FILE")
    if len(content) > settings.max_upload_bytes:
        raise ValidationError(
            f"File exceeds {settings.MAX_UPLOAD_MB}MB limit.", code="FILE_TOO_LARGE"
        )

    rx = Prescription(
        org_id=ctx.org_id,
        patient_id=patient_id,
        uploaded_by=ctx.user.id,
        status="processing",
    )
    db.add(rx)
    await db.flush()

    from app.core import storage

    ext = {"application/pdf": "pdf"}.get(mime, mime.split("/")[-1])
    rx.storage_path = storage.save(f"{ctx.org_id}/prescriptions/{rx.id}.{ext}", content)
    await db.flush()

    # Run the pipeline inline so the caller gets the result immediately. The
    # service captures its own failures on the row (never raises).
    await prescription_service.analyze_prescription(db, rx, content, mime)
    await db.commit()
    return PrescriptionOut.model_validate(rx)


@router.get("", response_model=Page[PrescriptionListItem])
async def list_prescriptions(
    ctx: CurrentContext,
    db: DbSession,
    page: PaginationDep,
) -> Page[PrescriptionListItem]:
    repo = TenantRepository(db, Prescription)
    rows, total = await repo.list(
        ctx.org_id, limit=page.limit, offset=page.offset,
        order_by=Prescription.created_at.desc(),
    )
    items = [
        PrescriptionListItem(
            id=r.id, status=r.status, doctor_name=r.doctor_name,
            hospital_name=r.hospital_name, prescribed_date=r.prescribed_date,
            medicine_count=len(r.medicines or []), created_at=r.created_at,
        )
        for r in rows
    ]
    return Page(
        items=items,
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.get("/{prescription_id}", response_model=PrescriptionOut)
async def get_prescription(
    prescription_id: uuid.UUID,
    ctx: CurrentContext,
    db: DbSession,
) -> PrescriptionOut:
    repo = TenantRepository(db, Prescription)
    rx = await repo.get(ctx.org_id, prescription_id)
    if not rx:
        raise NotFoundError("Prescription not found.")
    return PrescriptionOut.model_validate(rx)


@router.delete("/{prescription_id}", response_model=MessageResponse)
async def delete_prescription(
    prescription_id: uuid.UUID,
    ctx: CurrentContext,
    db: DbSession,
) -> MessageResponse:
    repo = TenantRepository(db, Prescription)
    rx = await repo.get(ctx.org_id, prescription_id)
    if not rx:
        raise NotFoundError("Prescription not found.")
    if rx.storage_path:
        from app.core import storage

        try:
            storage.delete(rx.storage_path)
        except Exception:  # noqa: BLE001 — best-effort file cleanup
            pass
    await repo.delete(rx)
    return MessageResponse(message="Prescription deleted.")
