# OmniAssist AI — MCP Server Verification Report

> Phase 1 · Generated 2026-06-08 · All checks run live against connected MCP servers.

## Summary

| # | MCP Server | Status | Verification Method | Result |
|---|-----------|--------|---------------------|--------|
| 1 | **Filesystem** | ✅ Live | Listed working dirs | `AI agent`, `Top-N sharpe rotation` mounted |
| 2 | **GitHub** | ✅ Live | `search_repositories(user:@me)` | User `astikarana17`, 4 repos, write token valid |
| 3 | **Supabase** | ✅ Live | `list_tables`, `list_extensions` | Project `pfcfrberlamzpopmbthr`, `public` empty, pgvector 0.8.0 available |
| 4 | **Pinecone** | ✅ Live | `list-indexes` | Connected, 0 indexes (clean) |
| 5 | **Twilio** | ✅ Live | `FetchBalance` | Account `AC7f52…f1fb`, balance **$14.35 USD** |
| 6 | **Figma** | ✅ Key set | API key present in `.mcp.json` | Needs a `fileKey` to pull a specific design |
| 7 | **Browser (BrowserMCP)** | ✅ Live | Tool registry | Navigate/click/snapshot available |
| 8 | **Playwright** | ✅ Live | Tool registry | Headless automation + network capture |
| 9 | **21st.dev (Magic)** | ✅ Live | Tool registry | Component builder + logo search |
| 10 | **Pinecone docs** | ✅ Live | `search-docs` | RAG reference available |
| — | **Zoho CRM** | 🚫 Excluded | Per user instruction | **Not used in this project** |
| — | **Canva** | ⏸ Optional | Auth-gated | Not required for MVP |
| — | **Slack** | ⚠️ Token needed | `.mcp.json` has placeholder token | Configure `SLACK_BOT_TOKEN` + `SLACK_TEAM_ID` |
| — | **Gmail** | ⏳ Connecting | OAuth auto-auth flow | Will be used for Email Agent |
| — | **Postgres (direct)** | ⚠️ Placeholder | Connection string not set | Optional — Supabase MCP covers DB |

## Key Findings (drives architecture decisions)

1. **Supabase has `pgvector 0.8.0`** with HNSW + IVFFlat. → We can run RAG vectors **inside Postgres** as a fallback/cheap tier, while **Pinecone** is the primary high-scale vector store. Hybrid strategy documented in `07-MCP-Usage-Plan.md`.
2. **`pgmq` (queue), `pg_cron` (scheduler), `pg_net` (async HTTP)** are available in Supabase. → We can offload some background jobs to Postgres-native primitives, reducing infra before Redis/Celery scale-up.
3. **`supabase_vault` + `pgcrypto`** available. → Encrypt tenant API keys, channel secrets (WhatsApp tokens, SMTP creds) at rest.
4. **Twilio balance is low ($14.35)** → fine for dev/testing WhatsApp + Voice; production needs top-up + a WhatsApp Business sender + a verified Voice number.
5. **Slack + Gmail need credential setup** before those modules go live (tracked in roadmap Phase 2).

## Action Items Before Phase 2

- [ ] Set `SLACK_BOT_TOKEN` and `SLACK_TEAM_ID` in `.mcp.json` (for Slack Notifications module).
- [ ] Complete Gmail OAuth auto-auth (for Email Agent).
- [ ] Provision a Twilio WhatsApp sender + Voice number; top up balance for production.
- [ ] Create Supabase project tables via migrations (Phase 2).
- [ ] Create Pinecone index `omniassist-kb` (Phase 2, after embedding model decided).
