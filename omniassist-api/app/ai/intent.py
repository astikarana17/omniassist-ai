"""Language detection and intent classification using Claude (fast model)."""
from __future__ import annotations

from app.ai import claude
from app.core.logging import get_logger

logger = get_logger("intent")

_SYSTEM = (
    "You are a precise classifier for an omnichannel support & sales platform. "
    "Analyze the customer's latest message in conversation context."
)


async def classify(message: str, history: str = "") -> dict:
    """Return {language, intent, is_sales, wants_human, urgency}."""
    prompt = (
        f"Conversation so far:\n{history or '(none)'}\n\n"
        f"Latest customer message:\n{message}\n\n"
        "Return JSON with keys: "
        "language (the language name of the latest message), "
        "intent (short label like 'billing_issue','refund','product_question',"
        "'pricing','demo_request','complaint','greeting','other'), "
        "is_sales (true if this is a sales/buying intent), "
        "wants_human (true if the customer explicitly asks for a human agent), "
        "urgency (one of 'low','medium','high')."
    )
    try:
        data = await claude.complete_json(system=_SYSTEM, prompt=prompt)
    except Exception as exc:  # noqa: BLE001
        logger.warning("intent_failed", error=str(exc))
        return {
            "language": "English",
            "intent": "other",
            "is_sales": False,
            "wants_human": False,
            "urgency": "medium",
        }
    return {
        "language": data.get("language", "English"),
        "intent": data.get("intent", "other"),
        "is_sales": bool(data.get("is_sales", False)),
        "wants_human": bool(data.get("wants_human", False)),
        "urgency": data.get("urgency", "medium"),
    }
