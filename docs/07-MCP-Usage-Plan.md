# OmniAssist AI — MCP Usage Plan

> Phase 1 · v1.0 · How each connected MCP server is used across build + runtime.
> **Zoho CRM is explicitly excluded from this project.**

## 1. MCP → Role Mapping

| MCP Server | Build-time use | Runtime analog (production) |
|-----------|----------------|-----------------------------|
| **Filesystem** | Scaffold repo, write code/docs, read configs | n/a (dev only) |
| **GitHub** | Create repo, push code, branches, PRs, CI files | CI/CD via GitHub Actions |
| **Supabase** | Create migrations, apply schema, RLS, seed, inspect | App uses Supabase client + Postgres |
| **Pinecone** | Create index, upsert KB vectors, test retrieval | RAG retrieval per query |
| **Twilio** | Provision numbers, configure WhatsApp/Voice, test sends | WhatsApp/Voice/SMS messaging + transcription |
| **Figma** | Pull design tokens/frames, export assets | n/a (design only) |
| **Browser / Playwright** | Crawl docs for KB, E2E test the dashboard | Site-crawl job for KB ingestion |
| **21st.dev (Magic)** | Generate premium UI components, logos | n/a (dev only) |
| **Slack** | Configure notification channel, test posts | Ops notifications (handoff, SLA, CSAT) |
| **Gmail** | Configure inbound parsing, test reply | Email Agent inbound/outbound |

## 2. Phase-2 Build Sequence per MCP

### GitHub
1. `create_repository("omniassist-ai", private)`
2. `push_files` for scaffold (monorepo skeleton + docs).
3. Branch protection + `.github/workflows` for CI.
4. Use PRs for each module milestone.

### Supabase
1. `apply_migration` for each `0001…0009` migration (tenancy → RLS → seed).
2. `list_tables(verbose)` to verify schema.
3. `get_advisors` for security/perf lint after schema.
4. `generate_typescript_types` → feed `packages/types`.
5. Enable `vector`, `pgmq`, `pg_cron` extensions as needed.
> Current MCP connection is **read-only** (`--read-only` flag). **Action:** to apply migrations in Phase 2, relaunch Supabase MCP without `--read-only`, or run migrations via Supabase CLI.

### Pinecone
1. `create-index-for-model` → index `omniassist-kb` (decide embedding model + dims).
2. Namespacing strategy: **one namespace per `org_id`** for tenant isolation.
3. `upsert-records` from embedding worker; `search-records` at query time.
4. Keep `kb_chunks.pinecone_id` in Postgres as the join key.

### Twilio
1. `ListAvailablePhoneNumberLocal` → buy a number (`CreateIncomingPhoneNumber`).
2. Configure WhatsApp sender (Business profile) + Voice webhook URLs.
3. `CreateMessage` for outbound WhatsApp/SMS; `CreateCall` + `CreateRealtimeTranscription` for Voice.
4. Verify with `FetchBalance` (currently **$14.35** — top up for production).

### Pinecone vs pgvector tiering
- **Free/Starter tenants:** pgvector (HNSW) inside Supabase → no extra cost.
- **Growth/Enterprise tenants:** Pinecone namespace per org → scale + speed.
- Retriever abstraction picks backend by tenant plan.

### Figma
- Provide `fileKey` → `get_figma_data` for tokens/frames; `download_figma_images` for assets.
- If no Figma file: proceed code-first using the token system in `06-UIUX-Plan.md`.

### Playwright / Browser
- KB site-crawl job: navigate, extract main content, chunk → embed.
- E2E tests: login, send message, handoff, ticket lifecycle.

### 21st.dev (Magic)
- Generate: KPI cards, inbox composer, data tables, pricing, hero, settings forms.
- Fetch brand logos for integrations page.

### Slack
- Needs `SLACK_BOT_TOKEN` + `SLACK_TEAM_ID` set. Then `slack_post_message` for: new handoff, SLA breach, low CSAT, new high-intent sales lead.

### Gmail
- Complete OAuth. Inbound: parse threads → create conversation/ticket. Outbound: AI-drafted replies (approve or auto-send).

## 3. Secrets & Config Handling

- All MCP credentials currently live in `.mcp.json` (dev). For production:
  - Move secrets to environment/secret manager (Railway/Vercel env, Supabase Vault).
  - **Do not commit** `.mcp.json` with live tokens to the public repo — add to `.gitignore`; provide `.mcp.example.json`.
- ⚠️ The current `.mcp.json` contains **live API keys** (GitHub PAT, Supabase, Pinecone, Figma, Twilio, 21st.dev). Recommend rotating these before pushing to GitHub.

## 4. Guardrails

- Zoho CRM tools: **never called** in this project (per user instruction).
- Twilio: rate-limit + sandbox in dev to protect balance.
- Pinecone/Supabase writes: tenant-scoped (namespace / `org_id`) always.
