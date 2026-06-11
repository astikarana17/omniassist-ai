# OmniAssist AI — UI/UX Design Plan

> Phase 1 · v1.0 · Dark-mode-first, premium SaaS. Inspired by Linear, Stripe, OpenAI, Vercel, Lovable.

## 1. Design Principles

1. **Dark-mode first**, light mode as a secondary theme.
2. **Calm, dense, fast** (Linear) — keyboard-first, instant transitions.
3. **Trustworthy & precise** (Stripe) — clear hierarchy, restrained color, great tables.
4. **Spacious & confident** (OpenAI/Vercel) — big type, generous spacing on marketing.
5. **Delightful micro-interactions** (Lovable) — subtle motion, never gratuitous.
6. **Pixel-perfect & responsive** — 4px spacing grid, consistent radii, mobile-friendly.

## 2. Design Tokens

| Token | Value (dark) |
|-------|--------------|
| Background base | `#0A0A0B` / `#0E0E10` |
| Surface / card | `#141417` with 1px `#232329` border |
| Glass | `rgba(20,20,23,0.6)` + `backdrop-blur-xl` |
| Primary accent | Indigo→Violet gradient `#6366F1 → #8B5CF6` |
| Success / Warn / Danger | `#22C55E` / `#F59E0B` / `#EF4444` |
| Text primary / muted | `#FAFAFA` / `#A1A1AA` |
| Radius | `lg=12px`, `xl=16px`, `2xl=20px` |
| Font | Geist / Inter (UI), Geist Mono (code/metrics) |
| Shadow | soft elevation + accent glow on hover |

## 3. Component Library Strategy

| Need | Library |
|------|---------|
| Primitives (button, input, dialog, table, dropdown) | **shadcn/ui** |
| Marketing/hero effects (spotlight, beams, bento, marquee) | **Aceternity UI** + **Magic UI** |
| Animated number tickers, bento metrics, shimmer, gradients | **Magic UI** |
| Production components on demand (forms, banners, cards) | **21st.dev (Magic MCP)** |
| Motion (page/element transitions, micro-interactions) | **Framer Motion** |
| Charts (animated) | Recharts/visx + Framer Motion |
| Icons | Lucide |

> Components will be fetched/generated via the **21st.dev Magic MCP** during Phase 2.

## 4. Key Screens

### Marketing / Landing
- Hero with animated gradient + spotlight, product preview, social proof, pricing, CTA.

### Auth
- Split layout: branded animated panel + clean form (email/OAuth). Glass card.

### Dashboard Shell
- Left rail nav (Inbox, Tickets, KB, Agents, Analytics, Channels, Team, Audit, Settings).
- Top bar: org switcher, global search (cmd-K), notifications, profile.
- Command palette (cmd-K) Linear-style.

### Inbox (flagship)
- 3-pane: conversation list · live thread · context panel (contact, AI confidence, sentiment, KB sources, handoff button).
- Streaming AI responses (token-by-token), typing indicators, presence.

### Tickets
- Data table (sortable, filterable), status pills, SLA countdown, bulk actions, detail drawer with AI summary.

### Knowledge Base
- Document grid, upload dropzone, crawl URL, indexing status, retrieval test playground.

### AI Agents
- Agent config: system prompt editor, tool toggles, model + temperature, confidence threshold, live test sandbox.

### Analytics
- Animated KPI cards (deflection, CSAT, FRT, volume), time-series charts, channel breakdown, AI-vs-human, heatmaps.

### Team / RBAC
- Members table, invite modal, role selector, permission matrix view.

### Audit Logs
- Filterable immutable timeline; actor, action, resource, diff viewer.

### Settings
- Channels, billing/plan, branding, API keys, notifications (Slack), security.

## 5. Motion & Micro-interactions

- Page transitions: fade + 8px rise (Framer Motion `layout`).
- Cards: hover lift + accent glow.
- Numbers: count-up on mount (Magic UI).
- Streaming text: cursor blink + smooth append.
- Skeleton shimmer for loading; optimistic UI for sends.
- Toasts: slide + blur (sonner).

## 6. Accessibility & Responsiveness

- WCAG AA contrast in both themes; visible focus rings.
- Full keyboard nav + cmd-K.
- Breakpoints: mobile (stacked inbox), tablet (2-pane), desktop (3-pane).
- Reduced-motion respected (`prefers-reduced-motion`).

## 7. Figma Workflow (MCP)

- Figma MCP key is configured. In Phase 2 we will: pull design tokens/frames via `get_figma_data(fileKey)`, export assets via `download_figma_images`, and reconcile with the token table above.
- **Action needed:** provide a Figma `fileKey` (or we proceed code-first from this token system and generate a Figma later).
