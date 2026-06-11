"""Billing routes — current plan/usage, Stripe checkout, customer portal, webhook."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.core.deps import CurrentContext, DbSession, require_permission
from app.core.exceptions import NotFoundError
from app.core.permissions import Permission
from app.models.organization import Organization
from app.schemas.common import MessageResponse
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["Billing"])


class CheckoutRequest(BaseModel):
    plan: str  # "starter" | "growth"


class UrlResponse(BaseModel):
    url: str


async def _org(db, org_id) -> Organization:
    org = await db.get(Organization, org_id)
    if not org:
        raise NotFoundError("Organization not found.")
    return org


@router.get("")
async def get_billing(ctx: CurrentContext, db: DbSession) -> dict:
    org = await _org(db, ctx.org_id)
    return await BillingService(db).usage(org)


@router.post("/checkout", response_model=UrlResponse)
async def checkout(
    payload: CheckoutRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.BILLING_MANAGE)),
) -> UrlResponse:
    org = await _org(db, ctx.org_id)
    url = await BillingService(db).create_checkout(org, payload.plan, ctx.user.email)
    return UrlResponse(url=url)


@router.post("/portal", response_model=UrlResponse)
async def portal(
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.BILLING_MANAGE)),
) -> UrlResponse:
    org = await _org(db, ctx.org_id)
    url = await BillingService(db).create_portal(org)
    return UrlResponse(url=url)


@router.post("/webhook", response_model=MessageResponse)
async def webhook(request: Request, db: DbSession) -> MessageResponse:
    """Stripe webhook — no JWT; verified by the Stripe signature header."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    await BillingService(db).handle_webhook(payload, sig)
    return MessageResponse(message="ok")
