"""Authentication routes: signup, login, refresh, logout, OAuth, password, sessions."""
from __future__ import annotations

from fastapi import APIRouter, Request, status

from app.core.config import settings
from app.core.deps import CurrentContext, DbSession
from app.schemas.auth import (
    AuthResponse,
    DeviceOut,
    ForgotPasswordRequest,
    GithubCallbackRequest,
    GoogleCallbackRequest,
    LoginRequest,
    OrgSummary,
    RefreshRequest,
    ResetPasswordRequest,
    SessionOut,
    SignupRequest,
    TokenPair,
    UserOut,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _client(request: Request) -> tuple[str | None, str | None, str | None]:
    fwd = request.headers.get("X-Forwarded-For")
    ip = fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else None)
    return ip, request.headers.get("User-Agent"), request.headers.get("X-Device-Fingerprint")


def _auth_response(user, org, role: str, access: str, refresh: str) -> AuthResponse:
    return AuthResponse(
        user=UserOut.model_validate(user),
        organization=OrgSummary(id=org.id, name=org.name, slug=org.slug, role=role),
        tokens=TokenPair(
            access_token=access,
            refresh_token=refresh,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
    )


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, request: Request, db: DbSession) -> AuthResponse:
    ip, ua, fp = _client(request)
    user, org, role, access, refresh = await AuthService(db).signup(
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password,
        workspace_name=payload.workspace_name,
        ip=ip,
        user_agent=ua,
        fingerprint=fp,
    )
    return _auth_response(user, org, role, access, refresh)


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, request: Request, db: DbSession) -> AuthResponse:
    ip, ua, fp = _client(request)
    user, org, role, access, refresh = await AuthService(db).login(
        email=payload.email, password=payload.password, ip=ip, user_agent=ua, fingerprint=fp
    )
    return _auth_response(user, org, role, access, refresh)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, db: DbSession) -> TokenPair:
    access, refresh_token = await AuthService(db).refresh(payload.refresh_token)
    return TokenPair(
        access_token=access,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    payload: RefreshRequest, ctx: CurrentContext, db: DbSession
) -> MessageResponse:
    await AuthService(db).logout(ctx.user.id, payload.refresh_token)
    return MessageResponse(message="Logged out.")


@router.post("/google/callback", response_model=AuthResponse)
async def google_callback(
    payload: GoogleCallbackRequest, request: Request, db: DbSession
) -> AuthResponse:
    ip, ua, _ = _client(request)
    user, org, role, access, refresh = await AuthService(db).google_login(
        payload.code, workspace_name=payload.workspace_name, ip=ip, user_agent=ua
    )
    return _auth_response(user, org, role, access, refresh)


@router.post("/github/callback", response_model=AuthResponse)
async def github_callback(
    payload: GithubCallbackRequest, request: Request, db: DbSession
) -> AuthResponse:
    ip, ua, _ = _client(request)
    user, org, role, access, refresh = await AuthService(db).github_login(
        payload.code, workspace_name=payload.workspace_name, ip=ip, user_agent=ua
    )
    return _auth_response(user, org, role, access, refresh)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(payload: ForgotPasswordRequest, db: DbSession) -> MessageResponse:
    token = await AuthService(db).forgot_password(payload.email)
    if token:
        # Enqueued email delivery happens in the notification worker.
        from app.workers.tasks import send_password_reset_email

        send_password_reset_email.delay(payload.email, token)
    # Always return the same response (no account enumeration).
    return MessageResponse(message="If an account exists, a reset link has been sent.")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(payload: ResetPasswordRequest, db: DbSession) -> MessageResponse:
    await AuthService(db).reset_password(payload.token, payload.new_password)
    return MessageResponse(message="Password updated. Please sign in again.")


@router.get("/me", response_model=UserOut)
async def me(ctx: CurrentContext) -> UserOut:
    return UserOut.model_validate(ctx.user)


@router.get("/sessions", response_model=list[SessionOut])
async def list_sessions(ctx: CurrentContext, db: DbSession) -> list[SessionOut]:
    sessions = await AuthService(db).list_sessions(ctx.user.id)
    return [SessionOut.model_validate(s) for s in sessions]


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def revoke_session(session_id, ctx: CurrentContext, db: DbSession) -> MessageResponse:
    await AuthService(db).revoke_session(ctx.user.id, session_id)
    return MessageResponse(message="Session revoked.")


@router.get("/devices", response_model=list[DeviceOut])
async def list_devices(ctx: CurrentContext, db: DbSession) -> list[DeviceOut]:
    from sqlalchemy import select

    from app.models.user import Device

    devices = (
        (await db.execute(select(Device).where(Device.user_id == ctx.user.id))).scalars().all()
    )
    return [DeviceOut.model_validate(d) for d in devices]
