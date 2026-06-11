"""Structured JSON logging with request-scoped context."""
from __future__ import annotations

import logging
import sys
from contextvars import ContextVar

import structlog

# Request-scoped context propagated into every log line.
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")
org_id_ctx: ContextVar[str] = ContextVar("org_id", default="-")
user_id_ctx: ContextVar[str] = ContextVar("user_id", default="-")


def _inject_context(_logger, _name, event_dict):
    event_dict["request_id"] = request_id_ctx.get()
    event_dict["org_id"] = org_id_ctx.get()
    event_dict["user_id"] = user_id_ctx.get()
    return event_dict


def configure_logging(level: str = "INFO", json_logs: bool = True) -> None:
    """Configure structlog + stdlib logging for the whole process."""
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        _inject_context,
        structlog.processors.StackInfoRenderer(),
    ]

    renderer = (
        structlog.processors.JSONRenderer()
        if json_logs
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[*shared_processors, structlog.processors.format_exc_info, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )
    for noisy in ("uvicorn.access", "sqlalchemy.engine.Engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
