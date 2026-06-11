# OmniAssist AI — Brand Identity

> Design System v1.0 · Creative Direction · "Calm intelligence, enterprise trust."

## 1. Brand Story

Every growing company drowns in the same problem: customers want instant, accurate, human-quality help on every channel — and the business can't scale humans fast enough. Support queues grow, sales leads go cold, and knowledge sits trapped in docs nobody reads.

**OmniAssist AI** was built to end that. It's not "a chatbot." It's an **AI workforce** — a support agent and a sales agent that know your business, speak every language, work every channel (chat, WhatsApp, email, voice), and hand off to a human the moment nuance demands it. It turns scattered knowledge into instant answers, and every conversation into insight.

The brand promise: **"Your customers always heard. Your team always ahead."**

## 2. Brand Personality

| Trait | What it means in the product |
|-------|------------------------------|
| **Intelligent, not flashy** | Substance over decoration. Motion has meaning. |
| **Calm & precise** | Linear-grade restraint. Dense but never cluttered. |
| **Trustworthy** | Stripe-grade polish signals "safe with enterprise data." |
| **Effortless** | Lovable-grade delight. Things feel alive, never heavy. |
| **Confident** | OpenAI/Vercel spaciousness. Big claims, clean execution. |

**Voice & tone:** Clear, warm, expert. Short sentences. Never hypey. "Resolved in 4s" beats "Amazing AI magic!"

**Archetype:** The Sage × The Magician — deep knowledge delivered effortlessly.

## 3. Logo Concepts

> Concepts (to be produced in Figma/vector during design build — code/export deferred).

**Wordmark:** `OmniAssist` set in Geist/Inter, medium weight, tight tracking. "Omni" in full white, "Assist" in a subtle indigo→violet gradient.

**Symbol — direction LOCKED: ✅ The Orbit** (other two kept as alternates).
1. **The Orbit (CHOSEN)** — a central node with an orbiting dot, forming an abstract "O" + "a". Represents *omni-channel intelligence revolving around the customer*. Works as a favicon, animates (the dot orbits on load / thinking states). This is the official OmniAssist symbol direction.
2. **The Pulse** — an "O" made of a soundwave/pulse line — represents voice + live conversation + "always listening."
3. **The Prism** — an "O" refracting a single input into multiple channel rays — represents one brain, many channels.

**Logo system:** full lockup (symbol + wordmark), symbol-only (app icon/favicon), monochrome, and an animated variant for splash/loading.

**Clear space:** min = height of the symbol's inner counter. **Min size:** 20px symbol, 88px lockup.

## 4. Color System

### Brand core
| Token | Hex | Use |
|-------|-----|-----|
| `brand-500` (primary) | `#6366F1` | Primary actions, focus, brand |
| `brand-400` | `#818CF8` | Hover, accents |
| `brand-600` | `#4F46E5` | Pressed |
| `violet-500` | `#8B5CF6` | Gradient partner |
| `gradient-brand` | `linear-gradient(135deg,#6366F1,#8B5CF6)` | Hero, CTAs, accents |

### Neutrals (dark-first ramp)
| Token | Hex | Use |
|-------|-----|-----|
| `bg-base` | `#08080A` | App background |
| `bg-subtle` | `#0E0E11` | Sections |
| `surface` | `#141417` | Cards |
| `surface-raised` | `#1A1A1F` | Popovers, modals |
| `border` | `#232329` | Hairlines |
| `border-strong` | `#2E2E36` | Inputs, dividers |
| `text-primary` | `#FAFAFA` | Headings/body |
| `text-secondary` | `#A1A1AA` | Supporting |
| `text-tertiary` | `#71717A` | Hints, meta |

### Semantic
| Token | Hex | Meaning |
|-------|-----|---------|
| `success` | `#22C55E` | Resolved, healthy |
| `warning` | `#F59E0B` | SLA at risk |
| `danger` | `#EF4444` | Breach, error |
| `info` | `#38BDF8` | Neutral info |
| `ai` | `#A78BFA` | AI-generated content marker |

### Data-viz palette (charts)
`#6366F1`, `#22D3EE`, `#A78BFA`, `#34D399`, `#F472B6`, `#FBBF24`, `#60A5FA`, `#F87171` — chosen for color-blind separation and dark-bg contrast.

### Light mode (mirrored)
`bg-base #FAFAFA`, `surface #FFFFFF`, `border #E4E4E7`, `text-primary #0A0A0A`, brand unchanged. (Full ramp in `12-design-tokens.json`.)

## 5. Typography System

| Role | Font | Notes |
|------|------|-------|
| **UI / Display** | **Geist** (fallback Inter) | Clean, modern, neutral |
| **Mono / Metrics / Code** | **Geist Mono** (fallback JetBrains Mono) | KPIs, IDs, code |

### Type scale (1.250 major-third, rem)
| Token | Size / Line | Weight | Use |
|-------|------------|--------|-----|
| `display-xl` | 60/64 | 600 | Landing hero |
| `display` | 48/52 | 600 | Section heroes |
| `h1` | 32/40 | 600 | Page titles |
| `h2` | 24/32 | 600 | Section titles |
| `h3` | 20/28 | 600 | Card titles |
| `body-lg` | 16/26 | 400 | Long-form |
| `body` | 14/22 | 400 | Default UI |
| `caption` | 12/16 | 500 | Labels, meta |
| `mono-kpi` | 28/32 | 500 | KPI numbers |

**Rules:** tracking tight on display (-0.02em), normal on body. Max line length 72ch for reading. Numbers always tabular (`font-variant-numeric: tabular-nums`).

## 6. Iconography

- **Library:** Lucide (1.5px stroke, 24px grid) for consistency with the linework brand.
- **AI/brand icons:** custom-drawn (orbit, pulse, prism) for AI features.
- **Rules:** 2px optical alignment, never mix stroke weights, status icons use semantic colors only, 20px in dense UI / 16px inline.
- **Channel icons:** WhatsApp, Email, Voice, Web — duotone with channel brand tint at low opacity.

## 7. Design Principles

1. **Clarity over cleverness** — if a user has to think, redesign it.
2. **Dense, not cramped** — maximize information, protect breathing room (Linear).
3. **Motion with meaning** — every animation explains a state change.
4. **AI is visible, never spooky** — always show sources, confidence, and a human escape hatch.
5. **Dark-first, light-perfect** — both themes are first-class, not afterthoughts.
6. **Trust by detail** — pixel alignment, consistent radii, real empty/loading/error states.
7. **Keyboard is a first-class citizen** — cmd-K everywhere, every action reachable.
8. **Accessible by default** — AA contrast, focus rings, reduced-motion respected.
