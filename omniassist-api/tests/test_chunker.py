"""Unit tests for the RAG token chunker."""
from __future__ import annotations

from app.ai.rag.chunker import chunk_text, count_tokens


def test_empty_text_yields_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   \n  ") == []


def test_short_text_single_chunk():
    chunks = chunk_text("This is a short knowledge base entry about refunds.")
    assert len(chunks) == 1
    assert chunks[0].index == 0
    assert chunks[0].token_count > 0


def test_long_text_splits_into_multiple_chunks():
    paragraph = "Refunds are processed within 3 to 5 business days. " * 60
    text = "\n".join([paragraph] * 5)
    chunks = chunk_text(text, max_tokens=200, overlap=40)
    assert len(chunks) > 1
    assert all(c.token_count <= 260 for c in chunks)  # max + overlap headroom
    # Indices are contiguous and start at 0.
    assert [c.index for c in chunks] == list(range(len(chunks)))


def test_oversized_single_paragraph_is_hard_split():
    big = "word " * 2000  # one giant paragraph
    chunks = chunk_text(big, max_tokens=300, overlap=50)
    assert len(chunks) > 1


def test_count_tokens_positive():
    assert count_tokens("hello world") >= 2
