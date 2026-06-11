"""Auth request/response schemas (Pydantic v2)."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class SignupRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    workspace_name: str = Field(min_length=2, max_length=160)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class GoogleCallbackRequest(BaseModel):
    code: str
    workspace_name: str | None = None


class GithubCallbackRequest(BaseModel):
    code: str
    workspace_name: str | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # access token lifetime, seconds


class OrgSummary(ORMModel):
    id: uuid.UUID
    name: str
    slug: str
    role: str


class UserOut(ORMModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    avatar_url: str | None = None
    title: str | None = None
    is_email_verified: bool
    mfa_enabled: bool
    last_login_at: datetime | None = None


class AuthResponse(BaseModel):
    user: UserOut
    organization: OrgSummary
    tokens: TokenPair


class SessionOut(ORMModel):
    id: uuid.UUID
    ip_address: str | None = None
    user_agent: str | None = None
    last_used_at: datetime | None = None
    created_at: datetime
    revoked: bool


class DeviceOut(ORMModel):
    id: uuid.UUID
    name: str | None = None
    os: str | None = None
    browser: str | None = None
    last_seen_at: datetime | None = None
    is_trusted: bool
