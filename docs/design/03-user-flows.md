# OmniAssist AI — Complete User Flows & Journeys

> v1.0 · Flows for Customer, Support Agent, Sales Agent, Admin. Mermaid diagrams.

## A. CUSTOMER FLOWS

### A1. Website Chat
```mermaid
flowchart TD
    V[Visitor lands on site] --> O[Widget bubble pulses bottom-right]
    O --> C[Opens chat: greeting + quick replies]
    C --> Q[Types question]
    Q --> AI[AI: typing indicator → streamed answer + sources]
    AI --> R{Resolved?}
    R -->|Yes| TU[Thumbs up + CSAT chip] --> END[Conversation closed]
    R -->|No / 'talk to human'| H[Handoff: 'Connecting you…' + agent presence]
    H --> AG[Human agent joins, full context] --> END
```
**UX notes:** instant first token, source pills under answers, persistent transcript, "still typing" never blocks input, offline → capture email.

### A2. WhatsApp Support
```mermaid
flowchart TD
    M[Customer messages WhatsApp number] --> WH[Twilio webhook → conversation]
    WH --> AIa[AI replies in WhatsApp w/ same brain]
    AIa --> MEDIA{Needs media/doc?}
    MEDIA -->|Yes| SEND[AI sends image/PDF/template]
    MEDIA -->|No| CONT[Continue]
    CONT --> ESC{Low confidence / human?}
    ESC -->|Yes| NOTIFY[Agent notified in dashboard + Slack] --> TAKE[Agent takes over in same thread]
    ESC -->|No| CLOSE[Resolved → CSAT via WhatsApp quick reply]
```

### A3. Voice Support
```mermaid
flowchart TD
    CALL[Customer calls number] --> IVR[Brief IVR / direct AI]
    IVR --> RT[Twilio realtime transcription]
    RT --> AIv[AI reasons on transcript → TTS reply]
    AIv --> NEED{Complex / escalate?}
    NEED -->|Yes| WARM[Warm transfer to human + on-screen summary]
    NEED -->|No| ENDc[Call ends]
    ENDc --> SUM[AI call summary + ticket auto-created]
    WARM --> SUM
```

### A4. Email Support
```mermaid
flowchart TD
    E[Customer emails support@] --> GP[Gmail push → parse thread]
    GP --> CLASS[AI classifies intent + sentiment]
    CLASS --> DRAFT[AI drafts reply grounded in KB]
    DRAFT --> MODE{Auto-send or review?}
    MODE -->|Auto| SENT[Reply sent, thread updated]
    MODE -->|Review| AGr[Agent approves/edits → send]
    SENT --> TK[Ticket created/updated]
    AGr --> TK
```

### A5. Ticket Tracking (customer self-serve)
```mermaid
flowchart TD
    L[Customer opens tracking link] --> STAT[Sees ticket status timeline]
    STAT --> UPD[Real-time updates: open → in progress → resolved]
    UPD --> REPLY[Can reply / add info]
    REPLY --> CSAT[On resolve: CSAT + reopen option]
```

## B. SUPPORT AGENT FLOWS

### B1. Dashboard → Ticket Handling
```mermaid
flowchart TD
    LOGIN[Agent logs in] --> DASH[Dashboard: my queue, SLA timers, live feed]
    DASH --> PICK[Opens conversation in Inbox]
    PICK --> CTX[Context panel: contact, AI summary, sentiment, KB sources]
    CTX --> ACT{Action}
    ACT -->|Reply| SEND[Send message / use AI suggestion]
    ACT -->|Need info| SEARCH[KB / copilot search]
    ACT -->|Resolve| RES[Resolve + tag + summary auto-generated]
    SEND --> RES
```

### B2. Human Handoff (receiving)
```mermaid
flowchart TD
    PING[Handoff request: toast + Slack + queue badge] --> ACCEPT[Agent clicks 'Take over']
    ACCEPT --> CONTEXT[AI hands full context: transcript + summary + intent + sentiment]
    CONTEXT --> LIVE[Agent live with customer; AI stays as copilot]
    LIVE --> RETURN{Return to AI?}
    RETURN -->|Yes| BACK[Hand back to AI w/ note]
    RETURN -->|No| RESOLVE[Resolve]
```

### B3. Analytics (agent view)
Personal stats: resolved, avg handle time, CSAT, SLA adherence → trend cards + leaderboard (opt-in).

## C. SALES AGENT FLOWS

### C1. Lead Management
```mermaid
flowchart TD
    SRC[Lead from chat/site/WhatsApp] --> CAP[AI captures + enriches contact]
    CAP --> QUAL[AI qualifies BANT in conversation]
    QUAL --> SCORE[Lead score + stage assigned]
    SCORE --> ROUTE{Hot?}
    ROUTE -->|Yes| ALERT[Slack alert to sales + appears in pipeline 'Hot']
    ROUTE -->|No| NUR[AI nurture sequence scheduled]
```

### C2. Pipeline Tracking
```mermaid
flowchart TD
    PIPE[Kanban pipeline: New → Qualified → Demo → Proposal → Won/Lost] --> DRAG[Drag lead between stages]
    DRAG --> DETAIL[Lead drawer: timeline, AI notes, next best action]
    DETAIL --> ACTs{Action}
    ACTs -->|Book demo| CAL[AI books demo / calendar]
    ACTs -->|Follow up| SEQ[Schedule follow-up]
```

### C3. Follow-ups
AI suggests + schedules follow-ups (email/WhatsApp), shows due tasks in a "Today" list, logs every touch on the lead timeline.

## D. ADMIN FLOWS

### D1. User & Role Management
```mermaid
flowchart TD
    TEAM[Team page] --> INV[Invite by email]
    INV --> ROLE[Assign role: Owner/Admin/Agent/Viewer]
    ROLE --> PERM[Permission matrix preview]
    PERM --> AUDIT[Change written to audit log]
```

### D2. Audit Logs
Filter by actor/action/resource/date → immutable timeline → diff viewer → export CSV.

### D3. Knowledge Base
```mermaid
flowchart TD
    KB[KB page] --> ADD{Add source}
    ADD -->|Upload| UP[PDF/DOCX/MD → chunk → embed]
    ADD -->|Crawl| CR[Enter URL → Playwright crawl → embed]
    ADD -->|FAQ| FQ[Manual Q&A entry]
    UP --> IDX[Indexing status: processing → ready]
    CR --> IDX
    FQ --> IDX
    IDX --> TEST[Retrieval playground: test a query → see chunks + scores]
```

## E. Cross-Persona Journey Map (emotional arc)
| Stage | Customer feeling | Design response |
|-------|------------------|-----------------|
| Awareness | curious/skeptical | confident landing, social proof |
| First contact | impatient | instant AI first token |
| Getting help | needs trust | cited sources, confidence shown |
| Friction | frustrated | one-tap human handoff, no dead ends |
| Resolution | relieved | clear close, CSAT, follow-up |
| Return | expectant | remembered context, faster path |
