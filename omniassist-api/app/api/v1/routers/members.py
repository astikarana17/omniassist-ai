"""Team member & RBAC management routes."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.core.deps import CurrentContext, DbSession, require_permission
from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from app.core.permissions import Permission, Role, can_manage_role
from app.models.organization import Membership
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.domain import InviteRequest, MemberOut, RoleChangeRequest
from app.services.audit_service import record_audit

router = APIRouter(prefix="/members", tags=["Team"])


@router.get("", response_model=list[MemberOut])
async def list_members(
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.MEMBER_READ)),
) -> list[MemberOut]:
    rows = (
        await db.execute(
            select(Membership, User)
            .join(User, User.id == Membership.user_id)
            .where(Membership.org_id == ctx.org_id)
            .order_by(Membership.created_at)
        )
    ).all()
    return [
        MemberOut(
            id=m.id, user_id=m.user_id, role=m.role, status=m.status,
            created_at=m.created_at, name=u.full_name, email=u.email,
            avatar_url=u.avatar_url,
        )
        for m, u in rows
    ]


@router.post("/invite", response_model=MessageResponse, status_code=201)
async def invite_member(
    payload: InviteRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.MEMBER_INVITE)),
) -> MessageResponse:
    try:
        target_role = Role(payload.role)
    except ValueError as exc:
        raise ValidationError("Invalid role.") from exc
    if not can_manage_role(ctx.role, target_role) and not ctx.user.is_superuser:
        raise PermissionDeniedError("You cannot assign a role at or above your own.")

    user = (
        await db.execute(select(User).where(User.email == payload.email.lower()))
    ).scalar_one_or_none()
    if user is None:
        user = User(email=payload.email.lower(), full_name=payload.email.split("@")[0])
        db.add(user)
        await db.flush()

    existing = (
        await db.execute(
            select(Membership).where(
                Membership.org_id == ctx.org_id, Membership.user_id == user.id
            )
        )
    ).scalar_one_or_none()
    if existing:
        raise ConflictError("User is already a member.")

    db.add(
        Membership(
            org_id=ctx.org_id, user_id=user.id, role=target_role, status="invited",
            invited_by=ctx.user.id,
        )
    )
    await record_audit(
        db, org_id=ctx.org_id, actor_id=ctx.user.id, actor_name=ctx.user.full_name,
        action="invited member", resource_type="team", resource_id=payload.email,
        detail=f"Role: {payload.role}",
    )
    from app.workers.tasks import send_invite_email

    # Commit the membership BEFORE enqueueing the email so a fast worker can't
    # process the invite before the row exists (and so we don't email on rollback).
    await db.commit()
    send_invite_email.delay(payload.email, ctx.user.full_name, payload.role)
    return MessageResponse(message="Invitation sent.")


@router.patch("/{membership_id}/role", response_model=MemberOut)
async def change_role(
    membership_id: uuid.UUID,
    payload: RoleChangeRequest,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.MEMBER_MANAGE)),
) -> MemberOut:
    membership = await db.get(Membership, membership_id)
    if not membership or membership.org_id != ctx.org_id:
        raise NotFoundError("Member not found.")
    try:
        new_role = Role(payload.role)
    except ValueError as exc:
        raise ValidationError("Invalid role.") from exc
    if not ctx.user.is_superuser and (
        not can_manage_role(ctx.role, new_role)
        or not can_manage_role(ctx.role, Role(membership.role))
    ):
        raise PermissionDeniedError("Insufficient privileges to change this role.")
    previous = membership.role
    membership.role = new_role
    await record_audit(
        db, org_id=ctx.org_id, actor_id=ctx.user.id, actor_name=ctx.user.full_name,
        action="changed role", resource_type="user", resource_id=str(membership.user_id),
        diff={"from": previous, "to": new_role.value},
    )
    return MemberOut.model_validate(membership)


@router.delete("/{membership_id}", response_model=MessageResponse)
async def remove_member(
    membership_id: uuid.UUID,
    ctx: CurrentContext,
    db: DbSession,
    _: object = Depends(require_permission(Permission.MEMBER_MANAGE)),
) -> MessageResponse:
    membership = await db.get(Membership, membership_id)
    if not membership or membership.org_id != ctx.org_id:
        raise NotFoundError("Member not found.")
    if membership.user_id == ctx.user.id:
        raise ValidationError("You cannot remove yourself.")
    await db.delete(membership)
    await record_audit(
        db, org_id=ctx.org_id, actor_id=ctx.user.id, actor_name=ctx.user.full_name,
        action="removed member", resource_type="user", resource_id=str(membership.user_id),
    )
    return MessageResponse(message="Member removed.")
