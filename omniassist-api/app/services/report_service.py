"""Medical Report Analyzer — upload a lab report → extract values → flag
abnormalities (deterministically) → explain in plain language.

Mirrors the Prescription Engine. The high/low/normal flag is computed in Python
(trustworthy, not left to the LLM); the LLM only writes the explanations.
"""
from __future__ import annotations

import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import openrouter
from app.core.documents import to_images
from app.core.logging import get_logger
from app.models.health import MedicalReport

logger = get_logger("report")

_EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "is_report": {"type": "boolean"},
        "report_type": {"type": "string"},
        "values": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "test_name": {"type": "string"},
                    "value": {"type": "string"},
                    "unit": {"type": "string"},
                    "reference_range": {"type": "string"},
                },
                "required": ["test_name", "value"],
            },
        },
    },
    "required": ["values", "is_report"],
}

_EXPLAIN_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "test_name": {"type": "string"},
                    "status": {"type": "string"},
                    "meaning": {"type": "string"},
                    "advice": {"type": "string"},
                },
                "required": ["test_name", "status"],
            },
        },
    },
    "required": ["summary", "findings"],
}

_EXTRACT_SYSTEM = (
    "You are a careful medical lab-report reader. Extract every test/parameter "
    "exactly as printed. Put the parameter name in 'test_name', the patient's "
    "result in 'value', the unit in 'unit', and the printed normal/reference "
    "range verbatim in 'reference_range' (e.g. '13.0-17.0' or '<200'). Never "
    "invent values or ranges. If the image is not a lab/medical report, set "
    "is_report=false and return an empty values list."
)

_EXPLAIN_SYSTEM = (
    "You are a calm, reassuring patient-education assistant. Explain lab results "
    "in simple language. RULES: (1) Use the STATUS provided for each value — do "
    "not recompute it. (2) Write a 'finding' for every High/Low/Borderline value: "
    "what it generally indicates in plain words ('meaning') and what to discuss "
    "with the doctor ('advice'). NEVER state a diagnosis. (3) Write an overall "
    "'summary' in 2-3 friendly sentences. (4) If an abnormal value can relate to "
    "serious conditions, stay general and advise seeing the doctor — do not alarm. "
    "Return strict JSON."
)


def _num(s: str) -> float | None:
    m = re.search(r"-?\d+\.?\d*", str(s).replace(",", ""))
    return float(m.group()) if m else None


def _compute_status(value: str | None, ref: str | None) -> str:
    """Deterministically classify a value against its printed reference range."""
    if not value or not ref:
        return "unknown"
    v = _num(value)
    if v is None:  # non-numeric result (e.g. Positive / Negative / Reactive)
        return "unknown"
    r = str(ref).strip().lower().replace("–", "-").replace("—", "-").replace(" to ", "-")
    rng = re.search(r"(-?\d+\.?\d*)\s*-\s*(-?\d+\.?\d*)", r)
    if rng:
        lo, hi = float(rng.group(1)), float(rng.group(2))
        if v < lo:
            return "low"
        return "high" if v > hi else "normal"
    upper = re.search(r"(?:<|<=|up\s*to|upto|less than|below)\s*(-?\d+\.?\d*)", r)
    if upper:
        return "high" if v > float(upper.group(1)) else "normal"
    lower = re.search(r"(?:>|>=|greater than|above|min)\s*(-?\d+\.?\d*)", r)
    if lower:
        return "low" if v < float(lower.group(1)) else "normal"
    return "unknown"


async def analyze_report(
    db: AsyncSession, report: MedicalReport, image: bytes, mime: str
) -> MedicalReport:
    """Run the full pipeline, mutating + persisting `report`. Never raises."""
    try:
        if not openrouter.is_configured():
            raise RuntimeError(
                "OpenRouter API key not configured — set OPENROUTER_API_KEY to enable analysis."
            )

        extraction = await openrouter.generate_json(
            prompt=(
                "Extract the report type and every test parameter (name, value, "
                "unit, reference range) from this lab report image. Return strict JSON."
            ),
            json_schema=_EXTRACT_SCHEMA,
            system=_EXTRACT_SYSTEM,
            images=to_images(image, mime),
        )
        if not extraction:
            raise RuntimeError("Could not read the image. Please upload a clearer report.")
        if not extraction.get("is_report", True) or not extraction.get("values"):
            report.status = "failed"
            report.error = (
                "This doesn't look like a lab report, or no values were legible. "
                "Please upload a clear photo of a medical/lab report."
            )
            await db.flush()
            return report

        # Deterministic abnormality flags — trustworthy, not LLM-guessed.
        values = extraction.get("values", [])
        for v in values:
            v["status"] = _compute_status(v.get("value"), v.get("reference_range"))
        report.report_type = extraction.get("report_type") or None
        report.values = values

        notable = [v for v in values if v["status"] in ("high", "low", "borderline")]
        value_lines = "\n".join(
            f"- {v.get('test_name')}: {v.get('value')} {v.get('unit') or ''} "
            f"(ref {v.get('reference_range') or 'n/a'}) -> {v['status'].upper()}"
            for v in values
        )
        explanation = await openrouter.generate_json(
            prompt=(
                f"LAB VALUES (status already computed — use it):\n{value_lines}\n\n"
                f"{len(notable)} value(s) are out of range. Write a friendly overall "
                "summary, and a finding (meaning + advice) for each High/Low/Borderline "
                "value. Return strict JSON."
            ),
            json_schema=_EXPLAIN_SCHEMA,
            system=_EXPLAIN_SYSTEM,
        )
        if not explanation:
            raise RuntimeError("Analysis failed while generating explanations. Please retry.")

        report.analysis = explanation.get("findings", []) or []
        report.summary = explanation.get("summary") or None
        report.status = "ready"
        report.error = None
        await db.flush()
        logger.info(
            "report_analyzed",
            report_id=str(report.id),
            values=len(values),
            abnormal=len(notable),
        )
        return report

    except Exception as exc:  # noqa: BLE001 — pipeline must never crash the request
        logger.error("report_failed", report_id=str(report.id), error=str(exc))
        report.status = "failed"
        # Keep raw cause in logs only; show users a safe, friendly message.
        report.error = (
            "We couldn't analyze this report. Please try again or upload a clearer photo or PDF."
        )
        await db.flush()
        return report
