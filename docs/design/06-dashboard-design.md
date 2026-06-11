# OmniAssist AI — Enterprise Dashboard Design

> v1.0 · The flagship surface. Must feel like a $100M product, not a template.

## 1. Layout Anatomy

- **Grid:** 12-col, responsive auto-fit cards (min 280px). Sidebar 264px, topbar 56px (glass on scroll).
- **Hierarchy:** Greeting/date row → KPI strip (4) → primary chart + AI insights → live feed + presence.
- **Density:** Linear-grade — lots of signal, generous 24px gutters, no wasted hero space.

## 2. Premium KPI Widgets

```
┌─────────────────────────┐
│ Deflection rate     ✦    │  label (caption) + AI badge
│ 72%            ↑ 4.2%    │  mono-kpi, animated count-up, delta pill (green)
│ ▁▂▃▅▆▇▆▅  vs last 30d    │  inline sparkline (animated draw)
└─────────────────────────┘
```
- **Count-up** on mount (Magic UI number ticker), tabular-nums, easing `motion-base`.
- **Delta pill:** green ↑ / red ↓ with arrow; neutral gray for flat.
- **Sparkline:** animated path draw, gradient fill at 12% opacity, hover tooltip.
- **States:** loading skeleton (shimmer), no-data ("—" + hint), drill-in on click.

Core KPIs: **Deflection · CSAT · Avg First Response · Open conversations · Resolved today · Hot leads.**

## 3. Animated Metrics & Charts

| Chart | Type | Motion |
|-------|------|--------|
| Conversation volume | Stacked area by channel | left-to-right reveal, gradient fills |
| Deflection | Radial gauge | arc sweeps to value |
| CSAT trend | Line | path draw + dot pop |
| Resolution time | Histogram | bars rise staggered |
| AI vs Human | Donut | segments sweep |
| Sentiment | Heatmap | cells fade-in grid |

Rules: 60fps (transform/opacity), animate once per data load, hover = crosshair + glassy tooltip, empty = ghost axis.

## 4. AI Insight Cards

```
┌── AI Insights ✦ ───────────────────────────┐
│ ⚡ WhatsApp volume up 23% this week.         │
│    Consider adding evening coverage.        │
│    [View conversations →]                   │
│─────────────────────────────────────────────│
│ ⚠ 3 tickets at SLA risk in next 30 min.     │
│    [Reassign →]                             │
│─────────────────────────────────────────────│
│ 🔥 2 high-intent leads idle 24h.            │
│    [Follow up →]                            │
└─────────────────────────────────────────────┘
```
- Gradient-AI left border, ✦ icon, each insight = headline + recommendation + 1 action.
- Generated server-side (Claude) on rollups; refresh subtly with a shimmer, never a jarring reload.

## 5. Real-Time Activity Feed

```
┌── Live activity ──────────────── ● live ──┐
│ ✦ AI resolved #1042            · 2s ago    │  new rows slide in (top), 35ms stagger
│ ⟳ Handoff requested · WhatsApp · now       │  pulse dot on "now"
│ 🔥 New hot lead: Acme Corp     · 1m        │
│ ◐ Arjun joined #1041           · 3m        │
└────────────────────────────────────────────┘
```
- WebSocket-driven; "● live" pulse; auto-scroll pause on hover; type icons color-coded.

## 6. Live Notifications

- **Bell** with count badge → dropdown grouped (Mentions / Handoffs / SLA / System).
- **Toasts:** slide+blur from bottom-right, auto-dismiss 5s, action button, stack max 3.
- **Critical** (SLA breach, handoff): persistent until acknowledged + optional Slack mirror.

## 7. Personalization & Filters

- Greeting by name + time-of-day. Date range selector (Today/7d/30d/Custom).
- Saved dashboard layouts per role (Support vs Sales vs Admin default widgets differ).
- Drag to reorder widgets (power users); reset to default.

## 8. Visual Polish Checklist (the "$100M feel")

- [ ] Every number animates in, never pops.
- [ ] Consistent 12px card radius, 1px borders, soft shadow + subtle inner highlight.
- [ ] Accent glow only on the single most important live element.
- [ ] Real empty/loading/error for every widget.
- [ ] Mesh gradient backdrop at 6–8% opacity behind hero KPIs.
- [ ] Perfect optical alignment of icons, numbers, baselines.
- [ ] Reduced-motion variant tested.
