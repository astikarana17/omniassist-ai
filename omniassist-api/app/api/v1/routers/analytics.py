"""Analytics routes — live KPIs and time series."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select

from app.core.deps import CurrentContext, DbSession, require_permission
from app.core.permissions import Permission
from app.models.agent import AgentRun
from app.models.conversation import Conversation
from app.models.enums import ConversationStatus, LeadStage, TicketStatus
from app.models.lead import Lead
from app.models.ops import Feedback
from app.models.ticket import Ticket
from app.schemas.domain import AnalyticsOverview

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
async def overview(
    ctx: CurrentContext,
    db: DbSession,
    days: int = Query(30, ge=1, le=365),
    _: object = Depends(require_permission(Permission.ANALYTICS_READ)),
) -> AnalyticsOverview:
    org = ctx.org_id
    since = datetime.now(UTC) - timedelta(days=days)

    total_runs = (
        await db.execute(
            select(func.count()).select_from(AgentRun).where(
                AgentRun.org_id == org, AgentRun.created_at >= since
            )
        )
    ).scalar_one()
    handed_off = (
        await db.execute(
            select(func.count()).select_from(AgentRun).where(
                AgentRun.org_id == org, AgentRun.created_at >= since,
                AgentRun.handed_off.is_(True),
            )
        )
    ).scalar_one()
    deflection = round((1 - handed_off / total_runs) * 100, 1) if total_runs else 0.0

    csat_avg = (
        await db.execute(
            select(func.avg(Feedback.rating)).where(
                Feedback.org_id == org, Feedback.type == "csat", Feedback.created_at >= since
            )
        )
    ).scalar_one()

    frt = (
        await db.execute(
            select(func.avg(func.extract("epoch", Ticket.first_response_at - Ticket.created_at)))
            .where(Ticket.org_id == org, Ticket.first_response_at.isnot(None),
                   Ticket.created_at >= since)
        )
    ).scalar_one()

    open_conv = (
        await db.execute(
            select(func.count()).select_from(Conversation).where(
                Conversation.org_id == org, Conversation.status == ConversationStatus.OPEN
            )
        )
    ).scalar_one()
    tickets_open = (
        await db.execute(
            select(func.count()).select_from(Ticket).where(
                Ticket.org_id == org,
                Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]),
            )
        )
    ).scalar_one()
    tickets_resolved = (
        await db.execute(
            select(func.count()).select_from(Ticket).where(
                Ticket.org_id == org,
                Ticket.status.in_([TicketStatus.RESOLVED, TicketStatus.CLOSED]),
                Ticket.resolved_at >= since,
            )
        )
    ).scalar_one()
    hot_leads = (
        await db.execute(
            select(func.count()).select_from(Lead).where(Lead.org_id == org, Lead.score >= 85)
        )
    ).scalar_one()
    revenue = (
        await db.execute(
            select(func.coalesce(func.sum(Lead.value), 0)).where(
                Lead.org_id == org, Lead.stage == LeadStage.WON
            )
        )
    ).scalar_one()

    return AnalyticsOverview(
        deflection_rate=deflection,
        csat=round(float(csat_avg), 2) if csat_avg else 0.0,
        avg_first_response_seconds=round(float(frt), 1) if frt else 0.0,
        open_conversations=int(open_conv),
        tickets_open=int(tickets_open),
        tickets_resolved=int(tickets_resolved),
        hot_leads=int(hot_leads),
        revenue_influenced=float(revenue),
    )


@router.get("/timeseries")
async def timeseries(
    ctx: CurrentContext,
    db: DbSession,
    days: int = Query(30, ge=1, le=90),
    _: object = Depends(require_permission(Permission.ANALYTICS_READ)),
) -> dict:
    since = datetime.now(UTC) - timedelta(days=days)
    rows = (
        await db.execute(
            select(
                func.date_trunc("day", Conversation.created_at).label("day"),
                Conversation.channel,
                func.count().label("count"),
            )
            .where(Conversation.org_id == ctx.org_id, Conversation.created_at >= since)
            .group_by("day", Conversation.channel)
            .order_by("day")
        )
    ).all()
    series: dict[str, dict[str, int]] = {}
    for day, channel, count in rows:
        key = day.date().isoformat()
        series.setdefault(key, {}).update({channel: int(count)})
    return {"data": [{"date": k, **v} for k, v in sorted(series.items())], "error": None}
