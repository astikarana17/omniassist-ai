import type {
  ActivityEvent,
  AiInsight,
  AuditEntry,
  Conversation,
  KbDocument,
  KpiMetric,
  Lead,
  Message,
  NotificationItem,
  Ticket,
  TimeseriesPoint,
  User,
} from "@/types";

const now = Date.now();
const minsAgo = (m: number) => new Date(now - m * 60_000).toISOString();
const hoursAgo = (h: number) => new Date(now - h * 3_600_000).toISOString();
const daysAgo = (d: number) => new Date(now - d * 86_400_000).toISOString();
const inMins = (m: number) => new Date(now + m * 60_000).toISOString();
const avatar = (seed: string) =>
  `https://api.dicebear.com/9.x/glass/svg?seed=${encodeURIComponent(seed)}`;

// ===== Users / Team =====
export const currentUser: User = {
  id: "u_1",
  name: "Priya Rao",
  email: "priya@acme.com",
  avatar: avatar("Priya Rao"),
  role: "owner",
  title: "Head of Customer Experience",
  status: "online",
  lastSeen: minsAgo(0),
};

export const users: User[] = [
  currentUser,
  {
    id: "u_2",
    name: "Arjun Kapoor",
    email: "arjun@acme.com",
    avatar: avatar("Arjun Kapoor"),
    role: "agent",
    title: "Support Agent",
    status: "online",
    lastSeen: minsAgo(2),
  },
  {
    id: "u_3",
    name: "Sara Mehta",
    email: "sara@acme.com",
    avatar: avatar("Sara Mehta"),
    role: "agent",
    title: "Sales Representative",
    status: "online",
    lastSeen: minsAgo(8),
  },
  {
    id: "u_4",
    name: "Dev Patel",
    email: "dev@acme.com",
    avatar: avatar("Dev Patel"),
    role: "admin",
    title: "Platform Administrator",
    status: "away",
    lastSeen: hoursAgo(1),
  },
  {
    id: "u_5",
    name: "Lena Cho",
    email: "lena@acme.com",
    avatar: avatar("Lena Cho"),
    role: "agent",
    title: "Support Agent",
    status: "offline",
    lastSeen: hoursAgo(5),
  },
  {
    id: "u_6",
    name: "Marco Rossi",
    email: "marco@acme.com",
    avatar: avatar("Marco Rossi"),
    role: "viewer",
    title: "Operations Analyst",
    status: "online",
    lastSeen: minsAgo(14),
  },
];

const byId = (id: string) => users.find((u) => u.id === id)!;

// ===== KPIs =====
export const dashboardKpis: KpiMetric[] = [
  {
    id: "deflection",
    label: "AI Deflection Rate",
    value: 72.4,
    format: "percent",
    delta: 4.2,
    ai: true,
    spark: [61, 63, 60, 65, 68, 67, 70, 69, 71, 72.4],
  },
  {
    id: "csat",
    label: "Customer Satisfaction",
    value: 4.6,
    format: "number",
    delta: 3.1,
    spark: [4.2, 4.3, 4.3, 4.4, 4.4, 4.5, 4.5, 4.6, 4.6, 4.6],
  },
  {
    id: "frt",
    label: "Avg First Response",
    value: 4.2,
    format: "duration",
    delta: -18.5,
    spark: [9, 8.2, 7.5, 6.8, 6, 5.4, 5, 4.6, 4.4, 4.2],
  },
  {
    id: "revenue",
    label: "Influenced Revenue",
    value: 284500,
    format: "currency",
    delta: 12.8,
    spark: [180, 198, 210, 225, 240, 248, 262, 270, 278, 284.5],
  },
  {
    id: "open",
    label: "Open Conversations",
    value: 38,
    format: "number",
    delta: -6.4,
    spark: [52, 48, 45, 44, 46, 42, 41, 40, 39, 38],
  },
  {
    id: "leads",
    label: "Hot Leads",
    value: 14,
    format: "number",
    delta: 21.0,
    ai: true,
    spark: [6, 7, 8, 9, 10, 11, 11, 12, 13, 14],
  },
];

// ===== Channel volume timeseries (30 days) =====
export const channelTimeseries: TimeseriesPoint[] = Array.from({ length: 30 }).map(
  (_, i) => {
    const wave = Math.sin(i / 3) * 18;
    return {
      date: new Date(now - (29 - i) * 86_400_000).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      }),
      web: Math.round(120 + wave + i * 2.4),
      whatsapp: Math.round(70 + wave * 0.8 + i * 1.8),
      email: Math.round(40 + Math.cos(i / 4) * 10 + i * 0.6),
      voice: Math.round(18 + Math.cos(i / 2) * 6 + i * 0.3),
    };
  }
);

export const csatTrend = Array.from({ length: 14 }).map((_, i) => ({
  date: new Date(now - (13 - i) * 86_400_000).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  }),
  csat: +(4.1 + Math.sin(i / 3) * 0.25 + i * 0.02).toFixed(2),
}));

export const revenueTrend = Array.from({ length: 12 }).map((_, i) => ({
  month: new Date(2025, i, 1).toLocaleDateString("en-US", { month: "short" }),
  revenue: Math.round(120000 + i * 14000 + Math.sin(i) * 9000),
  target: 130000 + i * 12000,
}));

export const conversionFunnel = [
  { stage: "Visitors", value: 24800, fill: "#6366F1" },
  { stage: "Engaged", value: 9200, fill: "#7C7CF0" },
  { stage: "Qualified", value: 3100, fill: "#8B5CF6" },
  { stage: "Demo", value: 940, fill: "#A78BFA" },
  { stage: "Won", value: 312, fill: "#22D3EE" },
];

export const sentimentByDay = Array.from({ length: 7 }).map((_, i) => ({
  day: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i],
  positive: Math.round(55 + Math.sin(i) * 10),
  neutral: Math.round(30 + Math.cos(i) * 6),
  negative: Math.round(15 + Math.sin(i / 2) * 5),
}));

export const resolutionHistogram = [
  { bucket: "<1m", count: 320 },
  { bucket: "1-5m", count: 540 },
  { bucket: "5-15m", count: 410 },
  { bucket: "15-60m", count: 220 },
  { bucket: "1-4h", count: 120 },
  { bucket: ">4h", count: 48 },
];

export const aiVsHuman = [
  { name: "AI Resolved", value: 68, fill: "#6366F1" },
  { name: "Human Resolved", value: 32, fill: "#22D3EE" },
];

export const teamPerformance = users
  .filter((u) => u.role === "agent" || u.role === "owner")
  .map((u, i) => ({
    name: u.name.split(" ")[0],
    resolved: 142 - i * 18,
    csat: +(4.7 - i * 0.12).toFixed(2),
    avgHandle: 6 + i * 1.4,
  }));

// ===== Activity feed =====
export const activityFeed: ActivityEvent[] = [
  { id: "a1", type: "ai_resolved", text: "AI resolved ticket #1042 — Refund processed", createdAt: minsAgo(0), channel: "web" },
  { id: "a2", type: "handoff", text: "Handoff requested by Rahul S.", createdAt: minsAgo(1), channel: "whatsapp" },
  { id: "a3", type: "lead", text: "New hot lead: Acme Corp — score 92", createdAt: minsAgo(3) },
  { id: "a4", type: "csat", text: "CSAT 5★ received on #1038", createdAt: minsAgo(6), channel: "email" },
  { id: "a5", type: "joined", text: "Arjun K. joined conversation #1041", createdAt: minsAgo(9), channel: "whatsapp" },
  { id: "a6", type: "ticket", text: "New ticket #1043 — Login issue", createdAt: minsAgo(12), channel: "web" },
  { id: "a7", type: "ai_resolved", text: "AI resolved #1037 — Shipping query", createdAt: minsAgo(18), channel: "whatsapp" },
  { id: "a8", type: "lead", text: "Demo booked with Beta Inc — Friday 3pm", createdAt: minsAgo(24) },
];

// ===== AI insights =====
export const aiInsights: AiInsight[] = [
  {
    id: "i1",
    kind: "trend",
    title: "WhatsApp volume up 23% this week",
    recommendation: "Consider adding evening coverage between 6–9pm IST.",
    actionLabel: "View conversations",
  },
  {
    id: "i2",
    kind: "risk",
    title: "3 tickets at SLA risk in the next 30 minutes",
    recommendation: "Reassign #1041, #1044, #1047 to available agents.",
    actionLabel: "Reassign now",
  },
  {
    id: "i3",
    kind: "opportunity",
    title: "2 high-intent leads idle for 24h",
    recommendation: "Trigger an AI follow-up to Acme Corp and Gamma Ltd.",
    actionLabel: "Follow up",
  },
];

// ===== Contacts & conversations =====
const supportThread: Message[] = [
  {
    id: "m1",
    conversationId: "c_1",
    sender: "contact",
    authorName: "Rahul Sharma",
    content: "Hi, I was charged twice for my last order. Can you help?",
    createdAt: minsAgo(14),
    language: "en",
  },
  {
    id: "m2",
    conversationId: "c_1",
    sender: "ai",
    content:
      "I'm sorry about the duplicate charge, Rahul. I can see order #882 was billed twice on June 6. I've initiated a refund for the extra ₹2,499 — it should reflect in 3–5 business days.",
    createdAt: minsAgo(13),
    confidence: 91,
    sources: [
      { title: "Billing & Refund Policy", chunk: "Duplicate charges are auto-refunded within 3–5 business days." },
    ],
    language: "en",
  },
  {
    id: "m3",
    conversationId: "c_1",
    sender: "contact",
    authorName: "Rahul Sharma",
    content: "Thanks! But I'd like to confirm this with a human agent.",
    createdAt: minsAgo(11),
    language: "en",
  },
  {
    id: "m4",
    conversationId: "c_1",
    sender: "system",
    content: "AI handed off to Priya Rao — full context attached.",
    createdAt: minsAgo(10),
  },
  {
    id: "m5",
    conversationId: "c_1",
    sender: "agent",
    authorName: "Priya Rao",
    authorAvatar: currentUser.avatar,
    content: "Hi Rahul, Priya here. I've confirmed the refund of ₹2,499 is processing. You'll get an email receipt shortly. Anything else I can help with?",
    createdAt: minsAgo(8),
    status: "read",
    language: "en",
  },
];

export const conversations: Conversation[] = [
  {
    id: "c_1",
    contact: { id: "ct_1", name: "Rahul Sharma", email: "rahul@gmail.com", phone: "+91 98765 43210", avatar: avatar("Rahul Sharma"), company: "Individual", pastConversations: 3 },
    channel: "whatsapp",
    status: "open",
    subject: "Double charge on order #882",
    preview: "I'd like to confirm this with a human agent.",
    unread: 2,
    sentiment: "negative",
    assignee: currentUser,
    aiHandled: true,
    lastMessageAt: minsAgo(8),
    language: "English",
    messages: supportThread,
  },
  {
    id: "c_2",
    contact: { id: "ct_2", name: "Meera Iyer", email: "meera@startup.io", avatar: avatar("Meera Iyer"), company: "Startup.io", pastConversations: 1 },
    channel: "web",
    status: "open",
    subject: "How do I upgrade my plan?",
    preview: "Can I switch to the Growth plan mid-cycle?",
    unread: 1,
    sentiment: "neutral",
    assignee: null,
    aiHandled: true,
    lastMessageAt: minsAgo(22),
    language: "English",
    messages: [
      { id: "m6", conversationId: "c_2", sender: "contact", authorName: "Meera Iyer", content: "Can I switch to the Growth plan mid-cycle?", createdAt: minsAgo(23), language: "en" },
      { id: "m7", conversationId: "c_2", sender: "ai", content: "Absolutely! You can upgrade anytime and we'll prorate the difference. Your new limits apply instantly.", createdAt: minsAgo(22), confidence: 88, sources: [{ title: "Billing FAQ", chunk: "Mid-cycle upgrades are prorated automatically." }], language: "en" },
    ],
  },
  {
    id: "c_3",
    contact: { id: "ct_3", name: "John Carter", email: "john@bigco.com", avatar: avatar("John Carter"), company: "BigCo", pastConversations: 7 },
    channel: "email",
    status: "pending",
    subject: "Invoice mismatch for May",
    preview: "The May invoice doesn't match our usage report…",
    unread: 0,
    sentiment: "neutral",
    assignee: byId("u_2"),
    aiHandled: false,
    lastMessageAt: hoursAgo(1),
    language: "English",
    messages: [
      { id: "m8", conversationId: "c_3", sender: "contact", authorName: "John Carter", content: "The May invoice doesn't match our usage report. Can someone check?", createdAt: hoursAgo(1), language: "en" },
    ],
  },
  {
    id: "c_4",
    contact: { id: "ct_4", name: "Sofia García", email: "sofia@empresa.es", avatar: avatar("Sofia Garcia"), company: "Empresa SL", pastConversations: 2 },
    channel: "whatsapp",
    status: "open",
    subject: "Problema con el pago",
    preview: "No puedo completar mi pago con tarjeta.",
    unread: 3,
    sentiment: "negative",
    assignee: null,
    aiHandled: true,
    lastMessageAt: minsAgo(34),
    language: "Spanish",
    messages: [
      { id: "m9", conversationId: "c_4", sender: "contact", authorName: "Sofia García", content: "No puedo completar mi pago con tarjeta.", createdAt: minsAgo(35), language: "es" },
      { id: "m10", conversationId: "c_4", sender: "ai", content: "Lamento el inconveniente, Sofia. Veo que tu tarjeta fue rechazada por tu banco. ¿Quieres intentar con otro método de pago o que te envíe un enlace seguro?", createdAt: minsAgo(34), confidence: 84, language: "es" },
    ],
  },
  {
    id: "c_5",
    contact: { id: "ct_5", name: "Tom Becker", email: "tom@voice.de", avatar: avatar("Tom Becker"), phone: "+49 151 2345678", company: "Voice GmbH", pastConversations: 0 },
    channel: "voice",
    status: "resolved",
    subject: "Voice call — Account access",
    preview: "Call summary: Reset 2FA, verified identity.",
    unread: 0,
    sentiment: "positive",
    assignee: byId("u_5"),
    aiHandled: true,
    lastMessageAt: hoursAgo(3),
    language: "German",
    messages: [
      { id: "m11", conversationId: "c_5", sender: "system", content: "Inbound voice call · 4m 12s · transcribed", createdAt: hoursAgo(3) },
      { id: "m12", conversationId: "c_5", sender: "ai", content: "Call summary: Customer locked out due to 2FA. Verified identity via email OTP, reset authenticator. Resolved on call.", createdAt: hoursAgo(3), confidence: 95 },
    ],
  },
];

// ===== Tickets =====
export const tickets: Ticket[] = [
  { id: "t_1042", number: 1042, subject: "Double charge on order #882", status: "in_progress", priority: "high", channel: "whatsapp", assignee: currentUser, requester: conversations[0].contact, tags: ["billing", "refund"], slaDueAt: inMins(12), createdAt: minsAgo(14), updatedAt: minsAgo(8), sentiment: "negative", aiSummary: "Customer double-charged ₹2,499 on order #882. Refund initiated, ETA 3–5 days. Awaiting customer confirmation." },
  { id: "t_1041", number: 1041, subject: "Cannot log in after password reset", status: "open", priority: "urgent", channel: "web", assignee: null, requester: conversations[1].contact, tags: ["auth", "login"], slaDueAt: inMins(2), createdAt: minsAgo(40), updatedAt: minsAgo(20), sentiment: "negative", aiSummary: "Password reset email not arriving; possible deliverability issue. Needs human + eng check." },
  { id: "t_1040", number: 1040, subject: "Feature request: bulk export", status: "open", priority: "low", channel: "email", assignee: byId("u_2"), requester: conversations[2].contact, tags: ["feature"], slaDueAt: null, createdAt: hoursAgo(5), updatedAt: hoursAgo(2), sentiment: "neutral", aiSummary: "Customer wants CSV bulk export for analytics. Logged to product backlog." },
  { id: "t_1039", number: 1039, subject: "Shipping delay for order #771", status: "resolved", priority: "medium", channel: "whatsapp", assignee: byId("u_5"), requester: conversations[4].contact, tags: ["shipping"], slaDueAt: null, createdAt: hoursAgo(8), updatedAt: hoursAgo(6), sentiment: "positive", aiSummary: "Shipping delayed 2 days due to weather. Provided tracking + 10% coupon. Resolved." },
  { id: "t_1038", number: 1038, subject: "Refund status inquiry", status: "closed", priority: "low", channel: "email", assignee: byId("u_2"), requester: conversations[2].contact, tags: ["billing"], slaDueAt: null, createdAt: daysAgo(2), updatedAt: daysAgo(1), sentiment: "positive", aiSummary: "Refund confirmed processed. Customer satisfied (5★)." },
  { id: "t_1037", number: 1037, subject: "Problema con el pago con tarjeta", status: "in_progress", priority: "high", channel: "whatsapp", assignee: byId("u_3"), requester: conversations[3].contact, tags: ["billing", "payments"], slaDueAt: inMins(45), createdAt: minsAgo(35), updatedAt: minsAgo(30), sentiment: "negative", aiSummary: "Card declined by issuing bank. Offered alternate payment link. Awaiting customer." },
  { id: "t_1044", number: 1044, subject: "API rate limit questions", status: "open", priority: "medium", channel: "web", assignee: null, requester: conversations[1].contact, tags: ["api", "developers"], slaDueAt: inMins(90), createdAt: hoursAgo(2), updatedAt: hoursAgo(1), sentiment: "neutral", aiSummary: "Developer asking about rate limits on Growth plan. KB answer provided, confirming edge case." },
];

// ===== Leads =====
export const leads: Lead[] = [
  { id: "l_1", name: "Acme Corp", company: "Acme Corporation", avatar: avatar("Acme Corp"), email: "ops@acme.co", value: 42000, score: 92, stage: "demo", owner: byId("u_3"), source: "web", nextAction: "Demo call", nextActionDue: inMins(60 * 26), createdAt: daysAgo(4) },
  { id: "l_2", name: "Beta Inc", company: "Beta Incorporated", avatar: avatar("Beta Inc"), email: "hi@beta.io", value: 18000, score: 68, stage: "qualified", owner: byId("u_3"), source: "whatsapp", nextAction: "Follow-up email", nextActionDue: inMins(60 * 5), createdAt: daysAgo(6) },
  { id: "l_3", name: "Gamma Ltd", company: "Gamma Limited", avatar: avatar("Gamma Ltd"), email: "sales@gamma.com", value: 65000, score: 81, stage: "proposal", owner: currentUser, source: "email", nextAction: "Send proposal", nextActionDue: inMins(60 * 2), createdAt: daysAgo(9) },
  { id: "l_4", name: "Delta Co", company: "Delta Company", avatar: avatar("Delta Co"), email: "contact@delta.co", value: 23000, score: 74, stage: "qualified", owner: byId("u_3"), source: "web", nextAction: "Discovery call", nextActionDue: inMins(60 * 48), createdAt: daysAgo(3) },
  { id: "l_5", name: "Echo Systems", company: "Echo Systems", avatar: avatar("Echo Systems"), email: "team@echo.sys", value: 31000, score: 88, stage: "won", owner: byId("u_3"), source: "web", nextAction: "Onboarding kickoff", nextActionDue: inMins(60 * 72), createdAt: daysAgo(14) },
  { id: "l_6", name: "Foxtrot LLC", company: "Foxtrot LLC", avatar: avatar("Foxtrot LLC"), email: "info@foxtrot.llc", value: 12000, score: 54, stage: "new", owner: currentUser, source: "whatsapp", nextAction: "Qualify (BANT)", nextActionDue: inMins(60 * 8), createdAt: daysAgo(1) },
  { id: "l_7", name: "Helix Health", company: "Helix Health", avatar: avatar("Helix Health"), email: "ops@helix.health", value: 88000, score: 95, stage: "demo", owner: currentUser, source: "email", nextAction: "Technical demo", nextActionDue: inMins(60 * 30), createdAt: daysAgo(5) },
  { id: "l_8", name: "Nimbus Cloud", company: "Nimbus Cloud", avatar: avatar("Nimbus Cloud"), email: "hello@nimbus.cloud", value: 47000, score: 63, stage: "new", owner: byId("u_3"), source: "web", nextAction: "Send intro deck", nextActionDue: inMins(60 * 12), createdAt: daysAgo(2) },
  { id: "l_9", name: "Orion Retail", company: "Orion Retail", avatar: avatar("Orion Retail"), email: "buy@orion.shop", value: 29000, score: 40, stage: "lost", owner: byId("u_3"), source: "whatsapp", nextAction: "Re-engage Q3", nextActionDue: inMins(60 * 200), createdAt: daysAgo(20) },
  { id: "l_10", name: "Pulse Media", company: "Pulse Media", avatar: avatar("Pulse Media"), email: "growth@pulse.media", value: 54000, score: 79, stage: "proposal", owner: currentUser, source: "web", nextAction: "Negotiate terms", nextActionDue: inMins(60 * 18), createdAt: daysAgo(11) },
];

// ===== Knowledge base =====
export const kbDocuments: KbDocument[] = [
  { id: "kb_1", title: "Billing & Refund Policy", sourceType: "upload", status: "ready", chunks: 128, updatedAt: daysAgo(3), sizeLabel: "240 KB · PDF" },
  { id: "kb_2", title: "Product Pricing Guide 2026", sourceType: "upload", status: "processing", chunks: 64, progress: 64, updatedAt: minsAgo(4), sizeLabel: "1.1 MB · PDF" },
  { id: "kb_3", title: "docs.omniassist.ai (crawled)", sourceType: "crawl", status: "ready", chunks: 412, updatedAt: daysAgo(1), sizeLabel: "84 pages" },
  { id: "kb_4", title: "Top 50 Support FAQs", sourceType: "faq", status: "ready", chunks: 50, updatedAt: daysAgo(7), sizeLabel: "50 Q&A" },
  { id: "kb_5", title: "Onboarding & Setup Guide", sourceType: "upload", status: "ready", chunks: 96, updatedAt: daysAgo(5), sizeLabel: "680 KB · DOCX" },
  { id: "kb_6", title: "Shipping & Logistics Handbook", sourceType: "upload", status: "failed", chunks: 0, updatedAt: hoursAgo(2), sizeLabel: "3.4 MB · PDF" },
];

// ===== Audit logs =====
export const auditLog: AuditEntry[] = [
  { id: "au_1", actor: byId("u_4"), action: "changed role", resourceType: "user", resource: "Arjun Kapoor", detail: "Agent → Admin", ip: "103.21.58.4", createdAt: minsAgo(24) },
  { id: "au_2", actor: currentUser, action: "deleted document", resourceType: "knowledge_base", resource: "Refund Policy v1", detail: "Replaced by v2", ip: "103.21.58.7", createdAt: minsAgo(58) },
  { id: "au_3", actor: { name: "System", avatar: avatar("System") }, action: "SLA breached", resourceType: "ticket", resource: "#1041", detail: "First response > 2m target", ip: "—", createdAt: hoursAgo(1) },
  { id: "au_4", actor: byId("u_4"), action: "updated channel", resourceType: "channel", resource: "WhatsApp", detail: "Enabled templates", ip: "103.21.58.4", createdAt: hoursAgo(3) },
  { id: "au_5", actor: byId("u_2"), action: "exported data", resourceType: "analytics", resource: "Conversations 30d", detail: "CSV export", ip: "117.5.12.88", createdAt: hoursAgo(4) },
  { id: "au_6", actor: currentUser, action: "invited member", resourceType: "team", resource: "marco@acme.com", detail: "Role: Viewer", ip: "103.21.58.7", createdAt: daysAgo(1) },
  { id: "au_7", actor: byId("u_4"), action: "rotated API key", resourceType: "security", resource: "prod-key-2", detail: "Scopes: read, write", ip: "103.21.58.4", createdAt: daysAgo(2) },
];

// ===== Notifications =====
export const notifications: NotificationItem[] = [
  { id: "n_1", type: "handoff", title: "Handoff requested", body: "Rahul S. wants to talk to a human on WhatsApp.", createdAt: minsAgo(1), read: false },
  { id: "n_2", type: "sla", title: "SLA at risk", body: "Ticket #1041 breaches SLA in 2 minutes.", createdAt: minsAgo(3), read: false },
  { id: "n_3", type: "lead", title: "New hot lead", body: "Acme Corp scored 92 — assigned to Sara.", createdAt: minsAgo(8), read: false },
  { id: "n_4", type: "csat", title: "5★ CSAT received", body: "Great rating on ticket #1038.", createdAt: minsAgo(26), read: true },
  { id: "n_5", type: "mention", title: "You were mentioned", body: "Arjun mentioned you in #1041.", createdAt: hoursAgo(1), read: true },
  { id: "n_6", type: "system", title: "Knowledge base updated", body: "Pricing Guide 2026 finished indexing.", createdAt: hoursAgo(2), read: true },
];

export const csatScore = 4.6;
export const npsScore = 62;
