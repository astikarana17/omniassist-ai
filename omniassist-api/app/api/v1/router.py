"""Aggregate v1 API router."""
from fastapi import APIRouter

from app.api.v1.routers import (
    agents,
    analytics,
    audit,
    auth,
    billing,
    company,
    conversations,
    customer_success,
    employee,
    insights,
    knowledge,
    knowledge_gaps,
    leads,
    meetings,
    members,
    notifications,
    onboarding,
    public,
    tickets,
    workflows,
)
from app.api.v1.webhooks import gmail, twilio_voice, twilio_whatsapp

api_router = APIRouter()

# Authenticated domain routers
api_router.include_router(auth.router)
api_router.include_router(conversations.router)
api_router.include_router(tickets.router)
api_router.include_router(leads.router)
api_router.include_router(knowledge.router)
api_router.include_router(agents.router)
api_router.include_router(analytics.router)
api_router.include_router(audit.router)
api_router.include_router(notifications.router)
api_router.include_router(members.router)
api_router.include_router(billing.router)

# Business Operations Platform modules
api_router.include_router(company.router)
api_router.include_router(onboarding.router)
api_router.include_router(customer_success.router)
api_router.include_router(knowledge_gaps.router)
api_router.include_router(insights.router)
api_router.include_router(meetings.router)
api_router.include_router(workflows.router)
api_router.include_router(employee.router)

# Public + webhooks (no JWT; verified by signature / slug)
api_router.include_router(public.router)
api_router.include_router(twilio_whatsapp.router)
api_router.include_router(twilio_voice.router)
api_router.include_router(gmail.router)
