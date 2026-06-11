"""Replace the TCS demo with OmniAssist AI's OWN knowledge base, end-to-end.

- Renames the org to "OmniAssist AI" (slug omniassist)
- Clears TCS structured data, KB, conversations
- Inserts OmniAssist structured data (profile, products, pricing, FAQs, competitors)
- Builds 15 KB docs + PDFs + kb_documents/kb_chunks
- Generates 500+ paraphrased FAQs
- Clears the Pinecone namespace and upserts all chunks (docs + FAQs)

Usage:  python -m scripts.rebuild_omni
"""
from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path

from sqlalchemy import text

from app.ai import pinecone_client
from app.ai.retriever import namespace_for
from app.core.database import AsyncSessionLocal
from scripts.build_kb import chunk_markdown, render_pdf
from scripts.omni_kb_content import (
    COMPANY,
    COMPETITORS,
    DOCS,
    FAQ_SEED,
    PRICING,
    PRODUCTS,
)

KB_DIR = Path("data/omni_kb")
PDF_DIR = KB_DIR / "pdf"

PREFIXES = [
    "", "Hi — ", "Hello, ", "Hey, ", "Quick question: ", "Sorry to bother, but ",
    "I was wondering — ", "Just checking: ", "Hi team, ", "Please advise: ",
    "Curious — ", "Can you help: ",
]


def paraphrases(q: str) -> list[str]:
    return [p + q for p in PREFIXES]


async def main() -> None:
    KB_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    async with AsyncSessionLocal() as db:
        org_id = (
            await db.execute(
                text("select id from organizations where slug in ('tcs','omniassist') limit 1")
            )
        ).scalar_one()

        await db.execute(
            text("update organizations set name='OmniAssist AI', slug='omniassist', "
                 "plan='growth' where id=:o"),
            {"o": org_id},
        )
        for t in ("kb_documents", "conversations", "contacts", "company_profiles",
                  "products", "pricing_plans", "faqs", "policies", "competitors",
                  "knowledge_gaps"):
            await db.execute(text(f"delete from {t} where org_id=:o"), {"o": org_id})

        # ---- structured company data ----
        await db.execute(
            text("insert into company_profiles(id,org_id,overview,mission,value_props,"
                 "website,industry,contact,meta) values (:id,:o,:ov,:mi,CAST(:vp AS jsonb),"
                 ":web,:ind,CAST(:ct AS jsonb),'{}')"),
            {"id": uuid.uuid4(), "o": org_id, "ov": COMPANY["overview"], "mi": COMPANY["mission"],
             "vp": json.dumps(COMPANY["value_props"]), "web": COMPANY["website"],
             "ind": COMPANY["industry"], "ct": json.dumps(COMPANY["contact"])},
        )
        for name, typ, summary in PRODUCTS:
            await db.execute(
                text("insert into products(id,org_id,name,type,summary,status,meta) "
                     "values (:id,:o,:n,:t,:s,'active','{}')"),
                {"id": uuid.uuid4(), "o": org_id, "n": name, "t": typ, "s": summary},
            )
        for i, (name, price, billing, feats) in enumerate(PRICING):
            await db.execute(
                text("insert into pricing_plans(id,org_id,name,price_amount,currency,"
                     "billing_period,features,limits,is_public,position,meta) values "
                     "(:id,:o,:n,:p,'USD',:b,CAST(:f AS jsonb),'{}',true,:pos,'{}')"),
                {"id": uuid.uuid4(), "o": org_id, "n": name, "p": price, "b": billing,
                 "f": json.dumps(feats), "pos": i},
            )
        for i, (cat, q, a) in enumerate(FAQ_SEED):
            await db.execute(
                text("insert into faqs(id,org_id,question,answer,category,tags,is_public,"
                     "position) values (:id,:o,:q,:a,:c,'{}',true,:pos)"),
                {"id": uuid.uuid4(), "o": org_id, "q": q, "a": a, "c": cat, "pos": i},
            )
        for name, pos, strengths, weaknesses in COMPETITORS:
            await db.execute(
                text("insert into competitors(id,org_id,name,positioning,strengths,"
                     "weaknesses,meta) values (:id,:o,:n,:p,CAST(:s AS jsonb),"
                     "CAST(:w AS jsonb),'{}')"),
                {"id": uuid.uuid4(), "o": org_id, "n": name, "p": pos,
                 "s": json.dumps(strengths), "w": json.dumps(weaknesses)},
            )

        # ---- KB docs -> chunks + PDFs + kb_documents/kb_chunks ----
        records: list[dict] = []
        for key, (title, category, body) in DOCS.items():
            (KB_DIR / f"{key}.md").write_text(body, encoding="utf-8")
            pdf = PDF_DIR / f"{key}.pdf"
            size = render_pdf(title, body, pdf)
            chunks = chunk_markdown(body)
            doc_id = uuid.uuid4()
            await db.execute(
                text("insert into kb_documents(id,org_id,title,source_type,source_url,"
                     "storage_path,content_type,status,chunk_count,size_bytes) values "
                     "(:id,:o,:t,'upload',:url,:p,'application/pdf','ready',:cc,:sz)"),
                {"id": doc_id, "o": org_id, "t": title, "url": COMPANY["website"],
                 "p": str(pdf), "cc": len(chunks), "sz": size},
            )
            for i, ctext in enumerate(chunks):
                cid = uuid.uuid4()
                await db.execute(
                    text("insert into kb_chunks(id,org_id,document_id,chunk_index,content,"
                         "token_count,pinecone_id,meta) values (:id,:o,:d,:i,:c,:tok,:pid,"
                         "CAST(:m AS jsonb))"),
                    {"id": cid, "o": org_id, "d": doc_id, "i": i, "c": ctext,
                     "tok": len(ctext.split()), "pid": str(cid),
                     "m": json.dumps({"title": title, "category": category})},
                )
                records.append({"_id": str(cid), "text": ctext, "title": title,
                                "category": category})

        await db.commit()
        namespace = namespace_for(org_id)

    # ---- 500+ paraphrased FAQs (Pinecone only) ----
    faq_records: list[dict] = []
    for cat, q, a in FAQ_SEED:
        for v in paraphrases(q):
            faq_records.append({"_id": str(uuid.uuid4()),
                                "text": f"Q: {v}\nA: {a}", "title": "OmniAssist FAQ",
                                "category": cat})
    faq_records = faq_records[:500]
    all_records = records + faq_records

    # ---- Pinecone: clear old (TCS) vectors + upsert OmniAssist ----
    pinecone_client.delete_namespace(namespace)
    pinecone_client.upsert_records(namespace, all_records)

    print("=== OmniAssist KB rebuild complete ===")
    print(f"  Org renamed: OmniAssist AI (omniassist)")
    print(f"  Products: {len(PRODUCTS)} | Pricing: {len(PRICING)} | "
          f"Competitors: {len(COMPETITORS)} | structured FAQs: {len(FAQ_SEED)}")
    print(f"  KB documents: {len(DOCS)} | doc chunks: {len(records)}")
    print(f"  Paraphrased FAQs: {len(faq_records)}")
    print(f"  Pinecone vectors upserted: {len(all_records)}  (namespace {namespace})")


if __name__ == "__main__":
    asyncio.run(main())
