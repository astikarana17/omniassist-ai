# OmniAssist AI — Phase 1 Documentation Index

Enterprise AI Customer Support + AI Sales Agent platform (Website Chat · WhatsApp · Email · Voice · RAG · Ticketing · Analytics).

**Status:** Phase 1 (planning) complete — awaiting approval before Phase 2 (code).

| # | Document | Contents |
|---|----------|----------|
| 00 | [MCP Verification](00-MCP-Verification.md) | Live checks of all MCP servers + action items |
| 01 | [PRD](01-PRD.md) | Vision, personas, modules, requirements, metrics |
| 02 | [System Architecture](02-System-Architecture.md) | C4 diagram, layers, AI agent graph, pipelines |
| 03 | [Database Design](03-Database-Design.md) | ER diagram, 21-table schema, RLS, vectors |
| 04 | [API & Auth Architecture](04-API-Auth-Architecture.md) | REST/WS map, JWT flow, RBAC, security |
| 05 | [Folder Structure](05-Folder-Structure.md) | Monorepo: web + api + worker + infra |
| 06 | [UI/UX Plan](06-UIUX-Plan.md) | Dark-first design system, screens, motion |
| 07 | [MCP Usage Plan](07-MCP-Usage-Plan.md) | How each MCP is used build + runtime |
| 08 | [Deployment & Roadmap](08-Deployment-Roadmap.md) | Vercel/Railway/Supabase topology, 7 sprints |

> **Excluded:** Zoho CRM is not used anywhere in this project (per project decision).

## Tech Stack
Frontend: Next.js 15 · TypeScript · TailwindCSS · shadcn/ui · Magic UI · Aceternity · Framer Motion
Backend: FastAPI · PostgreSQL · Redis
AI: Claude · LangGraph · LangChain · Pinecone (+ pgvector)
Data: Supabase PostgreSQL · Pinecone
Deploy: Vercel · Railway · Docker
