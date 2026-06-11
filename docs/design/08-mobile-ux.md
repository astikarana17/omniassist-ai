# OmniAssist AI — Mobile UX Spec

> v1.0 · Responsive web (no native app in v1). Mobile = first-class, not shrunk desktop.

## 1. Responsive Strategy

| Breakpoint | Layout |
|-----------|--------|
| `< 640` (mobile) | Single column, bottom tab bar, off-canvas nav, sheets instead of drawers |
| `640–1024` (tablet) | 2-pane (list + detail), collapsible sidebar |
| `> 1024` (desktop) | Full 3-pane, persistent sidebar |

**Navigation on mobile:** left rail → **bottom tab bar**: `Dashboard · Inbox · Tickets · Analytics · More`. cmd-K → floating search FAB.

## 2. Mobile — Dashboard
```
┌──────────────────────────┐
│ Acme ▾        🔔   ◐      │
│ Good evening, Priya       │
│ ┌──────────┐┌──────────┐  │  KPIs: 2-col, swipeable carousel
│ │Deflection││  CSAT    │  │
│ │ 72% ↑    ││ 4.6 ↑    │  │
│ └──────────┘└──────────┘  │
│ ┌── Volume (area) ─────┐  │  charts full-width, simplified
│ │ ▰▰▰▰▰▰              │  │
│ └──────────────────────┘  │
│ ✦ AI Insights (stacked)   │
│ ● Live feed (collapsible) │
├──────────────────────────┤
│ ⌂   ✉   ⊟   ▤   •••      │  bottom tabs
└──────────────────────────┘
```

## 3. Mobile — Chat / Inbox
```
┌──────────────────────────┐
│ ‹ Rahul · WhatsApp  🟢 ⋮ │  back + context (⋮ opens sheet)
│──────────────────────────│
│  ◇ AI: I can help…       │  full-width bubbles
│  📎 Billing FAQ          │
│              user msg ◐  │
│  ◇ ●●● typing            │
│──────────────────────────│
│ [ message…          ] ➤  │  sticky composer (safe-area)
└──────────────────────────┘
Context panel → swipe up / ⋮ → bottom sheet (contact, AI summary, sentiment, handoff)
```
- Inbox list ↔ thread = full-screen push navigation (not split).
- Quick actions via swipe on conversation rows (resolve, assign, snooze).

## 4. Mobile — Ticketing
```
┌──────────────────────────┐
│ Tickets   [My ▾]  ⌕  ⚲   │
│ ┌── #1042 Refund ───────┐ │  card list (not table)
│ │ ● Open  ▲High  ⏱12m   │ │
│ │ ◐ Priya               │ │
│ └────────────────────────┘ │
│ ┌── #1041 Login ────────┐ │
│ │ ◐ Pend ▲High ⏱02m!    │ │  red SLA pulse
│ └────────────────────────┘ │
│            [ + New ]  FAB  │
└──────────────────────────┘
Detail = full screen; properties in a bottom sheet; AI summary card on top.
```

## 5. Mobile — Analytics
```
┌──────────────────────────┐
│ Analytics  [30d ▾]  ⤓     │
│ KPI carousel ← swipe →    │
│ ┌── chart (tap = full) ─┐ │  tap chart → fullscreen landscape view
│ │ ▰▰▰▰▰▰               │ │
│ └──────────────────────┘  │
│ Tabs as horizontal scroll │
│ [Overview][Convos][Sales] │
└──────────────────────────┘
```

## 6. Mobile Interaction Rules

- **Touch targets:** ≥ 44×44px; spacing ≥ 8px.
- **Gestures:** swipe rows (actions), pull-to-refresh lists, swipe-down to dismiss sheets, long-press = multi-select.
- **Sheets over modals:** bottom sheets with drag handle; snap points (peek / full).
- **Thumb zone:** primary actions reachable bottom-third; FAB for create.
- **Safe areas:** respect notch/home indicator; sticky composer above keyboard.
- **Performance:** lazy-load lists (virtualized), reduce chart detail, defer animations.
- **Offline:** queue outgoing messages, show "sending…", reconcile on reconnect.

## 7. Responsive Component Behavior

| Component | Desktop | Mobile |
|-----------|---------|--------|
| Sidebar | persistent rail | bottom tabs + drawer |
| Data table | columns | stacked cards |
| Right drawer | side panel | bottom sheet |
| Command palette | centered modal | full-screen search |
| 3-pane inbox | side by side | push navigation |
| KPI strip | 4 across | 2-col carousel |
| Charts | full detail | simplified + tap-to-expand |
