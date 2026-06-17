"""Gemini client (REST via httpx) — the medical AI brain.

Multimodal: reads prescription / report images directly (OCR + reasoning in one
call, no separate OCR engine), generates structured JSON, and produces text
embeddings for the pgvector medical knowledge base.
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

logger = get_logger("gemini")

_BASE = "https://generativelanguage.googleapis.com/v1beta"

# Transient statuses worth retrying (overload / rate-limit / gateway hiccups).
_RETRY_STATUS = {429, 500, 502, 503, 504}
_MAX_RETRIES = 4


async def _post(
    url: str, body: dict[str, Any], *, timeout: float, label: str, headers: dict[str, str] | None = None
) -> httpx.Response:
    """POST with exponential backoff on transient Gemini errors."""
    delay = 1.0
    last: httpx.Response | None = None
    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(_MAX_RETRIES):
            resp = await client.post(url, json=body, headers=headers)
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
                delay *= 2  # 1s, 2s, 4s
    return last  # type: ignore[return-value]


def is_configured() -> bool:
    return bool(settings.GEMINI_API_KEY)


def _require_key() -> str:
    if not settings.GEMINI_API_KEY:
        raise ExternalServiceError(
            "Gemini is not configured. Set GEMINI_API_KEY.", code="GEMINI_NOT_CONFIGURED"
        )
    return settings.GEMINI_API_KEY


async def generate(
    *,
    prompt: str,
    system: str | None = None,
    images: list[tuple[str, bytes]] | None = None,
    json_schema: dict[str, Any] | None = None,
    temperature: float = 0.2,
    max_output_tokens: int = 8192,
    model: str | None = None,
) -> str:
    """Generate content. `images` is a list of (mime_type, raw_bytes). When
    `json_schema` is given, the model is constrained to return valid JSON."""
    key = _require_key()
    model = model or settings.GEMINI_MODEL
    parts: list[dict[str, Any]] = [{"text": prompt}]
    for mime, data in images or []:
        parts.append(
            {"inline_data": {"mime_type": mime, "data": base64.b64encode(data).decode()}}
        )

    gen_config: dict[str, Any] = {
        "temperature": temperature,
        "maxOutputTokens": max_output_tokens,
    }
    # Gemini 2.5 / 3.x "think" by default, consuming the output budget (which can
    # truncate JSON). These are extraction/explanation tasks, not reasoning puzzles
    # — disable thinking so the whole budget goes to the answer.
    if model.startswith(("gemini-2.5", "gemini-3")):
        gen_config["thinkingConfig"] = {"thinkingBudget": 0}

    body: dict[str, Any] = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": gen_config,
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if json_schema is not None:
        body["generationConfig"]["responseMimeType"] = "application/json"
        body["generationConfig"]["responseSchema"] = json_schema

    url = f"{_BASE}/models/{model}:generateContent"
    resp = await _post(url, body, timeout=120, label="gemini_generate", headers={"x-goog-api-key": key})
    if resp.status_code != 200:
        logger.error("gemini_generate_failed", status=resp.status_code, body=resp.text[:300])
        raise ExternalServiceError(
            "The AI service is busy right now. Please try again in a moment.",
            code="GEMINI_ERROR",
        )
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        # Safety blocks / empty candidates land here.
        logger.warning("gemini_empty_response", body=json.dumps(data)[:300])
        return ""


async def generate_json(
    *, prompt: str, json_schema: dict[str, Any], system: str | None = None,
    images: list[tuple[str, bytes]] | None = None, model: str | None = None,
) -> Any:
    """Generate and parse a JSON object against `json_schema`."""
    text = await generate(
        prompt=prompt, system=system, images=images, json_schema=json_schema, model=model
    )
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Strip markdown fences if the model added them despite JSON mode.
        cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("gemini_json_parse_failed", text=text[:200])
            return None


async def embed(text: str, *, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """Return an embedding for `text`, truncated to GEMINI_EMBED_DIM dims.

    Uses gemini-embedding-001 with Matryoshka `outputDimensionality` so the vector
    matches the pgvector column width (768) regardless of the model's native size.
    """
    key = _require_key()
    model = settings.GEMINI_EMBED_MODEL
    url = f"{_BASE}/models/{model}:embedContent"
    body = {
        "model": f"models/{model}",
        "content": {"parts": [{"text": text[:8000]}]},
        "taskType": task_type,
        "outputDimensionality": settings.GEMINI_EMBED_DIM,
    }
    resp = await _post(url, body, timeout=30, label="gemini_embed", headers={"x-goog-api-key": key})
    if resp.status_code != 200:
        logger.error("gemini_embed_failed", status=resp.status_code, body=resp.text[:200])
        raise ExternalServiceError("Gemini embedding failed.", code="GEMINI_EMBED_ERROR")
    return resp.json()["embedding"]["values"]
