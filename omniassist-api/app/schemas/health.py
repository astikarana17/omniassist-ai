"""Healthcare API schemas — Prescription Intelligence Engine (flagship)."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

AppointmentStatus = Literal["scheduled", "completed", "cancelled", "rescheduled", "no_show"]

from app.schemas.common import ORMModel

DISCLAIMER = (
    "This is an AI interpretation to help you understand your prescription. "
    "It is not a medical diagnosis or a substitute for professional advice. "
    "Always follow your doctor's and pharmacist's instructions."
)


# --- Pipeline artefacts (stored as JSONB) ---------------------------------


class ExtractedMedicine(BaseModel):
    """A medicine line as read off the prescription image."""

    name: str
    dosage: str | None = None       # e.g. "500 mg"
    frequency: str | None = None    # e.g. "twice daily"
    duration: str | None = None     # e.g. "5 days"
    notes: str | None = None        # e.g. "after food"


class MedicineExplanation(BaseModel):
    """Patient-friendly explanation for one medicine."""

    name: str
    generic_name: str | None = None
    what_it_is: str | None = None
    why_prescribed: str | None = None
    how_it_works: str | None = None
    side_effects: str | None = None
    timing: str | None = None
    food_instructions: str | None = None
    warnings: str | None = None
    grounded: bool = False  # True when backed by our medicine knowledge base


class PossibleCondition(BaseModel):
    """A non-diagnostic inference. NEVER a confirmed diagnosis."""

    condition: str
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str | None = None


# --- API responses ---------------------------------------------------------


class PrescriptionOut(ORMModel):
    id: uuid.UUID
    status: str
    doctor_name: str | None = None
    hospital_name: str | None = None
    prescribed_date: str | None = None
    medicines: list[ExtractedMedicine] = []
    analysis: list[MedicineExplanation] = []
    possible_conditions: list[PossibleCondition] = []
    error: str | None = None
    created_at: datetime
    disclaimer: str = DISCLAIMER


class PrescriptionListItem(ORMModel):
    id: uuid.UUID
    status: str
    doctor_name: str | None = None
    hospital_name: str | None = None
    prescribed_date: str | None = None
    medicine_count: int = 0
    created_at: datetime


# --- Medical Report Analyzer -----------------------------------------------


class ReportValue(BaseModel):
    """One extracted lab parameter with a deterministically-computed status."""

    test_name: str
    value: str | None = None
    unit: str | None = None
    reference_range: str | None = None
    status: str = "unknown"  # normal | high | low | borderline | unknown


class ReportFinding(BaseModel):
    """Plain-language explanation for a notable (usually abnormal) value."""

    test_name: str
    status: str = "unknown"
    meaning: str | None = None  # what this value generally indicates
    advice: str | None = None   # what to discuss with the doctor


class MedicalReportOut(ORMModel):
    id: uuid.UUID
    status: str
    report_type: str | None = None
    values: list[ReportValue] = []
    analysis: list[ReportFinding] = []
    summary: str | None = None
    error: str | None = None
    created_at: datetime
    disclaimer: str = DISCLAIMER


class MedicalReportListItem(ORMModel):
    id: uuid.UUID
    status: str
    report_type: str | None = None
    value_count: int = 0
    abnormal_count: int = 0
    created_at: datetime


# --- AI Health Assistant ---------------------------------------------------


class HealthChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str = Field(min_length=1, max_length=4000)


class HealthChatRequest(BaseModel):
    # Cap turns so the public (unauthenticated) demo can't be fed huge bodies.
    messages: list[HealthChatMessage] = Field(min_length=1, max_length=12)


class HealthChatResponse(BaseModel):
    reply: str
    disclaimer: str = DISCLAIMER


# --- Clinic: Patients ------------------------------------------------------


class PatientCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    allergies: str | None = None
    medical_history: str | None = None


class PatientUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    allergies: str | None = None
    medical_history: str | None = None


class PatientOut(ORMModel):
    id: uuid.UUID
    name: str
    email: str | None = None
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    allergies: str | None = None
    medical_history: str | None = None
    created_at: datetime


# --- Clinic: Doctors -------------------------------------------------------


class DoctorCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    specialty: str | None = None
    department: str | None = None
    license_no: str | None = None


class DoctorUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    specialty: str | None = None
    department: str | None = None
    license_no: str | None = None


class DoctorOut(ORMModel):
    id: uuid.UUID
    name: str
    email: str | None = None
    phone: str | None = None
    specialty: str | None = None
    department: str | None = None
    license_no: str | None = None
    created_at: datetime


# --- Clinic: Appointments --------------------------------------------------


class AppointmentCreate(BaseModel):
    patient_id: uuid.UUID
    doctor_id: uuid.UUID | None = None
    scheduled_at: datetime
    duration_min: int = 30
    reason: str | None = None


class AppointmentUpdate(BaseModel):
    doctor_id: uuid.UUID | None = None
    scheduled_at: datetime | None = None
    duration_min: int | None = None
    status: AppointmentStatus | None = None  # reject unknown statuses with 422
    reason: str | None = None
    notes: str | None = None


class AppointmentOut(ORMModel):
    id: uuid.UUID
    patient_id: uuid.UUID | None = None
    doctor_id: uuid.UUID | None = None
    patient_name: str | None = None
    doctor_name: str | None = None
    scheduled_at: datetime
    duration_min: int
    status: str
    reason: str | None = None
    notes: str | None = None
    created_at: datetime


# --- Clinic: Dashboard overview --------------------------------------------


class ClinicOverview(BaseModel):
    patients: int = 0
    doctors: int = 0
    appointments_total: int = 0
    appointments_today: int = 0
    appointments_upcoming: int = 0
    prescriptions: int = 0
    reports: int = 0
    medicines: int = 0
