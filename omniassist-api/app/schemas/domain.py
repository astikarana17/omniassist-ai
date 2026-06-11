"""Request/response schemas for conversations, tickets, leads, KB, analytics, etc."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import (
    Channel,
    ConversationStatus,
    LeadStage,
    Priority,
    TicketStatus,
)
from app.schemas.common import ORMModel


# ---------- Conversations ----------
class ContactOut(ORMModel):
    id: uuid.UUID
    name: str
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    avatar_url: str | None = None


class MessageOut(ORMModel):
    id: uuid.UUID
    sender_type: str
    author_name: str | None = None
    content: str
    confidence: float | None = None
    sources: list = []
    attachments: list = []
    language: str | None = None
    created_at: datetime


class ConversationOut(ORMModel):
    id: uuid.UUID
    channel: str
    status: str
    subject: str | None = None
    language: str
    sentiment: str | None = None
    ai_handled: bool
    unread_count: int
    last_message_at: datetime | None = None
    contact: ContactOut


class ConversationDetail(ConversationOut):
    messages: list[MessageOut] = []


class PostMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)


class WidgetMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)
    contact_name: str = Field(default="Visitor", max_length=160)
    contact_email: EmailStr | None = None
    conversation_id: uuid.UUID | None = None


class StartConversationRequest(BaseModel):
    contact_name: str = Field(min_length=1, max_length=160)
    contact_email: EmailStr | None = None
    channel: Channel = Channel.WEB
    content: str = Field(min_length=1, max_length=8000)


# ---------- Tickets ----------
class TicketOut(ORMModel):
    id: uuid.UUID
    number: int
    subject: str
    status: str
    priority: str
    channel: str
    sentiment: str | None = None
    tags: list[str] = []
    assignee_id: uuid.UUID | None = None
    requester_id: uuid.UUID | None = None
    sla_due_at: datetime | None = None
    sla_breached: bool
    created_at: datetime
    updated_at: datetime


class TicketCreateRequest(BaseModel):
    subject: str = Field(min_length=2, max_length=255)
    priority: Priority = Priority.MEDIUM
    channel: Channel = Channel.WEB
    tags: list[str] = []
    requester_id: uuid.UUID | None = None


class TicketUpdateRequest(BaseModel):
    status: TicketStatus | None = None
    priority: Priority | None = None
    assignee_id: uuid.UUID | None = None
    tags: list[str] | None = None


class CommentRequest(BaseModel):
    body: str = Field(min_length=1, max_length=8000)
    is_internal: bool = True


class TicketSummaryOut(ORMModel):
    summary: str
    resolution: str | None = None
    next_steps: list[str] = []


# ---------- Leads ----------
class LeadOut(ORMModel):
    id: uuid.UUID
    name: str
    company: str | None = None
    email: str | None = None
    stage: str
    score: int
    value: float
    source: str
    owner_id: uuid.UUID | None = None
    next_action: str | None = None
    next_action_due: datetime | None = None
    created_at: datetime


class LeadCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    company: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    value: float = 0
    source: Channel = Channel.WEB
    stage: LeadStage = LeadStage.NEW


class LeadStageRequest(BaseModel):
    stage: LeadStage


class FollowupRequest(BaseModel):
    when: datetime
    action: str = Field(min_length=2, max_length=255)


# ---------- Knowledge base ----------
class KbDocumentOut(ORMModel):
    id: uuid.UUID
    title: str
    source_type: str
    status: str
    chunk_count: int
    size_bytes: int
    error: str | None = None
    created_at: datetime
    updated_at: datetime


class CrawlRequest(BaseModel):
    url: str = Field(pattern=r"^https?://.+")
    title: str | None = None


class RetrievalTestRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunkOut(BaseModel):
    title: str
    text: str
    score: float


# ---------- Members ----------
class MemberOut(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    role: str
    status: str
    created_at: datetime
    name: str | None = None
    email: str | None = None
    avatar_url: str | None = None


class InviteRequest(BaseModel):
    email: EmailStr
    role: str = "support_agent"


class RoleChangeRequest(BaseModel):
    role: str


# ---------- Notifications ----------
class NotificationOut(ORMModel):
    id: uuid.UUID
    type: str
    title: str
    body: str | None = None
    read: bool
    created_at: datetime


# ---------- Audit ----------
class AuditOut(ORMModel):
    id: uuid.UUID
    actor_name: str | None = None
    action: str
    resource_type: str
    resource_id: str | None = None
    detail: str | None = None
    ip_address: str | None = None
    created_at: datetime

    @field_validator("ip_address", "resource_id", mode="before")
    @classmethod
    def _coerce_str(cls, v: object) -> str | None:
        return str(v) if v is not None else None


# ---------- Agents ----------
class AgentOut(ORMModel):
    id: uuid.UUID
    type: str
    name: str
    system_prompt: str
    model: str
    temperature: float
    tone: str
    confidence_threshold: int
    tools: list
    languages: list
    enabled: bool


class AgentUpdateRequest(BaseModel):
    name: str | None = None
    system_prompt: str | None = None
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0, le=1)
    tone: str | None = None
    confidence_threshold: int | None = Field(default=None, ge=0, le=100)
    tools: list | None = None
    languages: list | None = None
    enabled: bool | None = None


class AgentTestRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


# ---------- Analytics ----------
class AnalyticsOverview(BaseModel):
    deflection_rate: float
    csat: float
    avg_first_response_seconds: float
    open_conversations: int
    tickets_open: int
    tickets_resolved: int
    hot_leads: int
    revenue_influenced: float


# ---------- Conversation status update ----------
class StatusUpdateRequest(BaseModel):
    status: ConversationStatus
