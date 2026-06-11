"""Unit tests for the no-code workflow executor (node-walking logic, no DB)."""
from __future__ import annotations

import asyncio
import uuid

from app.models.enums import RunStatus
from app.models.workflow import Workflow, WorkflowRun, WorkflowRunStep
from app.services.ops_service import WorkflowService


class FakeSession:
    """Minimal async-session stand-in that records added objects."""

    def __init__(self) -> None:
        self.added: list = []

    def add(self, obj) -> None:
        self.added.append(obj)

    async def flush(self) -> None:  # no-op
        return None


def _workflow(nodes: list[dict]) -> Workflow:
    return Workflow(
        id=uuid.uuid4(), org_id=uuid.uuid4(), name="wf", trigger_type="manual",
        definition={"nodes": nodes, "edges": []}, run_count=0,
    )


def _run(workflow, context):
    db = FakeSession()
    run = asyncio.run(
        WorkflowService(db).run(workflow.org_id, workflow, context=context)
    )
    return db, run


def test_all_nodes_execute_when_condition_passes():
    wf = _workflow([
        {"id": "verify", "type": "condition", "config": {"when": "verified"}},
        {"id": "ticket", "type": "action"},
        {"id": "notify", "type": "notification"},
    ])
    db, run = _run(wf, {"verified": True})

    assert run.status == RunStatus.SUCCEEDED
    assert run.result["executed_nodes"] == ["verify", "ticket", "notify"]
    assert run.result["node_count"] == 3
    assert wf.run_count == 1
    steps = [o for o in db.added if isinstance(o, WorkflowRunStep)]
    assert len(steps) == 3
    assert all(s.status == RunStatus.SUCCEEDED for s in steps)


def test_failed_condition_short_circuits():
    wf = _workflow([
        {"id": "verify", "type": "condition", "config": {"when": "verified"}},
        {"id": "ticket", "type": "action"},
    ])
    db, run = _run(wf, {"verified": False})

    assert run.status == RunStatus.SUCCEEDED  # ran cleanly, just stopped early
    assert run.result["executed_nodes"] == ["verify"]
    steps = [o for o in db.added if isinstance(o, WorkflowRunStep)]
    assert len(steps) == 1
    assert steps[0].output == {"passed": False}


def test_run_record_is_created():
    wf = _workflow([{"id": "a", "type": "action"}])
    db, run = _run(wf, {})
    runs = [o for o in db.added if isinstance(o, WorkflowRun)]
    assert len(runs) == 1
    assert run.duration_ms is not None and run.duration_ms >= 0
