"""Conversation / inbox routes."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentContext, DbSession, PaginationDep, require_permission
from app.core.permissions import Permission
from app.models.conversation import Conversation, Message
from app.models.enums import ConversationStatus
from app.repositories.base import TenantRepository
from app.schemas.common import MessageResponse, Page, PageMeta
from app.schemas.domain import (
    ConversationDetail,
    ConversationOut,
    MessageOut,
    PostMessageRequest,
    StartConversationRequest,
    StatusUpdateRequest,
)
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


async def _load_detail(db, org_id, conversation_id) -> ConversationDetail:
    from app.core.exceptions import NotFoundError

    conv = (
        await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.contact), selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id, Conversation.org_id == org_id)
            .execution_options(populate_existing=True)  # refresh messages after handle_inbound
        )
    ).scalar_one_or_none()
    if not conv:
        raise NotFoundError("Conversation not found.")
    return ConversationDetail.model_validate(conv)


@router.get("", response_model=Page[ConversationOut])
async def list_conversations(
    ctx: CurrentContext,
    db: DbSession,
    page: PaginationDep,
    channel: str | None = Query(None),
    status: str | None = Query(None),
    _: object = Depends(require_permission(Permission.CONVERSATION_READ)),
) -> Page[ConversationOut]:
    repo = TenantRepository(db, Conversation)
    filters = []
    if channel:
        filters.append(Conversation.channel == channel)
    if status:
        filters.append(Conversation.status == status)
    rows, total = await repo.list(
        ctx.org_id, limit=page.limit, offset=page.offset, filters=filters,
        order_by=Conversation.last_message_at.desc().nullslast(),
    )
    # Eager-load contacts for serialization.
    ids = [c.id for c in rows]
    if ids:
        rows = list(
            (
                await db.execute(
                    select(Conversation)
                    .options(selectinload(Conversation.contact))
                    .where(Conversation.id.in_(ids))
                    .order_by(Conversation.last_message_at.desc().nullslast())
                )
            )
            .scalars()
            .all()
        )
    return Page(
        items=[ConversationOut.model_validate(c) for c in rows],
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(rows) < total),
    )


@router.post("", response_model=ConversationDetail, status_code=201)
async def start_conversation(
    payload: StartConversationRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.CONVERSATION_WRITE)),
) -> ConversationDetail:
    """Start a conversation with an inbound customer message; the AI replies."""
    svc = ConversationService(db)
    contact = await svc.resolve_contact(
        ctx.org_id, name=payload.contact_name, email=payload.contact_email
    )
    conv = await svc.resolve_conversation(ctx.org_id, contact, channel=payload.channel)
    conv.contact = contact  # ensure relationship is loaded for side-effects
    await svc.handle_inbound(
        org_id=ctx.org_id, conversation=conv, text=payload.content, author_name=contact.name
    )
    return await _load_detail(db, ctx.org_id, conv.id)


@router.post("/{conversation_id}/customer", response_model=ConversationDetail)
async def customer_message(
    conversation_id: uuid.UUID,
    payload: PostMessageRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.CONVERSATION_WRITE)),
) -> ConversationDetail:
    """Simulate an inbound customer message on an existing conversation → AI reply."""
    from app.core.exceptions import NotFoundError

    conv = (
        await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.contact), selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id, Conversation.org_id == ctx.org_id)
        )
    ).scalar_one_or_none()
    if not conv:
        raise NotFoundError("Conversation not found.")
    # This is the "test the AI" endpoint — make sure the AI always replies by
    # re-opening a resolved/handed-off conversation before processing.
    if conv.status != ConversationStatus.OPEN:
        conv.status = ConversationStatus.OPEN
        conv.ai_handled = True
    await ConversationService(db).handle_inbound(
        org_id=ctx.org_id, conversation=conv, text=payload.content,
        author_name=conv.contact.name if conv.contact else "Customer",
    )
    return await _load_detail(db, ctx.org_id, conversation_id)


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: uuid.UUID,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.CONVERSATION_READ)),
) -> ConversationDetail:
    conv = (
        await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.contact), selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id, Conversation.org_id == ctx.org_id)
        )
    ).scalar_one_or_none()
    if not conv:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Conversation not found.")
    conv.unread_count = 0
    return ConversationDetail.model_validate(conv)


@router.post("/{conversation_id}/messages", response_model=MessageOut)
async def post_message(
    conversation_id: uuid.UUID,
    payload: PostMessageRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.CONVERSATION_WRITE)),
) -> MessageOut:
    repo = TenantRepository(db, Conversation)
    conv = await repo.get(ctx.org_id, conversation_id)
    if not conv:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Conversation not found.")
    msg = await ConversationService(db).post_agent_message(
        ctx.org_id, conv, text=payload.content, author_name=ctx.user.full_name,
        author_id=ctx.user.id,
    )
    return MessageOut.model_validate(msg)


@router.post("/{conversation_id}/handoff", response_model=MessageResponse)
async def request_handoff(
    conversation_id: uuid.UUID,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.CONVERSATION_HANDOFF)),
) -> MessageResponse:
    repo = TenantRepository(db, Conversation)
    conv = await repo.get(ctx.org_id, conversation_id)
    if not conv:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Conversation not found.")
    conv.status = ConversationStatus.PENDING
    conv.ai_handled = False
    conv.assignee_id = ctx.user.id
    db.add(
        Message(org_id=ctx.org_id, conversation_id=conv.id, sender_type="system",
                content=f"{ctx.user.full_name} took over the conversation.")
    )
    return MessageResponse(message="Conversation handed off.")


@router.post("/{conversation_id}/status", response_model=MessageResponse)
async def update_status(
    conversation_id: uuid.UUID,
    payload: StatusUpdateRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.CONVERSATION_WRITE)),
) -> MessageResponse:
    repo = TenantRepository(db, Conversation)
    conv = await repo.get(ctx.org_id, conversation_id)
    if not conv:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Conversation not found.")
    conv.status = payload.status
    # Resolving a conversation also resolves any open ticket linked to it.
    if payload.status == ConversationStatus.RESOLVED:
        from datetime import UTC, datetime

        from app.models.enums import TicketStatus
        from app.models.ticket import Ticket

        tickets = (
            await db.execute(
                select(Ticket).where(
                    Ticket.org_id == ctx.org_id,
                    Ticket.conversation_id == conv.id,
                    Ticket.status.in_(
                        [TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.PENDING]
                    ),
                )
            )
        ).scalars().all()
        for t in tickets:
            t.status = TicketStatus.RESOLVED
            t.resolved_at = datetime.now(UTC)
    return MessageResponse(message=f"Status set to {payload.status}.")
