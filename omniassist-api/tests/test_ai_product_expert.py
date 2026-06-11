"""Unit tests for the Product Expert / Employee Assistant pure logic (no Claude/DB)."""
from __future__ import annotations

import pytest

from app.ai.company_knowledge import (
    CompanyKnowledge,
    format_company_context,
    rank_faqs,
)
from app.ai.graphs.ops_agents import (
    GROUNDED_CONFIDENCE,
    PARTIAL_CONFIDENCE,
    UNGROUNDED_CONFIDENCE,
    assess_confidence,
    looks_like_refusal,
    should_record_gap,
)
from app.models.company import Faq, Product


def _faq(q: str, a: str) -> Faq:
    return Faq(question=q, answer=a)


def _product(name: str, summary: str) -> Product:
    return Product(name=name, type="product", summary=summary)


# ---------------- Company knowledge formatting ----------------
def test_empty_knowledge_message():
    ctx = format_company_context(CompanyKnowledge())
    assert "No company knowledge" in ctx


def test_context_renders_sections():
    knowledge = CompanyKnowledge(
        products=[_product("OmniAssist", "AI support platform")],
        faqs=[_faq("How do I reset my password?", "Use the reset link.")],
    )
    ctx = format_company_context(knowledge, query="reset password")
    assert "Products & Services" in ctx
    assert "OmniAssist" in ctx
    assert "FAQs" in ctx
    assert "reset link" in ctx


def test_rank_faqs_orders_by_overlap():
    faqs = [
        _faq("How is billing handled?", "Monthly invoices."),
        _faq("How do I reset my password?", "Use the reset link."),
        _faq("What integrations exist?", "Slack and Teams."),
    ]
    ranked = rank_faqs(faqs, "I forgot my password reset", top_k=1)
    assert ranked[0].question == "How do I reset my password?"


def test_rank_faqs_falls_back_when_no_overlap():
    faqs = [_faq("Billing", "Monthly"), _faq("Integrations", "Slack")]
    ranked = rank_faqs(faqs, "completely unrelated xyz", top_k=2)
    assert len(ranked) == 2  # falls back to first N rather than empty


# ---------------- Confidence + gap decision ----------------
def test_assess_confidence_levels():
    assert assess_confidence(True, True, False) == GROUNDED_CONFIDENCE
    assert assess_confidence(True, False, False) == PARTIAL_CONFIDENCE
    assert assess_confidence(False, True, False) == PARTIAL_CONFIDENCE
    assert assess_confidence(False, False, False) == UNGROUNDED_CONFIDENCE
    assert assess_confidence(True, True, True) == UNGROUNDED_CONFIDENCE  # refused overrides


def test_should_record_gap():
    # below threshold -> gap
    assert should_record_gap(0.5, 0.7, has_any_knowledge=True) is True
    # above threshold with knowledge -> no gap
    assert should_record_gap(0.88, 0.7, has_any_knowledge=True) is False
    # no knowledge at all -> always a gap
    assert should_record_gap(0.88, 0.7, has_any_knowledge=False) is True


def test_refusal_detection():
    assert looks_like_refusal("I don't know the answer to that.")
    assert looks_like_refusal("I could not find any information on this.")
    assert not looks_like_refusal("Our Pro plan costs $49/month.")


# ---------------- Route auth (POST ask endpoints) ----------------
@pytest.mark.parametrize("path", ["/api/v1/company/ask", "/api/v1/employee/ask"])
def test_ask_endpoints_require_auth(client, path):
    resp = client.post(path, json={"question": "What does the product do?"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] in ("AUTH_REQUIRED",)
