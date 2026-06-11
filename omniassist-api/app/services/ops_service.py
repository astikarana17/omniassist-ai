"""Business-Operations services: customer health scoring, knowledge-gap
clustering and the no-code workflow executor.

The pure helpers (`compute_health`, `normalize_question`) carry the business
logic and are unit-tested without a database.
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import GapStatus, HealthCategory, RunStatus
from app.models.insights import KnowledgeGap
from app.models.success import CustomerHealthScore
from app.models.workflow import Workflow, WorkflowRun, WorkflowRunStep

# Relative weights for the composite health score (must sum to 1.0).
HEALTH_WEIGHTS = {
    "usage_score": 0.30,
    "engagement_score": 0.20,
    "support_score": 0.20,
    "satisfaction_score": 0.15,
    "adoption_score": 0.15,
}
HEALTHY_THRESHOLD = 70
AT_RISK_THRESHOLD = 40


def categorize(score: int) -> HealthCategory:
    if score >= HEALTHY_THRESHOLD:
        return HealthCategory.HEALTHY
    if score >= AT_RISK_THRESHOLD:
        return HealthCategory.AT_RISK
    return HealthCategory.CRITICAL


def compute_health(
    usage_score: int,
    engagement_score: int,
    support_score: int,
    satisfaction_score: int,
    adoption_score: int,
) -> dict:
    """Pure composite health-score computation.

    Returns score (0-100), category and churn_risk (0-1). The weakest dimension
    is surfaced in ``drivers`` so the CS agent can recommend a targeted action.
    """
    components = {
        "usage_score": usage_score,
        "engagement_score": engagement_score,
        "support_score": support_score,
        "satisfaction_score": satisfaction_score,
        "adoption_score": adoption_score,
    }
    score = round(sum(components[k] * w for k, w in HEALTH_WEIGHTS.items()))
    score = max(0, min(100, score))
    category = categorize(score)
    churn_risk = round((100 - score) / 100, 3)
    weakest = min(components, key=components.get)
    return {
        "score": score,
        "category": category.value,
        "churn_risk": churn_risk,
        "drivers": {"weakest": weakest, "components": components},
        **components,
    }


_PUNCT_RE = re.compile(r"[^\w\s]")
_WS_RE = re.compile(r"\s+")


def normalize_question(question: str) -> str:
    """Normalize a question for gap clustering: lowercase, strip punctuation
    and collapse whitespace so near-duplicate questions map to one gap."""
    text = _PUNCT_RE.sub(" ", question.lower())
    return _WS_RE.sub(" ", text).strip()


class CustomerSuccessService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def record_health(
        self,
        org_id: uuid.UUID,
        customer_id: uuid.UUID,
        *,
        usage_score: int,
        engagement_score: int,
        support_score: int,
        satisfaction_score: int,
        adoption_score: int,
    ) -> CustomerHealthScore:
        result = compute_health(
            usage_score, engagement_score, support_score,
            satisfaction_score, adoption_score,
        )
        row = CustomerHealthScore(
            org_id=org_id,
            customer_id=customer_id,
            score=result["score"],
            category=result["category"],
            churn_risk=result["churn_risk"],
            usage_score=usage_score,
            engagement_score=engagement_score,
            support_score=support_score,
            satisfaction_score=satisfaction_score,
            adoption_score=adoption_score,
            drivers=result["drivers"],
            computed_at=datetime.utcnow(),
        )
        self.db.add(row)
        await self.db.flush()
        return row


class KnowledgeGapService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def record(
        self,
        org_id: uuid.UUID,
        *,
        question: str,
        confidence: float,
        conversation_id: uuid.UUID | None = None,
        agent_run_id: uuid.UUID | None = None,
    ) -> KnowledgeGap:
        """Record a low-confidence answer as a knowledge gap. Near-duplicate
        questions (same normalized form) increment the existing gap's count and
        roll the running average confidence rather than creating a new row."""
        norm = normalize_question(question)
        existing = (
            await self.db.execute(
                select(KnowledgeGap).where(
                    KnowledgeGap.org_id == org_id,
                    KnowledgeGap.normalized_q == norm,
                    KnowledgeGap.status != GapStatus.RESOLVED,
                )
            )
        ).scalar_one_or_none()

        now = datetime.utcnow()
        if existing is not None:
            prev_avg = existing.avg_confidence or confidence
            existing.avg_confidence = round(
                (prev_avg * existing.occurrences + confidence)
                / (existing.occurrences + 1),
                3,
            )
            existing.occurrences += 1
            existing.last_seen_at = now
            await self.db.flush()
            return existing

        gap = KnowledgeGap(
            org_id=org_id,
            question=question.strip(),
            normalized_q=norm,
            conversation_id=conversation_id,
            agent_run_id=agent_run_id,
            occurrences=1,
            avg_confidence=round(confidence, 3),
            status=GapStatus.OPEN,
            last_seen_at=now,
        )
        self.db.add(gap)
        await self.db.flush()
        return gap

    async def counts_by_status(self, org_id: uuid.UUID) -> dict[str, int]:
        rows = (
            await self.db.execute(
                select(KnowledgeGap.status, func.count())
                .where(KnowledgeGap.org_id == org_id)
                .group_by(KnowledgeGap.status)
            )
        ).all()
        counts = {s.value: 0 for s in GapStatus}
        for status, count in rows:
            counts[status] = int(count)
        return counts


class WorkflowService:
    """A minimal sequential no-code workflow executor.

    Walks the ``definition.nodes`` list in order, recording one
    ``WorkflowRunStep`` per node. ``condition`` nodes short-circuit the run when
    their referenced context flag is falsy; all other node types are logged as
    executed actions. Real side effects (notifications, ticket creation, …) are
    dispatched by the worker — here we record a deterministic, auditable trace.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def run(
        self,
        org_id: uuid.UUID,
        workflow: Workflow,
        *,
        context: dict,
        triggered_by: uuid.UUID | None = None,
        trigger_source: str | None = None,
    ) -> WorkflowRun:
        started = datetime.utcnow()
        run = WorkflowRun(
            org_id=org_id,
            workflow_id=workflow.id,
            status=RunStatus.RUNNING,
            trigger_source=trigger_source,
            triggered_by=triggered_by,
            context=context or {},
            started_at=started,
        )
        self.db.add(run)
        await self.db.flush()

        nodes = (workflow.definition or {}).get("nodes", [])
        executed: list[str] = []
        final_status = RunStatus.SUCCEEDED
        error: str | None = None

        for order, node in enumerate(nodes):
            node_id = str(node.get("id", f"node_{order}"))
            node_type = str(node.get("type", "action"))
            step = WorkflowRunStep(
                org_id=org_id,
                run_id=run.id,
                node_id=node_id,
                node_type=node_type,
                step_order=order,
                status=RunStatus.RUNNING,
                input=node.get("config", {}),
                started_at=datetime.utcnow(),
            )
            self.db.add(step)

            if node_type == "condition":
                flag = node.get("config", {}).get("when")
                passed = bool(context.get(flag)) if flag else True
                step.status = RunStatus.SUCCEEDED
                step.output = {"passed": passed}
                step.finished_at = datetime.utcnow()
                if not passed:
                    final_status = RunStatus.SUCCEEDED
                    executed.append(node_id)
                    break
            else:
                step.status = RunStatus.SUCCEEDED
                step.output = {"executed": True, "type": node_type}
                step.finished_at = datetime.utcnow()

            executed.append(node_id)

        finished = datetime.utcnow()
        run.status = final_status
        run.error = error
        run.result = {"executed_nodes": executed, "node_count": len(nodes)}
        run.finished_at = finished
        run.duration_ms = int((finished - started).total_seconds() * 1000)

        workflow.run_count += 1
        workflow.last_run_at = finished
        await self.db.flush()
        return run
