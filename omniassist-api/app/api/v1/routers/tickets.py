"""Ticket routes."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query

from app.core.deps import CurrentContext, DbSession, PaginationDep, require_permission
from app.core.exceptions import NotFoundError
from app.core.permissions import Permission
from app.models.ticket import Ticket
from app.repositories.base import TenantRepository
from app.schemas.common import MessageResponse, Page, PageMeta
from app.schemas.domain import (
    CommentRequest,
    TicketCreateRequest,
    TicketOut,
    TicketSummaryOut,
    TicketUpdateRequest,
)
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("", response_model=Page[TicketOut])
async def list_tickets(
    ctx: CurrentContext,
    db: DbSession,
    page: PaginationDep,
    status: str | None = Query(None),
    priority: str | None = Query(None),
    assignee_id: uuid.UUID | None = Query(None),
    _: object = Depends(require_permission(Permission.TICKET_READ)),
) -> Page[TicketOut]:
    repo = TenantRepository(db, Ticket)
    filters = []
    if status:
        filters.append(Ticket.status == status)
    if priority:
        filters.append(Ticket.priority == priority)
    if assignee_id:
        filters.append(Ticket.assignee_id == assignee_id)
    rows, total = await repo.list(
        ctx.org_id, limit=page.limit, offset=page.offset, filters=filters,
        order_by=Ticket.created_at.desc(),
    )
    return Page(
        items=[TicketOut.model_validate(t) for t in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.post("", response_model=TicketOut, status_code=201)
async def create_ticket(
    payload: TicketCreateRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.TICKET_WRITE)),
) -> TicketOut:
    ticket = await TicketService(db).create(
        org_id=ctx.org_id, subject=payload.subject, priority=payload.priority,
        channel=payload.channel, requester_id=payload.requester_id, tags=payload.tags,
        actor_id=ctx.user.id,
    )
    return TicketOut.model_validate(ticket)


@router.get("/{ticket_id}", response_model=TicketOut)
async def get_ticket(
    ticket_id: uuid.UUID,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.TICKET_READ)),
) -> TicketOut:
    ticket = await TicketService(db).get(ctx.org_id, ticket_id)
    return TicketOut.model_validate(ticket)


@router.patch("/{ticket_id}", response_model=TicketOut)
async def update_ticket(
    ticket_id: uuid.UUID,
    payload: TicketUpdateRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.TICKET_WRITE)),
) -> TicketOut:
    svc = TicketService(db)
    ticket = await svc.get(ctx.org_id, ticket_id)
    if payload.status is not None:
        ticket = await svc.update_status(ctx.org_id, ticket_id, payload.status, ctx.user.id)
    if payload.assignee_id is not None:
        ticket = await svc.assign(ctx.org_id, ticket_id, payload.assignee_id, ctx.user.id)
    if payload.priority is not None:
        ticket.priority = payload.priority
    if payload.tags is not None:
        ticket.tags = payload.tags
    return TicketOut.model_validate(ticket)


@router.post("/{ticket_id}/comments", response_model=MessageResponse, status_code=201)
async def add_comment(
    ticket_id: uuid.UUID,
    payload: CommentRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.TICKET_WRITE)),
) -> MessageResponse:
    await TicketService(db).add_comment(
        ctx.org_id, ticket_id, body=payload.body, author_id=ctx.user.id,
        is_internal=payload.is_internal,
    )
    return MessageResponse(message="Comment added.")


@router.get("/{ticket_id}/summary", response_model=TicketSummaryOut)
async def get_summary(
    ticket_id: uuid.UUID,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.TICKET_READ)),
) -> TicketSummaryOut:
    ticket = await TicketService(db).get(ctx.org_id, ticket_id)
    if ticket.summary is None:
        raise NotFoundError("No AI summary yet. Trigger generation on resolution.")
    return TicketSummaryOut.model_validate(ticket.summary)
