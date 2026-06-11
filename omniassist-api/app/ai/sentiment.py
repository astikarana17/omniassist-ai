"""Sentiment analysis + escalation logic."""
from __future__ import annotations

from app.ai import claude
from app.core.logging import get_logger
from app.models.enums import Sentiment

logger = get_logger("sentiment")

_NEGATIVE = {Sentiment.NEGATIVE, Sentiment.ANGRY, Sentiment.FRUSTRATED}

_SYSTEM = (
    "You are a sentiment analyzer. Classify the emotional tone of a customer message "
    "into exactly one of: positive, neutral, negative, angry, frustrated, happy."
)


async def analyze(message: str) -> dict:
    """Return {label, score (0..1 intensity), escalate}."""
    prompt = (
        f"Message:\n{message}\n\n"
        "Return JSON with keys: label (one of "
        "positive|neutral|negative|angry|frustrated|happy), "
        "score (0.0-1.0 emotional intensity)."
    )
    try:
        data = await claude.complete_json(system=_SYSTEM, prompt=prompt)
    except Exception as exc:  # noqa: BLE001
        logger.warning("sentiment_failed", error=str(exc))
        return {"label": Sentiment.NEUTRAL.value, "score": 0.0, "escalate": False}

    label = str(data.get("label", "neutral")).lower()
    if label not in {s.value for s in Sentiment}:
        label = Sentiment.NEUTRAL.value
    score = float(data.get("score", 0.0))
    escalate = label in {s.value for s in _NEGATIVE} and score >= 0.6
    return {"label": label, "score": score, "escalate": escalate}


def should_escalate(label: str, score: float) -> bool:
    return label in {s.value for s in _NEGATIVE} and score >= 0.6
