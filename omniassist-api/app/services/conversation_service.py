"""Conversation engine — orchestrates inbound messages through the AI agents and
applies side effects (persistence, tickets, handoff, leads, notifications, sentiment).

Shared by the website inbox API and all channel webhooks (WhatsApp / Email / Voice).
"""
from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.graphs.sales_graph import run_sales_agent
from app.ai.graphs.state import AgentResult
from app.ai.graphs.support_graph import run_support_agent
from app.core.config import settings
from app.core.logging import get_logger
from app.models.agent import AgentRun, AiAgent
from app.models.conversation import Contact, Conversation, Message
from app.models.enums import (
    AgentType,
    Channel,
    ConversationStatus,
    NotificationChannel,
    Priority,
    SenderType,
)
from app.models.ops import SentimentRecord
from app.services.lead_service import LeadService
from app.services.notification_service import notify
from app.services.ticket_service import TicketService

logger = get_logger("conversation")

_TICKET_INTENTS = {"billing_issue", "refund", "complaint", "bug", "account_issue"}


class ConversationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ---------- contact / conversation resolution ----------
    async def resolve_contact(
        self, org_id: uuid.UUID, *, name: str, email: str | None = None,
        phone: str | None = None, external_id: str | None = None,
    ) -> Contact:
        query = select(Contact).where(Contact.org_id == org_id)
        if email:
            existing = (
                await self.db.execute(query.where(Contact.email == email))
            ).scalar_one_or_none()
            if existing:
                return existing
        if phone:
            existing = (
                await self.db.execute(query.where(Contact.phone == phone))
            ).scalar_one_or_none()
            if existing:
                return existing
        contact = Contact(
            org_id=org_id, name=name, email=email, phone=phone, external_id=external_id
        )
        self.db.add(contact)
        await self.db.flush()
        return contact

    async def resolve_conversation(
        self, org_id: uuid.UUID, contact: Contact, channel: Channel,
        external_ref: str | None = None,
    ) -> Conversation:
        if external_ref:
            existing = (
                await self.db.execute(
                    select(Conversation).where(
                        Conversation.org_id == org_id,
                        Conversation.external_ref == external_ref,
                        Conversation.status != ConversationStatus.RESOLVED,
                    )
                )
            ).scalar_one_or_none()
            if existing:
                return existing
        conversation = Conversation(
            org_id=org_id, contact_id=contact.id, channel=channel,
            status=ConversationStatus.OPEN, external_ref=external_ref,
        )
        self.db.add(conversation)
        await self.db.flush()
        return conversation

    async def _agent_config(self, org_id: uuid.UUID, agent_type: AgentType) -> dict:
        agent = (
            await self.db.execute(
                select(AiAgent).where(
                    AiAgent.org_id == org_id, AiAgent.type == agent_type,
                    AiAgent.enabled.is_(True),
                )
            )
        ).scalar_one_or_none()
        if not agent:
            return {"system_prompt": "You are a helpful assistant.", "confidence_threshold": 70}
        return {
            "system_prompt": agent.system_prompt,
            "model": agent.model,
            "temperature": agent.temperature,
            "confidence_threshold": agent.confidence_threshold,
        }

    async def _render_history(self, conversation_id: uuid.UUID, limit: int = 10) -> str:
        rows = (
            (
                await self.db.execute(
                    select(Message)
                    .where(Message.conversation_id == conversation_id)
                    .order_by(Message.created_at.desc())
                    .limit(limit)
                )
            )
            .scalars()
            .all()
        )
        rows = list(reversed(rows))
        labels = {
            SenderType.CONTACT: "Customer", SenderType.AI: "AI",
            SenderType.AGENT: "Agent", SenderType.SYSTEM: "System",
        }
        return "\n".join(f"{labels.get(m.sender_type, '?')}: {m.content}" for m in rows)

    # ---------- main entry ----------
    async def handle_inbound(
        self,
        *,
        org_id: uuid.UUID,
        conversation: Conversation,
        text: str,
        author_name: str | None = None,
        run_ai: bool = True,
    ) -> tuple[Message, Message | None]:
        """Persist an inbound customer message and (optionally) generate an AI reply."""
        inbound = Message(
            org_id=org_id, conversation_id=conversation.id, sender_type=SenderType.CONTACT,
            author_name=author_name or conversation.contact.name if conversation.contact else None,
            content=text,
        )
        self.db.add(inbound)
        conversation.last_message_at = datetime.now(UTC)
        conversation.unread_count += 1
        await self.db.flush()

        if not run_ai or conversation.status == ConversationStatus.PENDING:
            # Conversation is with a human — don't auto-reply.
            return inbound, None

        history = await self._render_history(conversation.id)
        result = await self._run_agent(org_id, conversation, text, history)

        ai_message = Message(
            org_id=org_id, conversation_id=conversation.id, sender_type=SenderType.AI,
            content=result.reply, confidence=result.confidence * 100,
            sources=result.sources, language=result.language,
        )
        self.db.add(ai_message)
        conversation.language = result.language or conversation.language
        conversation.sentiment = result.sentiment.get("label") if result.sentiment else None
        conversation.last_message_at = datetime.now(UTC)

        await self._persist_run(org_id, conversation, result)
        await self._apply_side_effects(org_id, conversation, result)
        await self.db.flush()
        return inbound, ai_message

    # Handoff triggers (no-LLM mode) — matches the configured business rules.
    # Phrases that signal "I want a human" — avoid bare "agent" so product names
    # like "WhatsApp agent" / "Sales agent" don't trigger a false handoff.
    _HUMAN_WORDS = ("human", "real person", "speak to someone", "talk to a person",
                    "talk to someone", "live agent", "human agent", "real agent",
                    "speak to an agent", "talk to an agent", "speak to a human",
                    "talk to a human", "representative", "connect me to someone")
    _REFUND_WORDS = ("refund", "money back", "double charge", "chargeback", "overcharged")
    _LEGAL_WORDS = ("legal", "lawyer", "gdpr", "lawsuit", "compliance", "data breach")

    async def _grounded_agent(
        self, org_id: uuid.UUID, conversation: Conversation, text: str, history: str
    ) -> AgentResult:
        """No-LLM agent: answer from the KB (Product Expert) and apply handoff rules.
        Used when no Anthropic key is configured so the AI inbox still works."""
        from app.ai.graphs.ops_agents import run_product_expert

        res = await run_product_expert(self.db, org_id, text, history=history, use_kb=True)
        low = text.lower()
        wants_human = any(w in low for w in self._HUMAN_WORDS)
        is_refund = any(w in low for w in self._REFUND_WORDS)
        is_legal = any(w in low for w in self._LEGAL_WORDS)
        threshold = 0.7

        intent = ("refund" if is_refund else "complaint" if is_legal
                  else "billing_issue" if "billing" in low or "invoice" in low else "other")
        handoff = wants_human or is_refund or is_legal or res.confidence < threshold
        reason = (
            "Customer requested a human" if wants_human
            else "Refund approval required" if is_refund
            else "Legal/compliance issue" if is_legal
            else "Low answer confidence" if res.confidence < threshold
            else None
        )
        return AgentResult(
            reply=res.reply, confidence=res.confidence, handoff=handoff,
            handoff_reason=reason, intent=intent, language="English", sentiment={},
            sources=res.sources, suggested_actions=[],
            input_tokens=res.input_tokens, output_tokens=res.output_tokens,
            tools_used=["kb_search"],
        )

    async def _run_agent(
        self, org_id: uuid.UUID, conversation: Conversation, text: str, history: str
    ) -> AgentResult:
        # No-LLM fallback so the inbox works without a paid Anthropic key.
        if not settings.ANTHROPIC_API_KEY:
            return await self._grounded_agent(org_id, conversation, text, history)

        # Decide which agent: a quick classify happens inside each graph; we pick by a
        # cheap heuristic on the conversation's channel + prior sales flag.
        from app.ai import intent as intent_mod

        signal = await intent_mod.classify(text, history)
        if signal["is_sales"]:
            cfg = await self._agent_config(org_id, AgentType.SALES)
            return await run_sales_agent(
                org_id=str(org_id), conversation_id=str(conversation.id),
                message=text, history=history, agent_config=cfg,
            )
        cfg = await self._agent_config(org_id, AgentType.SUPPORT)
        return await run_support_agent(
            org_id=str(org_id), conversation_id=str(conversation.id),
            message=text, history=history, agent_config=cfg,
        )

    async def _persist_run(
        self, org_id: uuid.UUID, conversation: Conversation, result: AgentResult
    ) -> None:
        self.db.add(
            AgentRun(
                org_id=org_id, conversation_id=conversation.id, intent=result.intent,
                confidence=result.confidence, handed_off=result.handoff,
                input_tokens=result.input_tokens, output_tokens=result.output_tokens,
                latency_ms=int(time.perf_counter() * 0),  # set by caller timing if needed
                tools_used=result.tools_used,
            )
        )
        if result.sentiment:
            self.db.add(
                SentimentRecord(
                    org_id=org_id, conversation_id=conversation.id,
                    label=result.sentiment.get("label", "neutral"),
                    score=result.sentiment.get("score", 0.0),
                    escalate=result.sentiment.get("escalate", False),
                )
            )

    async def _apply_side_effects(
        self, org_id: uuid.UUID, conversation: Conversation, result: AgentResult
    ) -> None:
        # 1) Ticket creation for trackable support intents.
        if result.intent in _TICKET_INTENTS and conversation.channel != Channel.VOICE:
            priority = Priority.HIGH if result.intent in {"billing_issue", "refund"} else Priority.MEDIUM
            ticket = await TicketService(self.db).create(
                org_id=org_id,
                subject=f"{result.intent.replace('_', ' ').title()} — {conversation.contact.name}"
                if conversation.contact else result.intent,
                priority=priority, channel=Channel(conversation.channel),
                conversation_id=conversation.id,
                requester_id=conversation.contact_id, sentiment=result.intent,
            )
            conversation.meta = {**conversation.meta, "ticket_number": ticket.number}

        # 2) Lead creation for sales intent.
        for action in result.suggested_actions:
            if action.get("tool") == "qualify_lead" and conversation.contact:
                await LeadService(self.db).upsert_from_conversation(
                    org_id=org_id, contact=conversation.contact,
                    conversation=conversation, qualification=action.get("input", {}),
                )

        # 3) Handoff → pending + notify.
        if result.handoff:
            conversation.status = ConversationStatus.PENDING
            conversation.ai_handled = False
            self.db.add(
                Message(
                    org_id=org_id, conversation_id=conversation.id,
                    sender_type=SenderType.SYSTEM,
                    content=f"AI handed off to a human — {result.handoff_reason or 'escalation'}.",
                )
            )
            await notify(
                self.db, org_id=org_id, type_="handoff",
                title="Handoff requested",
                body=f"{conversation.contact.name if conversation.contact else 'A customer'} "
                f"needs a human on {conversation.channel}. Reason: {result.handoff_reason}.",
                payload={"conversation_id": str(conversation.id)},
                channels=[NotificationChannel.IN_APP, NotificationChannel.SLACK],
            )

    async def post_agent_message(
        self, org_id: uuid.UUID, conversation: Conversation, *, text: str,
        author_name: str, author_id: uuid.UUID,
    ) -> Message:
        """A human agent replies in a conversation (used by the inbox API)."""
        msg = Message(
            org_id=org_id, conversation_id=conversation.id, sender_type=SenderType.AGENT,
            author_name=author_name, sender_id=author_id, content=text,
            delivery_status="sent",
        )
        self.db.add(msg)
        conversation.last_message_at = datetime.now(UTC)
        await self.db.flush()
        return msg
