# OmniAssist AI — Advanced Animation & Motion Spec

> v1.0 · Framer Motion principles. Motion has meaning; performance is non-negotiable.

## 1. Motion Principles

1. **Purposeful** — every animation communicates a state change (enter, exit, success, loading).
2. **Fast & natural** — 80–400ms, spring for physical objects, ease for UI.
3. **Performant** — animate `transform`/`opacity` only; never layout-thrash.
4. **Consistent** — same element type = same motion everywhere.
5. **Respectful** — `prefers-reduced-motion` → replace movement with instant cross-fades.

## 2. Duration & Easing Tokens (recap)

| Token | ms | Curve |
|-------|----|-------|
| instant | 80 | ease-out |
| fast | 160 | `cubic-bezier(.2,.8,.2,1)` |
| base | 240 | `cubic-bezier(.2,.8,.2,1)` |
| slow | 400 | spring(stiffness 300, damping 30) |
| ai | 600+ | soft spring |

## 3. Page Transitions

- Route change: outgoing fades+drops 8px (120ms), incoming fades+rises 8px (240ms) → no white flash.
- Shared layout: list item → detail uses Framer `layoutId` (card morphs into header).
- Tab switches: content cross-fade + 4px slide in scroll direction.

## 4. Hover & Press Interactions

| Element | Hover | Press |
|---------|-------|-------|
| Button (primary) | brightness +6%, subtle glow | scale 0.98 |
| Card | lift 2px + shadow-md + border brighten | — |
| Nav item | bg tint fade-in 80ms | active = brand bar slides in |
| Table row | bg tint + reveal row actions | — |
| Avatar | ring grow | — |
| KPI card | sparkline tooltip + scale 1.01 | drill-in |

## 5. Loading States

- **Skeletons** (preferred): shape-matched blocks with shimmer sweep (1.4s loop, gradient mask). Never spinners for content.
- **Spinners**: only for button-level async (inline, 16px) + full-page boot.
- **Progress**: KB indexing = animated determinate bar with % count-up.
- **Optimistic UI**: message sends appear instantly (muted) → confirm on ack.

## 6. Skeleton Screens (per surface)

- Dashboard: 4 KPI blocks + chart block + feed rows.
- Inbox: conversation list rows + thread bubbles.
- Tables: header + 8 shimmer rows.
- KB: card grid ghosts.

## 7. AI Typing & Streaming Indicators

- **Typing dots:** 3 dots, scale/opacity wave, 1.2s loop, gradient-AI color.
- **Streaming text:** tokens append with 1-char fade; soft blinking caret at tail.
- **Thinking state:** orbit logo micro-spin + "Thinking…" with shimmer (for tool-use/RAG latency).
- **Confidence reveal:** after answer, a small bar animates to confidence %.
- **Source pills:** fade+rise in, staggered 40ms, after the answer completes.

## 8. Animated Charts

- Area/line: path draw (`pathLength` 0→1) 600ms ease-out, gradient fill fades in after.
- Bars/histogram: rise from baseline, staggered 35ms.
- Gauge/donut: arc sweep with spring.
- Number tickers: count-up with easing, tabular-nums to avoid width jitter.
- Re-render on data change: morph values, don't re-draw from zero.

## 9. Animated Sidebar

- Collapse/expand: width spring 264↔72px; labels fade+slide; icons stay pinned.
- Active indicator: brand pill slides between items (`layoutId="nav-active"`).
- Sub-menu: height auto expand (spring) + child stagger.
- Mobile: off-canvas drawer slides in with scrim fade + content push.

## 10. Micro-interactions Library

- Toggle/switch: thumb spring + color cross-fade.
- Checkbox: check path draws.
- Toast: slide+blur in, swipe-to-dismiss.
- Copy button: ✓ morph + "Copied" tooltip.
- Drag (Kanban): card lifts (shadow-lg, scale 1.03, slight tilt), drop zone highlights, neighbors reflow with spring.
- Empty states: subtle floating illustration loop.
- Success: confetti-free — a single checkmark draw + green glow pulse.

## 11. Reduced Motion Mapping

| Normal | Reduced |
|--------|---------|
| slide/rise/scale | instant opacity cross-fade |
| path draw charts | final state shown immediately |
| streaming caret | text appears in chunks, no caret |
| parallax/mesh drift | static gradient |

## 12. Performance Budget

- 60fps target; no animation > 400ms except AI streaming.
- GPU-only properties; `will-change` used sparingly + removed after.
- Max 3 concurrent large animations on screen; defer off-screen ones.
