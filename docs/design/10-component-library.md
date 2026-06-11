# OmniAssist AI — Component Library Specification

> v1.0 · Component anatomy, variants, states, tokens. Built on shadcn primitives + Magic/Aceternity for flourish.
> (Visual/code build deferred to Phase 2; this is the design contract.)

## Component Hierarchy

```
Foundations (tokens) → Primitives → Composites → Patterns → Pages
```

---

## 1. Buttons
- **Variants:** `primary` (brand gradient), `secondary` (surface + border), `ghost` (transparent), `destructive` (danger), `ai` (gradient-ai + ✦).
- **Sizes:** sm (32h), md (36h), lg (40h), icon (square).
- **States:** default, hover (brightness/glow), active (scale .98), focus (ring), disabled (40% + no-drop), loading (inline spinner + label).
- **Radius:** md. **Tokens:** `space-3` padding-x, `body` text, weight 500.

## 2. Inputs
- **Types:** text, email, password (👁 toggle), number, textarea (auto-grow), search (⌕ + ⌘K hint).
- **Anatomy:** label (always visible) · field · helper/error · optional prefix/suffix icon.
- **States:** default, focus (brand ring + border), filled, error (danger border + message + icon), disabled, success.
- Radius md, height 36–40, `border-strong`, focus = `glow-brand` ring.

## 3. Dropdowns / Selects
- Trigger (button-like) + menu (e1/e2 surface, radius lg, shadow-md).
- Items: hover tint, selected ✓, sections w/ labels, keyboard nav, search for long lists.
- Multi-select → chips in trigger. Async → loading row.

## 4. Modals
- Center, max 560px, radius xl, e3 + scrim (blur 8px, 60% black).
- Anatomy: header (title + ✕) · body · footer (cancel + primary).
- Motion: scrim fade + dialog rise/scale spring. ESC + click-scrim close, focus trap.

## 5. Drawers / Sheets
- Side drawer (detail context) 420–560px; bottom sheet on mobile w/ drag handle + snap points.
- Slides from edge (spring), scrim fade, content stays mounted underneath.

## 6. Data Tables
- Sticky header, sortable columns (↕), row hover reveals actions, selection checkboxes + bulk bar.
- Cell types: text, status pill, avatar+name, tag chips, SLA timer, relative time, menu (⋮).
- Density toggle, column visibility, pagination (cursor), sticky first/last column on mobile→cards.
- Empty/loading (skeleton rows)/error states.

## 7. Chat Components
- **Message bubble:** AI (left, surface, ✦), user/customer (right, brand tint), agent (left, distinct), system (centered, muted).
- **Composer:** auto-grow textarea, attach, emoji, send (➤), AI-suggest (✦), slash-commands.
- **Typing indicator**, **streaming text + caret**, **source pills**, **quick replies**, **feedback (👍👎)**, **read/delivered ticks**.
- **Date dividers**, **unread divider**, scroll-to-latest FAB.

## 8. Ticket Cards
- Subject + #id, status pill, priority chip (▲/◦), SLA countdown (color-shifting), assignee avatar, tags, channel icon, last-update time.
- Hover lift; click → detail drawer; drag (board) optional.

## 9. Analytics Widgets
- KPI card (count-up + delta + sparkline), chart cards (area/line/bar/donut/gauge/heatmap), leaderboard rows, gauge.
- Shared: title + range + ⋮ (export/drill), loading skeleton, no-data ghost.

## 10. KPI Cards
- (See dashboard spec) label + AI badge · mono-kpi animated · delta pill · sparkline · drill-in. Variants: positive/negative/neutral, compact/large.

## 11. Command Palette (⌘K)
- Centered glass modal (e4), search field, grouped results (Navigate / Actions / Recent / Search results), keyboard-driven, fuzzy match, action icons + shortcuts shown.
- Nested actions ("Assign to…" → member list). Empty = recent + suggestions.

## 12. AI Assistant / Copilot Panel
- Right-docked panel (toggle), header ✦ "Copilot", message stream, suggestion chips ("Summarize", "Draft reply", "Find similar"), input.
- Inline action cards (accept/edit/regenerate), context badge ("reading: ticket #1042").

## 13. Supporting Primitives
- **Avatar** (image/initials, status ring, group stack), **Badge/Pill** (status, count, AI), **Tag/Chip** (removable), **Tooltip** (glass, fast), **Toast** (sonner-style), **Tabs** (underline slide), **Breadcrumbs**, **Pagination**, **Progress** (bar/ring), **Skeleton**, **Switch/Checkbox/Radio**, **Segmented control**, **Date range picker**, **Empty state**, **Banner/Alert**.

## 14. Component States Matrix (apply to all)
`default · hover · focus · active/pressed · selected · disabled · loading · error · empty · success`

## 15. Theming Contract
- Every component reads from tokens (`12-design-tokens.json`); no hard-coded colors.
- Dark + light parity guaranteed by token swap.
- Density + radius + motion all token-driven.
