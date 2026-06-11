"""Slack integration: post operational notifications."""
from __future__ import annotations

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("slack")

_client: WebClient | None = None


def _get() -> WebClient | None:
    global _client
    if not settings.SLACK_BOT_TOKEN:
        return None
    if _client is None:
        _client = WebClient(token=settings.SLACK_BOT_TOKEN)
    return _client


def post_message(text: str, channel: str | None = None) -> bool:
    client = _get()
    if client is None:
        logger.warning("slack_not_configured")
        return False
    try:
        client.chat_postMessage(channel=channel or settings.SLACK_DEFAULT_CHANNEL, text=text)
        return True
    except SlackApiError as exc:
        logger.warning("slack_error", error=str(exc))
        return False
