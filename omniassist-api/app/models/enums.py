"""Shared string enums used across models and schemas."""
from __future__ import annotations

from enum import StrEnum


class Channel(StrEnum):
    WEB = "web"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    VOICE = "voice"


class ConversationStatus(StrEnum):
    OPEN = "open"
    PENDING = "pending"
    RESOLVED = "resolved"
    SNOOZED = "snoozed"


class SenderType(StrEnum):
    CONTACT = "contact"
    AI = "ai"
    AGENT = "agent"
    SYSTEM = "system"


class TicketStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Sentiment(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    HAPPY = "happy"


class LeadStage(StrEnum):
    NEW = "new"
    QUALIFIED = "qualified"
    DEMO = "demo"
    PROPOSAL = "proposal"
    WON = "won"
    LOST = "lost"


class DocStatus(StrEnum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class DocSource(StrEnum):
    UPLOAD = "upload"
    CRAWL = "crawl"
    FAQ = "faq"


class AgentType(StrEnum):
    SUPPORT = "support"
    SALES = "sales"
    PRODUCT_EXPERT = "product_expert"
    ONBOARDING = "onboarding"
    CUSTOMER_SUCCESS = "customer_success"
    DEMO_MEETING = "demo_meeting"
    COMPETITOR_INTEL = "competitor_intel"
    EMPLOYEE_ASSISTANT = "employee_assistant"


class HealthCategory(StrEnum):
    HEALTHY = "healthy"
    AT_RISK = "at_risk"
    CRITICAL = "critical"


class GapStatus(StrEnum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class WorkflowStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MeetingStatus(StrEnum):
    SCHEDULED = "scheduled"
    RESCHEDULED = "rescheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class OnboardingStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class InsightKind(StrEnum):
    REVENUE = "revenue"
    TICKETS = "tickets"
    CSAT = "csat"
    CHURN = "churn"
    SUPPORT_PERF = "support_perf"
    SALES_PERF = "sales_perf"
    ADOPTION = "adoption"
    RECOMMENDATION = "recommendation"


class NotificationChannel(StrEnum):
    IN_APP = "in_app"
    EMAIL = "email"
    SLACK = "slack"


class MembershipStatus(StrEnum):
    INVITED = "invited"
    ACTIVE = "active"
    SUSPENDED = "suspended"
