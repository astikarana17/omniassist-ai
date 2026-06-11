"""Business Operations Platform expansion — 31 new tables across 11 modules.

Adds: company knowledge (Product Expert), competitor intelligence, onboarding,
customer success + health scores, knowledge-gap detector, executive insights,
business-impact (ROI) metrics, demo/meeting agent, no-code workflow engine and
the internal employee-assistant knowledge base (pgvector tier).

Only the new tables are created (idempotent via ``checkfirst``), so this applies
cleanly on top of 0001 whether or not 0001 already saw the expanded metadata.

Revision ID: 0002_business_operations
Revises: 0001_initial_schema
Create Date: 2026-06-08
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

from app.core.database import Base
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
from app.models.insights import BusinessImpactMetric, ExecutiveInsight, KnowledgeGap
from app.models.internal import HrPolicy, InternalChunk, InternalDocument
from app.models.meeting import Meeting, MeetingReminder
from app.models.onboarding import (
    OnboardingFlow,
    OnboardingStep,
    UserOnboarding,
    UserOnboardingStep,
)
from app.models.success import (
    CustomerAccount,
    CustomerHealthScore,
    EngagementAction,
    UsageEvent,
)
from app.models.workflow import Workflow, WorkflowRun, WorkflowRunStep

revision: str = "0002_business_operations"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# New tables in FK-safe create order (create_all also sorts by dependency).
NEW_TABLES = [
    CompanyProfile.__table__,
    Product.__table__,
    PricingPlan.__table__,
    Feature.__table__,
    RoadmapItem.__table__,
    IntegrationCatalog.__table__,
    Policy.__table__,
    Faq.__table__,
    Competitor.__table__,
    CompetitorComparison.__table__,
    OnboardingFlow.__table__,
    OnboardingStep.__table__,
    UserOnboarding.__table__,
    UserOnboardingStep.__table__,
    CustomerAccount.__table__,
    UsageEvent.__table__,
    CustomerHealthScore.__table__,
    EngagementAction.__table__,
    KnowledgeGap.__table__,
    ExecutiveInsight.__table__,
    BusinessImpactMetric.__table__,
    Meeting.__table__,
    MeetingReminder.__table__,
    Workflow.__table__,
    WorkflowRun.__table__,
    WorkflowRunStep.__table__,
    InternalDocument.__table__,
    InternalChunk.__table__,
    HrPolicy.__table__,
]


def upgrade() -> None:
    bind = op.get_bind()

    # Create the new tables + their declarative indexes (idempotent).
    Base.metadata.create_all(bind=bind, tables=NEW_TABLES, checkfirst=True)

    # Vector similarity index (cosine) for the internal employee-assistant tier.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_internal_chunks_embedding_hnsw "
        "ON internal_chunks USING hnsw (embedding vector_cosine_ops)"
    )

    # Trigram indexes for fuzzy lookup over questions / titles.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_faqs_question_trgm "
        "ON faqs USING gin (question gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_knowledge_gaps_question_trgm "
        "ON knowledge_gaps USING gin (question gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_internal_documents_title_trgm "
        "ON internal_documents USING gin (title gin_trgm_ops)"
    )

    # Lock the Supabase PostgREST auto-API: enable RLS (deny-all, no policies)
    # on every public table. The API connects as service_role and bypasses RLS,
    # so this only blocks anon/authenticated direct REST access — security is
    # still enforced in the FastAPI app layer. Idempotent; covers 0001 tables too.
    op.execute(
        """
        DO $$
        DECLARE r record;
        BEGIN
          FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
            EXECUTE 'ALTER TABLE public.' || quote_ident(r.tablename)
                    || ' ENABLE ROW LEVEL SECURITY';
          END LOOP;
        END $$;
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    op.execute("DROP INDEX IF EXISTS ix_internal_documents_title_trgm")
    op.execute("DROP INDEX IF EXISTS ix_knowledge_gaps_question_trgm")
    op.execute("DROP INDEX IF EXISTS ix_faqs_question_trgm")
    op.execute("DROP INDEX IF EXISTS ix_internal_chunks_embedding_hnsw")
    Base.metadata.drop_all(bind=bind, tables=list(reversed(NEW_TABLES)))
