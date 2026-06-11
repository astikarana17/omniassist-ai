"""Company knowledge routes — powers the AI Product Expert & Competitor Intelligence.

Manages the structured source-of-truth the agents answer from: company profile,
products, pricing, FAQs, policies, roadmap and competitor comparisons.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.ai.graphs import ops_agents
from app.core.deps import CurrentContext, DbSession, PaginationDep, require_permission
from app.core.exceptions import NotFoundError
from app.core.permissions import Permission
from app.models.company import (
    CompanyProfile,
    Competitor,
    CompetitorComparison,
    Faq,
    Policy,
    PricingPlan,
    Product,
    RoadmapItem,
)
from app.repositories.base import TenantRepository
from app.schemas.common import MessageResponse, Page, PageMeta
from app.schemas.ops import (
    AskRequest,
    AskResponse,
    CompanyProfileIn,
    CompanyProfileOut,
    ComparisonIn,
    ComparisonOut,
    CompetitorIn,
    CompetitorOut,
    FaqIn,
    FaqOut,
    PolicyIn,
    PolicyOut,
    PricingPlanIn,
    PricingPlanOut,
    ProductIn,
    ProductOut,
    RoadmapItemIn,
    RoadmapItemOut,
)
from app.services.ops_service import KnowledgeGapService

router = APIRouter(prefix="/company", tags=["Company Knowledge"])


@router.post("/ask", response_model=AskResponse)
async def ask_product_expert(
    payload: AskRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.COMPANY_READ)),
) -> AskResponse:
    """Ask the AI Product Expert. Answers are grounded in curated company knowledge
    + the KB; a low-confidence answer is automatically logged as a knowledge gap."""
    result = await ops_agents.run_product_expert(
        db, ctx.org_id, payload.question, history=payload.history or ""
    )
    gap_recorded = False
    if result.knowledge_gap:
        await KnowledgeGapService(db).record(
            ctx.org_id, question=payload.question, confidence=result.confidence,
        )
        gap_recorded = True
    return AskResponse(
        answer=result.reply,
        confidence=result.confidence,
        sources=result.sources,
        knowledge_gap_recorded=gap_recorded,
    )


def _page(items: list, total: int, page) -> Page:
    return Page(
        items=items,
        meta=PageMeta(total=total, limit=page.limit, offset=page.offset,
                      has_more=page.offset + len(items) < total),
    )


# ---------- Company profile (singleton per org) ----------
@router.get("/profile", response_model=CompanyProfileOut | None)
async def get_profile(
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.COMPANY_READ)),
) -> CompanyProfileOut | None:
    row = (
        await db.execute(select(CompanyProfile).where(CompanyProfile.org_id == ctx.org_id))
    ).scalar_one_or_none()
    return CompanyProfileOut.model_validate(row) if row else None


@router.put("/profile", response_model=CompanyProfileOut)
async def upsert_profile(
    payload: CompanyProfileIn,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.COMPANY_WRITE)),
) -> CompanyProfileOut:
    row = (
        await db.execute(select(CompanyProfile).where(CompanyProfile.org_id == ctx.org_id))
    ).scalar_one_or_none()
    if row is None:
        row = CompanyProfile(org_id=ctx.org_id, **payload.model_dump())
        db.add(row)
    else:
        for k, v in payload.model_dump().items():
            setattr(row, k, v)
    await db.flush()
    return CompanyProfileOut.model_validate(row)


# ---------- Products ----------
@router.get("/products", response_model=Page[ProductOut])
async def list_products(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    _: object = Depends(require_permission(Permission.COMPANY_READ)),
) -> Page[ProductOut]:
    repo = TenantRepository(db, Product)
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  order_by=Product.created_at.desc())
    return _page([ProductOut.model_validate(r) for r in rows], total, page)


@router.post("/products", response_model=ProductOut, status_code=201)
async def create_product(
    payload: ProductIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.COMPANY_WRITE)),
) -> ProductOut:
    repo = TenantRepository(db, Product)
    row = await repo.create(org_id=ctx.org_id, **payload.model_dump())
    return ProductOut.model_validate(row)


@router.delete("/products/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: uuid.UUID, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.COMPANY_WRITE)),
) -> MessageResponse:
    repo = TenantRepository(db, Product)
    row = await repo.get(ctx.org_id, product_id)
    if row is None:
        raise NotFoundError("Product not found.")
    await repo.delete(row)
    return MessageResponse(message="Product deleted.")


# ---------- Pricing plans ----------
@router.get("/pricing", response_model=Page[PricingPlanOut])
async def list_pricing(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    _: object = Depends(require_permission(Permission.COMPANY_READ)),
) -> Page[PricingPlanOut]:
    repo = TenantRepository(db, PricingPlan)
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  order_by=PricingPlan.position.asc())
    return _page([PricingPlanOut.model_validate(r) for r in rows], total, page)


@router.post("/pricing", response_model=PricingPlanOut, status_code=201)
async def create_pricing(
    payload: PricingPlanIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.COMPANY_WRITE)),
) -> PricingPlanOut:
    repo = TenantRepository(db, PricingPlan)
    row = await repo.create(org_id=ctx.org_id, **payload.model_dump())
    return PricingPlanOut.model_validate(row)


# ---------- FAQs ----------
@router.get("/faqs", response_model=Page[FaqOut])
async def list_faqs(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    _: object = Depends(require_permission(Permission.COMPANY_READ)),
) -> Page[FaqOut]:
    repo = TenantRepository(db, Faq)
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  order_by=Faq.position.asc())
    return _page([FaqOut.model_validate(r) for r in rows], total, page)


@router.post("/faqs", response_model=FaqOut, status_code=201)
async def create_faq(
    payload: FaqIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.COMPANY_WRITE)),
) -> FaqOut:
    repo = TenantRepository(db, Faq)
    row = await repo.create(org_id=ctx.org_id, **payload.model_dump())
    return FaqOut.model_validate(row)


# ---------- Policies ----------
@router.get("/policies", response_model=Page[PolicyOut])
async def list_policies(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    _: object = Depends(require_permission(Permission.COMPANY_READ)),
) -> Page[PolicyOut]:
    repo = TenantRepository(db, Policy)
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  order_by=Policy.created_at.desc())
    return _page([PolicyOut.model_validate(r) for r in rows], total, page)


@router.post("/policies", response_model=PolicyOut, status_code=201)
async def create_policy(
    payload: PolicyIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.COMPANY_WRITE)),
) -> PolicyOut:
    repo = TenantRepository(db, Policy)
    row = await repo.create(org_id=ctx.org_id, **payload.model_dump())
    return PolicyOut.model_validate(row)


# ---------- Roadmap ----------
@router.get("/roadmap", response_model=Page[RoadmapItemOut])
async def list_roadmap(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    _: object = Depends(require_permission(Permission.COMPANY_READ)),
) -> Page[RoadmapItemOut]:
    repo = TenantRepository(db, RoadmapItem)
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  order_by=RoadmapItem.position.asc())
    return _page([RoadmapItemOut.model_validate(r) for r in rows], total, page)


@router.post("/roadmap", response_model=RoadmapItemOut, status_code=201)
async def create_roadmap(
    payload: RoadmapItemIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.COMPANY_WRITE)),
) -> RoadmapItemOut:
    repo = TenantRepository(db, RoadmapItem)
    row = await repo.create(org_id=ctx.org_id, **payload.model_dump())
    return RoadmapItemOut.model_validate(row)


# ---------- Competitors + comparisons (Competitor Intelligence) ----------
@router.get("/competitors", response_model=Page[CompetitorOut])
async def list_competitors(
    ctx: CurrentContext, db: DbSession, page: PaginationDep,
    _: object = Depends(require_permission(Permission.COMPETITOR_READ)),
) -> Page[CompetitorOut]:
    repo = TenantRepository(db, Competitor)
    rows, total = await repo.list(ctx.org_id, limit=page.limit, offset=page.offset,
                                  order_by=Competitor.created_at.desc())
    return _page([CompetitorOut.model_validate(r) for r in rows], total, page)


@router.post("/competitors", response_model=CompetitorOut, status_code=201)
async def create_competitor(
    payload: CompetitorIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.COMPETITOR_WRITE)),
) -> CompetitorOut:
    repo = TenantRepository(db, Competitor)
    row = await repo.create(org_id=ctx.org_id, **payload.model_dump())
    return CompetitorOut.model_validate(row)


@router.post("/competitors/comparisons", response_model=ComparisonOut, status_code=201)
async def add_comparison(
    payload: ComparisonIn, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.COMPETITOR_WRITE)),
) -> ComparisonOut:
    competitor = await TenantRepository(db, Competitor).get(ctx.org_id, payload.competitor_id)
    if competitor is None:
        raise NotFoundError("Competitor not found.")
    repo = TenantRepository(db, CompetitorComparison)
    row = await repo.create(org_id=ctx.org_id, **payload.model_dump())
    return ComparisonOut.model_validate(row)


@router.get("/competitors/{competitor_id}/comparisons", response_model=list[ComparisonOut])
async def list_comparisons(
    competitor_id: uuid.UUID, ctx: CurrentContext, db: DbSession,
    _: object = Depends(require_permission(Permission.COMPETITOR_READ)),
    dimension: str | None = Query(None),
) -> list[ComparisonOut]:
    stmt = select(CompetitorComparison).where(
        CompetitorComparison.org_id == ctx.org_id,
        CompetitorComparison.competitor_id == competitor_id,
    )
    if dimension:
        stmt = stmt.where(CompetitorComparison.dimension == dimension)
    rows = (await db.execute(stmt)).scalars().all()
    return [ComparisonOut.model_validate(r) for r in rows]
