# OmniAssist AI — Product Requirements Document (PRD)

> Phase 1 · v1.0 · Owner: Founder/Staff Eng · Status: **Draft for approval**

## 1. Vision

**OmniAssist AI** is an enterprise-grade, multi-tenant SaaS platform that gives any business an **AI Customer Support Agent** and an **AI Sales Agent** across every channel — Website Chat, WhatsApp, Email, and Voice — grounded in the company's own knowledge via RAG, with full ticketing, human handoff, analytics, and governance (RBAC + audit logs).

**One-line pitch:** *"Intercom + Zendesk + a sales SDR, replaced by AI agents that actually know your business."*

## 2. Target Users & Personas

| Persona | Role | Primary needs |
|---------|------|---------------|
| **Priya — Support Lead** | Ops/CX manager | Deflect tickets, monitor CSAT, manage handoffs, see analytics |
| **Arjun — Support Agent** | Frontline human agent | Take over AI conversations, use AI summaries, resolve tickets fast |
| **Sara — Sales Manager** | Revenue | AI qualifies/nurtures leads, books demos, pushes to pipeline |
| **Dev — Admin/IT** | Platform owner | Configure channels, manage RBAC, upload KB, audit security |
| **End Customer** | Visitor/buyer | Get instant, accurate answers on any channel, escalate to a human |

## 3. Goals & Non-Goals

### Goals (MVP → v1)
- Multi-tenant (workspace/organization isolation, row-level security).
- AI Support + AI Sales agents powered by Claude + LangGraph, grounded in RAG.
- Omnichannel: Website widget, WhatsApp, Email, Voice.
- RAG knowledge base (upload docs, crawl site, sync FAQs).
- Ticketing with statuses, assignment, SLAs.
- Human handoff (AI → live agent) with full context.
- Sentiment analysis + AI ticket summaries.
- Analytics dashboard (deflection, CSAT, response time, volume).
- RBAC (Owner/Admin/Agent/Viewer) + audit logs.
- Feedback (thumbs + CSAT) and Slack notifications.

### Non-Goals (v1)
- Full CRM replacement (Zoho explicitly **excluded** from this project).
- Native mobile apps (responsive web only).
- On-prem deployment (cloud SaaS only).
- Outbound cold-call dialer at scale.

## 4. Core Modules & Requirements

| # | Module | Key requirements | Priority |
|---|--------|------------------|----------|
| 1 | **AI Customer Support Agent** | RAG-grounded answers, tool use, confidence scoring, auto-handoff on low confidence | P0 |
| 2 | **AI Sales Agent** | Lead qualification (BANT), product Q&A, demo booking, follow-ups | P0 |
| 3 | **WhatsApp Integration** | Twilio WhatsApp Business; inbound/outbound; media; templates | P0 |
| 4 | **Email Agent** | Gmail MCP inbound parse + AI reply draft/auto-send; threading | P1 |
| 5 | **Voice Support** | Twilio Voice + realtime transcription; IVR → AI; call summaries | P1 |
| 6 | **Multi-language Support** | Auto-detect + respond in customer language (Claude native) | P1 |
| 7 | **RAG Knowledge Base** | Upload (PDF/DOCX/MD), site crawl, chunk, embed → Pinecone/pgvector | P0 |
| 8 | **Ticket Management** | CRUD, status lifecycle, priority, assignment, SLA timers, tags | P0 |
| 9 | **Human Handoff** | Seamless AI→human with context, presence, takeover/return | P0 |
| 10 | **Sentiment Analysis** | Per-message + per-conversation sentiment; trend alerts | P1 |
| 11 | **AI Ticket Summaries** | TL;DR, resolution, next steps on close/handoff | P1 |
| 12 | **Analytics Dashboard** | Deflection rate, CSAT, FRT/ART, volume by channel, AI vs human | P0 |
| 13 | **RBAC** | Owner/Admin/Agent/Viewer; per-resource permissions | P0 |
| 14 | **Audit Logs** | Immutable log of security/data actions; export | P1 |
| 15 | **Feedback System** | Thumbs up/down per AI reply, CSAT survey post-resolution | P1 |
| 16 | **Slack Notifications** | New ticket, handoff request, low CSAT, SLA breach | P1 |

## 5. Key User Flows

1. **Website chat deflection** → Visitor asks → AI retrieves from KB → answers w/ sources → marks resolved or escalates.
2. **WhatsApp support** → Inbound message → AI replies → if low confidence or "talk to human" → handoff + Slack ping.
3. **Sales qualify** → Visitor on pricing page → AI Sales Agent engages → qualifies (BANT) → books demo → notifies sales in Slack.
4. **Email triage** → Inbound email → AI classifies + drafts reply → agent approves/auto-send → ticket created.
5. **Voice** → Inbound call → IVR → AI answers via transcription → summary + ticket logged.
6. **Handoff** → AI hands off → agent sees AI summary + transcript → resolves → CSAT survey → analytics update.

## 6. Functional Requirements (selected)

- **FR-1** System shall isolate all tenant data by `org_id` with Postgres RLS.
- **FR-2** AI agent shall cite KB sources for every factual answer.
- **FR-3** AI shall auto-handoff when confidence < threshold (configurable) or on explicit user request.
- **FR-4** Every inbound channel message shall create/append to a `conversation` and may spawn a `ticket`.
- **FR-5** All privileged actions (role change, KB delete, channel config) shall write an `audit_log` row.
- **FR-6** Analytics shall be queryable by date range, channel, agent, and tenant.

## 7. Non-Functional Requirements

| Category | Target |
|----------|--------|
| **Latency** | First AI token < 1.5s p95 (streaming) |
| **Availability** | 99.9% for API; graceful degradation if a channel is down |
| **Scale** | 10k tenants, 1M conversations/mo (design target) |
| **Security** | RLS, encrypted secrets (Vault/pgcrypto), JWT auth, audit logging |
| **Compliance posture** | GDPR-ready (data export/delete), PII redaction in logs |
| **Cost control** | Token budgeting per tenant; cheap pgvector tier + Pinecone tier |

## 8. Success Metrics (North Star + supporting)

- **North star:** % tickets resolved by AI without human (deflection rate).
- CSAT ≥ 4.3/5 on AI-handled conversations.
- First response time < 5s (AI), handoff time < 2 min.
- Sales: qualified-lead conversion + demos booked by AI.

## 9. Assumptions & Risks

- **Risk:** Twilio balance low → throttle Voice/WhatsApp in dev. *Mitigation:* dev sandbox + mock provider.
- **Risk:** RAG hallucination → *Mitigation:* source-grounded answers + confidence gating + handoff.
- **Risk:** Multi-tenant data leak → *Mitigation:* RLS + tenant-scoped vector namespaces.
- **Assumption:** Claude is the primary LLM; embeddings via a hosted model (see MCP plan).

## 10. Out of Scope for Phase 1 (this doc)

No application code. Phase 1 = PRD + architecture + DB design + folder structure + UI/UX plan + MCP usage plan + roadmap. **Code begins in Phase 2 after approval.**
