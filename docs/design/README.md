# OmniAssist AI — Design System & UX Architecture

> Complete product design documentation. Dark-first, premium SaaS — built to feel like a $100M+ venture-funded product.
> **Status:** Design phase complete — awaiting approval before frontend code.

## Contents

| # | Document | Covers |
|---|----------|--------|
| 01 | [Brand Identity](01-brand-identity.md) | Story, personality, logo concepts, color, type, icons, principles |
| 02 | [Design System Foundations](02-design-system.md) | Spacing, radius, elevation, shadows, glass, gradients, motion, dark/light, a11y |
| 03 | [User Flows & Journeys](03-user-flows.md) | Customer · Support · Sales · Admin flows (Mermaid) |
| 04 | [Information Architecture](04-information-architecture.md) | Nav hierarchy, sitemap, URLs, role visibility |
| 05 | [High-Fidelity Wireframes](05-wireframes.md) | All 17 screens (desktop) |
| 06 | [Enterprise Dashboard Design](06-dashboard-design.md) | KPIs, charts, AI insights, live feed |
| 07 | [Advanced Animations](07-animations.md) | Framer Motion spec, transitions, AI streaming, charts |
| 08 | [Mobile UX](08-mobile-ux.md) | Responsive dashboard, chat, ticketing, analytics |
| 09 | [Design Inspirations](09-design-inspirations.md) | Linear, Stripe, OpenAI, Cursor, Vercel, Notion, Lovable |
| 10 | [Component Library](10-component-library.md) | Every component: anatomy, variants, states |
| 11 | [AI-First Experience](11-ai-first-experience.md) | Copilot, suggestions, summaries, context, collaboration |
| 12 | [Design Tokens (JSON)](12-design-tokens.json) | Machine-readable tokens (single source of truth) |
| 13 | [Figma Structure](13-figma-structure.md) | File org, component hierarchy, MCP sync plan |

## Design Pillars
**Dark-first · Calm & dense (Linear) · Trustworthy (Stripe) · AI-native (Cursor/OpenAI) · Delightful motion (Lovable) · Premium dark canvas (Vercel) · Flexible structure (Notion).**

## Signature Differentiator
AI that is **fast (streaming), grounded (sources), honest (confidence + handoff), and collaborative (copilot + whisper)** — wrapped in pixel-perfect, accessible, animated UI.

## Tooling
- **shadcn/ui** primitives · **Magic UI** + **Aceternity UI** flourish · **Framer Motion** motion.
- **21st.dev (Magic MCP)** → generates production components in the code phase.
- **Figma MCP** → provide a `fileKey` to sync tokens/assets.

## Inputs still needed before code
- Logo direction (Orbit / Pulse / Prism — Orbit recommended).
- Figma `fileKey` (or approve code-first).
- Light mode priority (ship with dark only at MVP, or both?).

---
> Excludes Zoho CRM (not used in this project).
