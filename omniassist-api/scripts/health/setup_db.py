"""Enable pgvector + create the healthcare tables. Idempotent.

Usage: python -m scripts.health.setup_db
"""
from __future__ import annotations

import asyncio

from sqlalchemy import text

from app.core.database import Base, engine
from app.models.health import (  # noqa: F401 — registers tables on Base.metadata
    Appointment,
    Doctor,
    HealthKnowledge,
    MedicalReport,
    Medicine,
    MedicineEmbedding,
    Patient,
    Prescription,
)

TABLES = [
    Patient.__table__,
    Doctor.__table__,
    Appointment.__table__,
    Prescription.__table__,
    MedicalReport.__table__,
    Medicine.__table__,
    MedicineEmbedding.__table__,
    HealthKnowledge.__table__,
]


async def main() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all, tables=TABLES)
        # Note: with a small medicine set, exact cosine search is instant — an
        # IVFFlat/HNSW index can be added once the corpus grows past ~10k rows.
    print("[OK] pgvector enabled + healthcare tables created:")
    for t in TABLES:
        print(f"  - {t.name}")


if __name__ == "__main__":
    asyncio.run(main())
