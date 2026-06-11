"""Celery tasks: KB ingestion, crawling, emails, Slack, analytics rollups, SLA, summaries."""
from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.ai import summarize
from app.ai.rag import pipeline
from app.core.config import settings
from app.core.logging import get_logger
from app.integrations import email_client, slack_client
from app.models.conversation import Conversation
from app.models.enums import TicketStatus
from app.models.knowledge import KbDocument
from app.models.ops import AnalyticsDaily, Notification
from app.models.ticket import Ticket, TicketSummary
from app.models.user import Session as AuthSession
from app.workers.celery_app import celery_app

logger = get_logger("tasks")

_engine = create_engine(settings.DATABASE_SYNC_URL, pool_pre_ping=True, future=True)
_Session: sessionmaker[Session] = sessionmaker(bind=_engine, expire_on_commit=False)


# ---------------- Knowledge base ----------------
@celery_app.task(bind=True, max_retries=3, name="app.workers.tasks.ingest_kb_document")
def ingest_kb_document(self, doc_id: str, storage_path: str, content_type: str, filename: str):
    from app.core import storage

    try:
        content = storage.read(storage_path)
    except Exception as exc:  # noqa: BLE001
        logger.error("ingest_read_failed", doc_id=doc_id, error=str(exc))
        raise self.retry(exc=exc) from exc
    return pipeline.ingest_document(doc_id, content, content_type, filename)


@celery_app.task(name="app.workers.tasks.crawl_url")
def crawl_url(doc_id: str, url: str):
    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True)
        resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        with _Session() as db:
            doc = db.get(KbDocument, uuid.UUID(doc_id))
            if doc:
                doc.status = "failed"
                doc.error = f"Crawl failed: {exc}"
                db.commit()
        return 0
    return pipeline.ingest_document(doc_id, resp.content, "text/html", url)


@celery_app.task(name="app.workers.tasks.delete_kb_document_vectors")
def delete_kb_document_vectors(org_id: str, doc_id: str):
    pipeline.delete_document_vectors(org_id, doc_id)


# ---------------- Notifications ----------------
@celery_app.task(name="app.workers.tasks.send_email")
def send_email(to: str, subject: str, body: str):
    email_client.send_email(to, subject, body)


@celery_app.task(name="app.workers.tasks.send_slack_notification")
def send_slack_notification(org_id: str, text: str):
    slack_client.post_message(text)


@celery_app.task(name="app.workers.tasks.send_password_reset_email")
def send_password_reset_email(email: str, token: str):
    link = f"{settings.GOOGLE_REDIRECT_URI.rsplit('/api', 1)[0]}/reset-password?token={token}"
    email_client.send_email(
        email,
        "Reset your OmniAssist password",
        f"We received a request to reset your password.\n\nReset link (valid 1 hour):\n{link}\n\n"
        "If you didn't request this, you can ignore this email.",
    )


@celery_app.task(name="app.workers.tasks.send_invite_email")
def send_invite_email(email: str, inviter: str, role: str):
    email_client.send_email(
        email,
        f"{inviter} invited you to OmniAssist",
        f"{inviter} has invited you to join their OmniAssist workspace as a {role}.\n\n"
        "Sign in to accept the invitation.",
    )


# ---------------- Scheduled ----------------
@celery_app.task(name="app.workers.tasks.rollup_analytics")
def rollup_analytics():
    """Aggregate yesterday's conversations/tickets into analytics_daily per org/channel."""
    day = (datetime.now(UTC) - timedelta(days=1)).date()
    start = datetime.combine(day, datetime.min.time(), tzinfo=UTC)
    end = start + timedelta(days=1)
    with _Session() as db:
        rows = db.execute(
            select(Conversation.org_id, Conversation.channel, func.count())
            .where(Conversation.created_at >= start, Conversation.created_at < end)
            .group_by(Conversation.org_id, Conversation.channel)
        ).all()
        for org_id, channel, count in rows:
            existing = db.execute(
                select(AnalyticsDaily).where(
                    AnalyticsDaily.org_id == org_id,
                    AnalyticsDaily.day == day,
                    AnalyticsDaily.channel == channel,
                )
            ).scalar_one_or_none()
            if existing:
                existing.conversations = int(count)
            else:
                db.add(
                    AnalyticsDaily(
                        org_id=org_id, day=day, channel=channel, conversations=int(count)
                    )
                )
        db.commit()
    logger.info("rollup_done", day=str(day))
    return len(rows)


@celery_app.task(name="app.workers.tasks.check_sla_breaches")
def check_sla_breaches():
    """Flag tickets that breached their SLA and notify their org."""
    now = datetime.now(UTC)
    breached = 0
    with _Session() as db:
        tickets = db.execute(
            select(Ticket).where(
                Ticket.sla_due_at.isnot(None),
                Ticket.sla_due_at < now,
                Ticket.sla_breached.is_(False),
                Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]),
            )
        ).scalars().all()
        for t in tickets:
            t.sla_breached = True
            db.add(
                Notification(
                    org_id=t.org_id, type="sla", title="SLA breached",
                    body=f"Ticket #{t.number} ({t.subject}) missed its SLA.",
                    payload={"ticket_id": str(t.id)},
                )
            )
            breached += 1
        db.commit()
    logger.info("sla_check_done", breached=breached)
    return breached


@celery_app.task(name="app.workers.tasks.purge_expired_sessions")
def purge_expired_sessions():
    now = datetime.now(UTC)
    with _Session() as db:
        result = db.execute(delete(AuthSession).where(AuthSession.expires_at < now))
        db.commit()
    return result.rowcount


@celery_app.task(name="app.workers.tasks.summarize_ticket")
def summarize_ticket(ticket_id: str):
    """Generate an AI summary for a ticket from its conversation transcript."""
    with _Session() as db:
        ticket = db.get(Ticket, uuid.UUID(ticket_id))
        if not ticket:
            return None
        transcript = ""
        if ticket.conversation_id:
            from app.models.conversation import Message

            msgs = db.execute(
                select(Message)
                .where(Message.conversation_id == ticket.conversation_id)
                .order_by(Message.created_at)
            ).scalars().all()
            transcript = "\n".join(f"{m.sender_type}: {m.content}" for m in msgs)
        if not transcript:
            transcript = ticket.subject

        result = asyncio.run(summarize.summarize_conversation(transcript))
        existing = db.execute(
            select(TicketSummary).where(TicketSummary.ticket_id == ticket.id)
        ).scalar_one_or_none()
        if existing:
            existing.summary = result["summary"]
            existing.resolution = result["resolution"]
            existing.next_steps = result["next_steps"]
        else:
            db.add(
                TicketSummary(
                    org_id=ticket.org_id, ticket_id=ticket.id, summary=result["summary"],
                    resolution=result["resolution"], next_steps=result["next_steps"],
                    model=settings.CLAUDE_MODEL,
                )
            )
        db.commit()
    return ticket_id
