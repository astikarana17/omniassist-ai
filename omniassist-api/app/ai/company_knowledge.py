"""Structured company-knowledge loader + grounding context for the Product Expert.

Unlike the KB retriever (vector search over uploaded docs), this pulls the
*structured* company facts an org curates — products, pricing, FAQs, policies,
roadmap and competitor positioning — straight from Postgres, and renders them
into a deterministic grounding block the AI Product Expert answers from.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import (
    CompanyProfile,
    Competitor,
    Faq,
    Policy,
    PricingPlan,
    Product,
    RoadmapItem,
)


@dataclass
class CompanyKnowledge:
    profile: CompanyProfile | None = None
    products: list[Product] = field(default_factory=list)
    plans: list[PricingPlan] = field(default_factory=list)
    faqs: list[Faq] = field(default_factory=list)
    policies: list[Policy] = field(default_factory=list)
    roadmap: list[RoadmapItem] = field(default_factory=list)
    competitors: list[Competitor] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not any(
            [self.profile, self.products, self.plans, self.faqs,
             self.policies, self.roadmap, self.competitors]
        )


async def load_company_knowledge(
    db: AsyncSession, org_id: uuid.UUID, *, limit: int = 50
) -> CompanyKnowledge:
    """Load an org's curated company knowledge (bounded)."""
    async def _all(model, order=None):
        stmt = select(model).where(model.org_id == org_id).limit(limit)
        if order is not None:
            stmt = stmt.order_by(order)
        return list((await db.execute(stmt)).scalars().all())

    profile = (
        await db.execute(select(CompanyProfile).where(CompanyProfile.org_id == org_id))
    ).scalar_one_or_none()

    return CompanyKnowledge(
        profile=profile,
        products=await _all(Product),
        plans=await _all(PricingPlan, PricingPlan.position.asc()),
        faqs=await _all(Faq, Faq.position.asc()),
        policies=await _all(Policy),
        roadmap=await _all(RoadmapItem, RoadmapItem.position.asc()),
        competitors=await _all(Competitor),
    )


_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "am", "do", "does",
    "did", "done", "how", "what", "who", "whom", "whose", "when", "where", "why",
    "which", "that", "this", "these", "those", "to", "of", "in", "on", "for", "from",
    "with", "about", "into", "over", "under", "at", "by", "as", "and", "or", "but",
    "if", "then", "than", "so", "such", "i", "me", "my", "we", "us", "our", "you",
    "your", "it", "its", "he", "she", "they", "them", "their", "can", "could", "will",
    "would", "should", "may", "might", "must", "have", "has", "had", "much", "many",
    "more", "most", "some", "any", "no", "not", "there", "here", "tell", "know", "get",
    "want", "need", "please", "give", "show", "does", "doing",
    "company", "companies", "firm", "business", "organization", "organisation",
}


def _tokens(text: str) -> set[str]:
    """Content tokens (lowercased, stopwords removed) for keyword matching."""
    words = "".join(c.lower() if c.isalnum() else " " for c in text).split()
    return {w for w in words if w not in _STOPWORDS}


def rank_faqs(faqs: list[Faq], query: str, top_k: int = 3) -> list[Faq]:
    """Lightweight keyword-overlap ranking so the most relevant FAQs lead the
    grounding block (pure; unit-tested)."""
    q = _tokens(query)
    if not q:
        return faqs[:top_k]
    scored = [
        (len(q & _tokens(f.question + " " + f.answer)), f)
        for f in faqs
    ]
    scored.sort(key=lambda s: s[0], reverse=True)
    return [f for score, f in scored if score > 0][:top_k] or faqs[:top_k]


def best_faq(faqs: list[Faq], query: str) -> tuple[Faq | None, int]:
    """Return the FAQ with the highest keyword overlap and its score (pure)."""
    q = _tokens(query)
    best: Faq | None = None
    best_score = 0
    for f in faqs:
        score = len(q & _tokens(f.question + " " + f.answer))
        if score > best_score:
            best, best_score = f, score
    return best, best_score


_PRICING_WORDS = {"price", "pricing", "cost", "costs", "plan", "plans", "much", "expensive", "quote"}
_COMPARE_WORDS = {"competitor", "competitors", "compare", "comparison", "vs", "versus", "alternative", "alternatives", "rival"}


def grounded_answer(knowledge: CompanyKnowledge, query: str) -> tuple[str | None, float]:
    """Deterministic answer straight from curated knowledge — used when no LLM is
    configured. Returns (answer, confidence); answer is None when nothing matches
    (so the caller records a knowledge gap). Pure; unit-tested.
    """
    if knowledge.is_empty():
        return None, 0.0
    ql = _tokens(query)

    # 1) Direct FAQ match (tokens are stopword-filtered, so any overlap is real).
    faq, score = best_faq(knowledge.faqs, query)
    if faq and score >= 1:
        return faq.answer, round(min(0.85, 0.7 + (score - 1) * 0.075), 2)

    # 2) Pricing intent.
    if ql & _PRICING_WORDS and knowledge.plans:
        lines = []
        for pl in knowledge.plans:
            price = (
                f"{pl.currency} {pl.price_amount}/{pl.billing_period}"
                if pl.price_amount is not None
                else "custom-scoped"
            )
            lines.append(f"{pl.name}: {price}")
        return "Pricing / engagement models:\n" + "\n".join(lines), 0.8

    # 3) Competitor / comparison intent.
    if ql & _COMPARE_WORDS and knowledge.competitors:
        names = ", ".join(c.name for c in knowledge.competitors)
        return f"Key competitors: {names}.", 0.8

    # 4) Product mentioned by name.
    low = query.lower()
    for p in knowledge.products:
        if p.name.lower() in low:
            return f"{p.name}: {p.summary or p.description or ''}".strip(), 0.8

    # 5) Fall back to the company overview.
    if knowledge.profile and knowledge.profile.overview:
        return knowledge.profile.overview, 0.5

    return None, 0.0


def format_company_context(knowledge: CompanyKnowledge, query: str = "") -> str:
    """Render structured company knowledge into an LLM grounding block."""
    if knowledge.is_empty():
        return "No company knowledge has been configured yet."

    sections: list[str] = []
    p = knowledge.profile
    if p and (p.overview or p.mission):
        sections.append(
            "=== Company ===\n"
            + (f"Overview: {p.overview}\n" if p.overview else "")
            + (f"Mission: {p.mission}" if p.mission else "")
        )

    if knowledge.products:
        lines = [f"- {pr.name} ({pr.type}): {pr.summary or pr.description or ''}".rstrip()
                 for pr in knowledge.products]
        sections.append("=== Products & Services ===\n" + "\n".join(lines))

    if knowledge.plans:
        lines = []
        for pl in knowledge.plans:
            price = f"{pl.currency} {pl.price_amount}/{pl.billing_period}" if pl.price_amount is not None else "custom"
            lines.append(f"- {pl.name}: {price}")
        sections.append("=== Pricing ===\n" + "\n".join(lines))

    ranked_faqs = rank_faqs(knowledge.faqs, query) if knowledge.faqs else []
    if ranked_faqs:
        lines = [f"Q: {f.question}\nA: {f.answer}" for f in ranked_faqs]
        sections.append("=== FAQs ===\n" + "\n\n".join(lines))

    if knowledge.policies:
        lines = [f"- {po.title} ({po.type}): {(po.body or '')[:300]}" for po in knowledge.policies]
        sections.append("=== Policies ===\n" + "\n".join(lines))

    if knowledge.roadmap:
        lines = [f"- [{r.status}] {r.title}" + (f" ({r.quarter})" if r.quarter else "")
                 for r in knowledge.roadmap if r.is_public]
        if lines:
            sections.append("=== Roadmap (public) ===\n" + "\n".join(lines))

    if knowledge.competitors:
        lines = [f"- {c.name}: {c.positioning or ''}".rstrip() for c in knowledge.competitors]
        sections.append("=== Competitors ===\n" + "\n".join(lines))

    return "\n\n".join(sections)
