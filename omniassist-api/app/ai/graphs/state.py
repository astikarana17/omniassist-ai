"""Shared agent state and result types for the LangGraph agents."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    # Inputs
    org_id: str
    conversation_id: str
    message: str
    history: str  # rendered recent turns
    agent_config: dict[str, Any]

    # Working memory
    language: str
    intent: str
    is_sales: bool
    wants_human: bool
    urgency: str
    context: str
    sources: list[dict[str, Any]]

    # Outputs
    reply: str
    confidence: float
    handoff: bool
    handoff_reason: str
    sentiment: dict[str, Any]
    suggested_actions: list[dict[str, Any]]
    input_tokens: int
    output_tokens: int
    tools_used: list[str]


@dataclass
class AgentResult:
    reply: str
    confidence: float
    handoff: bool
    handoff_reason: str | None
    intent: str
    language: str
    sentiment: dict[str, Any]
    sources: list[dict[str, Any]] = field(default_factory=list)
    suggested_actions: list[dict[str, Any]] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    tools_used: list[str] = field(default_factory=list)

    @classmethod
    def from_state(cls, state: AgentState) -> "AgentResult":
        return cls(
            reply=state.get("reply", ""),
            confidence=state.get("confidence", 0.0),
            handoff=state.get("handoff", False),
            handoff_reason=state.get("handoff_reason"),
            intent=state.get("intent", "other"),
            language=state.get("language", "English"),
            sentiment=state.get("sentiment", {}),
            sources=state.get("sources", []),
            suggested_actions=state.get("suggested_actions", []),
            input_tokens=state.get("input_tokens", 0),
            output_tokens=state.get("output_tokens", 0),
            tools_used=state.get("tools_used", []),
        )
