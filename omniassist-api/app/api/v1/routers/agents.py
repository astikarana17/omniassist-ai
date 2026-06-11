"""AI agent configuration + sandbox routes."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.ai.graphs.sales_graph import run_sales_agent
from app.ai.graphs.support_graph import run_support_agent
from app.core.config import settings
from app.core.deps import CurrentContext, DbSession, require_permission
from app.core.exceptions import NotFoundError
from app.core.permissions import Permission
from app.models.agent import AiAgent
from app.models.enums import AgentType
from app.schemas.domain import AgentOut, AgentTestRequest, AgentUpdateRequest

router = APIRouter(prefix="/agents", tags=["AI Agents"])


@router.get("", response_model=list[AgentOut])
async def list_agents(
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.AGENT_READ)),
) -> list[AgentOut]:
    rows = (
        (await db.execute(select(AiAgent).where(AiAgent.org_id == ctx.org_id))).scalars().all()
    )
    return [AgentOut.model_validate(a) for a in rows]


@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent(
    agent_id: uuid.UUID,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.AGENT_READ)),
) -> AgentOut:
    agent = await db.get(AiAgent, agent_id)
    if not agent or agent.org_id != ctx.org_id:
        raise NotFoundError("Agent not found.")
    return AgentOut.model_validate(agent)


@router.patch("/{agent_id}", response_model=AgentOut)
async def update_agent(
    agent_id: uuid.UUID,
    payload: AgentUpdateRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.AGENT_WRITE)),
) -> AgentOut:
    agent = await db.get(AiAgent, agent_id)
    if not agent or agent.org_id != ctx.org_id:
        raise NotFoundError("Agent not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)
    return AgentOut.model_validate(agent)


@router.post("/{agent_id}/test")
async def test_agent(
    agent_id: uuid.UUID,
    payload: AgentTestRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.AGENT_READ)),
) -> dict:
    agent = await db.get(AiAgent, agent_id)
    if not agent or agent.org_id != ctx.org_id:
        raise NotFoundError("Agent not found.")

    # Without a Claude key, run the same grounded (OpenRouter/KB) engine the live
    # inbox uses, so the sandbox returns real RAG-grounded answers + handoff.
    if not settings.ANTHROPIC_API_KEY:
        from app.ai.graphs.ops_agents import run_product_expert

        res = await run_product_expert(db, ctx.org_id, payload.message, use_kb=True)
        low = payload.message.lower()
        human = ("human", "real person", "speak to someone", "talk to a person",
                 "talk to someone", "live agent", "human agent", "representative")
        refund = ("refund", "money back", "double charge", "chargeback", "overcharged")
        legal = ("legal", "lawyer", "gdpr", "lawsuit", "compliance", "data breach")
        wants_human = any(w in low for w in human)
        is_refund = any(w in low for w in refund)
        is_legal = any(w in low for w in legal)
        threshold = (agent.confidence_threshold or 70) / 100
        handoff = wants_human or is_refund or is_legal or res.confidence < threshold
        intent = (
            "refund" if is_refund else "complaint" if is_legal
            else "billing_issue" if ("billing" in low or "invoice" in low)
            else "qualify_lead" if agent.type == AgentType.SALES else "general"
        )
        return {
            "data": {
                "reply": res.reply, "confidence": res.confidence, "handoff": handoff,
                "intent": intent, "language": "English", "sources": res.sources,
                "sentiment": {},
            },
            "error": None,
        }

    cfg = {
        "system_prompt": agent.system_prompt, "model": agent.model,
        "temperature": agent.temperature, "confidence_threshold": agent.confidence_threshold,
    }
    runner = run_sales_agent if agent.type == AgentType.SALES else run_support_agent
    result = await runner(
        org_id=str(ctx.org_id), conversation_id="sandbox",
        message=payload.message, history="", agent_config=cfg,
    )
    return {
        "data": {
            "reply": result.reply,
            "confidence": result.confidence,
            "handoff": result.handoff,
            "intent": result.intent,
            "language": result.language,
            "sources": result.sources,
            "sentiment": result.sentiment,
        },
        "error": None,
    }
