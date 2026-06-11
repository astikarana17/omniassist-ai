"""Anthropic Claude client wrapper with retries, JSON mode and usage tracking."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from anthropic import AsyncAnthropic
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger("claude")

_client: AsyncAnthropic | None = None


def get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY, max_retries=0)
    return _client


@dataclass
class LLMResult:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str | None = None
    raw_tool_calls: list[dict] = field(default_factory=list)


class _Transient(Exception):
    pass


@retry(
    retry=retry_if_exception_type(_Transient),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=6),
    reraise=True,
)
async def complete(
    *,
    system: str,
    messages: list[dict[str, Any]],
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float = 0.3,
    tools: list[dict] | None = None,
) -> LLMResult:
    """Single Claude completion. Retries on transient API errors with backoff."""
    client = get_client()
    try:
        resp = await client.messages.create(
            model=model or settings.CLAUDE_MODEL,
            max_tokens=max_tokens or settings.CLAUDE_MAX_TOKENS,
            temperature=temperature,
            system=system,
            messages=messages,
            tools=tools or [],
        )
    except Exception as exc:  # noqa: BLE001
        status = getattr(exc, "status_code", None)
        if status in (408, 429, 500, 502, 503, 529):
            logger.warning("claude_transient", status=status)
            raise _Transient(str(exc)) from exc
        logger.error("claude_error", error=str(exc))
        raise ExternalServiceError("Claude request failed.", code="CLAUDE_ERROR") from exc

    text_parts: list[str] = []
    tool_calls: list[dict] = []
    for block in resp.content:
        if block.type == "text":
            text_parts.append(block.text)
        elif block.type == "tool_use":
            tool_calls.append({"id": block.id, "name": block.name, "input": block.input})

    return LLMResult(
        text="".join(text_parts).strip(),
        input_tokens=resp.usage.input_tokens,
        output_tokens=resp.usage.output_tokens,
        stop_reason=resp.stop_reason,
        raw_tool_calls=tool_calls,
    )


async def complete_json(
    *, system: str, prompt: str, model: str | None = None, temperature: float = 0.0
) -> dict[str, Any]:
    """Ask Claude for a strict JSON object and parse it robustly."""
    result = await complete(
        system=system + "\n\nRespond with a single valid JSON object and nothing else.",
        messages=[{"role": "user", "content": prompt}],
        model=model or settings.CLAUDE_FAST_MODEL,
        temperature=temperature,
        max_tokens=1024,
    )
    text = result.text
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ExternalServiceError("Claude did not return JSON.", code="CLAUDE_BAD_JSON")
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ExternalServiceError("Failed to parse Claude JSON.", code="CLAUDE_BAD_JSON") from exc


async def stream(
    *,
    system: str,
    messages: list[dict[str, Any]],
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float = 0.3,
):
    """Async generator yielding text deltas for streaming responses (SSE/WebSocket)."""
    client = get_client()
    async with client.messages.stream(
        model=model or settings.CLAUDE_MODEL,
        max_tokens=max_tokens or settings.CLAUDE_MAX_TOKENS,
        temperature=temperature,
        system=system,
        messages=messages,
    ) as stream_resp:
        async for text in stream_resp.text_stream:
            yield text
