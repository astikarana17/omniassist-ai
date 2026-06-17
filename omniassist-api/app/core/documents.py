"""Shared document helpers for the medical vision pipelines."""
from __future__ import annotations


def to_images(content: bytes, mime: str) -> list[tuple[str, bytes]]:
    """Normalise an upload to vision-model images. PDFs (which the OpenRouter
    vision model can't read directly) are rendered to PNGs — first 3 pages."""
    if mime != "application/pdf":
        return [(mime, content)]
    import fitz  # PyMuPDF — lazy import so non-PDF paths don't pay for it

    images: list[tuple[str, bytes]] = []
    doc = fitz.open(stream=content, filetype="pdf")
    try:
        for page in list(doc)[:3]:
            pix = page.get_pixmap(dpi=150)
            images.append(("image/png", pix.tobytes("png")))
    finally:
        doc.close()
    return images or [(mime, content)]
