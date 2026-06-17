"""OpenRouter client (OpenAI-compatible chat completions).

Used to generate natural-language answers GROUNDED in retrieved knowledge so the
agents read well without hallucinating. Any OpenRouter model works via config.
Also the medical LLM brain (vision OCR + structured explanation) for the
Healthcare Copilot — see `generate_json`.
"""
from __future__ import annotations

import asyncio
import base64
import json
from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger("openrouter")

_HEADERS = {
    "Content-Type": "application/json",
    "HTTP-Referer": "https://omniassist.ai",
    "X-Title": "OmniAssist AI",
}
_RETRY_STATUS = {408, 409, 429, 500, 502, 503, 504}
_MAX_RETRIES = 4


def is_configured() -> bool:
    return bool(settings.OPENROUTER_API_KEY)


def _auth_headers() -> dict[str, str]:
    return {**_HEADERS, "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"}


async def _post(payload: dict[str, Any], *, timeout: float, label: str) -> httpx.Response:
    """POST to chat/completions with exponential backoff on transient errors."""
    url = settings.OPENROUTER_BASE_URL.rstrip("/") + "/chat/completions"
    delay = 1.0
    last: httpx.Response | None = None
    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(_MAX_RETRIES):
            resp = await client.post(url, json=payload, headers=_auth_headers())
            if resp.status_code == 200:
                return resp
            last = resp
            if resp.status_code not in _RETRY_STATUS:
                break
            if attempt < _MAX_RETRIES - 1:
                logger.warning(
                    f"{label}_retry", status=resp.status_code, attempt=attempt + 1, sleep=delay
                )
                await asyncio.sleep(delay)
                delay *= 2
    return last  # type: ignore[return-value]


async def generate_json(
    *,
    prompt: str,
    json_schema: dict[str, Any],
    system: str | None = None,
    images: list[tuple[str, bytes]] | None = None,
    model: str | None = None,
    max_tokens: int = 8192,
) -> Any:
    """Vision-capable structured generation. Mirrors `gemini.generate_json` so the
    medical pipeline can run on OpenRouter. `images` is a list of (mime, raw_bytes)
    sent as data URLs. Returns parsed JSON, or None on empty/unparseable output."""
    if not is_configured():
        return None

    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                f"{prompt}\n\nReturn ONLY valid minified JSON (no markdown, no prose) "
                f"matching this JSON schema:\n{json.dumps(json_schema)}"
            ),
        }
    ]
    for mime, data in images or []:
        b64 = base64.b64encode(data).decode()
        content.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})

    messages: list[dict[str, Any]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": content})

    payload = {
        "model": model or settings.OPENROUTER_VISION_MODEL or settings.OPENROUTER_MODEL,
        "temperature": 0.2,
        "max_tokens": max_tokens,
        "messages": messages,
        "response_format": {"type": "json_object"},
    }
    resp = await _post(payload, timeout=120, label="openrouter_json")
    if resp.status_code != 200:
        logger.error("openrouter_json_failed", status=resp.status_code, body=resp.text[:300])
        raise ExternalServiceError(
            "The AI service is busy right now. Please try again in a moment.",
            code="OPENROUTER_ERROR",
        )
    text = (resp.json()["choices"][0]["message"]["content"] or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        cleaned = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("openrouter_json_parse_failed", text=text[:200])
            return None


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
