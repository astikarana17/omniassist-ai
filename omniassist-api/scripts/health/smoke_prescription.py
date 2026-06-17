"""End-to-end smoke test for the Prescription Intelligence Engine.

Renders a synthetic prescription image, runs the full pipeline (Gemini OCR →
KB grounding → explanation + possible conditions), and prints a readable report.

Usage: python -m scripts.health.smoke_prescription
"""
from __future__ import annotations

import argparse
import asyncio
import io
import pathlib
import sys

# Windows consoles default to cp1252 — force UTF-8 so arrows/checkmarks print.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.health import Prescription
from app.models.organization import Organization
from app.services import prescription_service

LINES = [
    "City Care Hospital & Clinic",
    "Dr. Rajesh Kumar, MBBS, MD (Medicine)",
    "Date: 10/06/2026",
    "",
    "Patient: Ramesh S.        Age: 46 / Male",
    "",
    "Rx",
    "1) Tab. Paracetamol 500mg    1-1-1   x 5 days  (after food)",
    "2) Tab. Amoxicillin 500mg    1-0-1   x 7 days",
    "3) Tab. Pantop 40mg          1-0-0   before breakfast",
    "4) Tab. Amlodipine 5mg       0-0-1   daily at night",
    "",
    "Advice: Plenty of oral fluids, rest. Review after 1 week.",
]


def _make_image() -> bytes:
    img = Image.new("RGB", (900, 620), "white")
    d = ImageDraw.Draw(img)
    try:
        title = ImageFont.truetype("arial.ttf", 28)
        body = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        title = body = ImageFont.load_default()
    y = 24
    for i, ln in enumerate(LINES):
        d.text((40, y), ln, fill="black", font=title if i == 0 else body)
        y += 40 if i == 0 else 34
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


async def main(image_path: str | None) -> None:
    if image_path:
        data = pathlib.Path(image_path).read_bytes()
        mime = "image/png" if image_path.lower().endswith("png") else "image/jpeg"
        image = data
        print(f"[1] loaded real prescription image: {image_path} ({len(image)} bytes)")
    else:
        image, mime = _make_image(), "image/png"
        print(f"[1] synthetic prescription rendered ({len(image)} bytes)")

    async with AsyncSessionLocal() as db:
        org = (await db.execute(select(Organization).limit(1))).scalar_one()
        rx = Prescription(org_id=org.id, status="processing")
        db.add(rx)
        await db.flush()

        print("[2] running pipeline (vision OCR → grounding → explanation)…")
        await prescription_service.analyze_prescription(db, rx, image, mime)
        await db.commit()

        print(f"\n=== RESULT: status={rx.status} ===")
        if rx.status != "ready":
            print("ERROR:", rx.error)
            return
        print(f"Doctor:   {rx.doctor_name}")
        print(f"Hospital: {rx.hospital_name}")
        print(f"Date:     {rx.prescribed_date}")
        print(f"\nExtracted {len(rx.medicines)} medicines:")
        for m in rx.medicines:
            print(f"  - {m.get('name')} | {m.get('dosage')} | {m.get('frequency')} | {m.get('notes')}")
        print(f"\nExplanations ({len(rx.analysis)}):")
        for a in rx.analysis:
            tag = "✓KB" if a.get("grounded") else "~gen"
            print(f"\n  [{tag}] {a.get('name')} ({a.get('generic_name') or '-'})")
            print(f"    what:    {a.get('what_it_is')}")
            print(f"    why:     {a.get('why_prescribed')}")
            print(f"    timing:  {a.get('timing')}  | food: {a.get('food_instructions')}")
        print(f"\nPossible conditions ({len(rx.possible_conditions)}):")
        for c in rx.possible_conditions:
            print(f"  - {c.get('condition')} ({round(c.get('confidence',0)*100)}%): {c.get('explanation')}")
        print(f"\n[ok] prescription id={rx.id} — visible in the UI history.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default=None, help="path to a real prescription image")
    args = parser.parse_args()
    asyncio.run(main(args.image))
