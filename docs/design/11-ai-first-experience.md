# OmniAssist AI — AI-First Experience Design

> v1.0 · The interactions that make OmniAssist feel like an AI-native product, not a CRM with a chatbot bolted on.

## 1. Philosophy

AI is a **visible, trustworthy teammate** — never a black box.
Three rules govern every AI surface:
1. **Show your work** — sources + confidence on every factual answer.
2. **Always an escape hatch** — a human is one tap away, everywhere.
3. **Suggest, don't seize** — AI proposes; the human (or rules) approves high-stakes actions.

## 2. AI Copilot (agent-facing)

A right-docked panel present across Inbox, Tickets, Leads.
```
┌── ✦ Copilot ──────────────── reading: #1042 ─┐
│ Suggestions                                   │
│ [✦ Summarize thread] [✦ Draft reply]          │
│ [✦ Find similar tickets] [✦ Sentiment]        │
│───────────────────────────────────────────────│
│ ✦ Suggested reply (grounded in Billing FAQ)   │
│ "Hi Rahul, I've refunded the duplicate…"      │
│ 📎 Billing Policy · confidence 91%            │
│ [Insert] [Edit] [Regenerate]                  │
│───────────────────────────────────────────────│
│ [ Ask copilot…                          ] ➤   │
└────────────────────────────────────────────────┘
```
- Context-aware (knows the open ticket/conversation).
- Actions: summarize, draft, translate, find similar, suggest next step, lookup KB.
- Every output: source pills + confidence + insert/edit/regenerate (Cursor-style accept loop).

## 3. Smart Suggestions

- **Reply suggestions** appear inline above the composer (1–3 chips) — tap to insert.
- **Next best action** on tickets/leads ("Offer refund", "Book demo", "Escalate").
- **Smart routing** — AI suggests the best agent/team for a handoff.
- **Tag/priority suggestions** auto-proposed, one-tap accept.
- Suggestions fade in subtly; dismiss is always available; learn from accept/reject.

## 4. AI-Generated Summaries

- **Conversation summary** (on handoff/close): TL;DR + intent + sentiment + resolution + next steps.
- **Ticket summary** card at top of detail — collapsible, regenerate-able, timestamped.
- **Daily digest** — AI insight cards on dashboard (trends, risks, opportunities).
- **Call summary** — auto after voice calls (transcript → summary → ticket).
- Visual marker: ✦ icon + `ai` color left-border so AI content is always distinguishable.

## 5. Context Panels

- Right panel on conversations shows AI-derived context: contact history, detected intent, live sentiment meter, matched KB sources, suggested actions.
- **Sentiment meter:** animated gauge (😠→😐→😊) updating per message.
- **Confidence indicator:** on every AI answer, a small animated bar + % (green ≥80, amber 50–79, red <50 → auto-handoff trigger).
- **Source explorer:** click a source pill → preview the exact KB chunk used.

## 6. Agent Collaboration UI (Human + AI together)

```
Conversation thread shows three actor types distinctly:
  ◇ AI        (✦, surface bubble)
  ◐ Agent     (avatar, brand-tinted)
  ◐ Customer  (avatar, right side)

Handoff ribbon:  ── ⟳ AI handed off to Priya · context attached ──
Return ribbon:   ── ↩ Priya handed back to AI · note: 'refund done' ──
```
- **Live co-presence:** when an agent takes over, AI stays as copilot (suggests, never sends without approval).
- **Whisper mode:** AI can suggest privately to the agent (not visible to customer).
- **Takeover/return** is one click, fully logged, context always preserved.

## 7. AI Transparency & Trust Patterns

| Pattern | UI |
|---------|----|
| Sources | pills under every factual answer → click to view chunk |
| Confidence | animated bar + %; low → auto-suggest handoff |
| "Why this?" | hover on suggestion → rationale tooltip |
| Edit before send | all auto-replies reviewable (configurable auto-send) |
| Human escape | "Talk to a human" always visible in every channel |
| Audit | every AI action logged (which agent, model, tokens, confidence) |
| Guardrails | AI says "I'm not sure" + escalates rather than hallucinate |

## 8. Onboarding the AI (admin-facing)

- **Agent config** as a friendly form: personality, tone, guardrails, allowed tools, confidence threshold, languages.
- **Test sandbox:** chat with the agent live while editing the prompt; see retrieved sources + confidence in real time.
- **KB health:** "Your AI can confidently answer 84% of common questions" → gaps highlighted with suggested docs to add.

## 9. AI Visual Language

- **Marker:** ✦ sparkle + `ai` (#A78BFA) accent / `gradient-ai` for AI surfaces.
- **Motion:** orbit-logo micro-spin while thinking; streaming caret; staggered source reveal.
- **Tone of microcopy:** confident but humble — "Here's what I found" / "I'm not certain, connecting a teammate."

## 10. Differentiator Summary
OmniAssist's AI is **fast (streaming), grounded (sources), honest (confidence + handoff), and collaborative (copilot + whisper)** — wrapped in premium motion. That combination is the product's signature experience.
