"""Billing & plan management (Stripe).

Plan limits live here and are enforced via `app.core.deps.require_feature`. Stripe
calls are guarded — if STRIPE_SECRET_KEY is unset the API returns a clear
"billing not configured" error instead of failing obscurely.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, ValidationError
from app.core.logging import get_logger
from app.models.conversation import Conversation
from app.models.organization import Membership, Organization

logger = get_logger("billing")

# Per-plan limits (-1 = unlimited).
PLAN_LIMITS: dict[str, dict] = {
    "free": {"conversations": 100, "seats": 1, "channels": ["web"], "features": []},
    "starter": {"conversations": 1000, "seats": 1, "channels": ["web"],
                "features": ["support_agent", "knowledge_base", "analytics_basic"]},
    "growth": {"conversations": 10000, "seats": 10, "channels": ["web", "whatsapp", "email"],
               "features": ["support_agent", "sales_agent", "knowledge_base", "ticketing",
                            "workflows", "analytics_full"]},
    "enterprise": {"conversations": -1, "seats": -1,
                   "channels": ["web", "whatsapp", "email", "voice"],
                   "features": ["all", "sso", "audit", "voice", "data_residency"]},
}

_PRICE = {"starter": lambda: settings.STRIPE_PRICE_STARTER,
          "growth": lambda: settings.STRIPE_PRICE_GROWTH}


def limits_for(plan: str) -> dict:
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])


def has_feature(plan: str, feature: str) -> bool:
    feats = limits_for(plan)["features"]
    return "all" in feats or feature in feats


def channel_allowed(plan: str, channel: str) -> bool:
    return channel in limits_for(plan)["channels"]


def is_configured() -> bool:
    return bool(settings.STRIPE_SECRET_KEY)


def _stripe():
    if not is_configured():
        raise ValidationError("Billing is not configured. Set STRIPE_SECRET_KEY.",
                              code="BILLING_NOT_CONFIGURED")
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


class BillingService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def usage(self, org: Organization) -> dict:
        month_start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        convos = (
            await self.db.execute(
                select(func.count()).select_from(Conversation).where(
                    Conversation.org_id == org.id, Conversation.created_at >= month_start
                )
            )
        ).scalar_one()
        seats = (
            await self.db.execute(
                select(func.count()).select_from(Membership).where(Membership.org_id == org.id)
            )
        ).scalar_one()
        lim = limits_for(org.plan)
        return {
            "plan": org.plan,
            "limits": lim,
            "usage": {"conversations": int(convos), "seats": int(seats)},
            "configured": is_configured(),
        }

    async def create_checkout(self, org: Organization, plan: str, email: str) -> str:
        if plan not in _PRICE:
            raise ValidationError("Choose 'starter' or 'growth'. Enterprise is custom — contact sales.")
        price = _PRICE[plan]()
        if not price:
            raise ValidationError(f"No Stripe price configured for the {plan} plan.")
        stripe = _stripe()
        customer_id = (org.settings or {}).get("stripe_customer_id")
        try:
            session = stripe.checkout.Session.create(
                mode="subscription",
                line_items=[{"price": price, "quantity": 1}],
                success_url=f"{settings.APP_URL}/settings?billing=success",
                cancel_url=f"{settings.APP_URL}/settings?billing=cancelled",
                customer=customer_id or None,
                customer_email=None if customer_id else email,
                client_reference_id=str(org.id),
                metadata={"org_id": str(org.id), "plan": plan},
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("stripe_checkout_failed", error=str(exc))
            raise ExternalServiceError("Could not start checkout.", code="STRIPE_ERROR") from exc
        return session.url

    async def create_portal(self, org: Organization) -> str:
        customer_id = (org.settings or {}).get("stripe_customer_id")
        if not customer_id:
            raise ValidationError("No billing account yet — subscribe to a plan first.")
        stripe = _stripe()
        session = stripe.billing_portal.Session.create(
            customer=customer_id, return_url=f"{settings.APP_URL}/settings"
        )
        return session.url

    async def handle_webhook(self, payload: bytes, signature: str) -> None:
        stripe = _stripe()
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except Exception as exc:  # noqa: BLE001
            raise ValidationError("Invalid webhook signature.", code="BAD_SIGNATURE") from exc

        kind = event["type"]
        obj = event["data"]["object"]
        if kind == "checkout.session.completed":
            org_id = obj.get("metadata", {}).get("org_id") or obj.get("client_reference_id")
            plan = obj.get("metadata", {}).get("plan", "growth")
            await self._set_plan(org_id, plan, customer_id=obj.get("customer"),
                                 subscription_id=obj.get("subscription"))
        elif kind in ("customer.subscription.deleted", "customer.subscription.canceled"):
            cust = obj.get("customer")
            await self._downgrade_by_customer(cust)
        logger.info("stripe_webhook", type=kind)

    async def _set_plan(self, org_id, plan, *, customer_id=None, subscription_id=None) -> None:
        if not org_id:
            return
        org = await self.db.get(Organization, uuid.UUID(str(org_id)))
        if not org:
            return
        org.plan = plan
        s = dict(org.settings or {})
        if customer_id:
            s["stripe_customer_id"] = customer_id
        if subscription_id:
            s["stripe_subscription_id"] = subscription_id
        org.settings = s
        await self.db.commit()

    async def _downgrade_by_customer(self, customer_id) -> None:
        if not customer_id:
            return
        org = (
            await self.db.execute(
                select(Organization).where(
                    Organization.settings["stripe_customer_id"].astext == customer_id
                )
            )
        ).scalar_one_or_none()
        if org:
            org.plan = "free"
            await self.db.commit()
