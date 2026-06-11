"""Request/response schemas for the Business-Operations modules.

Covers: company knowledge (Product Expert), competitor intelligence, onboarding,
customer success + health, knowledge gaps, executive insights, business impact,
meetings, workflow automation and the employee assistant.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


# ===================== Company knowledge =====================
class CompanyProfileIn(BaseModel):
    overview: str | None = None
    mission: str | None = None
    value_props: list = Field(default_factory=list)
    website: str | None = None
    industry: str | None = None
    contact: dict = Field(default_factory=dict)


class CompanyProfileOut(ORMModel):
    id: uuid.UUID
    overview: str | None = None
    mission: str | None = None
    value_props: list = []
    website: str | None = None
    industry: str | None = None
    contact: dict = {}
    updated_at: datetime


class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    slug: str | None = None
    type: str = "product"
    summary: str | None = None
    description: str | None = None
    status: str = "active"


class ProductOut(ORMModel):
    id: uuid.UUID
    name: str
    slug: str | None = None
    type: str
    summary: str | None = None
    description: str | None = None
    status: str
    created_at: datetime


class PricingPlanIn(BaseModel):
    product_id: uuid.UUID | None = None
    name: str = Field(min_length=1, max_length=120)
    price_amount: float | None = None
    currency: str = "USD"
    billing_period: str = "monthly"
    features: list = Field(default_factory=list)
    limits: dict = Field(default_factory=dict)
    is_public: bool = True
    position: int = 0


class PricingPlanOut(ORMModel):
    id: uuid.UUID
    product_id: uuid.UUID | None = None
    name: str
    price_amount: float | None = None
    currency: str
    billing_period: str
    features: list = []
    limits: dict = {}
    is_public: bool
    position: int


class FaqIn(BaseModel):
    product_id: uuid.UUID | None = None
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    is_public: bool = True
    position: int = 0


class FaqOut(ORMModel):
    id: uuid.UUID
    product_id: uuid.UUID | None = None
    question: str
    answer: str
    category: str | None = None
    tags: list[str] = []
    is_public: bool
    position: int


class PolicyIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    type: str = "general"
    body: str | None = None
    effective_date: date | None = None
    is_public: bool = True


class PolicyOut(ORMModel):
    id: uuid.UUID
    title: str
    type: str
    body: str | None = None
    effective_date: date | None = None
    is_public: bool


class RoadmapItemIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: str = "planned"
    quarter: str | None = None
    release_date: date | None = None
    is_public: bool = False
    position: int = 0


class RoadmapItemOut(ORMModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    status: str
    quarter: str | None = None
    release_date: date | None = None
    is_public: bool
    position: int


class CompetitorIn(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    website: str | None = None
    positioning: str | None = None
    strengths: list = Field(default_factory=list)
    weaknesses: list = Field(default_factory=list)


class CompetitorOut(ORMModel):
    id: uuid.UUID
    name: str
    website: str | None = None
    positioning: str | None = None
    strengths: list = []
    weaknesses: list = []
    created_at: datetime


class ComparisonIn(BaseModel):
    competitor_id: uuid.UUID
    dimension: str = Field(min_length=1, max_length=120)
    us_value: str | None = None
    them_value: str | None = None
    advantage: str | None = None  # us | them | parity
    notes: str | None = None


class ComparisonOut(ORMModel):
    id: uuid.UUID
    competitor_id: uuid.UUID
    dimension: str
    us_value: str | None = None
    them_value: str | None = None
    advantage: str | None = None
    notes: str | None = None


# ===================== Onboarding =====================
class OnboardingFlowIn(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    audience: str = "customer"
    is_active: bool = True
    is_default: bool = False


class OnboardingFlowOut(ORMModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    audience: str
    is_active: bool
    is_default: bool


class OnboardingStepIn(BaseModel):
    flow_id: uuid.UUID
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    action_type: str | None = None
    action_url: str | None = None
    position: int = 0
    is_required: bool = True


class OnboardingStepOut(ORMModel):
    id: uuid.UUID
    flow_id: uuid.UUID
    title: str
    description: str | None = None
    action_type: str | None = None
    action_url: str | None = None
    position: int
    is_required: bool


class CompleteStepRequest(BaseModel):
    step_id: uuid.UUID
    skipped: bool = False


class UserOnboardingOut(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    flow_id: uuid.UUID
    status: str
    completion_pct: int
    started_at: datetime | None = None
    completed_at: datetime | None = None


class OnboardingStats(BaseModel):
    total_users: int
    completed: int
    in_progress: int
    not_started: int
    completion_rate: float  # %


# ===================== Customer success + health =====================
class CustomerAccountIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    primary_email: str | None = None
    owner_id: uuid.UUID | None = None
    plan: str | None = None
    mrr: float = 0
    status: str = "active"
    lead_id: uuid.UUID | None = None


class CustomerAccountOut(ORMModel):
    id: uuid.UUID
    name: str
    primary_email: str | None = None
    owner_id: uuid.UUID | None = None
    plan: str | None = None
    mrr: float
    status: str
    last_active_at: datetime | None = None
    created_at: datetime


class HealthScoreOut(ORMModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    score: int
    category: str
    churn_risk: float | None = None
    usage_score: int | None = None
    engagement_score: int | None = None
    support_score: int | None = None
    satisfaction_score: int | None = None
    adoption_score: int | None = None
    drivers: dict = {}
    computed_at: datetime


class HealthInputs(BaseModel):
    usage_score: int = Field(ge=0, le=100)
    engagement_score: int = Field(ge=0, le=100)
    support_score: int = Field(ge=0, le=100)
    satisfaction_score: int = Field(ge=0, le=100)
    adoption_score: int = Field(ge=0, le=100)


class EngagementActionIn(BaseModel):
    customer_id: uuid.UUID
    type: str = Field(min_length=1, max_length=40)
    title: str = Field(min_length=1, max_length=255)
    reason: str | None = None
    priority: str = "medium"
    due_at: datetime | None = None


class EngagementActionOut(ORMModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    assignee_id: uuid.UUID | None = None
    type: str
    title: str
    reason: str | None = None
    priority: str
    status: str
    due_at: datetime | None = None
    ai_generated: bool
    created_at: datetime


# ===================== Knowledge gaps =====================
class RecordGapRequest(BaseModel):
    question: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    conversation_id: uuid.UUID | None = None
    agent_run_id: uuid.UUID | None = None


class ResolveGapRequest(BaseModel):
    suggested_answer: str | None = None
    document_id: uuid.UUID | None = None
    status: str = "resolved"


class KnowledgeGapOut(ORMModel):
    id: uuid.UUID
    question: str
    occurrences: int
    avg_confidence: float | None = None
    suggestion: str | None = None
    suggested_answer: str | None = None
    status: str
    last_seen_at: datetime
    created_at: datetime


class GapDashboard(BaseModel):
    open: int
    in_review: int
    resolved: int
    dismissed: int
    top_gaps: list[KnowledgeGapOut]


# ===================== Executive insights + business impact =====================
class ExecutiveInsightIn(BaseModel):
    kind: str = "recommendation"
    title: str = Field(min_length=1, max_length=255)
    summary: str = Field(min_length=1)
    recommendation: str | None = None
    severity: str = "info"
    metrics: dict = Field(default_factory=dict)


class ExecutiveInsightOut(ORMModel):
    id: uuid.UUID
    kind: str
    title: str
    summary: str
    recommendation: str | None = None
    severity: str
    metrics: dict = {}
    is_pinned: bool
    created_at: datetime


class BusinessImpactIn(BaseModel):
    period_start: date
    period_end: date
    granularity: str = "month"
    ai_resolution_rate: float | None = None
    cost_savings_usd: float | None = None
    revenue_influenced_usd: float | None = None
    churn_reduction_pct: float | None = None
    agent_productivity: float | None = None
    customer_retention_pct: float | None = None
    tickets_handled: int | None = None
    tickets_ai_resolved: int | None = None
    csat_avg: float | None = None


class BusinessImpactOut(ORMModel):
    id: uuid.UUID
    period_start: date
    period_end: date
    granularity: str
    ai_resolution_rate: float | None = None
    cost_savings_usd: float | None = None
    revenue_influenced_usd: float | None = None
    churn_reduction_pct: float | None = None
    agent_productivity: float | None = None
    customer_retention_pct: float | None = None
    tickets_handled: int | None = None
    tickets_ai_resolved: int | None = None
    csat_avg: float | None = None
    computed_at: datetime


# ===================== Meetings =====================
class MeetingIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    type: str = "demo"
    lead_id: uuid.UUID | None = None
    customer_id: uuid.UUID | None = None
    attendee_name: str | None = None
    attendee_email: str | None = None
    starts_at: datetime
    ends_at: datetime | None = None
    timezone: str = "UTC"
    location: str | None = None
    meeting_url: str | None = None
    notes: str | None = None


class MeetingOut(ORMModel):
    id: uuid.UUID
    title: str
    type: str
    status: str
    lead_id: uuid.UUID | None = None
    customer_id: uuid.UUID | None = None
    attendee_name: str | None = None
    attendee_email: str | None = None
    starts_at: datetime
    ends_at: datetime | None = None
    timezone: str
    meeting_url: str | None = None
    followup_sent: bool
    created_at: datetime


class ReminderIn(BaseModel):
    remind_at: datetime
    channel: str = "email"


class ReminderOut(ORMModel):
    id: uuid.UUID
    meeting_id: uuid.UUID
    remind_at: datetime
    channel: str
    status: str
    sent_at: datetime | None = None


# ===================== Workflow automation =====================
class WorkflowIn(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    status: str = "draft"
    trigger_type: str = "manual"
    trigger_config: dict = Field(default_factory=dict)
    definition: dict = Field(default_factory=lambda: {"nodes": [], "edges": []})


class WorkflowOut(ORMModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    status: str
    trigger_type: str
    trigger_config: dict = {}
    definition: dict = {}
    version: int
    run_count: int
    last_run_at: datetime | None = None
    created_at: datetime


class TriggerWorkflowRequest(BaseModel):
    context: dict = Field(default_factory=dict)
    trigger_source: str | None = None


class WorkflowRunStepOut(ORMModel):
    id: uuid.UUID
    node_id: str
    node_type: str
    step_order: int
    status: str
    output: dict = {}
    error: str | None = None


class WorkflowRunOut(ORMModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    status: str
    trigger_source: str | None = None
    context: dict = {}
    result: dict = {}
    error: str | None = None
    duration_ms: int | None = None
    created_at: datetime


class WorkflowRunDetail(WorkflowRunOut):
    steps: list[WorkflowRunStepOut] = []


# ===================== Employee assistant =====================
class InternalDocIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    category: str = "general"
    content: str | None = None
    source_url: str | None = None
    visibility: str = "all_employees"
    tags: list[str] = Field(default_factory=list)


class InternalDocOut(ORMModel):
    id: uuid.UUID
    title: str
    category: str
    content: str | None = None
    visibility: str
    status: str
    tags: list[str] = []
    created_at: datetime


class HrPolicyIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    type: str = "general"
    body: str = Field(min_length=1)
    effective_date: date | None = None
    applies_to: str = "all"


class HrPolicyOut(ORMModel):
    id: uuid.UUID
    title: str
    type: str
    body: str
    effective_date: date | None = None
    applies_to: str
    created_at: datetime


# ===================== AI agent Q&A =====================
class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    # Recent conversation turns (rendered) so the agent has memory of the chat.
    history: str | None = Field(default=None, max_length=8000)


class AskResponse(BaseModel):
    answer: str
    confidence: float
    sources: list = []
    knowledge_gap_recorded: bool = False
