"""TCS demo knowledge-base content (authored from public TCS data + research).

Single source of truth for the OmniAssist demo KB: build_kb.py writes these as
markdown docs, renders PDFs, stores them in Supabase (kb_documents/kb_chunks) and
upserts the chunks into Pinecone for RAG retrieval.
"""
from __future__ import annotations

# Each entry: key -> (title, category, markdown_body)
DOCS: dict[str, tuple[str, str, str]] = {
    "company_overview": (
        "TCS — Company Overview", "company",
        """# Tata Consultancy Services — Company Overview

Tata Consultancy Services (TCS) is one of the world's largest IT services,
consulting and business solutions organizations and a part of the Tata Group.

- **Founded:** 1968, as a division of Tata Sons.
- **Headquarters:** Mumbai, Maharashtra, India.
- **Parent:** Tata Group (Tata Sons holds ~71.7%).
- **Leadership:** K. Krithivasan (CEO & Managing Director, since 2023);
  Natarajan Chandrasekaran (Chairman).
- **Employees:** Over 584,000 across 46 countries (as of March 2026).
- **Global presence:** 150+ locations in 46 countries, 500+ offices and 194
  service delivery centers worldwide.
- **Revenue:** ~US$28 billion (FY2025-26). First Indian IT company to cross a
  US$200 billion market capitalization (2021).
- **Tagline / belief:** "Building on Belief."

**Mission:** To help customers achieve their business objectives by providing
innovative, best-in-class consulting, IT solutions and services, building greater
futures through innovation and collective knowledge.

TCS partners with many of the world's largest enterprises on their digital
transformation journeys, combining deep domain expertise, a global delivery model
and proprietary products and platforms.
""",
    ),
    "services": (
        "TCS — Services & Offerings", "services",
        """# TCS Services & Offerings

TCS delivers a full spectrum of technology and business services:

- **Consulting & Advisory** — business and technology strategy, operating-model
  design, and transformation advisory.
- **Cloud** — cloud strategy, migration, modernization and managed services across
  AWS, Microsoft Azure and Google Cloud.
- **Artificial Intelligence & Generative AI** — AI/GenAI advisory, model
  engineering, and deployment to embed intelligence across business processes.
- **Data & Analytics** — data platforms, analytics, and decisioning.
- **Cybersecurity** — cyber strategy, managed detection & response (MDR), identity
  and access management, and data protection.
- **Enterprise Solutions** — ERP and packaged application services (SAP, Oracle,
  Microsoft, Salesforce, etc.).
- **IoT & Digital Engineering** — connected products, engineering and R&D services.
- **Business Process Services (BPS)** — managed business operations and outsourcing.
- **Application Development & Maintenance** — building, modernizing and running
  enterprise applications.

Engagements use TCS's global network delivery model with onsite, nearshore and
offshore delivery centers.
""",
    ),
    "products": (
        "TCS — Products & Platforms", "products",
        """# TCS Products & Platforms

TCS builds proprietary software products and platforms:

## TCS BaNCS
A flagship financial-services platform spanning banking, capital markets and
insurance. Used by 500+ financial institutions across 100+ markets, covering the
value chain from core banking to asset servicing, brokerage and custody.

## ignio (by Digitate, a TCS venture)
An award-winning AI-powered cognitive automation / AIOps product (launched 2015)
that autonomously resolves and prevents enterprise IT operations issues. The suite
includes ignio AIOps, ignio AI.WorkloadManagement, ignio AI.ERPOps, Cognitive
Procurement and ignio AI.Digital Workspace.

## TCS iON
A "phygital" platform for digital learning, vocational skilling, and large-scale
assessments, examinations and recruitment. Serves institutions, governments and
enterprises with multimodal learning, live online lectures, gamified learning and
simulation-based training.

## Other platforms
TCS also offers platforms such as TCS MasterCraft (intelligent automation for the
software lifecycle and data management) and Quartz (blockchain and digital
solutions).
""",
    ),
    "industries": (
        "TCS — Industries Served", "industries",
        """# Industries Served by TCS

TCS serves clients across these industries, organized into vertical clusters:

**Banking, Financial Services & Insurance (BFSI)**
- Banking
- Capital Markets
- Insurance

**Communications, Media & Technology (CMT)**
- Communications, Media & Information Services
- High Tech

**Consumer Business**
- Retail
- Consumer Packaged Goods (CPG) & Distribution
- Travel, Transportation & Logistics

**Life Sciences & Healthcare**
- Healthcare
- Life Sciences (Pharma)

**Manufacturing**
- Manufacturing
- Automotive
- Industrial & Process

**Energy, Resources & Public Services**
- Energy, Resources & Utilities
- Public Services / Government
- Education

For each industry, TCS combines contextual domain knowledge with its services and
platforms to deliver outcome-focused transformation.
""",
    ),
    "faqs": (
        "TCS — Frequently Asked Questions", "faqs",
        """# Frequently Asked Questions

**Q: What is TCS?**
A: Tata Consultancy Services is one of the world's largest IT services, consulting
and business solutions firms, part of the Tata Group, founded in 1968.

**Q: Where is TCS headquartered?**
A: Mumbai, India. TCS operates in 150+ locations across 46 countries.

**Q: Who is the CEO of TCS?**
A: K. Krithivasan is the CEO & Managing Director (since 2023). Natarajan
Chandrasekaran is the Chairman.

**Q: What services does TCS offer?**
A: IT services & consulting, cloud, AI & Generative AI, cybersecurity, data &
analytics, enterprise solutions, IoT/engineering, and business process services.

**Q: What products does TCS make?**
A: TCS BaNCS (financial services), ignio (AIOps automation), TCS iON (learning &
assessments), plus platforms like TCS MasterCraft and Quartz.

**Q: How do I engage TCS / what does it cost?**
A: TCS engagements are enterprise and custom-scoped; pricing depends on services,
scale and the contract model (fixed-price, time-and-materials or outcome-based).
Contact TCS sales for a tailored proposal.

**Q: How can I contact TCS support?**
A: Toll-free 1800 572 3858 (Mon-Fri, 10am-6pm), email contact.us@tcs.com, or the
global helpdesk global.helpdesk@tcs.com / +91 22 6656 8484.

**Q: Does TCS work with my industry?**
A: TCS serves BFSI, communications/media, retail & consumer, life sciences &
healthcare, manufacturing, energy & utilities, public services and education.

**Q: Is my data secure with TCS?**
A: TCS maintains enterprise-grade security aligned to ISO 27001, with encryption,
access management and continuous monitoring per contractual requirements.

**Q: Who are TCS's competitors?**
A: Infosys, Accenture, Cognizant, Wipro and HCLTech.
""",
    ),
    "pricing": (
        "TCS — Pricing & Engagement Models", "pricing",
        """# Pricing & Engagement Models

TCS is an enterprise services and products company; pricing is **custom-scoped**
rather than published per-seat tiers. Typical commercial models:

- **Fixed-Price** — agreed scope and deliverables for a fixed fee.
- **Time & Materials (T&M)** — billed by effort and rates for evolving scope.
- **Outcome / Managed Services** — priced against business outcomes or SLAs.
- **Product licensing** — for products such as TCS BaNCS (license + implementation
  + support) and TCS iON (subscription, per learner / per assessment).

Final pricing depends on the services, scale, geography and contract term. Contact
TCS sales for a tailored proposal and total cost of engagement.
""",
    ),
    "support_policies": (
        "TCS — Support Policies & SLAs", "support",
        """# Support Policies & Service Levels

- **Support hours:** Standard customer support operates Monday-Friday, 10:00am-
  6:00pm (local business hours); enterprise contracts may include 24x7 support.
- **Service Level Agreements (SLAs):** Availability, response and resolution times
  are defined per engagement contract and governed by agreed KPIs and escalation
  paths.
- **Priority levels:** Issues are triaged as P1 (critical/outage), P2 (high),
  P3 (medium) and P4 (low), each with target response and resolution windows.
- **Escalation:** Unresolved or breached issues follow a documented escalation
  matrix to delivery and account management.
- **Information security:** Controls align to ISO 27001; data is encrypted in
  transit and at rest, with role-based access and continuous monitoring.
- **Data protection & privacy:** Personal data is processed lawfully, for specified
  purposes, in line with applicable regulations (e.g., GDPR where relevant).
- **Business continuity:** Delivery is backed by BCP/DR plans across global centers.
""",
    ),
    "contact": (
        "TCS — Contact Information", "contact",
        """# Contact Information

- **Customer support (toll-free, India):** 1800 572 3858 (Mon-Fri, 10am-6pm)
- **General email:** contact.us@tcs.com
- **Global helpdesk:** global.helpdesk@tcs.com / +91 22 6656 8484
- **Board line:** +91 22 6778 9999
- **Fraudulent recruitment reporting:** 1800 209 3111
- **TCS iON customer care:** 1800 266 6282
- **Registered/HQ address:** TCS House, Raveline Street, Fort, Mumbai 400001 /
  corporate office at 247 Park, L.B.S. Marg, Vikhroli (West), Mumbai 400083, India.
- **Website:** https://www.tcs.com

For sales and partnership enquiries, use the "Contact Us" form on tcs.com or reach
out to your TCS account manager.
""",
    ),
    "support_scenarios": (
        "TCS — Customer Support Scenarios", "support",
        """# Customer Support Scenarios (Playbook)

**Scenario: Customer can't log in to a TCS portal.**
Verify identity, confirm the correct portal/URL, check for known outages, guide a
password reset, and if unresolved raise a P2 ticket to the portal support team.

**Scenario: Reporting a production outage (P1).**
Acknowledge immediately, classify as P1, open an incident, notify the on-call
delivery team and account manager, and provide status updates per SLA until
resolution and root-cause analysis.

**Scenario: Billing or invoice query.**
Confirm the contract and engagement, pull the relevant invoice, explain the
commercial model (fixed-price/T&M/outcome), and route disputes to the account/
finance team.

**Scenario: Requesting a new service or scope change.**
Capture requirements, route to the account manager/solution team for a proposal,
and explain that pricing is custom-scoped.

**Scenario: Data privacy / security concern.**
Reassure on ISO 27001 controls and encryption, escalate to the security/DPO team,
and follow the incident process if a breach is suspected.

**Scenario: Recruitment / job-offer verification (fraud check).**
TCS never charges candidates; direct the person to 1800 209 3111 and official
careers channels to verify any offer.

**Scenario: TCS iON exam/assessment help.**
Direct learners/candidates to TCS iON customer care 1800 266 6282, verify the
exam/event, and escalate technical issues to the iON support team.
""",
    ),
}
