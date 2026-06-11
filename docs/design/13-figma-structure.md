# OmniAssist AI — Figma File Structure & Component Hierarchy

> v1.0 · How the design is organized in Figma. (Figma MCP key is configured; provide a `fileKey` to sync/pull.)

## 1. Figma File / Project Organization

```
📁 OmniAssist AI (Figma Project)
├── 📄 00 · Cover & Index
├── 📄 01 · Foundations
│     ├── Colors (dark + light styles)
│     ├── Typography (text styles)
│     ├── Spacing & Grid
│     ├── Radius & Elevation
│     ├── Shadows & Glass (effect styles)
│     └── Iconography
├── 📄 02 · Components (the library)
│     ├── Buttons / Inputs / Selects
│     ├── Cards / Tables / Tabs
│     ├── Modals / Drawers / Sheets
│     ├── Chat (bubbles, composer, typing)
│     ├── Ticket & Lead cards
│     ├── KPI & Analytics widgets
│     ├── Command palette
│     ├── AI Copilot / Context panels
│     └── Navigation (sidebar, topbar, tabs, bottom-bar)
├── 📄 03 · Patterns
│     ├── Empty / Loading / Error states
│     ├── Forms
│     └── Data viz set
├── 📄 04 · Marketing
│     ├── Landing · Pricing · Docs shell
├── 📄 05 · App — Desktop
│     ├── Auth (Login, Signup)
│     ├── Dashboard
│     ├── Inbox (Web / WhatsApp / Email / Voice)
│     ├── Tickets (list + detail)
│     ├── Leads (list + pipeline)
│     ├── AI Agents (config + sandbox)
│     ├── Knowledge Base
│     ├── Analytics
│     ├── Team / Roles
│     ├── Settings / Audit
│     └── Profile
├── 📄 06 · App — Mobile
│     ├── Dashboard · Chat · Tickets · Analytics
├── 📄 07 · Prototypes & Flows
│     └── Linked interactive flows per user journey
└── 📄 08 · Handoff & Specs
      └── Redlines, tokens export, dev notes
```

## 2. Figma Variables & Styles (maps to design tokens)

- **Color variables** → two modes: `Dark` (default), `Light`. Names match `12-design-tokens.json` (`color/brand/500`, `color/surface`, etc.).
- **Number variables** → spacing, radius (`space/4`, `radius/lg`).
- **Text styles** → `display-xl … caption`, mono set.
- **Effect styles** → shadows + glass.
- **Mode switch** on any frame toggles dark/light instantly.

## 3. Component Hierarchy (atomic structure)

```
Atoms        → color, type, icon, spacing, radius (variables)
Primitives   → Button, Input, Avatar, Badge, Tag, Tooltip, Switch, Skeleton
Composites   → Dropdown, Modal, Drawer, Table, Tabs, Chat bubble, KPI card,
               Command palette item, Toast, Form field
Patterns     → Inbox 3-pane, Ticket detail, Pipeline board, Analytics grid,
               Copilot panel, Empty/Loading/Error
Templates    → Page layouts (App shell, Auth, Marketing)
Pages        → Final composed screens (desktop + mobile)
```

### Component variant properties (Figma)
- Every component built with **variants + props**: `variant`, `size`, `state`, `theme` (via mode), `hasIcon`, `loading`, `disabled`.
- **Auto-layout** everywhere (responsive resize).
- **Boolean props** for optional parts (badge, trailing icon, sources).

## 4. Naming Conventions

- Components: `Category/Name` → `Button/Primary`, `Card/KPI`, `Chat/Bubble`.
- Frames: `NN · Screen Name` (ordered).
- Layers: semantic (`header`, `kpi-strip`, `chart/area`) not "Group 14".
- Styles/variables mirror token JSON paths exactly → 1:1 dev handoff.

## 5. MCP Sync Plan (Figma)

When a `fileKey` is provided:
1. `get_figma_data(fileKey)` → pull frames, styles, variables → reconcile with `12-design-tokens.json`.
2. `download_figma_images` → export logo, icons, illustrations, empty-state art.
3. Keep tokens as **single source of truth**: Figma variables ↔ JSON ↔ code theme stay in sync.
> If no Figma file exists yet, design proceeds **code-first** from this documented system; a Figma library can be generated afterward to match.

## 6. Prototype Coverage (clickable flows)
- Customer: website chat → handoff.
- Agent: dashboard → inbox → resolve.
- Sales: lead → pipeline → demo booked.
- Admin: invite member → role change → audit.
- Each prototype uses real components + Smart Animate matching the motion spec (`07-animations.md`).
