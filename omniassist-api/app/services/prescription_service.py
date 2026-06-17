"""Prescription Intelligence Engine — the flagship pipeline.

Upload image/PDF → Gemini multimodal OCR + structured extraction → ground each
medicine against the knowledge base → Gemini produces a patient-friendly
explanation + NON-DIAGNOSTIC possible conditions. All safety rails live here.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import medical_rag, openrouter
from app.core.documents import to_images as _to_images
from app.core.logging import get_logger
from app.models.health import Medicine, Prescription

logger = get_logger("prescription")

# --- Gemini structured-output schemas -------------------------------------

_EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "doctor_name": {"type": "string"},
        "hospital_name": {"type": "string"},
        "prescribed_date": {"type": "string"},
        "is_prescription": {"type": "boolean"},
        "medicines": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "dosage": {"type": "string"},
                    "frequency": {"type": "string"},
                    "duration": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["name"],
            },
        },
    },
    "required": ["medicines", "is_prescription"],
}

_EXPLAIN_SCHEMA = {
    "type": "object",
    "properties": {
        "medicines": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "generic_name": {"type": "string"},
                    "what_it_is": {"type": "string"},
                    "why_prescribed": {"type": "string"},
                    "how_it_works": {"type": "string"},
                    "side_effects": {"type": "string"},
                    "timing": {"type": "string"},
                    "food_instructions": {"type": "string"},
                    "warnings": {"type": "string"},
                },
                "required": ["name"],
            },
        },
        "possible_conditions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "condition": {"type": "string"},
                    "confidence": {"type": "number"},
                    "explanation": {"type": "string"},
                },
                "required": ["condition", "confidence"],
            },
        },
    },
    "required": ["medicines"],
}

_EXTRACT_SYSTEM = (
    "You are a careful medical OCR assistant. Read the prescription image exactly "
    "as written. Transcribe medicine names faithfully (do not invent or 'correct' "
    "to similar drugs). IMPORTANT: put ONLY the drug name (brand or generic) in "
    "'name' — NO strength or quantity. Put the strength like '500 mg' in 'dosage', "
    "the daily pattern (e.g. '1-0-1' or 'twice daily') in 'frequency', the course "
    "length (e.g. '5 days') in 'duration', and anything else (e.g. 'after food') in "
    "'notes'. If the image is not a medical prescription, set is_prescription=false "
    "and return an empty medicines list."
)

_EXPLAIN_SYSTEM = (
    "You are a patient-education assistant for a healthcare app. Explain medicines "
    "in simple, reassuring language a non-medical person understands. "
    "RULES: (1) Prefer the REFERENCE DATA provided for each medicine; only use "
    "general knowledge when no reference is given, and keep it conservative and "
    "widely-accepted. (2) Never give dosing advice beyond what the prescription "
    "states. (3) For possible_conditions: infer only GENERAL, NON-DIAGNOSTIC "
    "possibilities suggested by the combination of medicines, each with a "
    "confidence 0-1. These are NOT a diagnosis. If you are unsure, return an empty "
    "list. Never name a serious/alarming condition speculatively."
)


def _kb_reference(extracted: list[dict], matches: dict[str, Medicine]) -> str:
    """Build the grounding context from KB matches. Handles both rich curated rows
    and sparse catalogue rows (brand → composition only) — only emits known fields."""
    lines: list[str] = []
    for med in extracted:
        name = med.get("name", "")
        m = matches.get(name)
        if not m:
            lines.append(f"- {name}: (no reference in knowledge base — use general medical knowledge)")
            continue
        parts = [f"- {name} → '{m.name}'"]
        if m.generic_name:
            parts.append(f"active ingredients: {m.generic_name}")
        for label, val in (
            ("Purpose", m.purpose), ("How it works", m.how_it_works),
            ("Side effects", m.side_effects), ("Warnings", m.warnings),
            ("Food", m.food_instructions), ("Timing", m.timing),
        ):
            if val:
                parts.append(f"{label}: {val}")
        lines.append(". ".join(parts))
    return "\n".join(lines)


async def analyze_prescription(
    db: AsyncSession, prescription: Prescription, image: bytes, mime: str
) -> Prescription:
    """Run the full pipeline, mutating + persisting `prescription`. Never raises —
    failures are captured on the row as status='failed'."""
    try:
        if not openrouter.is_configured():
            raise RuntimeError(
                "OpenRouter API key not configured — set OPENROUTER_API_KEY to enable analysis."
            )

        # 1) Multimodal OCR + structured extraction ------------------------
        extraction = await openrouter.generate_json(
            prompt=(
                "Extract the prescription header and every medicine line from this "
                "image. Return strict JSON matching the schema."
            ),
            json_schema=_EXTRACT_SCHEMA,
            system=_EXTRACT_SYSTEM,
            images=_to_images(image, mime),
        )
        if not extraction:
            raise RuntimeError("Could not read the image. Please upload a clearer photo.")
        if not extraction.get("is_prescription", True) or not extraction.get("medicines"):
            prescription.status = "failed"
            prescription.error = (
                "This doesn't look like a prescription, or no medicines were legible. "
                "Please upload a clear photo of a prescription."
            )
            await db.flush()
            return prescription

        extracted: list[dict] = extraction.get("medicines", [])
        prescription.doctor_name = extraction.get("doctor_name") or None
        prescription.hospital_name = extraction.get("hospital_name") or None
        prescription.prescribed_date = extraction.get("prescribed_date") or None
        prescription.medicines = extracted

        # 2) Ground each medicine against the knowledge base ---------------
        matches: dict[str, Medicine] = {}
        grounded_terms: set[str] = set()
        for med in extracted:
            name = med.get("name", "")
            match = await medical_rag.match_medicine(db, name)
            if match:
                matches[name] = match
                grounded_terms.add(match.name.lower())
                if match.generic_name:
                    grounded_terms.add(match.generic_name.lower())

        def _is_grounded(item: dict) -> bool:
            # Robust to strength suffixes + brand/generic drift between the two
            # LLM steps: match by containment against the matched KB names.
            nm = (item.get("name") or "").lower()
            gn = (item.get("generic_name") or "").lower()
            return any(
                t and (t in nm or nm in t or (gn and (t in gn or gn in t)))
                for t in grounded_terms
            )

        # 3) Patient-friendly explanation + possible conditions ------------
        med_list = "\n".join(
            f"- {m.get('name','')} {m.get('dosage','') or ''} "
            f"{m.get('frequency','') or ''} {m.get('notes','') or ''}".strip()
            for m in extracted
        )
        explanation = await openrouter.generate_json(
            prompt=(
                f"PRESCRIBED MEDICINES:\n{med_list}\n\n"
                f"REFERENCE DATA (prefer this):\n{_kb_reference(extracted, matches)}\n\n"
                "For every medicine above, write a simple explanation (what it is, why "
                "it's commonly prescribed, how it works, common side effects, when to "
                "take it, food instructions, key warnings). Then add possible_conditions "
                "per the rules. Return strict JSON."
            ),
            json_schema=_EXPLAIN_SCHEMA,
            system=_EXPLAIN_SYSTEM,
        )
        if not explanation:
            raise RuntimeError("Analysis failed while generating explanations. Please retry.")

        analysis = explanation.get("medicines", [])
        for item in analysis:
            item["grounded"] = _is_grounded(item)

        prescription.analysis = analysis
        prescription.possible_conditions = explanation.get("possible_conditions", []) or []
        prescription.status = "ready"
        prescription.error = None
        await db.flush()
        logger.info(
            "prescription_analyzed",
            prescription_id=str(prescription.id),
            medicines=len(extracted),
            grounded=len(matches),
        )
        return prescription

    except Exception as exc:  # noqa: BLE001 — pipeline must never crash the request
        logger.error("prescription_failed", prescription_id=str(prescription.id), error=str(exc))
        prescription.status = "failed"
        # Keep raw cause in logs only; show users a safe, friendly message.
        prescription.error = (
            "We couldn't analyze this file. Please try again or upload a clearer photo or PDF."
        )
        await db.flush()
        return prescription
