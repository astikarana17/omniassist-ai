"""Append-only audit logging."""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ops import AuditLog


async def record_audit(
    db: AsyncSession,
    *,
    action: str,
    resource_type: str,
    org_id: uuid.UUID | None = None,
    actor_id: uuid.UUID | None = None,
    actor_name: str | None = None,
    resource_id: str | None = None,
    detail: str | None = None,
    diff: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    """Write an immutable audit entry. Never updated or deleted."""
    entry = AuditLog(
        org_id=org_id,
        actor_id=actor_id,
        actor_name=actor_name,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        detail=detail,
        diff=diff or {},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(entry)
    await db.flush()
    return entry
