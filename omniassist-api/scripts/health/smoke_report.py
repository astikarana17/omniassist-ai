"""End-to-end smoke test for the Medical Report Analyzer.

Renders a synthetic lab report (with deliberate abnormal values), runs the full
pipeline, and prints the extracted values + computed flags + explanations.

Usage: python -m scripts.health.smoke_report
"""
from __future__ import annotations

import asyncio
import io
import sys

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.health import MedicalReport
from app.models.organization import Organization
from app.services import report_service

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LINES = [
    "City Care Diagnostics",
    "Patient: Ramesh S, 46/M          Date: 10/06/2026",
    "",
    "COMPLETE BLOOD COUNT (CBC)",
    "Test                 Result    Unit      Reference",
    "Hemoglobin           10.5      g/dL      13.0 - 17.0",
    "WBC Count            11200     /uL       4000 - 11000",
    "Platelet Count       250000    /uL       150000 - 410000",
    "RBC Count            4.8       mil/uL    4.5 - 5.5",
    "",
    "THYROID PROFILE",
    "TSH                  6.8       uIU/mL    0.4 - 4.0",
    "T3                   1.2       ng/mL     0.8 - 2.0",
    "T4                   7.5       ug/dL     5.0 - 12.0",
    "",
    "LIPID / SUGAR",
    "Total Cholesterol    245       mg/dL     < 200",
    "HDL Cholesterol      38        mg/dL     > 40",
    "Fasting Glucose      105       mg/dL     70 - 100",
]


def _make_image() -> bytes:
    img = Image.new("RGB", (760, 720), "white")
    d = ImageDraw.Draw(img)
    try:
        title = ImageFont.truetype("arial.ttf", 24)
        body = ImageFont.truetype("cour.ttf", 18)  # monospace → aligned columns
    except OSError:
        title = body = ImageFont.load_default()
    y = 22
    for i, ln in enumerate(LINES):
        d.text((34, y), ln, fill="black", font=title if i == 0 else body)
        y += 36 if i == 0 else 32
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


async def main() -> None:
    image = _make_image()
    print(f"[1] synthetic lab report rendered ({len(image)} bytes)")
    async with AsyncSessionLocal() as db:
        org = (await db.execute(select(Organization).limit(1))).scalar_one()
        report = MedicalReport(org_id=org.id, status="processing")
        db.add(report)
        await db.flush()
        print("[2] running pipeline (vision OCR → range check → explanation)…")
        await report_service.analyze_report(db, report, image, "image/png")
        await db.commit()

        print(f"\n=== RESULT: status={report.status} | type={report.report_type} ===")
        if report.status != "ready":
            print("ERROR:", report.error)
            return
        print(f"\nSummary: {report.summary}\n")
        print(f"{'TEST':22}{'RESULT':12}{'REF':18}STATUS")
        for v in report.values:
            print(
                f"{v.get('test_name','')[:21]:22}"
                f"{(str(v.get('value',''))+' '+(v.get('unit') or ''))[:11]:12}"
                f"{(v.get('reference_range') or '')[:17]:18}"
                f"{v.get('status','').upper()}"
            )
        print(f"\nFindings ({len(report.analysis)}):")
        for f in report.analysis:
            print(f"  • {f.get('test_name')} [{f.get('status','').upper()}]: {f.get('meaning')}")
            if f.get("advice"):
                print(f"      ↳ {f.get('advice')}")
        print(f"\n[ok] report id={report.id}")


if __name__ == "__main__":
    asyncio.run(main())
