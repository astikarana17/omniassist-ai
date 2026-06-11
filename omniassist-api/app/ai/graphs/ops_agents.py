"""Business-Operations AI agents (LangGraph).

- **Product Expert** — answers anything about the company, grounded in the
  curated structured knowledge (products/pricing/FAQs/policies/roadmap) plus the
  vector KB. When it can't answer confidently it flags a knowledge gap.
- **Employee Assistant** — answers internal questions (HR/handbook/SOP) grounded
  only in internal documents (never customer-facing content).

The graphs stay pure: DB loading happens in the ``run_*`` orchestrators; the
confidence + gap-decision logic lives in module-level helpers that are unit-tested
without Claude or a database.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, TypedDict

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import claude, company_knowledge, retriever
from app.core.config import settings
from app.core.logging import get_logger
from app.models.internal import InternalDocument

logger = get_logger("ops_agents")

# Confidence assigned when the answer is grounded in curated/KB knowledge vs not.
GROUNDED_CONFIDENCE = 0.88
PARTIAL_CONFIDENCE = 0.6
UNGROUNDED_CONFIDENCE = 0.35


# ---------------- Pure decision helpers (unit-tested) ----------------
def assess_confidence(has_structured: bool, has_kb: bool, refused: bool) -> float:
    """Heuristic answer confidence from grounding signals."""
    if refused:
        return UNGROUNDED_CONFIDENCE
    if has_structured and has_kb:
        return GROUNDED_CONFIDENCE
    if has_structured or has_kb:
        return PARTIAL_CONFIDENCE
    return UNGROUNDED_CONFIDENCE


def should_record_gap(confidence: float, threshold: float, has_any_knowledge: bool) -> bool:
    """Record a knowledge gap when the answer is below the agent's confidence
    threshold, or when there was no grounding knowledge at all."""
    return confidence < threshold or not has_any_knowledge


@dataclass
class ExpertResult:
    reply: str
    confidence: float
    sources: list[dict[str, Any]] = field(default_factory=list)
    knowledge_gap: bool = False
    gap_question: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0


class _ExpertState(TypedDict, total=False):
    message: str
    history: str  # rendered recent turns — gives the agent conversation memory
    context: str
    has_structured: bool
    has_kb: bool
    agent_config: dict[str, Any]
    system_extra: str
    reply: str
    confidence: float
    refused: bool
    input_tokens: int
    output_tokens: int


_REFUSAL_MARKERS = ("i don't know", "i do not know", "not sure", "cannot find",
                    "no information", "couldn't find", "could not find",
                    "unable to find", "don't have that information",
                    "do not have that information")


def looks_like_refusal(text: str) -> bool:
    low = text.lower()
    return any(m in low for m in _REFUSAL_MARKERS)


# ---------------- Product Expert ----------------
async def _expert_reason(state: _ExpertState) -> _ExpertState:
    cfg = state.get("agent_config", {})
    system = (
        "You are the company's AI Product Expert. Answer questions about the company, "
        "its products, pricing, features, policies, roadmap and how it compares to "
        "competitors. Ground every answer ONLY in the knowledge below. If the answer is "
        "not present, clearly say you don't have that information rather than guessing.\n\n"
        f"{state.get('system_extra', '')}"
        f"=== Company Knowledge ===\n{state.get('context', '')}\n=== End ==="
    )
    messages: list[dict[str, Any]] = []
    if state.get("history"):
        # Conversation memory: prior turns so the expert can resolve follow-ups
        # like "and how much does that cost?".
        messages.append({"role": "user", "content": f"Conversation so far:\n{state['history']}"})
    messages.append({"role": "user", "content": state["message"]})

    result = await claude.complete(
        system=system,
        messages=messages,
        model=cfg.get("model", settings.CLAUDE_MODEL),
        temperature=cfg.get("temperature", 0.2),
    )
    state["reply"] = result.text or "I don't have that information yet."
    state["refused"] = looks_like_refusal(state["reply"])
    state["input_tokens"] = result.input_tokens
    state["output_tokens"] = result.output_tokens
    return state


async def run_product_expert(
    db: AsyncSession,
    org_id: uuid.UUID,
    question: str,
    *,
    history: str = "",
    agent_config: dict | None = None,
    use_kb: bool = True,
) -> ExpertResult:
    """Run the Product Expert: structured company knowledge + KB → grounded answer
    → confidence assessment → knowledge-gap flag. ``history`` carries recent
    conversation turns so the agent remembers context across questions."""
    cfg = agent_config or {}
    knowledge = await company_knowledge.load_company_knowledge(db, org_id)
    structured_ctx = company_knowledge.format_company_context(knowledge, question)
    has_structured = not knowledge.is_empty()

    kb_chunks = []
    if use_kb:
        kb_chunks = await retriever.retrieve(org_id, question, top_k=4)
    has_kb = bool(kb_chunks)
    kb_ctx = retriever.format_context(kb_chunks) if kb_chunks else ""

    context = structured_ctx + (("\n\n=== Knowledge Base ===\n" + kb_ctx) if kb_ctx else "")

    sources = [
        {"title": c.title, "document_id": c.document_id, "score": round(c.score, 3)}
        for c in kb_chunks
    ]
    threshold = cfg.get("confidence_threshold", 70) / 100

    # Preferred: a natural-language answer GROUNDED in the retrieved knowledge via
    # OpenRouter — reads well and won't hallucinate (instructed to use only context).
    from app.ai import openrouter

    if openrouter.is_configured():
        system = (
            "You are OmniAssist's AI Product Expert. Answer the user's question using ONLY the "
            "knowledge below. If the answer is not in the knowledge, say you don't have that "
            "information yet and offer to connect a human — do NOT invent facts. Be concise, "
            "accurate and friendly.\n\n=== KNOWLEDGE ===\n" + context + "\n=== END KNOWLEDGE ==="
        )
        msgs: list[dict[str, Any]] = []
        if history:
            msgs.append({"role": "user", "content": f"Conversation so far:\n{history}"})
        msgs.append({"role": "user", "content": question})
        try:
            reply, tin, tout = await openrouter.complete(system=system, messages=msgs)
        except Exception as exc:  # noqa: BLE001
            logger.warning("openrouter_failed", error=str(exc))
            reply = ""
        if reply:
            refused = looks_like_refusal(reply)
            confidence = assess_confidence(has_structured, has_kb, refused)
            gap = should_record_gap(confidence, threshold, has_structured or has_kb)
            return ExpertResult(
                reply=reply, confidence=round(confidence, 2), sources=sources,
                knowledge_gap=gap, gap_question=question if gap else None,
                input_tokens=tin, output_tokens=tout,
            )
        # else fall through to the deterministic answer below

    # No-LLM mode: when no LLM is configured, answer deterministically straight from
    # the curated knowledge (correct + varied per question, just not rephrased).
    if not settings.ANTHROPIC_API_KEY:
        answer, confidence = company_knowledge.grounded_answer(knowledge, question)
        # RAG fallback: when structured knowledge isn't a strong direct hit, answer
        # from the most relevant vector-KB passage (the curated knowledge base).
        if (answer is None or confidence < 0.7) and kb_chunks and kb_chunks[0].score >= 0.6:
            answer = kb_chunks[0].text
            # A retrieved, on-topic passage is answerable; floor above the gap threshold.
            confidence = round(min(0.85, max(0.72, float(kb_chunks[0].score))), 2)
        threshold = cfg.get("confidence_threshold", 70) / 100
        gap = answer is None or should_record_gap(confidence, threshold, has_structured or has_kb)
        sources = [
            {"title": c.title, "document_id": c.document_id, "score": round(c.score, 3)}
            for c in kb_chunks
        ]
        return ExpertResult(
            reply=answer or "I don't have that information yet — I've flagged it for our team.",
            confidence=round(confidence, 2),
            sources=sources,
            knowledge_gap=gap,
            gap_question=question if gap else None,
        )

    state: _ExpertState = {
        "message": question, "history": history, "context": context,
        "has_structured": has_structured, "has_kb": has_kb, "agent_config": cfg,
    }
    state = await _expert_reason(state)

    confidence = assess_confidence(has_structured, has_kb, state.get("refused", False))
    threshold = cfg.get("confidence_threshold", 70) / 100
    gap = should_record_gap(confidence, threshold, has_structured or has_kb)

    sources = [
        {"title": c.title, "document_id": c.document_id, "score": round(c.score, 3)}
        for c in kb_chunks
    ]
    return ExpertResult(
        reply=state["reply"],
        confidence=round(confidence, 2),
        sources=sources,
        knowledge_gap=gap,
        gap_question=question if gap else None,
        input_tokens=state.get("input_tokens", 0),
        output_tokens=state.get("output_tokens", 0),
    )


# ---------------- Employee Assistant ----------------
async def _load_internal_context(
    db: AsyncSession, org_id: uuid.UUID, question: str, *, limit: int = 5
) -> tuple[str, bool]:
    """Keyword-match internal documents (HR/handbook/SOP) for grounding.
    Internal-only — never touches customer-facing KB."""
    terms = [t for t in company_knowledge._tokens(question)]  # noqa: SLF001
    stmt = select(InternalDocument).where(InternalDocument.org_id == org_id)
    if terms:
        like = [InternalDocument.title.ilike(f"%{t}%") for t in terms]
        like += [InternalDocument.content.ilike(f"%{t}%") for t in terms]
        stmt = stmt.where(or_(*like))
    rows = list((await db.execute(stmt.limit(limit))).scalars().all())
    if not rows:
        return "No internal documentation matched this question.", False
    blocks = [f"[{d.category}] {d.title}\n{(d.content or '')[:600]}" for d in rows]
    return "\n\n".join(blocks), True


async def run_employee_assistant(
    db: AsyncSession,
    org_id: uuid.UUID,
    question: str,
    *,
    agent_config: dict | None = None,
) -> ExpertResult:
    """Internal company assistant — answers from internal docs / HR policies only."""
    cfg = agent_config or {}
    context, has_docs = await _load_internal_context(db, org_id, question)

    # No-LLM mode: return the matched internal-doc snippet directly.
    if not settings.ANTHROPIC_API_KEY:
        return ExpertResult(
            reply=(context if has_docs else "I couldn't find that in our internal documentation."),
            confidence=0.8 if has_docs else UNGROUNDED_CONFIDENCE,
            sources=[],
            knowledge_gap=False,
        )

    system = (
        "You are the internal AI Employee Assistant. Answer employees' questions about "
        "HR policies, the handbook, SOPs and internal processes. Ground answers ONLY in "
        "the internal documentation below; if it's not covered, say so.\n\n"
        f"=== Internal Documentation ===\n{context}\n=== End ==="
    )
    result = await claude.complete(
        system=system,
        messages=[{"role": "user", "content": question}],
        model=cfg.get("model", settings.CLAUDE_MODEL),
        temperature=cfg.get("temperature", 0.1),
    )
    reply = result.text or "I couldn't find that in our internal documentation."
    refused = looks_like_refusal(reply)
    confidence = assess_confidence(has_docs, False, refused)
    return ExpertResult(
        reply=reply,
        confidence=round(confidence, 2),
        sources=[],
        knowledge_gap=False,  # internal gaps aren't tracked in the public dashboard
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )
