# OmniAssist AI — Design System Foundations

> v1.0 · Tokens, spacing, elevation, glass, motion, themes, accessibility.
> Machine-readable values live in `12-design-tokens.json`.

## 1. Spacing Scale (4px base grid)

| Token | px | Use |
|-------|----|-----|
| `space-0` | 0 | reset |
| `space-1` | 4 | icon ↔ text |
| `space-2` | 8 | tight stacks |
| `space-3` | 12 | input padding |
| `space-4` | 16 | default gap |
| `space-5` | 20 | card padding |
| `space-6` | 24 | section gap |
| `space-8` | 32 | block spacing |
| `space-10` | 40 | page gutters |
| `space-12` | 48 | major sections |
| `space-16` | 64 | hero spacing |
| `space-24` | 96 | landing rhythm |

**Layout:** 12-col grid, 1280px max content, 24px gutters desktop / 16px mobile. Dashboard sidebar 264px (collapsed 72px).

## 2. Border Radius System

| Token | px | Use |
|-------|----|-----|
| `radius-sm` | 6 | chips, tags, inputs (compact) |
| `radius-md` | 8 | buttons, inputs |
| `radius-lg` | 12 | cards |
| `radius-xl` | 16 | modals, panels |
| `radius-2xl` | 20 | feature cards, sheets |
| `radius-full` | 9999 | avatars, pills, toggles |

Rule: nested elements step down one level (card `lg` → inner `md`).

## 3. Elevation System (z + surface + shadow)

| Level | Surface | Shadow | Use |
|-------|---------|--------|-----|
| `e0` | `bg-base` | none | page |
| `e1` | `surface` | `shadow-sm` | cards |
| `e2` | `surface-raised` | `shadow-md` | dropdowns, popovers |
| `e3` | `surface-raised` | `shadow-lg` + border | modals, command palette |
| `e4` | glass | `shadow-xl` + glow | toasts, AI copilot panel |

## 4. Shadows (dark-tuned — soft, low-opacity)

```
shadow-sm:  0 1px 2px rgba(0,0,0,.40)
shadow-md:  0 4px 12px rgba(0,0,0,.45)
shadow-lg:  0 12px 32px rgba(0,0,0,.55)
shadow-xl:  0 24px 64px rgba(0,0,0,.60)
glow-brand: 0 0 0 1px rgba(99,102,241,.30), 0 8px 32px rgba(99,102,241,.25)
glow-ai:    0 0 24px rgba(167,139,250,.30)
```
In light mode shadows shift to `rgba(16,24,40,.06–.14)` (Stripe-like, subtle).

## 5. Glassmorphism Rules

Use **sparingly** — only for floating/overlay surfaces, never base content.
```
glass-panel:
  background: rgba(20,20,23,0.60)
  backdrop-filter: blur(20px) saturate(140%)
  border: 1px solid rgba(255,255,255,0.08)
  inner-highlight: inset 0 1px 0 rgba(255,255,255,0.06)
```
Allowed on: top bar (on scroll), command palette, AI copilot panel, toasts, modal scrim cards. **Banned on:** data tables, long text, dense lists (legibility).

## 6. Gradients

| Token | Value | Use |
|-------|-------|-----|
| `gradient-brand` | `135deg, #6366F1 → #8B5CF6` | CTAs, key accents |
| `gradient-ai` | `135deg, #8B5CF6 → #22D3EE` | AI features, copilot |
| `gradient-surface` | `180deg, #141417 → #0E0E11` | card depth |
| `gradient-mesh` | radial multi-stop (indigo/violet/cyan @ 6–10% opacity) | hero/empty-state backdrops |
| `gradient-text` | brand gradient clipped to text | hero headlines, KPI emphasis |

Rule: gradients are accents, not fills for large readable areas. Always pair with a solid fallback.

## 7. Animation Rules (see `07-animations.md` for full spec)

| Token | Duration | Easing | Use |
|-------|----------|--------|-----|
| `motion-instant` | 80ms | ease-out | hovers, toggles |
| `motion-fast` | 160ms | `cubic-bezier(.2,.8,.2,1)` | buttons, tooltips |
| `motion-base` | 240ms | `cubic-bezier(.2,.8,.2,1)` | cards, drawers |
| `motion-slow` | 400ms | spring(stiffness 300, damping 30) | page transitions, modals |
| `motion-ai` | 600ms+ | spring soft | AI typing, streaming |

Principles: animate transform/opacity only (60fps), stagger lists 30–40ms, always honor `prefers-reduced-motion` (swap to instant fades).

## 8. Dark Mode System (default)

- Base `#08080A`, never pure black (reduces smear/halation).
- Surfaces lighten as they rise (e0→e4), borders carry hierarchy (not heavy shadows).
- Text contrast: primary ≥ 14:1, secondary ≥ 7:1, tertiary ≥ 4.5:1.
- Accent glow used to draw the eye to primary action / live data.

## 9. Light Mode System

- Base `#FAFAFA`, surfaces `#FFFFFF`, borders `#E4E4E7` (Stripe/Notion calm).
- Shadows replace glow for elevation; brand color unchanged for parity.
- Same token names → theme is a value swap, not a redesign.

## 10. Accessibility Standards

| Standard | Rule |
|----------|------|
| **Contrast** | WCAG **AA** min (text 4.5:1, UI 3:1); target AAA for body |
| **Focus** | Visible 2px brand focus ring on every interactive element |
| **Keyboard** | Full nav, cmd-K, focus traps in modals, ESC to close |
| **Motion** | `prefers-reduced-motion` → disable non-essential animation |
| **Targets** | Min 40×40px hit area (44 on mobile) |
| **Semantics** | ARIA roles/labels, live regions for streaming AI + toasts |
| **Color** | Never color-only meaning; pair with icon/label |
| **Forms** | Labels always visible, inline errors with text + icon |
| **Screen reader** | AI responses announced via `aria-live="polite"` |
