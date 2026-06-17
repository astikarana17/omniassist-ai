"""Clinic management — Patients, Doctors and Appointments (tenant-scoped CRUD)."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from fastapi import APIRouter

from app.core.deps import CurrentContext, DbSession, PaginationDep
from app.core.exceptions import NotFoundError
from app.models.health import Appointment, Doctor, MedicalReport, Medicine, Patient, Prescription
from app.repositories.base import TenantRepository
from app.schemas.common import MessageResponse, Page, PageMeta
from app.schemas.health import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentUpdate,
    ClinicOverview,
    DoctorCreate,
    DoctorOut,
    DoctorUpdate,
    PatientCreate,
    PatientOut,
    PatientUpdate,
)

router = APIRouter(tags=["Clinic"])


@router.get("/clinic/overview", response_model=ClinicOverview)
async def clinic_overview(ctx: CurrentContext, db: DbSession) -> ClinicOverview:
    """Aggregate counts for the healthcare dashboard (single round-trip)."""
    org = ctx.org_id

    async def count(model, *filters) -> int:
        stmt = select(func.count()).select_from(model).where(model.org_id == org, *filters)
        return int((await db.execute(stmt)).scalar_one())

    now = datetime.now(timezone.utc)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    medicines = int(
        (await db.execute(select(func.count()).select_from(Medicine))).scalar_one()
    )
    return ClinicOverview(
        patients=await count(Patient),
        doctors=await count(Doctor),
        appointments_total=await count(Appointment),
        appointments_today=await count(
            Appointment, Appointment.scheduled_at >= day_start, Appointment.scheduled_at < day_end
        ),
        appointments_upcoming=await count(
            Appointment, Appointment.scheduled_at >= now, Appointment.status == "scheduled"
        ),
        prescriptions=await count(Prescription),
        reports=await count(MedicalReport),
        medicines=medicines,
    )


def _page(items, total, page) -> Page:
    return Page(
        items=items,
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(items) < total),
    )


# ----------------------------- Patients ------------------------------------


@router.get("/patients", response_model=Page[PatientOut])
async def list_patients(ctx: CurrentContext, db: DbSession, page: PaginationDep) -> Page[PatientOut]:
    rows, total = await TenantRepository(db, Patient).list(
        ctx.org_id, limit=page.limit, offset=page.offset, order_by=Patient.created_at.desc()
    )
    return _page([PatientOut.model_validate(r) for r in rows], total, page)


@router.post("/patients", response_model=PatientOut, status_code=201)
async def create_patient(payload: PatientCreate, ctx: CurrentContext, db: DbSession) -> PatientOut:
    patient = Patient(org_id=ctx.org_id, **payload.model_dump())
    db.add(patient)
    await db.flush()
    await db.refresh(patient)  # populate server-generated created_at/updated_at
    return PatientOut.model_validate(patient)


@router.get("/patients/{patient_id}", response_model=PatientOut)
async def get_patient(patient_id: uuid.UUID, ctx: CurrentContext, db: DbSession) -> PatientOut:
    patient = await TenantRepository(db, Patient).get(ctx.org_id, patient_id)
    if not patient:
        raise NotFoundError("Patient not found.")
    return PatientOut.model_validate(patient)


@router.patch("/patients/{patient_id}", response_model=PatientOut)
async def update_patient(
    patient_id: uuid.UUID, payload: PatientUpdate, ctx: CurrentContext, db: DbSession
) -> PatientOut:
    patient = await TenantRepository(db, Patient).get(ctx.org_id, patient_id)
    if not patient:
        raise NotFoundError("Patient not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(patient, k, v)
    await db.flush()
    return PatientOut.model_validate(patient)


@router.delete("/patients/{patient_id}", response_model=MessageResponse)
async def delete_patient(patient_id: uuid.UUID, ctx: CurrentContext, db: DbSession) -> MessageResponse:
    repo = TenantRepository(db, Patient)
    patient = await repo.get(ctx.org_id, patient_id)
    if not patient:
        raise NotFoundError("Patient not found.")
    await repo.delete(patient)
    return MessageResponse(message="Patient deleted.")


# ------------------------------ Doctors ------------------------------------


@router.get("/doctors", response_model=Page[DoctorOut])
async def list_doctors(ctx: CurrentContext, db: DbSession, page: PaginationDep) -> Page[DoctorOut]:
    rows, total = await TenantRepository(db, Doctor).list(
        ctx.org_id, limit=page.limit, offset=page.offset, order_by=Doctor.created_at.desc()
    )
    return _page([DoctorOut.model_validate(r) for r in rows], total, page)


@router.post("/doctors", response_model=DoctorOut, status_code=201)
async def create_doctor(payload: DoctorCreate, ctx: CurrentContext, db: DbSession) -> DoctorOut:
    doctor = Doctor(org_id=ctx.org_id, **payload.model_dump())
    db.add(doctor)
    await db.flush()
    await db.refresh(doctor)  # populate server-generated created_at/updated_at
    return DoctorOut.model_validate(doctor)


@router.get("/doctors/{doctor_id}", response_model=DoctorOut)
async def get_doctor(doctor_id: uuid.UUID, ctx: CurrentContext, db: DbSession) -> DoctorOut:
    doctor = await TenantRepository(db, Doctor).get(ctx.org_id, doctor_id)
    if not doctor:
        raise NotFoundError("Doctor not found.")
    return DoctorOut.model_validate(doctor)


@router.patch("/doctors/{doctor_id}", response_model=DoctorOut)
async def update_doctor(
    doctor_id: uuid.UUID, payload: DoctorUpdate, ctx: CurrentContext, db: DbSession
) -> DoctorOut:
    doctor = await TenantRepository(db, Doctor).get(ctx.org_id, doctor_id)
    if not doctor:
        raise NotFoundError("Doctor not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(doctor, k, v)
    await db.flush()
    return DoctorOut.model_validate(doctor)


@router.delete("/doctors/{doctor_id}", response_model=MessageResponse)
async def delete_doctor(doctor_id: uuid.UUID, ctx: CurrentContext, db: DbSession) -> MessageResponse:
    repo = TenantRepository(db, Doctor)
    doctor = await repo.get(ctx.org_id, doctor_id)
    if not doctor:
        raise NotFoundError("Doctor not found.")
    await repo.delete(doctor)
    return MessageResponse(message="Doctor deleted.")


# --------------------------- Appointments ----------------------------------


async def _enrich(db: DbSession, org_id: uuid.UUID, rows: list[Appointment]) -> list[AppointmentOut]:
    """Attach patient/doctor display names (batched, no N+1)."""
    pids = {r.patient_id for r in rows if r.patient_id}
    dids = {r.doctor_id for r in rows if r.doctor_id}
    pnames: dict[uuid.UUID, str] = {}
    dnames: dict[uuid.UUID, str] = {}
    # Scope name lookups to this org so a forged/stale cross-tenant id never
    # resolves to another clinic's patient/doctor name (tenant isolation).
    if pids:
        for p in (await db.execute(
            select(Patient).where(Patient.org_id == org_id, Patient.id.in_(pids))
        )).scalars():
            pnames[p.id] = p.name
    if dids:
        for d in (await db.execute(
            select(Doctor).where(Doctor.org_id == org_id, Doctor.id.in_(dids))
        )).scalars():
            dnames[d.id] = d.name
    out = []
    for r in rows:
        o = AppointmentOut.model_validate(r)
        o.patient_name = pnames.get(r.patient_id) if r.patient_id else None
        o.doctor_name = dnames.get(r.doctor_id) if r.doctor_id else None
        out.append(o)
    return out


@router.get("/appointments", response_model=Page[AppointmentOut])
async def list_appointments(
    ctx: CurrentContext, db: DbSession, page: PaginationDep
) -> Page[AppointmentOut]:
    rows, total = await TenantRepository(db, Appointment).list(
        ctx.org_id, limit=page.limit, offset=page.offset, order_by=Appointment.scheduled_at.desc()
    )
    return _page(await _enrich(db, ctx.org_id, rows), total, page)


@router.post("/appointments", response_model=AppointmentOut, status_code=201)
async def create_appointment(
    payload: AppointmentCreate, ctx: CurrentContext, db: DbSession
) -> AppointmentOut:
    # Validate the patient (and doctor, if given) belong to this org.
    if not await TenantRepository(db, Patient).get(ctx.org_id, payload.patient_id):
        raise NotFoundError("Patient not found.")
    if payload.doctor_id is not None and not await TenantRepository(db, Doctor).get(
        ctx.org_id, payload.doctor_id
    ):
        raise NotFoundError("Doctor not found.")
    appt = Appointment(org_id=ctx.org_id, status="scheduled", **payload.model_dump())
    db.add(appt)
    await db.flush()
    await db.refresh(appt)  # populate server-generated created_at/updated_at
    return (await _enrich(db, ctx.org_id, [appt]))[0]


@router.patch("/appointments/{appointment_id}", response_model=AppointmentOut)
async def update_appointment(
    appointment_id: uuid.UUID, payload: AppointmentUpdate, ctx: CurrentContext, db: DbSession
) -> AppointmentOut:
    appt = await TenantRepository(db, Appointment).get(ctx.org_id, appointment_id)
    if not appt:
        raise NotFoundError("Appointment not found.")
    data = payload.model_dump(exclude_unset=True)
    # Validate a (re)assigned doctor belongs to this org before persisting it.
    if data.get("doctor_id") is not None and not await TenantRepository(db, Doctor).get(
        ctx.org_id, data["doctor_id"]
    ):
        raise NotFoundError("Doctor not found.")
    for k, v in data.items():
        setattr(appt, k, v)
    await db.flush()
    return (await _enrich(db, ctx.org_id, [appt]))[0]


@router.delete("/appointments/{appointment_id}", response_model=MessageResponse)
async def delete_appointment(
    appointment_id: uuid.UUID, ctx: CurrentContext, db: DbSession
) -> MessageResponse:
    repo = TenantRepository(db, Appointment)
    appt = await repo.get(ctx.org_id, appointment_id)
    if not appt:
        raise NotFoundError("Appointment not found.")
    await repo.delete(appt)
    return MessageResponse(message="Appointment cancelled.")
