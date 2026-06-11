"""Celery application + beat schedule."""
from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "omniassist",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_max_tasks_per_child=200,
    task_default_retry_delay=30,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)

celery_app.conf.beat_schedule = {
    "rollup-analytics-hourly": {
        "task": "app.workers.tasks.rollup_analytics",
        "schedule": crontab(minute=0),
    },
    "check-sla-every-5-min": {
        "task": "app.workers.tasks.check_sla_breaches",
        "schedule": crontab(minute="*/5"),
    },
    "purge-expired-sessions-daily": {
        "task": "app.workers.tasks.purge_expired_sessions",
        "schedule": crontab(hour=3, minute=0),
    },
}
