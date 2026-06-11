"""OpenRouter client (OpenAI-compatible chat completions).

Used to generate natural-language answers GROUNDED in retrieved knowledge so the
agents read well without hallucinating. Any OpenRouter model works via config.
"""
from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("openrouter")


def is_configured() -> bool:
    return bool(settings.OPENROUTER_API_KEY)


async def complete(
    *,
    system: str,
    messages: list[dict[str, Any]],
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 700,
) -> tuple[str, int, int]:
    """Return (text, prompt_tokens, completion_tokens). Raises on transport/API error."""
    url = settings.OPENROUTER_BASE_URL.rstrip("/") + "/chat/completions"
    payload = {
        "model": model or settings.OPENROUTER_MODEL,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": system}, *messages],
    }
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://omniassist.ai",
        "X-Title": "OmniAssist AI",
    }
    async with httpx.AsyncClient(timeout=45) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    choice = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {}) or {}
    return (
        (choice or "").strip(),
        int(usage.get("prompt_tokens", 0)),
        int(usage.get("completion_tokens", 0)),
    )
