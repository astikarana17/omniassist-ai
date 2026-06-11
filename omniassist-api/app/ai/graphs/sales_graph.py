"""Sales agent — a LangGraph workflow.

classify → retrieve → qualify (BANT scoring) → reason (objection handling, recs) → assess
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.ai import claude, intent, retriever
from app.ai.graphs.state import AgentResult, AgentState
from app.ai.tools import SALES_TOOLS
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("sales_graph")

_QUALIFY_SYSTEM = (
    "You are a sales qualification engine. From the conversation, infer BANT "
    "(Budget, Authority, Need, Timeline) and a 0-100 lead score reflecting buying intent."
)


async def _classify(state: AgentState) -> AgentState:
    result = await intent.classify(state["message"], state.get("history", ""))
    state.update(
        language=result["language"], intent=result["intent"], urgency=result["urgency"]
    )
    return state


async def _retrieve(state: AgentState) -> AgentState:
    chunks = await retriever.retrieve(state["org_id"], state["message"], top_k=4)
    state["context"] = retriever.format_context(chunks)
    state["sources"] = [{"title": c.title, "score": round(c.score, 3)} for c in chunks]
    return state


async def _qualify(state: AgentState) -> AgentState:
    prompt = (
        f"Conversation:\n{state.get('history', '')}\n{state['message']}\n\n"
        "Return JSON: budget, authority, need, timeline (each a short string or null), "
        "score (0-100 integer)."
    )
    try:
        bant = await claude.complete_json(system=_QUALIFY_SYSTEM, prompt=prompt)
    except Exception:  # noqa: BLE001
        bant = {"score": 50}
    score = int(bant.get("score", 50))
    state["suggested_actions"] = [
        {"tool": "qualify_lead", "input": {**bant, "score": score}}
    ]
    state.setdefault("tools_used", []).append("qualify_lead")
    state["_score"] = score  # type: ignore[typeddict-unknown-key]
    return state


async def _reason(state: AgentState) -> AgentState:
    cfg = state.get("agent_config", {})
    score = state.get("_score", 50)
    system = (
        f"{cfg.get('system_prompt', 'You are a persuasive but honest sales agent.')}\n\n"
        f"Reply in: {state.get('language', 'English')}. Handle objections with empathy and "
        "facts grounded in the context. If buying intent is high, propose booking a demo.\n\n"
        f"Lead score so far: {score}/100.\n\n"
        f"=== Product Knowledge ===\n{state.get('context', '')}\n=== End ==="
    )
    messages = []
    if state.get("history"):
        messages.append({"role": "user", "content": f"History:\n{state['history']}"})
    messages.append({"role": "user", "content": state["message"]})

    result = await claude.complete(
        system=system,
        messages=messages,
        model=cfg.get("model", settings.CLAUDE_MODEL),
        temperature=cfg.get("temperature", 0.4),
        tools=SALES_TOOLS,
    )
    state["reply"] = result.text
    state["input_tokens"] = result.input_tokens
    state["output_tokens"] = result.output_tokens
    for call in result.raw_tool_calls:
        state["suggested_actions"].append({"tool": call["name"], "input": call["input"]})
        state.setdefault("tools_used", []).append(call["name"])
    return state


async def _assess(state: AgentState) -> AgentState:
    score = state.get("_score", 50)
    state["confidence"] = 0.9 if state.get("sources") else 0.7
    # Sales agents only hand off when explicitly asked; otherwise they keep nurturing.
    state["handoff"] = score >= 85  # hot lead → notify human sales rep
    if state["handoff"]:
        state["handoff_reason"] = f"Hot lead (score {score}) — route to sales rep"
    state["sentiment"] = {"label": "neutral", "score": 0.0, "escalate": False}
    return state


def build_sales_graph():
    graph = StateGraph(AgentState)
    graph.add_node("classify", _classify)
    graph.add_node("retrieve", _retrieve)
    graph.add_node("qualify", _qualify)
    graph.add_node("reason", _reason)
    graph.add_node("assess", _assess)

    graph.add_edge(START, "classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "qualify")
    graph.add_edge("qualify", "reason")
    graph.add_edge("reason", "assess")
    graph.add_edge("assess", END)
    return graph.compile()


_compiled = None


async def run_sales_agent(
    *, org_id: str, conversation_id: str, message: str, history: str, agent_config: dict
) -> AgentResult:
    global _compiled
    if _compiled is None:
        _compiled = build_sales_graph()
    state: AgentState = {
        "org_id": org_id,
        "conversation_id": conversation_id,
        "message": message,
        "history": history,
        "agent_config": agent_config,
        "suggested_actions": [],
        "tools_used": [],
    }
    final = await _compiled.ainvoke(state)
    return AgentResult.from_state(final)
