"""FastAPI dependencies: auth context, RBAC guards, pagination."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.logging import org_id_ctx, user_id_ctx
from app.core.permissions import Permission, Role, has_permission
from app.core.security import decode_token
from app.models.organization import Membership
from app.models.user import User

DbSession = Annotated[AsyncSession, Depends(get_db)]


@dataclass
class AuthContext:
    user: User
    org_id: uuid.UUID
    role: Role
    membership_id: uuid.UUID

    def require(self, permission: Permission) -> None:
        if self.user.is_superuser:
            return
        if not has_permission(self.role, permission):
            raise PermissionDeniedError(
                f"Missing permission: {permission.value}", details={"required": permission.value}
            )


def _bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthenticationError("Missing bearer token.")
    return authorization.split(" ", 1)[1].strip()


async def get_current_context(
    request: Request,
    db: DbSession,
    authorization: Annotated[str | None, Header()] = None,
) -> AuthContext:
    """Resolve the authenticated user + active org membership from the access JWT.

    The org is taken from the ``org_id`` JWT claim (set at login / org-switch) and
    re-verified against the membership table — never trusted from the request body.
    """
    token = _bearer_token(authorization)
    payload = decode_token(token, expected_type="access")
    user_id = payload.get("sub")
    org_claim = payload.get("org_id")
    if not user_id or not org_claim:
        raise AuthenticationError("Invalid token claims.")

    user = await db.get(User, uuid.UUID(user_id))
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive.")

    membership = (
        await db.execute(
            select(Membership).where(
                Membership.user_id == user.id,
                Membership.org_id == uuid.UUID(org_claim),
                Membership.status == "active",
            )
        )
    ).scalar_one_or_none()
    if not membership:
        raise AuthenticationError("No active membership for this organization.")

    # Bind log context for the rest of the request.
    org_id_ctx.set(str(membership.org_id))
    user_id_ctx.set(str(user.id))

    return AuthContext(
        user=user,
        org_id=membership.org_id,
        role=Role(membership.role),
        membership_id=membership.id,
    )


CurrentContext = Annotated[AuthContext, Depends(get_current_context)]


def require_permission(permission: Permission):
    """Route guard factory: ``deps = [Depends(require_permission(Permission.X))]``."""

    async def _guard(ctx: CurrentContext) -> AuthContext:
        ctx.require(permission)
        return ctx

    return _guard


def require_role(*roles: Role):
    async def _guard(ctx: CurrentContext) -> AuthContext:
        if ctx.user.is_superuser:
            return ctx
        if ctx.role not in roles:
            raise PermissionDeniedError("Insufficient role.")
        return ctx

    return _guard


def require_feature(feature: str):
    """Plan gate: allow only if the org's subscription plan includes ``feature``."""

    async def _guard(ctx: CurrentContext, db: DbSession) -> AuthContext:
        if ctx.user.is_superuser:
            return ctx
        from app.models.organization import Organization
        from app.services.billing_service import has_feature

        org = await db.get(Organization, ctx.org_id)
        if not org or not has_feature(org.plan, feature):
            raise PermissionDeniedError(
                f"Your plan doesn't include this feature ({feature}). Please upgrade.",
                details={"feature": feature, "upgrade_required": True},
            )
        return ctx

    return _guard


@dataclass
class Pagination:
    limit: int
    offset: int
    cursor: str | None


def pagination(
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    cursor: Annotated[str | None, Query()] = None,
) -> Pagination:
    return Pagination(limit=limit, offset=offset, cursor=cursor)


PaginationDep = Annotated[Pagination, Depends(pagination)]
