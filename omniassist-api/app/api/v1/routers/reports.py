"""Medical Report Analyzer API — upload, analyse, list, detail."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, File, UploadFile

from app.core.config import settings
from app.core.deps import CurrentContext, DbSession, PaginationDep
from app.core.exceptions import NotFoundError, ValidationError
from app.models.health import MedicalReport
from app.repositories.base import TenantRepository
from app.schemas.common import MessageResponse, Page, PageMeta
from app.schemas.health import MedicalReportListItem, MedicalReportOut
from app.services import report_service

router = APIRouter(prefix="/medical-reports", tags=["Medical Report Analyzer"])

_ALLOWED = {"image/jpeg", "image/jpg", "image/png", "image/webp", "application/pdf"}


@router.post("", response_model=MedicalReportOut, status_code=201)
async def upload_report(
    ctx: CurrentContext,
    db: DbSession,
    file: UploadFile = File(...),
    patient_id: uuid.UUID | None = None,
) -> MedicalReportOut:
    """Upload a lab report image/PDF and get a plain-language explanation."""
    mime = (file.content_type or "").lower()
    if mime not in _ALLOWED:
        raise ValidationError(
            "Please upload a JPG, PNG, WEBP or PDF report.", code="UNSUPPORTED_FILE"
        )
    content = await file.read()
    if not content:
        raise ValidationError("Empty file.", code="EMPTY_FILE")
    if len(content) > settings.max_upload_bytes:
        raise ValidationError(
            f"File exceeds {settings.MAX_UPLOAD_MB}MB limit.", code="FILE_TOO_LARGE"
        )

    report = MedicalReport(
        org_id=ctx.org_id, patient_id=patient_id, uploaded_by=ctx.user.id, status="processing"
    )
    db.add(report)
    await db.flush()

    from app.core import storage

    ext = {"application/pdf": "pdf"}.get(mime, mime.split("/")[-1])
    report.storage_path = storage.save(f"{ctx.org_id}/reports/{report.id}.{ext}", content)
    await db.flush()

    await report_service.analyze_report(db, report, content, mime)
    await db.commit()
    return MedicalReportOut.model_validate(report)


@router.get("", response_model=Page[MedicalReportListItem])
async def list_reports(
    ctx: CurrentContext,
    db: DbSession,
    page: PaginationDep,
) -> Page[MedicalReportListItem]:
    repo = TenantRepository(db, MedicalReport)
    rows, total = await repo.list(
        ctx.org_id, limit=page.limit, offset=page.offset,
        order_by=MedicalReport.created_at.desc(),
    )
    items = [
        MedicalReportListItem(
            id=r.id, status=r.status, report_type=r.report_type,
            value_count=len(r.values or []),
            abnormal_count=sum(
                1 for v in (r.values or []) if v.get("status") in ("high", "low", "borderline")
            ),
            created_at=r.created_at,
        )
        for r in rows
    ]
    return Page(
        items=items,
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.get("/{report_id}", response_model=MedicalReportOut)
async def get_report(
    report_id: uuid.UUID, ctx: CurrentContext, db: DbSession
) -> MedicalReportOut:
    repo = TenantRepository(db, MedicalReport)
    report = await repo.get(ctx.org_id, report_id)
    if not report:
        raise NotFoundError("Report not found.")
    return MedicalReportOut.model_validate(report)


@router.delete("/{report_id}", response_model=MessageResponse)
async def delete_report(
    report_id: uuid.UUID, ctx: CurrentContext, db: DbSession
) -> MessageResponse:
    repo = TenantRepository(db, MedicalReport)
    report = await repo.get(ctx.org_id, report_id)
    if not report:
        raise NotFoundError("Report not found.")
    if report.storage_path:
        from app.core import storage

        try:
            storage.delete(report.storage_path)
        except Exception:  # noqa: BLE001 — best-effort cleanup
            pass
    await repo.delete(report)
    return MessageResponse(message="Report deleted.")
