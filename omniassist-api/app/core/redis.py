"""Shared async Redis client + helpers (cache, rate-limit counters, pub/sub)."""
from __future__ import annotations

from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings

_redis: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            health_check_interval=30,
            # Fail fast when Redis is unavailable so callers (e.g. the rate limiter,
            # which fails open) don't block on the OS connect timeout (~5s).
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
            retry_on_timeout=False,
        )
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None


async def cache_get(key: str) -> str | None:
    return await get_redis().get(key)


async def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    await get_redis().set(key, value, ex=ttl_seconds)


async def cache_delete(*keys: str) -> None:
    if keys:
        await get_redis().delete(*keys)


async def incr_with_ttl(key: str, ttl_seconds: int) -> int:
    """Atomic counter used by the rate limiter; sets TTL on first increment."""
    redis = get_redis()
    async with redis.pipeline(transaction=True) as pipe:
        pipe.incr(key)
        pipe.expire(key, ttl_seconds, nx=True)
        result = await pipe.execute()
    return int(result[0])
