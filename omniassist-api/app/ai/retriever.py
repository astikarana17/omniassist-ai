"""RAG retrieval: tenant-scoped semantic search over the knowledge base."""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.ai import pinecone_client
from app.core.logging import get_logger

logger = get_logger("retriever")


@dataclass
class RetrievedChunk:
    chunk_id: str
    document_id: str
    title: str
    text: str
    score: float


def namespace_for(org_id: uuid.UUID | str) -> str:
    return f"org_{org_id}"


async def retrieve(
    org_id: uuid.UUID | str, query: str, top_k: int = 5, min_score: float = 0.30
) -> list[RetrievedChunk]:
    """Retrieve the most relevant KB chunks for a query within an org's namespace."""
    ns = namespace_for(org_id)
    try:
        hits = pinecone_client.search(ns, query, top_k=top_k)
    except Exception as exc:  # noqa: BLE001
        logger.warning("retrieve_failed", org_id=str(org_id), error=str(exc))
        return []

    chunks: list[RetrievedChunk] = []
    for h in hits:
        score = float(h.get("score") or 0.0)
        if score < min_score:
            continue
        meta = h.get("metadata", {})
        chunks.append(
            RetrievedChunk(
                chunk_id=h.get("id", ""),
                document_id=str(meta.get("document_id", "")),
                title=str(meta.get("title", "Knowledge Base")),
                text=h.get("text", ""),
                score=score,
            )
        )
    return chunks


def format_context(chunks: list[RetrievedChunk]) -> str:
    """Render retrieved chunks into a grounding block for the LLM prompt."""
    if not chunks:
        return "No relevant knowledge base entries were found."
    blocks = []
    for i, c in enumerate(chunks, 1):
        blocks.append(f"[Source {i}: {c.title}]\n{c.text}")
    return "\n\n".join(blocks)
