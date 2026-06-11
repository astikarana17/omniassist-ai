"""Company knowledge graph — powers the Product Expert & Competitor Intelligence agents.

Structured source-of-truth for everything the AI can say about the company:
overview, products/services, pricing, features, roadmap, integrations, policies,
FAQs and competitor positioning.
"""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import (
    ARRAY,
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin


class CompanyProfile(UUIDMixin, TimestampMixin, Base):
    """One profile per org (the company the AI represents)."""

    __tablename__ = "company_profiles"
    __table_args__ = (UniqueConstraint("org_id", name="uq_company_profile_org"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    overview: Mapped[str | None] = mapped_column(Text, nullable=True)
    mission: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_props: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    website: Mapped[str | None] = mapped_column(String(512), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    contact: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class Product(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (Index("ix_products_org", "org_id"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str | None] = mapped_column(String(120), nullable=True)
    type: Mapped[str] = mapped_column(String(20), default="product", nullable=False)  # product|service
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    pricing_plans: Mapped[list["PricingPlan"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class PricingPlan(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "pricing_plans"
    __table_args__ = (Index("ix_pricing_plans_org", "org_id"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    price_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    billing_period: Mapped[str] = mapped_column(String(20), default="monthly", nullable=False)
    features: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    limits: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    product: Mapped["Product | None"] = relationship(back_populates="pricing_plans")


class Feature(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "features"
    __table_args__ = (Index("ix_features_org", "org_id"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class RoadmapItem(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "roadmap_items"
    __table_args__ = (Index("ix_roadmap_items_org", "org_id"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="planned", nullable=False)
    quarter: Mapped[str | None] = mapped_column(String(16), nullable=True)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class IntegrationCatalog(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "integrations_catalog"
    __table_args__ = (Index("ix_integrations_catalog_org", "org_id"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    docs_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class Policy(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "policies"
    __table_args__ = (Index("ix_policies_org", "org_id"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(40), default="general", nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class Faq(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "faqs"
    __table_args__ = (Index("ix_faqs_org", "org_id"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Competitor(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "competitors"
    __table_args__ = (Index("ix_competitors_org", "org_id"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    website: Mapped[str | None] = mapped_column(String(512), nullable=True)
    positioning: Mapped[str | None] = mapped_column(Text, nullable=True)
    strengths: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    weaknesses: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    comparisons: Mapped[list["CompetitorComparison"]] = relationship(
        back_populates="competitor", cascade="all, delete-orphan"
    )


class CompetitorComparison(UUIDMixin, TimestampMixin, Base):
    """A single side-by-side row: us vs them on one dimension."""

    __tablename__ = "competitor_comparisons"
    __table_args__ = (
        Index("ix_competitor_comparisons_org", "org_id"),
        Index("ix_competitor_comparisons_competitor", "competitor_id"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False
    )
    dimension: Mapped[str] = mapped_column(String(120), nullable=False)  # pricing|features|<feature>
    us_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    them_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    advantage: Mapped[str | None] = mapped_column(String(12), nullable=True)  # us|them|parity
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    competitor: Mapped["Competitor"] = relationship(back_populates="comparisons")
