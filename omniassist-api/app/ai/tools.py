"""Tool schemas exposed to the agents (Anthropic tool-use format).

Tool *execution* (side effects: ticket/lead creation, handoff, demo booking) is
performed by the conversation/lead services after the graph returns its decision,
so the graph stays pure and testable. These schemas drive the model's structured
suggestions.
"""
from __future__ import annotations

SUPPORT_TOOLS = [
    {
        "name": "create_ticket",
        "description": "Create a support ticket when the issue needs tracking or follow-up.",
        "input_schema": {
            "type": "object",
            "properties": {
                "subject": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["subject", "priority"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": "Escalate to a human agent when confidence is low, the customer asks "
        "for a human, or sentiment is strongly negative.",
        "input_schema": {
            "type": "object",
            "properties": {"reason": {"type": "string"}},
            "required": ["reason"],
        },
    },
]

SALES_TOOLS = [
    {
        "name": "qualify_lead",
        "description": "Record BANT qualification details extracted from the conversation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "budget": {"type": "string"},
                "authority": {"type": "string"},
                "need": {"type": "string"},
                "timeline": {"type": "string"},
                "score": {"type": "integer", "minimum": 0, "maximum": 100},
            },
            "required": ["score"],
        },
    },
    {
        "name": "book_demo",
        "description": "Book a product demo when buying intent is high.",
        "input_schema": {
            "type": "object",
            "properties": {"preferred_time": {"type": "string"}, "notes": {"type": "string"}},
            "required": [],
        },
    },
    {
        "name": "schedule_followup",
        "description": "Schedule a follow-up touch for a lead that is not yet ready.",
        "input_schema": {
            "type": "object",
            "properties": {"when": {"type": "string"}, "channel": {"type": "string"}},
            "required": ["when"],
        },
    },
]
