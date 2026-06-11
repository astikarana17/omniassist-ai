"""Import all models so SQLAlchemy's metadata + Alembic autogenerate see them."""
from app.core.database import Base
from app.models.agent import AgentRun, AiAgent
from app.models.company import (
    CompanyProfile,
    Competitor,
    CompetitorComparison,
    Faq,
    Feature,
    IntegrationCatalog,
    Policy,
    PricingPlan,
    Product,
    RoadmapItem,
)
from app.models.conversation import Contact, Conversation, Message
from app.models.insights import (
    BusinessImpactMetric,
    ExecutiveInsight,
    KnowledgeGap,
)
from app.models.internal import HrPolicy, InternalChunk, InternalDocument
from app.models.knowledge import KbChunk, KbDocument
from app.models.lead import Activity, Lead
from app.models.meeting import Meeting, MeetingReminder
from app.models.onboarding import (
    OnboardingFlow,
    OnboardingStep,
    UserOnboarding,
    UserOnboardingStep,
)
from app.models.ops import (
    AnalyticsDaily,
    AuditLog,
    Feedback,
    Notification,
    SentimentRecord,
    VoiceCall,
)
from app.models.organization import ApiKey, Membership, Organization, Setting
from app.models.success import (
    CustomerAccount,
    CustomerHealthScore,
    EngagementAction,
    UsageEvent,
)
from app.models.ticket import Ticket, TicketAttachment, TicketComment, TicketSummary
from app.models.user import Device, PasswordResetToken, Session, User
from app.models.workflow import Workflow, WorkflowRun, WorkflowRunStep

__all__ = [
    "Base",
    # Tenancy + identity
    "Organization",
    "Membership",
    "ApiKey",
    "Setting",
    "User",
    "Session",
    "Device",
    "PasswordResetToken",
    # Conversations + tickets
    "Contact",
    "Conversation",
    "Message",
    "Ticket",
    "TicketComment",
    "TicketAttachment",
    "TicketSummary",
    # Sales / CRM
    "Lead",
    "Activity",
    # Knowledge base (customer-facing)
    "KbDocument",
    "KbChunk",
    # AI agents
    "AiAgent",
    "AgentRun",
    # Ops
    "Notification",
    "AuditLog",
    "Feedback",
    "SentimentRecord",
    "AnalyticsDaily",
    "VoiceCall",
    # --- Business Operations Platform expansion ---
    # Company knowledge (Product Expert + Competitor Intelligence)
    "CompanyProfile",
    "Product",
    "PricingPlan",
    "Feature",
    "RoadmapItem",
    "IntegrationCatalog",
    "Policy",
    "Faq",
    "Competitor",
    "CompetitorComparison",
    # Onboarding
    "OnboardingFlow",
    "OnboardingStep",
    "UserOnboarding",
    "UserOnboardingStep",
    # Customer Success + Health
    "CustomerAccount",
    "UsageEvent",
    "CustomerHealthScore",
    "EngagementAction",
    # Insights / gaps / impact
    "KnowledgeGap",
    "ExecutiveInsight",
    "BusinessImpactMetric",
    # Meetings
    "Meeting",
    "MeetingReminder",
    # Workflow engine
    "Workflow",
    "WorkflowRun",
    "WorkflowRunStep",
    # Employee assistant (internal)
    "InternalDocument",
    "InternalChunk",
    "HrPolicy",
]
