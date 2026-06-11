"""AI summaries for tickets, conversations and voice calls."""
from __future__ import annotations

from app.ai import claude
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("summarize")

_SYSTEM = (
    "You are an expert support operations assistant. Produce concise, factual summaries "
    "for agents. Never invent details not present in the transcript."
)


async def summarize_conversation(transcript: str) -> dict:
    """Return {summary, resolution, next_steps[]} for a ticket/conversation."""
    prompt = (
        f"Transcript:\n{transcript}\n\n"
        "Return JSON with keys: summary (2-3 sentence TL;DR), "
        "resolution (what was done, or null if unresolved), "
        "next_steps (array of short action strings)."
    )
    try:
        data = await claude.complete_json(
            system=_SYSTEM, prompt=prompt, model=settings.CLAUDE_MODEL
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("summarize_failed", error=str(exc))
        return {"summary": "", "resolution": None, "next_steps": []}
    steps = data.get("next_steps") or []
    if isinstance(steps, str):
        steps = [steps]
    return {
        "summary": data.get("summary", ""),
        "resolution": data.get("resolution"),
        "next_steps": [str(s) for s in steps][:6],
    }


async def summarize_call(transcript_lines: list[dict]) -> dict:
    """Summarize a voice call transcript (list of {speaker, text})."""
    text = "\n".join(f"{line.get('speaker', '?')}: {line.get('text', '')}" for line in transcript_lines)
    return await summarize_conversation(text)
