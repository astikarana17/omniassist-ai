// Mock data for the Business Operations Platform dashboards.
// Mirrors the shape returned by the omniassist-api /api/v1 endpoints
// (customer-success, knowledge-gaps, insights, workflows, company/ask).

import type {
  BusinessImpact,
  CustomerHealth,
  ExecInsight,
  KnowledgeGapItem,
  WorkflowItem,
  WorkflowRunItem,
} from "@/types";

const daysAgo = (d: number) => new Date(Date.now() - d * 86400_000).toISOString();
const hoursAgo = (h: number) => new Date(Date.now() - h * 3600_000).toISOString();

export const customerHealth: CustomerHealth[] = [
  { id: "ca_1", name: "Northwind Trading", plan: "Enterprise", mrr: 4200, score: 91, category: "healthy", churnRisk: 0.09, usage: 95, engagement: 88, support: 92, satisfaction: 90, adoption: 89, owner: "Priya N.", lastActive: hoursAgo(2) },
  { id: "ca_2", name: "Acme Robotics", plan: "Pro", mrr: 1800, score: 74, category: "healthy", churnRisk: 0.26, usage: 70, engagement: 76, support: 80, satisfaction: 72, adoption: 71, owner: "Daniel K.", lastActive: hoursAgo(9) },
  { id: "ca_3", name: "Lumen Health", plan: "Pro", mrr: 1500, score: 58, category: "at_risk", churnRisk: 0.42, usage: 44, engagement: 55, support: 70, satisfaction: 62, adoption: 58, owner: "Priya N.", lastActive: daysAgo(4) },
  { id: "ca_4", name: "Tilde Studio", plan: "Starter", mrr: 290, score: 47, category: "at_risk", churnRisk: 0.53, usage: 30, engagement: 50, support: 60, satisfaction: 48, adoption: 45, owner: "Daniel K.", lastActive: daysAgo(8) },
  { id: "ca_5", name: "Greycliff Capital", plan: "Enterprise", mrr: 5200, score: 33, category: "critical", churnRisk: 0.71, usage: 18, engagement: 28, support: 45, satisfaction: 35, adoption: 30, owner: "Priya N.", lastActive: daysAgo(15) },
  { id: "ca_6", name: "Pixel & Co", plan: "Starter", mrr: 190, score: 28, category: "critical", churnRisk: 0.78, usage: 12, engagement: 22, support: 40, satisfaction: 30, adoption: 24, owner: "Sam R.", lastActive: daysAgo(21) },
  { id: "ca_7", name: "Vertex Logistics", plan: "Pro", mrr: 2100, score: 82, category: "healthy", churnRisk: 0.17, usage: 84, engagement: 80, support: 88, satisfaction: 83, adoption: 79, owner: "Sam R.", lastActive: hoursAgo(5) },
];

export const knowledgeGaps: KnowledgeGapItem[] = [
  { id: "kg_1", question: "Do you support SAML SSO with Okta?", occurrences: 23, avgConfidence: 0.31, status: "open", suggestion: "Add an SSO/Okta setup guide to the knowledge base.", lastSeen: hoursAgo(3) },
  { id: "kg_2", question: "What is your data residency in the EU?", occurrences: 17, avgConfidence: 0.28, status: "open", suggestion: "Publish a data-residency / GDPR policy page.", lastSeen: hoursAgo(11) },
  { id: "kg_3", question: "Can I export conversations to CSV?", occurrences: 12, avgConfidence: 0.44, status: "in_review", suggestion: "Document the export API + UI button.", lastSeen: daysAgo(1) },
  { id: "kg_4", question: "Is there a Zapier integration?", occurrences: 9, avgConfidence: 0.39, status: "open", suggestion: "Add Zapier to the integrations catalog.", lastSeen: daysAgo(2) },
  { id: "kg_5", question: "How do annual discounts work?", occurrences: 7, avgConfidence: 0.52, status: "in_review", lastSeen: daysAgo(2) },
  { id: "kg_6", question: "What is the uptime SLA on Pro?", occurrences: 5, avgConfidence: 0.58, status: "resolved", lastSeen: daysAgo(6) },
];

export const gapCounts = { open: 3, in_review: 2, resolved: 1, dismissed: 0 };

export const execInsights: ExecInsight[] = [
  { id: "ei_1", kind: "churn", title: "Churn risk concentrated in Starter tier", summary: "2 critical accounts ($380 MRR) inactive >14 days; 5 at-risk overall.", recommendation: "Trigger the re-engagement playbook and assign a CSM check-in this week.", severity: "critical", createdAt: hoursAgo(4) },
  { id: "ei_2", kind: "revenue", title: "Expansion opportunity: Vertex Logistics", summary: "Usage up 38% MoM and nearing the Pro plan seat limit.", recommendation: "Reach out with an Enterprise upgrade offer.", severity: "positive", createdAt: hoursAgo(20) },
  { id: "ei_3", kind: "support_perf", title: "AI deflection improved to 68%", summary: "Resolution rate up 6pts after the last KB update; FRT down 22%.", severity: "positive", createdAt: daysAgo(1) },
  { id: "ei_4", kind: "csat", title: "CSAT dip on WhatsApp channel", summary: "WhatsApp CSAT fell to 4.1 (from 4.5) — driven by slow media handling.", recommendation: "Investigate media latency in the Twilio webhook.", severity: "warning", createdAt: daysAgo(2) },
];

export const businessImpact: BusinessImpact = {
  aiResolutionRate: 68.4,
  costSavings: 142_000,
  revenueInfluenced: 318_500,
  churnReduction: 14.2,
  agentProductivity: 31.0,
  retention: 92.6,
  ticketsHandled: 8420,
  ticketsAiResolved: 5760,
  csat: 4.5,
  trend: [
    { month: "Jan", savings: 18000, revenue: 38000 },
    { month: "Feb", savings: 21000, revenue: 44000 },
    { month: "Mar", savings: 23500, revenue: 47000 },
    { month: "Apr", savings: 25000, revenue: 52000 },
    { month: "May", savings: 26500, revenue: 64000 },
    { month: "Jun", savings: 28000, revenue: 73500 },
  ],
};

export const workflows: WorkflowItem[] = [
  { id: "wf_1", name: "Refund Request", description: "Verify → Ticket → Finance notify → Customer update", status: "active", trigger: "event: refund_request", nodes: 4, runCount: 312, lastRun: hoursAgo(1) },
  { id: "wf_2", name: "Lead Capture", description: "Qualify → CRM entry → Demo scheduling", status: "active", trigger: "event: lead_captured", nodes: 3, runCount: 540, lastRun: hoursAgo(3) },
  { id: "wf_3", name: "Support Escalation", description: "Assign ticket → Notify manager", status: "active", trigger: "event: escalation", nodes: 2, runCount: 198, lastRun: hoursAgo(7) },
  { id: "wf_4", name: "Onboarding Nudge", description: "Detect stalled onboarding → Email nudge", status: "paused", trigger: "schedule: daily", nodes: 2, runCount: 64, lastRun: daysAgo(3) },
  { id: "wf_5", name: "NPS Follow-up", description: "Detractor → Create task → Slack alert", status: "draft", trigger: "event: nps_submitted", nodes: 3, runCount: 0, lastRun: "" },
];

export const workflowRuns: WorkflowRunItem[] = [
  { id: "wr_1", workflow: "Refund Request", status: "succeeded", steps: 4, durationMs: 1240, createdAt: hoursAgo(1) },
  { id: "wr_2", workflow: "Lead Capture", status: "succeeded", steps: 3, durationMs: 890, createdAt: hoursAgo(2) },
  { id: "wr_3", workflow: "Support Escalation", status: "succeeded", steps: 2, durationMs: 410, createdAt: hoursAgo(3) },
  { id: "wr_4", workflow: "Refund Request", status: "failed", steps: 2, durationMs: 700, createdAt: hoursAgo(5) },
  { id: "wr_5", workflow: "Lead Capture", status: "running", steps: 1, durationMs: 0, createdAt: hoursAgo(0.1) },
];

// Canned Product-Expert answers for the demo chat.
export const expertCanned: Record<string, { answer: string; confidence: number; sources: { title: string; kind: "faq" | "pricing" | "policy" | "product" | "kb" }[] }> = {
  default: {
    answer:
      "OmniAssist AI is an AI Business Operations platform combining customer support, sales automation, customer success, product knowledge, executive insights, workflow automation and an employee assistant. Ask me about pricing, features, integrations, policies or how we compare to competitors.",
    confidence: 0.88,
    sources: [{ title: "Company overview", kind: "product" }],
  },
  pricing: {
    answer:
      "We offer four plans — Free, Starter ($29/mo), Pro ($99/mo) and Enterprise (custom). Pro includes unlimited AI conversations, the workflow engine and analytics; Enterprise adds SSO, data residency and a dedicated CSM.",
    confidence: 0.93,
    sources: [
      { title: "Pricing — Pro plan", kind: "pricing" },
      { title: "FAQ: annual discounts", kind: "faq" },
    ],
  },
};
