<div align="center">

# OmniAssist AI

**The AI workforce for customer support & sales.**
One AI brain across Website Chat, WhatsApp, Email and Voice — grounded in your knowledge, escalates to humans.

Next.js 15 · TypeScript · TailwindCSS · shadcn/ui · Framer Motion · React Query · Zustand · Recharts

</div>

---

## ✨ Features

- **AI Customer Support & Sales agents** — RAG-grounded, source-cited, confidence-aware
- **Omnichannel inbox** — Website chat, WhatsApp, Email, Voice
- **Tickets** — lifecycle, SLA timers, AI summaries, human handoff
- **Leads & CRM pipeline** — Kanban, lead scoring, follow-ups
- **Knowledge Base** — upload, crawl, FAQ, retrieval playground
- **Analytics** — deflection, CSAT, revenue, sentiment, team performance
- **Governance** — RBAC, audit logs, notifications
- **AI-first UX** — Copilot panel, smart suggestions, streaming, command palette
- **Premium design** — dark-mode-first, glassmorphism, animated charts, fully responsive

## 🧱 Tech Stack

| Layer | Tech |
|-------|------|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript |
| Styling | TailwindCSS + design tokens |
| Components | shadcn/ui (Radix) |
| Motion | Framer Motion |
| Data | TanStack React Query |
| State | Zustand |
| Charts | Recharts |
| Icons | Lucide |

## 🚀 Getting Started

```bash
npm install
cp .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## 📁 Structure

```
src/
├── app/
│   ├── (app)/          # Authenticated dashboard pages
│   ├── (auth)/         # Login, signup, forgot password
│   └── (marketing)/    # Landing page
├── components/
│   ├── ui/             # shadcn primitives
│   ├── layout/         # Sidebar, navbar, command palette, copilot
│   ├── shared/         # Reusable building blocks
│   ├── dashboard/      # Dashboard widgets
│   ├── inbox/          # Chat components
│   ├── tickets/ leads/ analytics/ kb/
├── hooks/              # Custom hooks
├── lib/                # utils, sample data, nav config
├── store/              # Zustand stores
└── types/              # Shared types
```

## 🎨 Design System

Dark-mode-first, built on a token system (see `docs/design` in the planning repo). Brand gradient `#6366F1 → #8B5CF6`, Geist typography, 4px spacing grid, glassmorphism for overlays.

---

> Built with Claude Code. Backend (FastAPI + Supabase + Pinecone + Claude/LangGraph) lives in a separate service.
