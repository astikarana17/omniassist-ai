# OmniAssist AI — Folder / Repository Structure

> Phase 1 · v1.0 · Monorepo (Turborepo) with `apps/` + `packages/` + `infra/`.

## 1. Top-Level Monorepo

```
omniassist-ai/
├── apps/
│   ├── web/                 # Next.js 15 dashboard + marketing + widget host
│   ├── api/                 # FastAPI backend (modular monolith)
│   └── worker/              # Async AI/jobs worker (LangGraph runs, embeddings, crawls)
├── packages/
│   ├── ui/                  # Shared React UI (shadcn + Magic + Aceternity wrappers)
│   ├── widget/              # Embeddable chat widget (standalone bundle)
│   ├── types/               # Shared TS types / OpenAPI-generated client
│   ├── config/              # ESLint, TS, Tailwind preset, env schema
│   └── sdk/                 # OmniAssist JS SDK (for customers)
├── infra/
│   ├── docker/              # Dockerfiles, docker-compose.yml
│   ├── supabase/            # migrations, seed, RLS policies
│   ├── railway/             # Railway service config
│   └── vercel/              # Vercel project config
├── docs/                    # ← Phase 1 documents (this folder)
├── .github/workflows/       # CI/CD pipelines
├── turbo.json
├── package.json
└── README.md
```

## 2. Frontend — `apps/web/` (Next.js 15 App Router)

```
apps/web/
├── src/
│   ├── app/
│   │   ├── (marketing)/                # public landing, pricing
│   │   ├── (auth)/login, signup
│   │   ├── (dashboard)/
│   │   │   ├── inbox/                   # conversations live view
│   │   │   ├── tickets/
│   │   │   ├── knowledge-base/
│   │   │   ├── agents/                  # AI agent config
│   │   │   ├── analytics/
│   │   │   ├── channels/
│   │   │   ├── team/                    # members + RBAC
│   │   │   ├── audit-logs/
│   │   │   └── settings/
│   │   ├── api/                         # Next route handlers (BFF/proxy)
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/                          # shadcn primitives
│   │   ├── magic/                       # Magic UI / Aceternity wrappers
│   │   ├── charts/                      # animated analytics
│   │   ├── inbox/                       # message list, composer, handoff
│   │   └── shared/
│   ├── lib/                             # api client, supabase client, hooks
│   ├── store/                           # state (Zustand)
│   ├── styles/                          # tailwind, themes (dark-first)
│   └── types/
├── public/
├── tailwind.config.ts
└── next.config.ts
```

## 3. Backend — `apps/api/` (FastAPI)

```
apps/api/
├── app/
│   ├── main.py                          # app factory, middleware, routers
│   ├── core/
│   │   ├── config.py                    # settings (pydantic-settings)
│   │   ├── security.py                  # JWT verify, RBAC deps
│   │   ├── db.py                        # async SQLAlchemy / asyncpg
│   │   ├── redis.py
│   │   └── logging.py
│   ├── api/v1/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── orgs.py
│   │   │   ├── members.py
│   │   │   ├── channels.py
│   │   │   ├── conversations.py
│   │   │   ├── messages.py
│   │   │   ├── tickets.py
│   │   │   ├── kb.py
│   │   │   ├── agents.py
│   │   │   ├── analytics.py
│   │   │   ├── feedback.py
│   │   │   └── audit.py
│   │   └── webhooks/
│   │       ├── twilio_whatsapp.py
│   │       ├── twilio_voice.py
│   │       └── gmail_push.py
│   ├── services/                        # business logic (one per domain)
│   ├── repositories/                    # data access (RLS-aware)
│   ├── models/                          # SQLAlchemy models
│   ├── schemas/                         # Pydantic request/response
│   ├── ai/
│   │   ├── graphs/                      # LangGraph: support_graph.py, sales_graph.py
│   │   ├── tools/                       # kb_search, create_ticket, escalate...
│   │   ├── retrievers/                  # pinecone + pgvector
│   │   ├── prompts/
│   │   ├── sentiment.py
│   │   └── summarize.py
│   ├── integrations/                    # twilio, gmail, slack clients
│   └── realtime/                        # websocket manager, pubsub
├── tests/
├── pyproject.toml
└── Dockerfile
```

## 4. Worker — `apps/worker/`

```
apps/worker/
├── worker/
│   ├── main.py                          # queue consumer (Redis/pgmq)
│   ├── jobs/
│   │   ├── embed_document.py
│   │   ├── crawl_site.py                # uses Playwright
│   │   ├── rollup_analytics.py
│   │   ├── sla_check.py
│   │   └── summarize_ticket.py
│   └── scheduler.py                     # cron-style triggers
├── pyproject.toml
└── Dockerfile
```

## 5. Infra — `infra/supabase/`

```
infra/supabase/
├── migrations/
│   ├── 0001_core_tenancy.sql
│   ├── 0002_channels_contacts.sql
│   ├── 0003_conversations_messages.sql
│   ├── 0004_tickets_handoffs.sql
│   ├── 0005_kb_vectors.sql
│   ├── 0006_ai_agents_runs.sql
│   ├── 0007_analytics_audit.sql
│   ├── 0008_rls_policies.sql
│   └── 0009_seed_roles.sql
├── seed.sql
└── config.toml
```

## 6. Conventions

- **TypeScript** strict; **Python** typed (mypy) + Pydantic.
- One domain = one service file + one repository + one router.
- Shared types generated from FastAPI **OpenAPI** schema → `packages/types`.
- Env validated at boot via a schema (`packages/config/env`).
- Feature flags via org `settings` jsonb.
