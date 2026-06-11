# OmniAssist AI — High-Fidelity Wireframes

> v1.0 · Low-detail-loss ASCII wireframes (layout, hierarchy, components) for every screen.
> Render reference: dark-first, 1280px content, 264px sidebar. `[≡]` = nav, `◐` = avatar, `▰` = chart.

---

## 1. Landing Page
```
┌───────────────────────────────────────────────────────────────────────┐
│ ◇ OmniAssist        Product  Solutions  Pricing  Docs    [Login] [Start]│  ← glass on scroll
├───────────────────────────────────────────────────────────────────────┤
│                    ✦ mesh gradient backdrop ✦                           │
│              The AI workforce for customer support & sales              │  display-xl, gradient text
│        One AI brain across chat, WhatsApp, email & voice — grounded     │
│                 in your knowledge, escalates to humans.                 │
│               [ Start free → ]   [ Book a demo ]                        │
│        ┌───────────────── product preview (animated) ─────────────────┐ │
│        │  live inbox mock · streaming AI reply · KPI counters tick up  │ │
│        └───────────────────────────────────────────────────────────────┘│
│   ▢ logos: trusted by …  (marquee)                                      │
│   ── Bento features grid: Omnichannel · RAG · Handoff · Analytics ──    │
│   ── "How it works" 3 steps · Testimonials · Pricing teaser · CTA ──    │
│   Footer: product / company / legal / socials                          │
└───────────────────────────────────────────────────────────────────────┘
```

## 2. Login
```
┌──────────────────────────────┬────────────────────────────────────────┐
│  ✦ animated brand panel       │   ◇ OmniAssist                          │
│  orbit logo + gradient mesh   │   Welcome back                          │
│  "Your customers always       │   Email   [______________________]      │
│   heard."                     │   Password[______________________] 👁    │
│  • testimonial quote          │   [  Continue  ]  (brand gradient)      │
│                               │   ───────  or  ───────                  │
│                               │   [G  Google]   [⌥ GitHub]              │
│                               │   New here? Create account →            │
└──────────────────────────────┴────────────────────────────────────────┘
```

## 3. Signup
```
Same split layout. Right side:
  Create your workspace
  Full name [______]   Work email [______]
  Password  [______]   (strength meter)
  Workspace name [______]  → slug preview omniassist.ai/acme
  [ Create workspace ]   · SSO option · ToS checkbox
  Step indicator: 1 Account · 2 Workspace · 3 Invite team (skippable)
```

## 4. Dashboard
```
┌────────┬──────────────────────────────────────────────────────────────┐
│[≡]Nav  │ Topbar: [Acme ▾]  ⌕ Search (⌘K)        🔔3   ? ◐               │
│ ⌂ Dash │──────────────────────────────────────────────────────────────│
│ ✉ Inbox│ Good evening, Priya 👋        Today ▾   [+ New]                │
│ ⊟ Tick │ ┌─KPI──────┐┌─KPI──────┐┌─KPI──────┐┌─KPI──────┐              │
│ ◆ Leads│ │Deflection││  CSAT    ││ Avg FRT  ││ Open     │  count-up + ▰ │
│ ✦ Agnt │ │  72% ↑4  ││ 4.6 ↑.2  ││  4.2s ↓  ││  38      │  sparkline    │
│ ▣ KB   │ └──────────┘└──────────┘└──────────┘└──────────┘              │
│ ▤ Anlt │ ┌── Conversations volume (area chart) ──┐ ┌─ AI Insights ──┐ │
│ ◫ Team │ │ ▰▰▰▰▰▰▰▰▰  by channel, animated        │ │ ✦ "WhatsApp up  │ │
│ ⚙ Set  │ └────────────────────────────────────────┘ │   23% — staff?"│ │
│        │ ┌── Live activity feed (real-time) ──────┐ │ ✦ "3 SLA risks"│ │
│ ◐ Priya│ │ • AI resolved #1042 · 2s ago           │ └────────────────┘ │
│        │ │ • Handoff requested · WhatsApp · now    │  ┌ Team presence ┐ │
│        │ │ • New hot lead: Acme Corp · 1m          │  │ ◐◐◐ 5 online  │ │
│        │ └─────────────────────────────────────────┘ └────────────────┘ │
└────────┴──────────────────────────────────────────────────────────────┘
```

## 5. AI Chat (widget — customer side)
```
        ┌───────────────────────────────┐
        │ ◇ Acme Support      — _  ✕     │  glass header
        │───────────────────────────────│
        │  ◇ Hi! How can I help today?   │  AI bubble
        │  [Track order][Pricing][Human] │  quick replies
        │                                │
        │              Where's my order? ◐│ user bubble (right)
        │  ◇ ●●● typing…                 │  AI typing dots
        │  ◇ Your order #882 ships today.│  streamed
        │     📎 Sources: Shipping FAQ   │  source pill
        │     👍 👎   Was this helpful?   │
        │───────────────────────────────│
        │ [ Type a message…        ] ➤  │  composer
        │ powered by OmniAssist          │
        └───────────────────────────────┘
```

## 6. WhatsApp Inbox (agent side)
```
┌────────┬──────────────────┬─────────────────────────┬──────────────────┐
│ Nav    │ Conversations     │  Thread · WhatsApp       │ Context panel    │
│        │ [All|WA|Email|Web]│  ◐ Rahul  🟢 online      │ Contact          │
│        │ ⌕ filter          │  ┌──────────────────────┐│  Rahul Sharma    │
│        │ ● Rahul   2m  🟢  │  │ Rahul: bill issue?   ││  +91 98xxx       │
│        │ ○ Meera   8m      │  │ ◇AI: I can help…     ││  3 past convos   │
│        │ ○ John    1h ✓    │  │     📎 Billing FAQ   ││──────────────────│
│        │ ○ …               │  │ Rahul: talk to human ││ AI Summary ✦     │
│        │                   │  │ ⟳ Handoff requested  ││ "Billing dispute,│
│        │                   │  └──────────────────────┘│  wants refund."  │
│        │                   │  [Take over] suggested ✦ ││ Sentiment 😠 neg │
│        │                   │  [ msg…           ] ➤    ││ [KB][Copilot]    │
└────────┴──────────────────┴─────────────────────────┴──────────────────┘
```

## 7. Email Inbox
```
┌────────┬──────────────────┬─────────────────────────────────────────────┐
│ Nav    │ Email threads     │  Subject: Refund request — #1042             │
│        │ ⌕  [Unread|All]   │  ◐ from rahul@acme.com · 10:24                │
│        │ ● Refund request  │  ┌── original email ──────────────────────┐  │
│        │ ○ Demo follow-up  │  │ "I was charged twice…"                  │  │
│        │ ○ Invoice query   │  └─────────────────────────────────────────┘  │
│        │                   │  ✦ AI draft reply (editable)                 │
│        │                   │  ┌─────────────────────────────────────────┐ │
│        │                   │  │ Hi Rahul, sorry about that. I've…       │ │
│        │                   │  │ 📎 grounded in Billing Policy           │ │
│        │                   │  └─────────────────────────────────────────┘ │
│        │                   │  [ Send ] [ Edit ] [ Regenerate ✦ ]          │
└────────┴──────────────────┴─────────────────────────────────────────────┘
```

## 8. Ticket Dashboard
```
┌────────┬──────────────────────────────────────────────────────────────┐
│ Nav    │ Tickets        [My|Unassigned|All]   ⌕   [Filters ▾] [+ New]   │
│        │ ┌──────────────────────────────────────────────────────────┐  │
│        │ │ # ▢ Subject          Status    Priority  SLA      Assignee│  │
│        │ │ 1042 Refund issue    ● Open    ▲ High    ⏱ 12m   ◐ Priya │  │
│        │ │ 1041 Login broken    ◐ Pend.   ▲ High    ⏱ 02m!  —       │  │  red SLA
│        │ │ 1040 Feature ask     ○ Open    ◦ Low     —       ◐ Arjun │  │
│        │ │ 1039 …                                                    │  │
│        │ └──────────────────────────────────────────────────────────┘  │
│        │ bulk: [Assign][Tag][Resolve]   · pagination ‹ 1 2 3 ›          │
└────────┴──────────────────────────────────────────────────────────────┘
```

## 9. Ticket Details
```
┌────────┬───────────────────────────────────────┬────────────────────────┐
│ Nav    │ ‹ Tickets / #1042                       │  Properties            │
│        │ Refund issue        ● Open  ▲ High      │  Status   [Open ▾]     │
│        │ ┌── conversation timeline ────────────┐ │  Priority [High ▾]     │
│        │ │ ◐ Rahul: charged twice…             │ │  Assignee [◐ Priya ▾]  │
│        │ │ ◇ AI: looked into it…  📎           │ │  Tags  [billing][refund]│
│        │ │ ◐ Priya (agent): processing refund  │ │  SLA   ⏱ 12m left      │
│        │ └──────────────────────────────────────┘ │────────────────────────│
│        │ ✦ AI Summary: "Double charge, refund    │  Linked conversation → │
│        │   approved, ETA 3 days. Next: confirm." │  Activity / audit      │
│        │ [ reply…                       ] ➤      │  [Copilot ✦]           │
└────────┴───────────────────────────────────────┴────────────────────────┘
```

## 10. Lead Dashboard
```
┌────────┬──────────────────────────────────────────────────────────────┐
│ Nav    │ Leads   [Pipeline|All|Tasks]    ⌕   [Filters ▾]   [+ Lead]     │
│        │ ┌── KPI: New 24 · Qualified 11 · Demos 6 · Won 3 ──┐           │
│        │ │ Lead          Score  Stage      Owner   Next action          │
│        │ │ Acme Corp     🔥92   Demo       ◐ Sara  Demo Fri 3pm         │
│        │ │ Beta Inc      68     Qualified  ◐ Sara  Follow-up email      │
│        │ │ …                                                            │
│        │ └──────────────────────────────────────────────────────────────┘
└────────┴──────────────────────────────────────────────────────────────┘
```

## 11. CRM Pipeline (Kanban)
```
┌────────┬──────────────────────────────────────────────────────────────┐
│ Nav    │ Pipeline                                  [Board|List]  ⌕      │
│  ┌ New ──────┐┌ Qualified ┐┌ Demo ─────┐┌ Proposal ┐┌ Won ───┐         │
│  │┌────────┐ ││┌────────┐ ││┌────────┐ ││┌────────┐││┌──────┐│         │
│  ││Acme 🔥 │ │││Beta    │ │││Gamma   │ │││Delta   ││││Echo  ││  drag-drop
│  ││$12k    │ │││$8k     │ │││$20k    │ │││$15k    ││││$9k   ││  cards
│  ││◐ Sara  │ │││◐ Sara  │ │││◐ Raj   │ │││◐ Sara  ││││◐ Raj ││         │
│  │└────────┘ ││└────────┘ ││└────────┘ ││└────────┘││└──────┘│         │
│  │ + add     ││           ││           ││          ││        │         │
│  └───────────┘└───────────┘└───────────┘└──────────┘└────────┘         │
└────────┴──────────────────────────────────────────────────────────────┘
```

## 12. Knowledge Base
```
┌────────┬──────────────────────────────────────────────────────────────┐
│ Nav    │ Knowledge Base  [Docs|Sites|FAQs|Test]   [+ Add source ▾]      │
│        │ ┌─ dropzone: drag PDFs/DOCX or paste URL to crawl ───────────┐ │
│        │ └────────────────────────────────────────────────────────────┘ │
│        │ ┌────────┐┌────────┐┌────────┐┌────────┐                       │
│        │ │📄 Refund││📄 Pricing││🌐 docs ││❓ FAQ  │  status chips:        │
│        │ │● ready  ││◐ indexing││● ready ││● ready │  ready/processing    │
│        │ │128 chunk││ 64%      ││412 chk ││22 Q&A  │                      │
│        │ └────────┘└────────┘└────────┘└────────┘                       │
│        │ ── Retrieval test: [ query… ] → top chunks + similarity score ─ │
└────────┴──────────────────────────────────────────────────────────────┘
```

## 13. Analytics
```
┌────────┬──────────────────────────────────────────────────────────────┐
│ Nav    │ Analytics  [Overview|Convos|Tickets|Sales|AI]  Range[30d ▾] ⤓  │
│        │ ┌KPI┐┌KPI┐┌KPI┐┌KPI┐  animated count + delta + sparkline        │
│        │ ┌── Volume by channel (stacked area) ──┐┌ Deflection gauge ──┐ │
│        │ │ ▰▰▰▰▰▰▰▰▰▰▰▰▰▰                       ││   ◔ 72%            │ │
│        │ └───────────────────────────────────────┘└────────────────────┘ │
│        │ ┌ CSAT trend (line) ┐┌ Resolution time ┐┌ AI vs Human split ─┐ │
│        │ │ ▰▰▱▰▰▰            ││ ▰ histogram      ││  donut 68/32       │ │
│        │ └───────────────────┘└──────────────────┘└────────────────────┘ │
│        │ ── Top intents · Sentiment heatmap · Agent leaderboard ──        │
└────────┴──────────────────────────────────────────────────────────────┘
```

## 14. Team Management
```
┌────────┬──────────────────────────────────────────────────────────────┐
│ Nav    │ Team  [Members|Roles|Invites]              [+ Invite]          │
│        │ Member          Email            Role        Status   Last seen│
│        │ ◐ Priya R.      priya@acme.com   Owner       ●active  now      │
│        │ ◐ Arjun K.      arjun@…          Agent       ●active  2m       │
│        │ ◐ Sara M.       sara@…           Agent(Sales)●active  1h       │
│        │ ◐ Dev P.        dev@…            Admin       ●active  3h       │
│        │  [role ▾] inline · remove · resend invite                      │
└────────┴──────────────────────────────────────────────────────────────┘
```

## 15. Audit Logs
```
┌────────┬──────────────────────────────────────────────────────────────┐
│ Nav    │ Audit Logs   [Actor▾][Action▾][Resource▾][Date▾]   ⤓ Export    │
│        │ ⏱ 10:24  ◐ Dev    changed role  user:Arjun  Agent→Admin  [diff]│
│        │ ⏱ 09:58  ◐ Priya  deleted doc   kb:Refund-v1            [diff] │
│        │ ⏱ 09:30  ◐ system breached SLA  ticket:#1041                   │
│        │  (immutable · click row → side diff viewer)                    │
└────────┴──────────────────────────────────────────────────────────────┘
```

## 16. Settings
```
┌────────┬──────────┬───────────────────────────────────────────────────┐
│ Nav    │ Settings  │ Channels                                          │
│        │ General   │ ┌ Website   ● connected   [Configure]            │ │
│        │ ▸Channels │ │ WhatsApp  ● connected   +1 415…   [Configure]  │ │
│        │ AI config │ │ Email     ⚠ setup       [Connect Gmail]        │ │
│        │ Notify    │ │ Voice     ● connected   [Configure]            │ │
│        │ API keys  │ └─────────────────────────────────────────────────┘ │
│        │ Billing   │ (each section is a card with inline forms)        │
│        │ Audit     │                                                   │
│        │ Security  │                                                   │
└────────┴──────────┴───────────────────────────────────────────────────┘
```

## 17. Profile
```
┌────────┬──────────────────────────────────────────────────────────────┐
│ Nav    │ Profile                                                       │
│        │ ◐ (upload)   Full name [Priya Rao]   Email [priya@acme.com]   │
│        │ Title [Support Lead]   Timezone [IST ▾]   Language [EN ▾]      │
│        │ ── Preferences: Theme [Dark ▾]  Notifications [✓ email ✓ slack]│
│        │ ── Security: Password · 2FA [Enable]  Active sessions          │
│        │ [ Save changes ]                                              │
└────────┴──────────────────────────────────────────────────────────────┘
```

> Every screen ships with documented **empty / loading (skeleton) / error** variants per `04-information-architecture.md §6`.
