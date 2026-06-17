"""Ingest the A-Z Medicine Dataset of India (Kaggle) into the medicine KB.

Adds ~250k Indian brand medicines as reference rows (name → active-ingredient
composition) so the Prescription Engine can resolve real brand names like
"Azithral 500" → Azithromycin. These rows carry no rich patient-education text
(that stays on the curated set) and are NOT embedded — they power fast SQL
name-matching. A pg_trgm GIN index keeps prefix/contains matching fast.

Usage:
    python -m scripts.health.seed_az_medicines            # ingest all
    python -m scripts.health.seed_az_medicines --limit 5000
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import uuid

import kagglehub
import pandas as pd
from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.database import AsyncSessionLocal, engine
from app.models.health import Medicine

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SOURCE = "az-india"
BATCH = 5000
DATASET = "shudhanshusingh/az-medicine-dataset-of-india"


def _composition(c1, c2) -> str | None:
    parts = []
    for c in (c1, c2):
        if pd.notna(c):
            s = str(c).strip()
            if s and s.lower() != "nan":
                parts.append(s)
    return " + ".join(parts) or None


def _load_frame(limit: int | None) -> pd.DataFrame:
    import glob
    import os

    base = kagglehub.dataset_download(DATASET)
    csv = glob.glob(os.path.join(base, "*.csv"))[0]
    df = pd.read_csv(csv, usecols=["name", "short_composition1", "short_composition2"])
    df = df.dropna(subset=["name"]).drop_duplicates(subset=["name"])
    if limit:
        df = df.head(limit)
    return df


async def _index() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_medicines_name_trgm "
                "ON medicines USING gin (lower(name) gin_trgm_ops)"
            )
        )
    print("[index] pg_trgm GIN index on lower(name) ready")


async def main(limit: int | None) -> None:
    df = _load_frame(limit)
    print(f"[load] {len(df)} unique catalogue rows")

    async with AsyncSessionLocal() as db:
        existing = {
            n.lower()
            for (n,) in (await db.execute(select(Medicine.name))).all()
        }
    print(f"[skip] {len(existing)} names already in KB")

    batch: list[dict] = []
    inserted = skipped = 0
    async with AsyncSessionLocal() as db:
        for row in df.itertuples(index=False):
            name = str(row.name).strip()
            if not name or name.lower() in existing:
                skipped += 1
                continue
            existing.add(name.lower())
            batch.append(
                {
                    "id": uuid.uuid4(),
                    "name": name[:200],
                    "generic_name": (_composition(row.short_composition1, row.short_composition2) or None),
                    "source": SOURCE,
                }
            )
            if len(batch) >= BATCH:
                await db.execute(pg_insert(Medicine.__table__), batch)
                await db.commit()
                inserted += len(batch)
                batch.clear()
                print(f"  …{inserted} inserted")
        if batch:
            await db.execute(pg_insert(Medicine.__table__), batch)
            await db.commit()
            inserted += len(batch)

    print(f"[done] inserted {inserted}, skipped {skipped}")
    await _index()

    async with AsyncSessionLocal() as db:
        total = (await db.execute(text("SELECT count(*) FROM medicines"))).scalar_one()
    print(f"[ok] medicine KB now holds {total} rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    asyncio.run(main(args.limit))
