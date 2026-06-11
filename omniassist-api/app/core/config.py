"""Application configuration via pydantic-settings (12-factor, env-driven)."""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # --- App ---
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    APP_NAME: str = "OmniAssist AI"
    # Demo: when set, new signups join this existing org (by slug) instead of
    # creating a fresh empty workspace — so anyone can log in and see the demo data.
    DEMO_ORG_SLUG: str = ""
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = Field(min_length=16)
    LOG_LEVEL: str = "INFO"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # --- Database ---
    DATABASE_URL: str
    DATABASE_SYNC_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # --- JWT ---
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # --- Encryption ---
    ENCRYPTION_KEY: str = ""

    # --- Google OAuth ---
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/auth/callback"

    # --- GitHub OAuth ---
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:3000/auth/callback"

    # --- Claude ---
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-opus-4-8"
    CLAUDE_FAST_MODEL: str = "claude-haiku-4-5-20251001"
    CLAUDE_MAX_TOKENS: int = 2048

    # --- OpenRouter (OpenAI-compatible LLM gateway) — used for grounded RAG answers ---
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct:free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # --- Pinecone ---
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX: str = "omniassist-kb"
    PINECONE_HOST: str = ""
    EMBEDDING_DIM: int = 1024

    # --- Twilio ---
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""
    TWILIO_VOICE_NUMBER: str = ""

    # --- Email ---
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "support@omniassist.ai"

    # --- Slack ---
    SLACK_BOT_TOKEN: str = ""
    SLACK_DEFAULT_CHANNEL: str = "#support"

    # --- Observability ---
    SENTRY_DSN: str = ""

    # --- Storage ---
    STORAGE_BUCKET: str = "omniassist-uploads"
    MAX_UPLOAD_MB: int = 25

    # --- Billing (Stripe) ---
    APP_URL: str = "http://localhost:3000"
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_STARTER: str = ""   # Stripe Price ID for the Starter plan
    STRIPE_PRICE_GROWTH: str = ""    # Stripe Price ID for the Growth plan

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
