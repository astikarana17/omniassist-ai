"""HTTP middleware: request-id, structured access logs, security headers, rate limiting."""
from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.core.logging import get_logger, org_id_ctx, request_id_ctx, user_id_ctx
from app.core.redis import incr_with_ttl

logger = get_logger("http")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assigns a request id, binds log context and emits access logs."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token_req = request_id_ctx.set(request_id)
        token_org = org_id_ctx.set("-")
        token_user = user_id_ctx.set("-")
        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                "request",
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
            )
            request_id_ctx.reset(token_req)
            org_id_ctx.reset(token_org)
            user_id_ctx.reset(token_user)
        response.headers["X-Request-ID"] = request_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """OWASP-aligned security headers on every response."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        if settings.is_production:
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload"
            )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window-ish fixed-window rate limiter backed by Redis.

    Limits per client IP. Auth endpoints get a stricter bucket.
    """

    _redis_down_until: float = 0.0  # circuit breaker: skip Redis while it's unreachable

    def __init__(self, app, default_limit: int = 120, window: int = 60, auth_limit: int = 20):
        super().__init__(app)
        self.default_limit = default_limit
        self.window = window
        self.auth_limit = auth_limit

    def _client_ip(self, request: Request) -> str:
        fwd = request.headers.get("X-Forwarded-For")
        if fwd:
            return fwd.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/healthz", "/readyz", "/metrics"):
            return await call_next(request)

        ip = self._client_ip(request)
        is_auth = request.url.path.startswith(f"{settings.API_V1_PREFIX}/auth")
        limit = self.auth_limit if is_auth else self.default_limit
        bucket = "auth" if is_auth else "api"
        key = f"ratelimit:{bucket}:{ip}:{int(time.time() // self.window)}"

        # Circuit breaker: if Redis was recently unreachable, skip it (fail-open)
        # without paying the connect timeout on every request.
        now = time.time()
        if now < RateLimitMiddleware._redis_down_until:
            return await call_next(request)
        try:
            count = await incr_with_ttl(key, self.window)
        except Exception:
            RateLimitMiddleware._redis_down_until = now + 30  # back off for 30s
            return await call_next(request)

        if count > limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {"code": "RATE_LIMITED", "message": "Too many requests."},
                    "data": None,
                },
                headers={"Retry-After": str(self.window)},
            )
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - count))
        return response
