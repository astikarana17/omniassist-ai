<div align="center">

# OmniAssist AI — Backend

**Enterprise AI Customer Support & Sales platform — API & workers.**

FastAPI · Python 3.12 · SQLAlchemy 2 · PostgreSQL (Supabase) · Redis · Celery · Claude · LangGraph · Pinecone

</div>

---

## Architecture

```
Clients ──► FastAPI (REST + webhooks)
                │
                ├── Auth & RBAC (JWT, sessions, devices)
                ├── Domain services (conversations, tickets, leads, KB, analytics)
                ├── AI orchestration (LangGraph: support + sales agents)
                ├── RAG (parse → chunk → embed → Pinecone/pgvector → Claude)
                └── Integrations (Twilio WhatsApp/Voice, Gmail/SMTP, Slack)
                │
       ┌────────┼─────────────┐
   PostgreSQL  Redis        Pinecone
   (Supabase)  (cache/queue) (vectors)
                │
            Celery workers (embeddings, crawls, rollups, SLA, summaries)
```

## Tech

| Concern | Choice |
|---------|--------|
| API | FastAPI + Uvicorn/Gunicorn |
| ORM | SQLAlchemy 2 (async) + Alembic |
| DB | Supabase PostgreSQL + pgvector |
| Cache / broker | Redis |
| Background | Celery |
| LLM | Claude (Anthropic) |
| Agents | LangGraph + LangChain |
| Vectors | Pinecone (`omniassist-kb`, multilingual-e5-large, dim 1024) |
| Auth | JWT (access + rotating refresh), bcrypt, Google OAuth |
| Channels | Twilio (WhatsApp/Voice), Gmail/SMTP, Slack |

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                    # fill in secrets

# Database
alembic upgrade head

# Run API
uvicorn app.main:app --reload --port 8000

# Run workers (separate shells)
celery -A app.workers.celery_app worker --loglevel=info
celery -A app.workers.celery_app beat --loglevel=info
```

Docs: http://localhost:8000/docs · Health: `/healthz` · Readiness: `/readyz` · Metrics: `/metrics`

## Project structure

```
app/
├── core/          # config, db, redis, security, permissions, logging, middleware, deps
├── models/        # SQLAlchemy models (20+ tables, multi-tenant by org_id)
├── schemas/       # Pydantic v2 request/response
├── repositories/  # data access (tenant-scoped)
├── services/      # business logic
├── api/v1/        # routers + webhooks
├── ai/            # LangGraph agents, retrievers, tools, sentiment, summaries
├── integrations/  # twilio, email, slack clients
├── workers/       # celery app + tasks
└── main.py        # app factory
alembic/           # migrations
tests/             # pytest
deploy/            # Docker, compose, CI, Railway
```

## Security

Multi-tenant isolation by `org_id` + RBAC (7 roles), JWT with rotating refresh tokens and
session/device tracking, bcrypt password hashing, Fernet field encryption for channel secrets,
rate limiting, security headers, signed webhooks, append-only audit logs, PII-safe logging.

---

> Frontend: [`omniassist-ai`](https://github.com/astikarana17/omniassist-ai) · Built with Claude Code.
