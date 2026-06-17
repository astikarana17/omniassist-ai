"""Healthcare domain models — patients, doctors, appointments, prescriptions,
medical reports, and the medicine knowledge base (pgvector RAG).

Multi-tenant: org = hospital/clinic. Medicine reference data is global (org_id NULL).
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Date, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base, TimestampMixin, UUIDMixin


def _org_fk() -> Mapped[uuid.UUID]:
    return mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )


class Patient(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "patients"
    __table_args__ = (Index("ix_patients_org", "org_id", "created_at"),)

    org_id: Mapped[uuid.UUID] = _org_fk()
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(8), nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    medical_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class Doctor(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "doctors"
    __table_args__ = (Index("ix_doctors_org", "org_id"),)

    org_id: Mapped[uuid.UUID] = _org_fk()
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    specialty: Mapped[str | None] = mapped_column(String(120), nullable=True)
    department: Mapped[str | None] = mapped_column(String(120), nullable=True)
    license_no: Mapped[str | None] = mapped_column(String(80), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class Appointment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointments_org_time", "org_id", "scheduled_at"),
        Index("ix_appointments_doctor", "doctor_id", "scheduled_at"),
        Index("ix_appointments_patient", "patient_id"),
    )

    org_id: Mapped[uuid.UUID] = _org_fk()
    patient_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=True
    )
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_min: Mapped[int] = mapped_column(default=30, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="scheduled", nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class Prescription(UUIDMixin, TimestampMixin, Base):
    """An uploaded prescription analysed by the Prescription Intelligence Engine."""

    __tablename__ = "prescriptions"
    __table_args__ = (Index("ix_prescriptions_org", "org_id", "created_at"),)

    org_id: Mapped[uuid.UUID] = _org_fk()
    patient_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("patients.id", ondelete="SET NULL"), nullable=True
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # OCR-extracted header
    doctor_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    hospital_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    prescribed_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # Pipeline artefacts
    storage_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    medicines: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)  # extracted
    analysis: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)   # AI explanations
    possible_conditions: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="processing", nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class MedicalReport(UUIDMixin, TimestampMixin, Base):
    """An uploaded lab/medical report analysed by the Report Analyzer."""

    __tablename__ = "medical_reports"
    __table_args__ = (Index("ix_medical_reports_org", "org_id", "created_at"),)

    org_id: Mapped[uuid.UUID] = _org_fk()
    patient_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("patients.id", ondelete="SET NULL"), nullable=True
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    report_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    values: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)   # extracted rows
    analysis: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="processing", nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class Medicine(UUIDMixin, TimestampMixin, Base):
    """Global medicine reference data (org_id NULL) powering the medical RAG."""

    __tablename__ = "medicines"
    __table_args__ = (Index("ix_medicines_name", "name"),)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    generic_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    how_it_works: Mapped[str | None] = mapped_column(Text, nullable=True)
    side_effects: Mapped[str | None] = mapped_column(Text, nullable=True)
    warnings: Mapped[str | None] = mapped_column(Text, nullable=True)
    food_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    timing: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(80), nullable=True)

    embedding_row: Mapped["MedicineEmbedding | None"] = relationship(
        back_populates="medicine", uselist=False, cascade="all, delete-orphan"
    )


class MedicineEmbedding(UUIDMixin, TimestampMixin, Base):
    """pgvector embedding for semantic medicine retrieval."""

    __tablename__ = "medicine_embeddings"

    medicine_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("medicines.id", ondelete="CASCADE"),
        nullable=False, unique=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.GEMINI_EMBED_DIM), nullable=False)

    medicine: Mapped["Medicine"] = relationship(back_populates="embedding_row")


class HealthKnowledge(UUIDMixin, TimestampMixin, Base):
    """Curated general-health knowledge powering the AI Health Assistant's RAG.

    Global (no org) — conditions, symptoms, lab tests, first aid, prevention,
    medication classes, lifestyle, mental health, emergencies, etc. Each row is
    embedded so the assistant can retrieve grounded references before answering.
    """

    __tablename__ = "health_knowledge"
    __table_args__ = (Index("ix_health_knowledge_category", "category"),)

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    category: Mapped[str | None] = mapped_column(String(60), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # Nullable so rows can be inserted before the (Gemini) embedding pass runs.
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.GEMINI_EMBED_DIM), nullable=True
    )
