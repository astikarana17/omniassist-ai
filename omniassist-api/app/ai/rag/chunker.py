"""Token-aware text chunking with overlap (tiktoken)."""
from __future__ import annotations

from dataclasses import dataclass

import tiktoken

_ENC = tiktoken.get_encoding("cl100k_base")


@dataclass
class Chunk:
    index: int
    text: str
    token_count: int


def count_tokens(text: str) -> int:
    return len(_ENC.encode(text))


def chunk_text(text: str, max_tokens: int = 400, overlap: int = 60) -> list[Chunk]:
    """Split text into overlapping, token-bounded chunks, respecting paragraph breaks."""
    text = text.strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: list[Chunk] = []
    current: list[str] = []
    current_tokens = 0
    idx = 0

    def flush() -> None:
        nonlocal current, current_tokens, idx
        if not current:
            return
        body = "\n".join(current).strip()
        if body:
            chunks.append(Chunk(index=idx, text=body, token_count=count_tokens(body)))
            idx += 1

    for para in paragraphs:
        para_tokens = count_tokens(para)
        # A single oversized paragraph is hard-split by tokens.
        if para_tokens > max_tokens:
            flush()
            current, current_tokens = [], 0
            tokens = _ENC.encode(para)
            for start in range(0, len(tokens), max_tokens - overlap):
                window = tokens[start : start + max_tokens]
                body = _ENC.decode(window).strip()
                if body:
                    chunks.append(Chunk(index=idx, text=body, token_count=len(window)))
                    idx += 1
            continue

        if current_tokens + para_tokens > max_tokens:
            flush()
            # Carry overlap from the tail of the previous chunk.
            if overlap and chunks:
                tail_tokens = _ENC.encode(chunks[-1].text)[-overlap:]
                carry = _ENC.decode(tail_tokens)
                current, current_tokens = [carry], len(tail_tokens)
            else:
                current, current_tokens = [], 0

        current.append(para)
        current_tokens += para_tokens

    flush()
    return chunks
