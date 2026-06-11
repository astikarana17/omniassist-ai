# OmniAssist AI

An enterprise **AI customer-support & sales platform** — AI agents across website chat, WhatsApp, email and voice that answer from your knowledge base (RAG-grounded, no hallucinations), qualify leads, create tickets, and hand off to humans when needed.

This is a monorepo with two apps:

| App | Path | Stack |
|---|---|---|
| **Frontend** | [`omniassist-web/`](omniassist-web) | Next.js 15 · React Query · Zustand · Tailwind / shadcn-ui |
| **Backend** | [`omniassist-api/`](omniassist-api) | FastAPI · SQLAlchemy 2 (async) · Alembic · Supabase Postgres · Pinecone |

## Features

- **AI agents on every channel** — one RAG brain (OpenRouter / Claude) grounds every answer in your knowledge base with cited sources + confidence
- **Live inbox** — real conversations, AI auto-reply, human handoff (refund / "talk to human" / low-confidence)
- **Ticketing** — auto-created on billing/refund/bug/account intents, SLA timers, AI summaries
- **Knowledge base (RAG)** — upload docs / crawl sites → chunk → Pinecone embeddings → grounded retrieval
- **Product Expert + Copilot** — ask anything about the product, grounded answers
- **AI Agent sandbox** — test your support/sales agent live with real RAG replies
- **Billing** — Stripe checkout + plan gating (Starter / Growth / Enterprise)
- **Multi-tenant** — each signup gets its own isolated workspace (org-level RLS)
- **Auth** — JWT + Google/GitHub OAuth, RBAC

## Quick start

### Backend (`omniassist-api`)
```bash
cd omniassist-api
python -m venv .venv && . .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # fill in DATABASE_URL, OPENROUTER_API_KEY, PINECONE_API_KEY, ...
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend (`omniassist-web`)
```bash
cd omniassist-web
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev                        # http://localhost:3000
```

## Environment

Secrets live in `.env` (backend) and `.env.local` (frontend) — both are git-ignored. See the `.env.example` / `.env.local.example` templates in each app for the required variables.

## Configuration notes

- **LLM**: set `OPENROUTER_API_KEY` (+ `OPENROUTER_MODEL`) for grounded answers, or `ANTHROPIC_API_KEY` for Claude.
- **Vector search**: `PINECONE_API_KEY` + `PINECONE_INDEX` power the RAG knowledge base.
- **Billing**: add `STRIPE_SECRET_KEY` + price IDs to enable checkout.
- **OAuth**: add Google / GitHub client IDs to enable social login (buttons hide when unset).

---

© 2026 OmniAssist AI.
