"""Support agent — a LangGraph workflow.

classify → retrieve → reason → sentiment → assess (respond | handoff)
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.ai import claude, intent, retriever, sentiment
from app.ai.graphs.state import AgentResult, AgentState
from app.ai.tools import SUPPORT_TOOLS
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("support_graph")


async def _classify(state: AgentState) -> AgentState:
    result = await intent.classify(state["message"], state.get("history", ""))
    state.update(
        language=result["language"],
        intent=result["intent"],
        is_sales=result["is_sales"],
        wants_human=result["wants_human"],
        urgency=result["urgency"],
    )
    return state


async def _retrieve(state: AgentState) -> AgentState:
    chunks = await retriever.retrieve(state["org_id"], state["message"], top_k=5)
    state["context"] = retriever.format_context(chunks)
    state["sources"] = [
        {"title": c.title, "document_id": c.document_id, "score": round(c.score, 3)}
        for c in chunks
    ]
    state.setdefault("tools_used", []).append("kb_search")
    return state


async def _reason(state: AgentState) -> AgentState:
    cfg = state.get("agent_config", {})
    system = (
        f"{cfg.get('system_prompt', 'You are a helpful customer support agent.')}\n\n"
        f"Always reply in the customer's language: {state.get('language', 'English')}.\n"
        "Ground your answer ONLY in the knowledge base context below. If the answer is not "
        "in the context, say you are not certain and use the escalate_to_human tool.\n\n"
        f"=== Knowledge Base Context ===\n{state.get('context', '')}\n=== End Context ==="
    )
    messages = []
    if state.get("history"):
        messages.append({"role": "user", "content": f"Conversation history:\n{state['history']}"})
    messages.append({"role": "user", "content": state["message"]})

    result = await claude.complete(
        system=system,
        messages=messages,
        model=cfg.get("model", settings.CLAUDE_MODEL),
        temperature=cfg.get("temperature", 0.3),
        tools=SUPPORT_TOOLS,
    )
    state["reply"] = result.text or "Let me connect you with a teammate who can help."
    state["input_tokens"] = result.input_tokens
    state["output_tokens"] = result.output_tokens

    actions = []
    escalated = False
    for call in result.raw_tool_calls:
        actions.append({"tool": call["name"], "input": call["input"]})
        state.setdefault("tools_used", []).append(call["name"])
        if call["name"] == "escalate_to_human":
            escalated = True
            state["handoff_reason"] = call["input"].get("reason", "Agent requested escalation")
    state["suggested_actions"] = actions
    state["_escalated"] = escalated  # type: ignore[typeddict-unknown-key]
    return state


async def _sentiment(state: AgentState) -> AgentState:
    state["sentiment"] = await sentiment.analyze(state["message"])
    return state


async def _assess(state: AgentState) -> AgentState:
    cfg = state.get("agent_config", {})
    threshold = cfg.get("confidence_threshold", 70) / 100
    has_sources = bool(state.get("sources"))
    escalated = bool(state.get("_escalated"))
    senti = state.get("sentiment", {})

    # Heuristic confidence: grounded answers are trusted; ungrounded are not.
    confidence = 0.9 if has_sources else 0.5
    if escalated:
        confidence = 0.3

    handoff = (
        escalated
        or state.get("wants_human", False)
        or confidence < threshold
        or bool(senti.get("escalate"))
    )
    if handoff and not state.get("handoff_reason"):
        if state.get("wants_human"):
            state["handoff_reason"] = "Customer requested a human agent"
        elif senti.get("escalate"):
            state["handoff_reason"] = f"Negative sentiment ({senti.get('label')})"
        else:
            state["handoff_reason"] = "Low answer confidence"

    state["confidence"] = round(confidence, 2)
    state["handoff"] = handoff
    return state


def build_support_graph():
    graph = StateGraph(AgentState)
    graph.add_node("classify", _classify)
    graph.add_node("retrieve", _retrieve)
    graph.add_node("reason", _reason)
    graph.add_node("sentiment", _sentiment)
    graph.add_node("assess", _assess)

    graph.add_edge(START, "classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "reason")
    graph.add_edge("reason", "sentiment")
    graph.add_edge("sentiment", "assess")
    graph.add_edge("assess", END)
    return graph.compile()


_compiled = None


async def run_support_agent(
    *, org_id: str, conversation_id: str, message: str, history: str, agent_config: dict
) -> AgentResult:
    global _compiled
    if _compiled is None:
        _compiled = build_support_graph()
    state: AgentState = {
        "org_id": org_id,
        "conversation_id": conversation_id,
        "message": message,
        "history": history,
        "agent_config": agent_config,
        "tools_used": [],
    }
    final = await _compiled.ainvoke(state)
    return AgentResult.from_state(final)
