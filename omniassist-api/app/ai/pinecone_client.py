"""Pinecone access with integrated inference (server-side multilingual embeddings).

The index ``omniassist-kb`` was created with integrated inference
(model = multilingual-e5-large, dim 1024), so we upsert/search raw text records and
Pinecone performs embedding server-side. Tenant isolation = one namespace per org_id.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from pinecone import Pinecone

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("pinecone")


@lru_cache
def _pc() -> Pinecone:
    return Pinecone(api_key=settings.PINECONE_API_KEY)


@lru_cache
def _index():
    return _pc().Index(host=settings.PINECONE_HOST) if settings.PINECONE_HOST else _pc().Index(
        settings.PINECONE_INDEX
    )


def upsert_records(namespace: str, records: list[dict[str, Any]]) -> None:
    """Upsert text records (server-side embedding). Each record needs ``_id`` and ``text``."""
    if not records:
        return
    index = _index()
    # Pinecone integrated-inference upsert is capped per request; batch in chunks of 96.
    for i in range(0, len(records), 96):
        index.upsert_records(namespace=namespace, records=records[i : i + 96])
    logger.info("pinecone_upsert", namespace=namespace, count=len(records))


def search(namespace: str, query: str, top_k: int = 5, flt: dict | None = None) -> list[dict]:
    """Semantic search via integrated inference. Returns hits with id/score/fields.

    The Pinecone SDK returns a response object (not a plain dict); normalize both
    object- and dict-shaped responses.
    """
    index = _index()
    payload: dict[str, Any] = {"inputs": {"text": query}, "top_k": top_k}
    if flt:
        payload["filter"] = flt
    result = index.search(namespace=namespace, query=payload)

    if hasattr(result, "to_dict"):
        result = result.to_dict()
    if isinstance(result, dict):
        hits = result.get("result", {}).get("hits", [])
    else:  # attribute-style response object
        inner = getattr(result, "result", None)
        hits = getattr(inner, "hits", []) if inner is not None else []

    def _pick(obj: Any, *keys: str) -> Any:
        for k in keys:
            v = obj.get(k) if isinstance(obj, dict) else getattr(obj, k, None)
            if v is not None:
                return v
        return None

    out: list[dict] = []
    for h in hits:
        fields = _pick(h, "fields") or {}
        if hasattr(fields, "to_dict"):
            fields = fields.to_dict()
        score = _pick(h, "_score", "score_", "score")
        out.append({
            "id": _pick(h, "_id", "id_", "id"),
            "score": float(score) if score is not None else 0.0,
            "text": fields.get("text", ""),
            "metadata": {k: v for k, v in fields.items() if k != "text"},
        })
    return out


def delete_records(namespace: str, ids: list[str]) -> None:
    if ids:
        _index().delete(ids=ids, namespace=namespace)


def delete_namespace(namespace: str) -> None:
    try:
        _index().delete(delete_all=True, namespace=namespace)
    except Exception as exc:  # noqa: BLE001
        logger.warning("pinecone_delete_ns_fail", namespace=namespace, error=str(exc))
