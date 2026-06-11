"""Build the TCS demo knowledge base end-to-end.

1. Write structured markdown docs (data/tcs_kb/*.md)
2. Render a PDF per doc (data/tcs_kb/pdf/*.pdf)
3. Chunk the content
4. Store kb_documents + kb_chunks in Supabase (for the seeded `tcs` org)
5. Dump chunks to data/tcs_kb/chunks.json for the Pinecone upsert step

Usage:  python -m scripts.build_kb
"""
from __future__ import annotations

import asyncio
import json
import os
import uuid
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from sqlalchemy import text

from app.core.database import AsyncSessionLocal
from scripts.tcs_kb_content import DOCS

KB_DIR = Path("data/tcs_kb")
PDF_DIR = KB_DIR / "pdf"
ORG_SLUG = "tcs"


def chunk_markdown(body: str, max_chars: int = 600) -> list[str]:
    """Split into chunks on blank lines, merging small paragraphs up to max_chars."""
    paras = [p.strip() for p in body.split("\n\n") if p.strip()]
    chunks: list[str] = []
    buf = ""
    for p in paras:
        if buf and len(buf) + len(p) + 2 > max_chars:
            chunks.append(buf.strip())
            buf = p
        else:
            buf = f"{buf}\n\n{p}" if buf else p
    if buf.strip():
        chunks.append(buf.strip())
    return chunks


def render_pdf(title: str, body: str, path: Path) -> int:
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(path), pagesize=A4, title=title)
    flow = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
    for line in body.splitlines():
        s = line.rstrip()
        if not s:
            flow.append(Spacer(1, 6))
        elif s.startswith("# "):
            flow.append(Paragraph(s[2:], styles["Heading1"]))
        elif s.startswith("## "):
            flow.append(Paragraph(s[3:], styles["Heading2"]))
        elif s.startswith("- "):
            flow.append(Paragraph("• " + s[2:], styles["Normal"]))
        else:
            flow.append(Paragraph(s.replace("**", ""), styles["Normal"]))
    doc.build(flow)
    return path.stat().st_size


async def main() -> None:
    KB_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    async with AsyncSessionLocal() as db:
        org_id = (
            await db.execute(text("select id from organizations where slug=:s"), {"s": ORG_SLUG})
        ).scalar_one()

        # Clean prior KB for an idempotent rebuild (kb_chunks cascades).
        await db.execute(text("delete from kb_documents where org_id=:o"), {"o": org_id})

        all_chunks: list[dict] = []
        summary = []
        for key, (title, category, body) in DOCS.items():
            md_path = KB_DIR / f"{key}.md"
            md_path.write_text(body, encoding="utf-8")
            pdf_path = PDF_DIR / f"{key}.pdf"
            size = render_pdf(title, body, pdf_path)

            chunks = chunk_markdown(body)
            doc_id = uuid.uuid4()
            await db.execute(
                text(
                    "insert into kb_documents(id, org_id, title, source_type, source_url, "
                    "storage_path, content_type, status, chunk_count, size_bytes) values "
                    "(:id,:org,:title,'upload','https://www.tcs.com',:path,'application/pdf',"
                    "'ready',:cc,:sz)"
                ),
                {"id": doc_id, "org": org_id, "title": title,
                 "path": str(pdf_path), "cc": len(chunks), "sz": size},
            )
            for i, ctext in enumerate(chunks):
                chunk_id = uuid.uuid4()
                await db.execute(
                    text(
                        "insert into kb_chunks(id, org_id, document_id, chunk_index, content, "
                        "token_count, pinecone_id, meta) values "
                        "(:id,:org,:doc,:idx,:content,:tok,:pid, CAST(:meta AS jsonb))"
                    ),
                    {"id": chunk_id, "org": org_id, "doc": doc_id, "idx": i, "content": ctext,
                     "tok": len(ctext.split()), "pid": str(chunk_id),
                     "meta": json.dumps({"title": title, "category": category})},
                )
                all_chunks.append({
                    "id": str(chunk_id), "text": ctext,
                    "document_id": str(doc_id), "title": title, "category": category,
                })
            summary.append((title, len(chunks)))

        await db.commit()

    chunks_path = KB_DIR / "chunks.json"
    chunks_path.write_text(json.dumps(all_chunks, indent=2), encoding="utf-8")
    namespace = f"org_{org_id}"

    print("=== KB build complete ===")
    for title, n in summary:
        print(f"  {n:>2} chunks  {title}")
    print(f"\nDocuments: {len(summary)} | Chunks: {len(all_chunks)} | PDFs in {PDF_DIR}")
    print(f"Pinecone namespace: {namespace}")
    print(f"Chunks JSON: {chunks_path}")


if __name__ == "__main__":
    asyncio.run(main())
