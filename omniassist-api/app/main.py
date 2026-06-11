"""FastAPI application factory: middleware, lifespan, health, metrics, routes."""
from __future__ import annotations

from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import (
    RateLimitMiddleware,
    RequestContextMiddleware,
    SecurityHeadersMiddleware,
)
from app.core.permissions import permission_matrix
from app.core.redis import close_redis, get_redis

logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.LOG_LEVEL, json_logs=settings.is_production)
    if settings.SENTRY_DSN:
        sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT, traces_sample_rate=0.1)
    logger.info("startup", env=settings.ENVIRONMENT, app=settings.APP_NAME)
    yield
    await close_redis()
    await engine.dispose()
    logger.info("shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Enterprise AI Customer Support & Sales backend.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Middleware (order matters: context → security → rate limit → CORS).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/healthz", tags=["System"])
    async def healthz():
        return {"status": "ok", "service": settings.APP_NAME, "version": "1.0.0"}

    @app.get("/readyz", tags=["System"])
    async def readyz():
        checks = {"database": False, "redis": False}
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            checks["database"] = True
        except Exception as exc:  # noqa: BLE001
            logger.warning("readyz_db_fail", error=str(exc))
        try:
            await get_redis().ping()
            checks["redis"] = True
        except Exception as exc:  # noqa: BLE001
            logger.warning("readyz_redis_fail", error=str(exc))
        ready = all(checks.values())
        return {"ready": ready, "checks": checks}

    @app.get("/metrics", tags=["System"])
    async def metrics():
        return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.get(f"{settings.API_V1_PREFIX}/rbac/matrix", tags=["System"])
    async def rbac_matrix():
        return {"data": permission_matrix(), "error": None}

    return app


app = create_app()
