"""Ticket lifecycle: creation, assignment, SLA, escalation, resolution, comments."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.enums import Channel, Priority, TicketStatus
from app.models.ticket import Ticket, TicketComment
from app.services.audit_service import record_audit

logger = get_logger("tickets")

# SLA first-response targets per priority (minutes).
SLA_TARGETS = {
    Priority.URGENT: 15,
    Priority.HIGH: 60,
    Priority.MEDIUM: 240,
    Priority.LOW: 1440,
}


class TicketService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _next_number(self, org_id: uuid.UUID) -> int:
        current = (
            await self.db.execute(
                select(func.coalesce(func.max(Ticket.number), 1000)).where(
                    Ticket.org_id == org_id
                )
            )
        ).scalar_one()
        return int(current) + 1

    async def create(
        self,
        *,
        org_id: uuid.UUID,
        subject: str,
        priority: Priority = Priority.MEDIUM,
        channel: Channel = Channel.WEB,
        conversation_id: uuid.UUID | None = None,
        requester_id: uuid.UUID | None = None,
        tags: list[str] | None = None,
        sentiment: str | None = None,
        actor_id: uuid.UUID | None = None,
    ) -> Ticket:
        sla_minutes = SLA_TARGETS.get(Priority(priority), 240)
        ticket = Ticket(
            org_id=org_id,
            number=await self._next_number(org_id),
            subject=subject[:255],
            priority=priority,
            channel=channel,
            status=TicketStatus.OPEN,
            conversation_id=conversation_id,
            requester_id=requester_id,
            tags=tags or [],
            sentiment=sentiment,
            sla_due_at=datetime.now(UTC) + timedelta(minutes=sla_minutes),
        )
        self.db.add(ticket)
        await self.db.flush()
        await record_audit(
            self.db,
            org_id=org_id,
            actor_id=actor_id,
            action="created ticket",
            resource_type="ticket",
            resource_id=f"#{ticket.number}",
            detail=subject[:120],
        )
        logger.info("ticket_created", org_id=str(org_id), number=ticket.number)
        return ticket

    async def get(self, org_id: uuid.UUID, ticket_id: uuid.UUID) -> Ticket:
        ticket = await self.db.get(Ticket, ticket_id)
        if not ticket or ticket.org_id != org_id:
            raise NotFoundError("Ticket not found.")
        return ticket

    async def assign(
        self, org_id: uuid.UUID, ticket_id: uuid.UUID, assignee_id: uuid.UUID | None,
        actor_id: uuid.UUID,
    ) -> Ticket:
        ticket = await self.get(org_id, ticket_id)
        ticket.assignee_id = assignee_id
        if ticket.status == TicketStatus.OPEN and assignee_id:
            ticket.status = TicketStatus.IN_PROGRESS
        await record_audit(
            self.db, org_id=org_id, actor_id=actor_id, action="assigned ticket",
            resource_type="ticket", resource_id=f"#{ticket.number}",
            detail=str(assignee_id) if assignee_id else "unassigned",
        )
        return ticket

    async def update_status(
        self, org_id: uuid.UUID, ticket_id: uuid.UUID, status: TicketStatus, actor_id: uuid.UUID
    ) -> Ticket:
        ticket = await self.get(org_id, ticket_id)
        previous = ticket.status
        ticket.status = status
        if status in (TicketStatus.RESOLVED, TicketStatus.CLOSED) and not ticket.resolved_at:
            ticket.resolved_at = datetime.now(UTC)
        await record_audit(
            self.db, org_id=org_id, actor_id=actor_id, action="updated ticket status",
            resource_type="ticket", resource_id=f"#{ticket.number}",
            diff={"from": previous, "to": status},
        )
        return ticket

    async def mark_first_response(self, ticket: Ticket) -> None:
        if ticket.first_response_at is None:
            now = datetime.now(UTC)
            ticket.first_response_at = now
            if ticket.sla_due_at and now > ticket.sla_due_at:
                ticket.sla_breached = True

    async def add_comment(
        self, org_id: uuid.UUID, ticket_id: uuid.UUID, *, body: str, author_id: uuid.UUID,
        is_internal: bool = True,
    ) -> TicketComment:
        ticket = await self.get(org_id, ticket_id)
        comment = TicketComment(
            org_id=org_id, ticket_id=ticket.id, author_id=author_id,
            body=body, is_internal=is_internal,
        )
        self.db.add(comment)
        await self.db.flush()
        return comment
