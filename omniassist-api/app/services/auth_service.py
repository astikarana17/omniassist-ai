"""Authentication & session management business logic."""
from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.core.permissions import Role
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.agent import AiAgent
from app.models.enums import AgentType
from app.models.organization import Membership, Organization
from app.models.user import Device, PasswordResetToken, Session, User
from app.services.audit_service import record_audit

logger = get_logger("auth")

_SUPPORT_PROMPT = (
    "You are OmniAssist, the AI customer support agent. Ground every answer in the "
    "knowledge base and cite sources. Be warm, concise and empathetic. If confidence "
    "is low or the customer asks for a human, hand off gracefully. Never invent policies."
)
_SALES_PROMPT = (
    "You are OmniAssist Sales, the AI sales development agent. Qualify visitors using "
    "BANT, answer product and pricing questions from the knowledge base, book demos when "
    "intent is high, and hand hot leads to the sales team. Be persuasive but never pushy."
)


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or f"org-{uuid.uuid4().hex[:8]}"


def _device_name_from_ua(user_agent: str | None) -> str | None:
    """Best-effort human-friendly device label from a User-Agent string."""
    if not user_agent:
        return None
    ua = user_agent.lower()
    browser = next(
        (b.title() for b in ("edg", "chrome", "firefox", "safari") if b in ua), "Browser"
    )
    if browser == "Edg":
        browser = "Edge"
    os_name = next(
        (o for o in ("Windows", "Mac", "Linux", "Android", "iPhone") if o.lower() in ua),
        "Unknown OS",
    )
    return f"{browser} on {os_name}"


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ---------- helpers ----------
    async def _unique_slug(self, base: str) -> str:
        slug = _slugify(base)
        candidate = slug
        i = 1
        while (
            await self.db.execute(select(Organization.id).where(Organization.slug == candidate))
        ).scalar_one_or_none() is not None:
            i += 1
            candidate = f"{slug}-{i}"
        return candidate

    async def _seed_default_agents(self, org_id: uuid.UUID) -> None:
        self.db.add_all(
            [
                AiAgent(
                    org_id=org_id,
                    type=AgentType.SUPPORT,
                    name="Support Agent",
                    system_prompt=_SUPPORT_PROMPT,
                    model=settings.CLAUDE_MODEL,
                    tools=[
                        {"key": "kb_search", "enabled": True},
                        {"key": "create_ticket", "enabled": True},
                        {"key": "escalate", "enabled": True},
                    ],
                    languages=["auto"],
                ),
                AiAgent(
                    org_id=org_id,
                    type=AgentType.SALES,
                    name="Sales Agent",
                    system_prompt=_SALES_PROMPT,
                    model=settings.CLAUDE_MODEL,
                    tools=[
                        {"key": "kb_search", "enabled": True},
                        {"key": "qualify_lead", "enabled": True},
                        {"key": "book_demo", "enabled": True},
                    ],
                    languages=["auto"],
                ),
            ]
        )

    async def _issue_tokens(
        self,
        user: User,
        org_id: uuid.UUID,
        role: str,
        *,
        ip: str | None,
        user_agent: str | None,
        device: Device | None,
    ) -> tuple[str, str]:
        access = create_access_token(str(user.id), org_id=str(org_id), role=role)
        refresh, jti, expires = create_refresh_token(str(user.id))
        session = Session(
            user_id=user.id,
            device_id=device.id if device else None,
            refresh_jti=jti,
            refresh_token_hash=hash_token(refresh),
            expires_at=expires,
            ip_address=ip,
            user_agent=user_agent,
            last_used_at=datetime.now(UTC),
        )
        self.db.add(session)
        await self.db.flush()
        return access, refresh

    async def _resolve_device(
        self, user_id: uuid.UUID, fingerprint: str | None, ip: str | None, user_agent: str | None
    ) -> Device | None:
        """Find-or-create the device for this fingerprint and refresh its last-seen."""
        if not fingerprint:
            return None
        device = (
            await self.db.execute(
                select(Device).where(
                    Device.user_id == user_id, Device.fingerprint == fingerprint
                )
            )
        ).scalar_one_or_none()
        if device is None:
            device = Device(
                user_id=user_id,
                fingerprint=fingerprint,
                name=_device_name_from_ua(user_agent),
            )
            self.db.add(device)
        device.last_ip = ip
        device.last_seen_at = datetime.now(UTC)
        await self.db.flush()
        return device

    # ---------- public API ----------
    async def signup(
        self,
        *,
        full_name: str,
        email: str,
        password: str,
        workspace_name: str,
        ip: str | None = None,
        user_agent: str | None = None,
        fingerprint: str | None = None,
    ) -> tuple[User, Organization, str, str, str]:
        existing = (
            await self.db.execute(select(User).where(User.email == email.lower()))
        ).scalar_one_or_none()
        if existing:
            raise ConflictError("An account with this email already exists.", code="EMAIL_TAKEN")

        user = User(
            email=email.lower(),
            full_name=full_name,
            hashed_password=hash_password(password),
            auth_provider="email",
            is_email_verified=False,
        )
        self.db.add(user)
        await self.db.flush()

        # Demo mode: join an existing shared org so any new signup sees the demo
        # data; otherwise create a fresh workspace.
        demo_org = None
        if settings.DEMO_ORG_SLUG:
            demo_org = (
                await self.db.execute(
                    select(Organization).where(Organization.slug == settings.DEMO_ORG_SLUG)
                )
            ).scalar_one_or_none()

        if demo_org is not None:
            org = demo_org
            role = Role.ADMIN
        else:
            org = Organization(name=workspace_name, slug=await self._unique_slug(workspace_name))
            self.db.add(org)
            await self.db.flush()
            role = Role.SUPER_ADMIN

        membership = Membership(org_id=org.id, user_id=user.id, role=role, status="active")
        self.db.add(membership)
        if demo_org is None:
            await self._seed_default_agents(org.id)

        device = await self._resolve_device(user.id, fingerprint, ip, user_agent)
        access, refresh = await self._issue_tokens(
            user, org.id, role, ip=ip, user_agent=user_agent, device=device
        )
        user.last_login_at = datetime.now(UTC)
        await record_audit(
            self.db,
            org_id=org.id,
            actor_id=user.id,
            actor_name=user.full_name,
            action="signup",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=ip,
            user_agent=user_agent,
        )
        logger.info("signup", user_id=str(user.id), org_id=str(org.id))
        return user, org, role, access, refresh

    async def login(
        self,
        *,
        email: str,
        password: str,
        ip: str | None = None,
        user_agent: str | None = None,
        fingerprint: str | None = None,
    ) -> tuple[User, Organization, str, str, str]:
        user = (
            await self.db.execute(select(User).where(User.email == email.lower()))
        ).scalar_one_or_none()
        if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password.", code="BAD_CREDENTIALS")
        if not user.is_active:
            raise AuthenticationError("Account is disabled.", code="ACCOUNT_DISABLED")

        membership, org = await self._primary_membership(user.id)
        device = await self._resolve_device(user.id, fingerprint, ip, user_agent)
        access, refresh = await self._issue_tokens(
            user, org.id, membership.role, ip=ip, user_agent=user_agent, device=device
        )
        user.last_login_at = datetime.now(UTC)
        await record_audit(
            self.db,
            org_id=org.id,
            actor_id=user.id,
            actor_name=user.full_name,
            action="login",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=ip,
            user_agent=user_agent,
        )
        return user, org, membership.role, access, refresh

    async def _primary_membership(self, user_id: uuid.UUID) -> tuple[Membership, Organization]:
        row = (
            await self.db.execute(
                select(Membership, Organization)
                .join(Organization, Organization.id == Membership.org_id)
                .where(Membership.user_id == user_id, Membership.status == "active")
                .order_by(Membership.created_at.asc())
                .limit(1)
            )
        ).first()
        if not row:
            raise AuthenticationError("No active organization for this user.")
        return row[0], row[1]

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        from app.core.security import decode_token

        payload = decode_token(refresh_token, expected_type="refresh")
        jti = payload.get("jti")
        user_id = payload.get("sub")
        session = (
            await self.db.execute(select(Session).where(Session.refresh_jti == jti))
        ).scalar_one_or_none()
        if not session or session.revoked:
            raise AuthenticationError("Refresh token revoked.", code="REFRESH_REVOKED")
        if session.refresh_token_hash != hash_token(refresh_token):
            # Token reuse / theft → revoke the whole session.
            session.revoked = True
            session.revoked_at = datetime.now(UTC)
            raise AuthenticationError("Refresh token mismatch.", code="REFRESH_REUSE")
        if session.expires_at < datetime.now(UTC):
            raise AuthenticationError("Refresh token expired.", code="REFRESH_EXPIRED")

        user = await self.db.get(User, uuid.UUID(user_id))
        if not user or not user.is_active:
            raise AuthenticationError("User inactive.")
        membership, org = await self._primary_membership(user.id)

        # Rotate: issue a new refresh token, revoke the old jti.
        access = create_access_token(str(user.id), org_id=str(org.id), role=membership.role)
        new_refresh, new_jti, expires = create_refresh_token(str(user.id))
        session.refresh_jti = new_jti
        session.refresh_token_hash = hash_token(new_refresh)
        session.expires_at = expires
        session.last_used_at = datetime.now(UTC)
        return access, new_refresh

    async def logout(self, user_id: uuid.UUID, refresh_token: str | None) -> None:
        query = select(Session).where(Session.user_id == user_id, Session.revoked.is_(False))
        if refresh_token:
            query = query.where(Session.refresh_token_hash == hash_token(refresh_token))
        sessions = (await self.db.execute(query)).scalars().all()
        for s in sessions:
            s.revoked = True
            s.revoked_at = datetime.now(UTC)

    async def list_sessions(self, user_id: uuid.UUID) -> list[Session]:
        return list(
            (
                await self.db.execute(
                    select(Session)
                    .where(Session.user_id == user_id)
                    .order_by(Session.created_at.desc())
                )
            )
            .scalars()
            .all()
        )

    async def revoke_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> None:
        session = await self.db.get(Session, session_id)
        if not session or session.user_id != user_id:
            raise NotFoundError("Session not found.")
        session.revoked = True
        session.revoked_at = datetime.now(UTC)

    async def forgot_password(self, email: str) -> str | None:
        """Returns the raw reset token (to email). None if user doesn't exist (no enumeration)."""
        user = (
            await self.db.execute(select(User).where(User.email == email.lower()))
        ).scalar_one_or_none()
        if not user:
            return None
        raw = generate_token()
        self.db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hash_token(raw),
                expires_at=datetime.now(UTC) + timedelta(hours=1),
            )
        )
        return raw

    async def reset_password(self, token: str, new_password: str) -> None:
        record = (
            await self.db.execute(
                select(PasswordResetToken).where(
                    PasswordResetToken.token_hash == hash_token(token)
                )
            )
        ).scalar_one_or_none()
        if not record or record.used or record.expires_at < datetime.now(UTC):
            raise ValidationError("Invalid or expired reset token.", code="RESET_INVALID")
        user = await self.db.get(User, record.user_id)
        if not user:
            raise NotFoundError("User not found.")
        user.hashed_password = hash_password(new_password)
        record.used = True
        # Revoke all sessions on password change.
        for s in await self.list_sessions(user.id):
            s.revoked = True
            s.revoked_at = datetime.now(UTC)

    async def google_login(
        self,
        code: str,
        *,
        workspace_name: str | None,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, Organization, str, str, str]:
        profile = await self._exchange_google_code(code)
        email = profile["email"].lower()
        user = (
            await self.db.execute(select(User).where(User.email == email))
        ).scalar_one_or_none()
        created = False
        if not user:
            user = User(
                email=email,
                full_name=profile.get("name", email.split("@")[0]),
                avatar_url=profile.get("picture"),
                auth_provider="google",
                google_sub=profile.get("sub"),
                is_email_verified=True,
            )
            self.db.add(user)
            await self.db.flush()
            created = True

        if created:
            org = Organization(
                name=workspace_name or f"{user.full_name}'s Workspace",
                slug=await self._unique_slug(workspace_name or user.full_name),
            )
            self.db.add(org)
            await self.db.flush()
            self.db.add(
                Membership(org_id=org.id, user_id=user.id, role=Role.SUPER_ADMIN, status="active")
            )
            await self._seed_default_agents(org.id)
            role = Role.SUPER_ADMIN
        else:
            membership, org = await self._primary_membership(user.id)
            role = Role(membership.role)

        device = await self._resolve_device(user.id, None, ip, user_agent)
        access, refresh = await self._issue_tokens(
            user, org.id, role, ip=ip, user_agent=user_agent, device=device
        )
        user.last_login_at = datetime.now(UTC)
        return user, org, role, access, refresh

    async def _exchange_google_code(self, code: str) -> dict:
        async with httpx.AsyncClient(timeout=15) as client:
            token_resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            if token_resp.status_code != 200:
                raise AuthenticationError("Google authentication failed.", code="OAUTH_FAILED")
            access_token = token_resp.json()["access_token"]
            info = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            return info.json()

    async def github_login(
        self,
        code: str,
        *,
        workspace_name: str | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, Organization, str, str, str]:
        profile = await self._exchange_github_code(code)
        return await self._oauth_login(
            profile, provider="github", workspace_name=workspace_name, ip=ip, user_agent=user_agent
        )

    async def _oauth_login(
        self, profile: dict, *, provider: str, workspace_name: str | None,
        ip: str | None, user_agent: str | None,
    ) -> tuple[User, Organization, str, str, str]:
        """Shared upsert-then-login for OAuth providers (matches by email)."""
        email = profile["email"].lower()
        user = (
            await self.db.execute(select(User).where(User.email == email))
        ).scalar_one_or_none()
        created = False
        if not user:
            user = User(
                email=email,
                full_name=profile.get("name") or email.split("@")[0],
                avatar_url=profile.get("avatar_url"),
                auth_provider=provider,
                is_email_verified=True,
            )
            self.db.add(user)
            await self.db.flush()
            created = True

        if created:
            org = Organization(
                name=workspace_name or f"{user.full_name}'s Workspace",
                slug=await self._unique_slug(workspace_name or user.full_name),
            )
            self.db.add(org)
            await self.db.flush()
            self.db.add(
                Membership(org_id=org.id, user_id=user.id, role=Role.SUPER_ADMIN, status="active")
            )
            await self._seed_default_agents(org.id)
            role = Role.SUPER_ADMIN
        else:
            membership, org = await self._primary_membership(user.id)
            role = Role(membership.role)

        device = await self._resolve_device(user.id, None, ip, user_agent)
        access, refresh = await self._issue_tokens(
            user, org.id, role, ip=ip, user_agent=user_agent, device=device
        )
        user.last_login_at = datetime.now(UTC)
        return user, org, role, access, refresh

    async def _exchange_github_code(self, code: str) -> dict:
        async with httpx.AsyncClient(timeout=15) as client:
            token_resp = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "code": code,
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "redirect_uri": settings.GITHUB_REDIRECT_URI,
                },
            )
            access_token = token_resp.json().get("access_token") if token_resp.status_code == 200 else None
            if not access_token:
                raise AuthenticationError("GitHub authentication failed.", code="OAUTH_FAILED")
            headers = {"Authorization": f"Bearer {access_token}",
                       "Accept": "application/vnd.github+json"}
            u = (await client.get("https://api.github.com/user", headers=headers)).json()
            email = u.get("email")
            if not email:
                emails = (await client.get("https://api.github.com/user/emails", headers=headers)).json()
                primary = next(
                    (e for e in emails if e.get("primary") and e.get("verified")), None
                ) or (emails[0] if emails else None)
                email = primary["email"] if primary else None
            if not email:
                raise AuthenticationError("Could not read your GitHub email.", code="OAUTH_NO_EMAIL")
            return {"email": email, "name": u.get("name") or u.get("login"),
                    "avatar_url": u.get("avatar_url")}
