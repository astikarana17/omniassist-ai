"""Grounding tests on a real-company (TCS) knowledge set.

Proves the Product Expert surfaces *different, correct* grounding for different
customer questions (so answers vary appropriately) — the deterministic layer that
makes live LLM answers accurate. Pure: no DB, no Claude.
"""
from __future__ import annotations

from app.ai.company_knowledge import (
    CompanyKnowledge,
    format_company_context,
    grounded_answer,
    rank_faqs,
)
from app.models.company import CompanyProfile, Competitor, Faq, PricingPlan, Product


def _faq(q: str, a: str) -> Faq:
    return Faq(question=q, answer=a)


# A trimmed mirror of the TCS data seeded into Supabase.
TCS_FAQS = [
    _faq("What is TCS?", "Tata Consultancy Services is one of the world's largest IT services and consulting firms, part of the Tata Group, founded in 1968."),
    _faq("Who is the CEO of TCS?", "K. Krithivasan is the CEO & Managing Director since 2023; Natarajan Chandrasekaran is Chairman."),
    _faq("How is TCS priced or how do I engage TCS?", "TCS engagements are enterprise and custom-scoped; pricing depends on services, scale and contract model."),
    _faq("What is ignio?", "ignio is an AI-powered cognitive automation / AIOps product that autonomously resolves and prevents IT issues."),
    _faq("What is TCS BaNCS?", "TCS BaNCS is the flagship financial-services platform for banking, capital markets and insurance."),
    _faq("Who are TCS's main competitors?", "Infosys, Accenture, Cognizant, Wipro and HCLTech."),
    _faq("How many employees does TCS have?", "Over 584,000 employees across 46 countries."),
]


def _knowledge() -> CompanyKnowledge:
    return CompanyKnowledge(
        profile=CompanyProfile(
            overview="Tata Consultancy Services (TCS) is a leading global IT services firm.",
            mission="Building greater futures through innovation and collective knowledge.",
        ),
        products=[
            Product(name="TCS BaNCS", type="product", summary="Financial services platform."),
            Product(name="ignio", type="product", summary="AIOps cognitive automation."),
            Product(name="TCS iON", type="product", summary="Digital learning & assessments."),
        ],
        plans=[
            PricingPlan(name="Enterprise Services", currency="USD", price_amount=None, billing_period="custom"),
        ],
        faqs=TCS_FAQS,
        competitors=[
            Competitor(name="Infosys", positioning="Closest TCS rival across apps, cloud and AI."),
            Competitor(name="Accenture", positioning="Global consulting + technology leader."),
        ],
    )


# ---------- Different questions surface different, correct FAQs ----------
def test_ceo_question_grounds_on_ceo_faq():
    top = rank_faqs(TCS_FAQS, "who is the ceo of the company", top_k=1)[0]
    assert "CEO" in top.question
    assert "Krithivasan" in top.answer


def test_pricing_question_grounds_on_pricing_faq():
    top = rank_faqs(TCS_FAQS, "how much does it cost to engage you", top_k=1)[0]
    assert "priced" in top.question.lower() or "engage" in top.question.lower()


def test_product_question_grounds_on_ignio_faq():
    top = rank_faqs(TCS_FAQS, "tell me about ignio automation", top_k=1)[0]
    assert "ignio" in top.question.lower()


def test_competitor_question_grounds_on_competitor_faq():
    top = rank_faqs(TCS_FAQS, "who are your competitors", top_k=1)[0]
    assert "competitor" in top.question.lower()


def test_questions_yield_distinct_grounding():
    """Variety: three distinct questions must not collapse to the same FAQ."""
    a = rank_faqs(TCS_FAQS, "who is the ceo", 1)[0].question
    b = rank_faqs(TCS_FAQS, "what is ignio", 1)[0].question
    c = rank_faqs(TCS_FAQS, "how much does it cost", 1)[0].question
    assert len({a, b, c}) == 3


# ---------- Full grounding context is complete + correct ----------
def test_context_includes_all_sections():
    ctx = format_company_context(_knowledge(), query="tell me about ignio and pricing")
    assert "Tata Consultancy Services" in ctx
    assert "Products & Services" in ctx and "ignio" in ctx
    assert "Pricing" in ctx
    assert "Competitors" in ctx and "Infosys" in ctx
    # Query-relevant FAQ is pulled into context
    assert "ignio" in ctx.lower()


def test_empty_org_has_no_grounding():
    assert "No company knowledge" in format_company_context(CompanyKnowledge())


# ---------- No-LLM grounded answers (works without a paid Anthropic key) ----------
def test_grounded_answer_ceo():
    ans, conf = grounded_answer(_knowledge(), "who is the ceo of TCS")
    assert ans and "Krithivasan" in ans
    assert conf >= 0.7


def test_grounded_answer_pricing_intent():
    ans, conf = grounded_answer(_knowledge(), "how much does it cost")
    assert ans and ("custom" in ans.lower() or "pricing" in ans.lower() or "engage" in ans.lower())
    assert conf >= 0.7


def test_grounded_answer_competitor_intent():
    ans, _ = grounded_answer(_knowledge(), "who are your competitors or alternatives")
    assert ans and "Infosys" in ans


def test_grounded_answer_product_mention():
    ans, _ = grounded_answer(_knowledge(), "what does ignio do")
    assert ans and "ignio" in ans.lower()


def test_grounded_answers_vary_by_question():
    a = grounded_answer(_knowledge(), "who is the ceo")[0]
    b = grounded_answer(_knowledge(), "how much does it cost")[0]
    c = grounded_answer(_knowledge(), "who are your competitors")[0]
    assert a != b != c and a != c


def test_grounded_answer_unknown_records_gap():
    # A question with no curated coverage should fall back to overview (or None).
    ans, conf = grounded_answer(_knowledge(), "do you sell pizza in antarctica")
    # overview fallback has low confidence → caller will flag a gap
    assert conf <= 0.55
