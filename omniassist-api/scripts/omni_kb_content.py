"""OmniAssist AI — the company's OWN knowledge base content (replaces the TCS demo).

Single source of truth: rebuild_omni.py turns this into structured company data,
markdown docs, PDFs, kb_documents/kb_chunks and Pinecone embeddings so the Product
Expert + inbox agents answer about OmniAssist itself.
"""
from __future__ import annotations

COMPANY = {
    "name": "OmniAssist AI",
    "overview": (
        "OmniAssist AI is an enterprise AI customer-support and sales platform. It "
        "deploys AI agents across website chat, WhatsApp, Email and Voice that answer "
        "questions from your knowledge base, qualify leads, create tickets, and hand "
        "off to humans when needed — with analytics across every channel."
    ),
    "mission": (
        "To let every business deliver instant, accurate, human-quality support and "
        "sales conversations on every channel, powered by AI grounded in their own "
        "knowledge."
    ),
    "vision": (
        "A world where customers get correct answers in seconds, on any channel, any "
        "language — and teams focus only on the conversations that truly need a human."
    ),
    "value_props": [
        "One AI brain across Website, WhatsApp, Email and Voice",
        "Answers grounded in your knowledge base (RAG) — no hallucinations",
        "Built-in ticketing, lead capture and analytics",
        "Human handoff with full context when confidence is low",
        "Setup in minutes, no code",
    ],
    "industry": "AI Customer Support & Sales SaaS",
    "website": "https://omniassist.ai",
    "contact": {
        "support_email": "support@omniassist.ai",
        "sales_email": "sales@omniassist.ai",
        "docs": "https://docs.omniassist.ai",
        "status": "https://status.omniassist.ai",
        "hours": "24x7 in-app chat; email Mon-Fri",
    },
}

# Products / services (name, type, summary)
PRODUCTS = [
    ("AI Support Agent", "product", "Answers customer questions from your KB, creates tickets and escalates to humans when needed."),
    ("AI Sales Agent", "product", "Qualifies leads with BANT, answers product/pricing questions, books demos and hands hot leads to sales."),
    ("WhatsApp Agent", "product", "Brings the AI agent to WhatsApp via Twilio — inbound/outbound, media and templates."),
    ("Email Agent", "product", "Reads inbound email, drafts and sends grounded replies, and threads conversations."),
    ("Voice Agent", "product", "Handles phone calls with speech-to-text, AI reasoning, live transcription and call summaries (Twilio Voice)."),
    ("Ticketing System", "product", "Auto-creates and routes tickets with SLA timers, priorities, assignment and AI summaries."),
    ("Analytics Dashboard", "product", "Tracks deflection, CSAT, first-response time, channel volume, revenue influence and agent productivity."),
    ("Knowledge Base (RAG)", "service", "Upload docs; OmniAssist chunks, embeds (Pinecone) and grounds every answer with citations."),
]

# Pricing plans (name, price/mo USD or None=custom, billing, features[])
PRICING = [
    ("Starter", 49, "monthly", [
        "1 AI agent (Support)", "Website chat widget", "Up to 1,000 AI conversations/mo",
        "Knowledge base (up to 100 docs)", "Email support", "Basic analytics",
    ]),
    ("Growth", 199, "monthly", [
        "All AI agents (Support + Sales)", "Website + WhatsApp + Email channels",
        "Up to 10,000 AI conversations/mo", "Ticketing + workflow automation",
        "Full analytics + CSAT", "Priority support", "Up to 10 seats",
    ]),
    ("Enterprise", None, "custom", [
        "All channels incl. Voice", "Unlimited conversations + seats", "SSO/SAML, audit logs",
        "Data residency + custom retention", "Dedicated CSM + SLA", "Custom integrations",
    ]),
]

COMPETITORS = [
    ("Intercom", "Established support + Fin AI agent; strong but premium-priced.",
     ["Mature product", "Large app ecosystem"], ["Expensive at scale", "Resolution priced per-resolution"]),
    ("Zendesk", "Incumbent ticketing suite with add-on AI.",
     ["Deep ticketing", "Enterprise trust"], ["AI is an add-on", "Heavier to set up"]),
    ("Freshdesk / Freshchat", "Mid-market support suite with bots.",
     ["Good value", "Broad suite"], ["Bots less grounded", "Channel depth varies"]),
]

# ---------------- 15 Knowledge-base documents ----------------
DOCS: dict[str, tuple[str, str, str]] = {
    "company-overview": ("OmniAssist AI — Company Overview", "company", f"""# OmniAssist AI — Company Overview

## What is OmniAssist AI
{COMPANY['overview']}

## Vision
{COMPANY['vision']}

## Mission
{COMPANY['mission']}

## Benefits
- {chr(10).join('- ' + v for v in COMPANY['value_props']).replace(chr(10) + '- ', chr(10) + '- ')}
- Lower support costs through AI deflection (typically 60-70%).
- Faster first response and higher CSAT.
- More qualified leads and booked demos from the same traffic.
- One platform instead of separate chat, helpdesk and bot tools.
"""),

    "products-and-services": ("OmniAssist AI — Products & Services", "products", """# Products & Services

OmniAssist AI is one platform with multiple AI agents and tools:

- **AI Support Agent** — answers customer questions grounded in your knowledge base, creates tickets, escalates to humans when needed.
- **AI Sales Agent** — qualifies leads (BANT), answers product & pricing questions, books demos, hands hot leads to sales.
- **WhatsApp Agent** — the AI agent on WhatsApp (via Twilio): inbound/outbound, media, templates.
- **Email Agent** — reads inbound email and sends grounded, threaded replies.
- **Voice Agent** — phone support with speech-to-text, AI reasoning, live transcription and auto call summaries (Twilio Voice).
- **Ticketing System** — auto-creates, prioritizes, routes and summarizes tickets with SLA timers.
- **Analytics Dashboard** — deflection rate, CSAT, first-response time, channel volume, revenue influence, agent productivity.
- **Knowledge Base (RAG)** — upload docs; OmniAssist chunks, embeds (Pinecone) and cites sources in every answer.
"""),

    "pricing-plans": ("OmniAssist AI — Pricing Plans", "pricing", """# Pricing Plans

## Starter — $49/month
For small teams getting started. 1 AI Support Agent, website chat, up to 1,000 AI conversations/month, knowledge base (up to 100 docs), email support, basic analytics.

## Growth — $199/month
For growing teams. All AI agents (Support + Sales), Website + WhatsApp + Email channels, up to 10,000 AI conversations/month, ticketing + workflow automation, full analytics + CSAT, priority support, up to 10 seats.

## Enterprise — Custom
For large orgs. All channels including Voice, unlimited conversations + seats, SSO/SAML, audit logs, data residency, dedicated CSM + SLA, custom integrations.

## Feature comparison
| Feature | Starter | Growth | Enterprise |
|---|---|---|---|
| AI Support Agent | ✓ | ✓ | ✓ |
| AI Sales Agent | — | ✓ | ✓ |
| Channels | Web | Web + WhatsApp + Email | All + Voice |
| Conversations/mo | 1,000 | 10,000 | Unlimited |
| Ticketing + Workflows | — | ✓ | ✓ |
| SSO/SAML + Audit | — | — | ✓ |
| Support | Email | Priority | Dedicated CSM |

A 14-day free trial is available on all plans; no credit card required. Annual billing saves ~20%.
"""),

    "whatsapp-agent-guide": ("WhatsApp Agent — Guide", "whatsapp", """# WhatsApp Agent Guide

## Setup
1. Go to Settings → Channels → WhatsApp.
2. Connect your Twilio account (Account SID + Auth Token) and WhatsApp-enabled number.
3. Set the webhook URL shown to your Twilio WhatsApp sender.
4. Choose which AI agent answers and enable the channel.

## Features
- Two-way WhatsApp messaging answered by the AI agent, grounded in your KB.
- Media (images, documents) and approved message templates.
- Automatic ticket creation and human handoff with full context.
- Multi-language replies.

## FAQs
- **Do I need a Twilio account?** Yes, WhatsApp runs via Twilio. Growth and Enterprise plans include it.
- **Can it send proactive messages?** Yes, using approved WhatsApp templates.

## Troubleshooting
- *Messages not arriving:* re-check the Twilio webhook URL and that the number is WhatsApp-enabled.
- *Template rejected:* templates must be approved by WhatsApp; check formatting and category.
"""),

    "email-agent-guide": ("Email Agent — Guide", "email", """# Email Agent Guide

## Setup
1. Settings → Channels → Email.
2. Connect your support inbox (Gmail OAuth or SMTP/IMAP).
3. Set the from-address and signature; enable the agent.

## Features
- Reads inbound email, drafts grounded replies and sends (or suggests for approval).
- Threads conversations and creates tickets for trackable issues.
- Auto-detects language and sentiment.

## FAQs
- **Does it reply automatically?** You can run in auto-send or human-approval mode.
- **Which providers?** Gmail (OAuth) and standard SMTP/IMAP.

## Troubleshooting
- *Replies not sending:* verify SMTP credentials / Gmail OAuth scope.
- *Wrong threading:* ensure the In-Reply-To headers are preserved.
"""),

    "voice-agent-guide": ("Voice Agent — Guide", "voice", """# Voice Agent Guide

## Setup
1. Settings → Channels → Voice.
2. Connect Twilio Voice and buy/assign a phone number.
3. Point the number's voice webhook to OmniAssist; enable the agent.

## Features
- Inbound call handling with speech-to-text and AI reasoning.
- Live transcription and automatic post-call summaries.
- Warm transfer to a human agent; auto-created tickets.

## FAQs
- **What telephony?** Twilio Voice.
- **Languages?** Multiple, auto-detected.

## Troubleshooting
- *No audio / call drops:* check the Twilio number's voice webhook and region.
- *Poor transcription:* verify call quality and language setting.
"""),

    "support-agent-guide": ("AI Support Agent — Guide", "support", """# AI Support Agent Guide

## Features
- Answers grounded in your KB with cited sources.
- Confidence scoring; auto-handoff when unsure.
- Auto ticket creation and sentiment detection.

## Workflows
1. Customer asks a question on any channel.
2. The agent retrieves relevant KB passages and answers.
3. For trackable issues (billing, bug, account) it creates a ticket.
4. If it can't answer confidently, it hands off to a human with full context.

## Escalation rules
The agent hands off to a human when:
- The user explicitly asks for a human/agent.
- AI confidence is below 70%.
- A refund approval is required.
- A legal/compliance issue is raised.
"""),

    "sales-agent-guide": ("AI Sales Agent — Guide", "sales", """# AI Sales Agent Guide

## Lead qualification
The agent qualifies visitors using BANT (Budget, Authority, Need, Timeline) and scores the lead.

## Demo booking
When buying intent is high, it offers and books a demo, syncing to the CRM/calendar.

## Objection handling
It answers pricing and competitor questions from the KB, addresses common objections (price, security, migration) with grounded responses.

## Conversion flows
1. Greet → discover need → qualify (BANT).
2. Answer product/pricing questions from the KB.
3. Book a demo for hot leads or schedule a follow-up for nurturing.
4. Create/update the lead in CRM and notify sales.
"""),

    "ticketing-system-guide": ("Ticketing System — Guide", "ticketing", """# Ticketing System Guide

## Ticket creation
Tickets are created automatically for trackable intents (billing, refund, bug, account) or manually by an agent. Each gets a number, priority and channel.

## Ticket status
open → in_progress → pending → resolved → closed. Priorities: low, medium, high, urgent. SLA timers track response and resolution targets.

## Escalation process
Breached SLAs or high-priority tickets escalate to managers per the escalation matrix; handoffs notify the assigned team in-app and via Slack.
"""),

    "analytics-dashboard-guide": ("Analytics Dashboard — Guide", "analytics", """# Analytics Dashboard Guide

## Metrics
- AI deflection rate, CSAT, first-response time (FRT), conversation volume by channel.
- Tickets created/resolved, leads created, revenue influenced.

## Reports
Daily rollups per channel; export to CSV. Executive insights summarize trends and recommendations.

## KPIs
- **Deflection rate** — % of conversations resolved by AI without a human.
- **CSAT** — customer satisfaction score.
- **FRT** — average first-response time.
- **Resolution rate** and **handoff rate**.
"""),

    "integrations-guide": ("Integrations — Guide", "integrations", """# Integrations Guide

## Twilio
Powers WhatsApp and Voice channels. Connect your Account SID, Auth Token and numbers in Settings → Channels.

## Supabase
OmniAssist stores data in Supabase (PostgreSQL + Auth + Storage). Multi-tenant with row-level isolation per organization.

## Pinecone
The RAG knowledge base uses Pinecone for vector search (multilingual embeddings) so answers are grounded with citations.

## Email providers
Gmail (OAuth) and standard SMTP/IMAP for the Email Agent. Slack is supported for handoff notifications.
"""),

    "account-management": ("Account Management", "account", """# Account Management

## Signup
Create a workspace at omniassist.ai with your name, work email and a password. A 14-day free trial starts immediately.

## Login
Sign in with email + password, or Google OAuth. Sessions support multiple devices.

## Password reset
Use 'Forgot password' on the login page; a secure reset link is emailed to you.

## Subscription management
Manage your plan, seats and billing in Settings → Billing. Upgrade, downgrade or cancel anytime; changes take effect at the next cycle.
"""),

    "billing-and-refund-policy": ("Billing & Refund Policy", "billing", """# Billing & Refund Policy

## Billing
Plans are billed monthly or annually (annual saves ~20%). Usage above your plan's conversation limit is billed as overage or prompts an upgrade.

## Refunds
We offer a 14-day money-back guarantee on the first paid month. Refund approvals for other cases are reviewed by our team — a human always approves refunds.

## Cancellation policy
Cancel anytime from Settings → Billing. Your plan stays active until the end of the current billing period; no further charges after that.
"""),

    "security-and-compliance": ("Security & Compliance", "security", """# Security & Compliance

## Data security
Enterprise-grade controls: encryption in transit (TLS) and at rest, role-based access, and continuous monitoring. Multi-tenant data isolation per organization.

## Encryption
All data is encrypted at rest and in transit. Secrets are stored in a vault; API keys are never exposed to the browser.

## Privacy
We process personal data lawfully and only to provide the service. Customers control retention. SSO/SAML, audit logs and data residency are available on Enterprise. We align to SOC 2 / ISO 27001 practices and support GDPR requirements.
"""),

    "faq-master": ("OmniAssist AI — FAQ Master", "faqs", """# FAQ Master

A categorized set of common questions and answers about OmniAssist AI covering the
product, channels, pricing, setup, billing, security and account management. (The
full 500+ question dataset is generated from these and embedded into the knowledge
base for retrieval.)
"""),
}

# ---------------- FAQ seed (category, question, answer) ----------------
# Paraphrased into 500+ during rebuild for better retrieval recall.
FAQ_SEED: list[tuple[str, str, str]] = [
    ("company", "What is OmniAssist AI?", COMPANY["overview"]),
    ("company", "What does OmniAssist do?", "OmniAssist deploys AI agents across website chat, WhatsApp, email and voice that answer questions from your knowledge base, qualify leads, create tickets and hand off to humans when needed."),
    ("company", "What is your mission?", COMPANY["mission"]),
    ("company", "Who is OmniAssist for?", "Support and sales teams of any size that want instant, accurate, AI-powered conversations across every channel."),
    ("products", "What channels do you support?", "Website chat, WhatsApp, Email and Voice — all answered by the same AI brain grounded in your knowledge base."),
    ("products", "What is the AI Support Agent?", "It answers customer questions from your knowledge base with cited sources, creates tickets and escalates to a human when confidence is low."),
    ("products", "What is the AI Sales Agent?", "It qualifies leads using BANT, answers product and pricing questions, books demos and hands hot leads to your sales team."),
    ("products", "Do you have a WhatsApp agent?", "Yes. The WhatsApp Agent (via Twilio) answers customers on WhatsApp with media and templates, creates tickets and hands off to humans."),
    ("products", "Do you have an email agent?", "Yes. The Email Agent reads inbound email and sends grounded, threaded replies in auto or human-approval mode."),
    ("products", "Do you support voice calls?", "Yes. The Voice Agent (Twilio Voice) handles calls with speech-to-text, AI reasoning, live transcription and automatic call summaries."),
    ("products", "Do you have ticketing?", "Yes. Tickets are auto-created and routed with SLA timers, priorities, assignment and AI summaries."),
    ("products", "Do you have analytics?", "Yes. The Analytics Dashboard tracks deflection, CSAT, first-response time, channel volume, revenue influence and productivity."),
    ("products", "How does the knowledge base work?", "Upload your docs; OmniAssist chunks them, generates embeddings (Pinecone) and grounds every answer with citations so there are no hallucinations."),
    ("pricing", "How much does OmniAssist cost?", "Starter is $49/month, Growth is $199/month, and Enterprise is custom-priced. A 14-day free trial is available on all plans."),
    ("pricing", "What is in the Starter plan?", "Starter ($49/mo): 1 AI Support Agent, website chat, up to 1,000 AI conversations/month, knowledge base (100 docs), email support, basic analytics."),
    ("pricing", "What is in the Growth plan?", "Growth ($199/mo): all AI agents, Website + WhatsApp + Email, up to 10,000 conversations/month, ticketing + workflows, full analytics, priority support, up to 10 seats."),
    ("pricing", "What is in the Enterprise plan?", "Enterprise (custom): all channels incl. Voice, unlimited conversations + seats, SSO/SAML, audit logs, data residency, dedicated CSM + SLA, custom integrations."),
    ("pricing", "Is there a free trial?", "Yes — a 14-day free trial on all plans, no credit card required."),
    ("pricing", "Do you offer annual billing?", "Yes, annual billing is available and saves about 20% versus monthly."),
    ("whatsapp", "How do I set up WhatsApp?", "Settings → Channels → WhatsApp, connect your Twilio account and WhatsApp number, set the webhook, choose the agent and enable the channel."),
    ("whatsapp", "Do I need Twilio for WhatsApp?", "Yes, WhatsApp runs via Twilio. It's included on Growth and Enterprise plans."),
    ("email", "How do I set up the email agent?", "Settings → Channels → Email, connect your inbox (Gmail OAuth or SMTP/IMAP), set the from-address and enable the agent."),
    ("email", "Does the email agent reply automatically?", "You can run it in auto-send mode or human-approval mode where it drafts replies for review."),
    ("voice", "How do I set up the voice agent?", "Settings → Channels → Voice, connect Twilio Voice, assign a phone number, point its webhook to OmniAssist and enable the agent."),
    ("support", "When do you escalate to a human?", "When the user asks for a human, AI confidence is below 70%, a refund approval is needed, or a legal/compliance issue is raised."),
    ("support", "How are tickets created?", "Automatically for trackable issues (billing, refund, bug, account) or manually by an agent, each with a number, priority, SLA and channel."),
    ("sales", "How does lead qualification work?", "The AI Sales Agent qualifies visitors using BANT (Budget, Authority, Need, Timeline) and scores the lead."),
    ("sales", "Can the AI book a demo?", "Yes — when buying intent is high it offers and books a demo and notifies your sales team."),
    ("analytics", "What metrics do you track?", "Deflection rate, CSAT, first-response time, conversation volume by channel, tickets, leads and revenue influence."),
    ("analytics", "What is the deflection rate?", "The percentage of conversations resolved by the AI without a human — a core measure of AI impact."),
    ("integrations", "What integrations do you support?", "Twilio (WhatsApp/Voice), Supabase (database/auth/storage), Pinecone (RAG vector search), Gmail/SMTP for email, and Slack for handoff alerts."),
    ("integrations", "Do you use Pinecone?", "Yes. The knowledge base uses Pinecone for vector search so answers are grounded with citations."),
    ("account", "How do I sign up?", "Create a workspace at omniassist.ai with your name, work email and a password; a 14-day free trial starts immediately."),
    ("account", "How do I reset my password?", "Use 'Forgot password' on the login page; a secure reset link is emailed to you."),
    ("account", "How do I manage my subscription?", "In Settings → Billing you can upgrade, downgrade or cancel; changes take effect at the next billing cycle."),
    ("billing", "What is your refund policy?", "We offer a 14-day money-back guarantee on the first paid month. Other refunds are reviewed and approved by a human."),
    ("billing", "How do I cancel?", "Cancel anytime in Settings → Billing. Your plan stays active until the end of the current period with no further charges."),
    ("security", "Is my data secure?", "Yes. Data is encrypted in transit and at rest, with role-based access, continuous monitoring and per-organization isolation."),
    ("security", "Are you GDPR compliant?", "We support GDPR requirements, customer-controlled retention, and align to SOC 2 / ISO 27001 practices; SSO/SAML and data residency are available on Enterprise."),
    ("security", "Do you support SSO?", "Yes — SSO/SAML and audit logs are available on the Enterprise plan."),
    ("competitors", "How do you compare to Intercom or Zendesk?", "OmniAssist gives you one AI brain across Website, WhatsApp, Email and Voice, grounded in your KB, with ticketing and analytics built in — typically faster to set up and better value than bolting AI onto Intercom or Zendesk."),
    ("company", "What makes OmniAssist different?", "One grounded AI across every channel, no-code setup in minutes, built-in ticketing, lead capture and analytics, and human handoff with full context."),
    ("support", "Can it answer in multiple languages?", "Yes, the agents auto-detect and reply in the customer's language."),
    ("products", "Does it avoid hallucinations?", "Yes — every answer is grounded in your knowledge base via RAG and cites its sources; if it isn't sure, it hands off to a human."),
]
