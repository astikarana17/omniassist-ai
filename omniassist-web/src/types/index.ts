// ===== Shared domain types for OmniAssist AI =====

export type Channel = "web" | "whatsapp" | "email" | "voice";

export type ConversationStatus = "open" | "pending" | "resolved" | "snoozed" | "closed";

export type TicketStatus = "open" | "in_progress" | "pending" | "resolved" | "closed";

export type Priority = "low" | "medium" | "high" | "urgent";

export type Sentiment = "positive" | "neutral" | "negative";

export type Role = "owner" | "admin" | "agent" | "viewer";

export type SenderType = "contact" | "ai" | "agent" | "system";

export type LeadStage = "new" | "qualified" | "demo" | "proposal" | "won" | "lost";

export interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  role: Role;
  title: string;
  status: "online" | "away" | "offline";
  lastSeen: string;
}

export interface Contact {
  id: string;
  name: string;
  email: string;
  phone?: string;
  avatar: string;
  company?: string;
  pastConversations: number;
}

export interface MessageAttachment {
  id: string;
  type: "image" | "file" | "audio";
  name: string;
  size?: string;
  url: string;
  durationSec?: number;
}

export interface Message {
  id: string;
  conversationId: string;
  sender: SenderType;
  authorName?: string;
  authorAvatar?: string;
  content: string;
  createdAt: string;
  sources?: { title: string; chunk: string }[];
  confidence?: number;
  attachments?: MessageAttachment[];
  reactions?: { emoji: string; count: number }[];
  language?: string;
  status?: "sent" | "delivered" | "read";
}

export interface Conversation {
  id: string;
  contact: Contact;
  channel: Channel;
  status: ConversationStatus;
  subject: string;
  preview: string;
  unread: number;
  sentiment: Sentiment;
  assignee?: User | null;
  aiHandled: boolean;
  lastMessageAt: string;
  language: string;
  messages: Message[];
}

export interface Ticket {
  id: string;
  number: number;
  subject: string;
  status: TicketStatus;
  priority: Priority;
  channel: Channel;
  assignee: User | null;
  requester: Contact;
  tags: string[];
  slaDueAt: string | null;
  createdAt: string;
  updatedAt: string;
  aiSummary?: string;
  sentiment: Sentiment;
}

export interface Lead {
  id: string;
  name: string;
  company: string;
  avatar: string;
  email: string;
  value: number;
  score: number;
  stage: LeadStage;
  owner: User;
  source: Channel;
  nextAction: string;
  nextActionDue: string;
  createdAt: string;
}

export interface KbDocument {
  id: string;
  title: string;
  sourceType: "upload" | "crawl" | "faq";
  status: "ready" | "processing" | "failed";
  chunks: number;
  progress?: number;
  updatedAt: string;
  sizeLabel: string;
}

export interface AuditEntry {
  id: string;
  actor: User | { name: string; avatar: string };
  action: string;
  resourceType: string;
  resource: string;
  detail: string;
  ip: string;
  createdAt: string;
}

export interface NotificationItem {
  id: string;
  type: "handoff" | "sla" | "mention" | "lead" | "system" | "csat";
  title: string;
  body: string;
  createdAt: string;
  read: boolean;
}

export interface KpiMetric {
  id: string;
  label: string;
  value: number;
  format: "number" | "currency" | "percent" | "duration";
  delta: number;
  spark: number[];
  ai?: boolean;
}

export interface ActivityEvent {
  id: string;
  type: "ai_resolved" | "handoff" | "lead" | "joined" | "ticket" | "csat";
  text: string;
  createdAt: string;
  channel?: Channel;
}

export interface AiInsight {
  id: string;
  kind: "opportunity" | "risk" | "trend";
  title: string;
  recommendation: string;
  actionLabel: string;
}

export interface TimeseriesPoint {
  date: string;
  web: number;
  whatsapp: number;
  email: number;
  voice: number;
}

// ===== Business Operations Platform =====

export type HealthCategory = "healthy" | "at_risk" | "critical";

export interface CustomerHealth {
  id: string;
  name: string;
  plan: string;
  mrr: number;
  score: number;
  category: HealthCategory;
  churnRisk: number; // 0..1
  usage: number;
  engagement: number;
  support: number;
  satisfaction: number;
  adoption: number;
  owner: string;
  lastActive: string;
}

export type GapStatus = "open" | "in_review" | "resolved" | "dismissed";

export interface KnowledgeGapItem {
  id: string;
  question: string;
  occurrences: number;
  avgConfidence: number; // 0..1
  status: GapStatus;
  suggestion?: string;
  lastSeen: string;
}

export type InsightKind =
  | "revenue"
  | "churn"
  | "csat"
  | "adoption"
  | "support_perf"
  | "sales_perf"
  | "recommendation";

export interface ExecInsight {
  id: string;
  kind: InsightKind;
  title: string;
  summary: string;
  recommendation?: string;
  severity: "info" | "positive" | "warning" | "critical";
  createdAt: string;
}

export interface BusinessImpact {
  aiResolutionRate: number;
  costSavings: number;
  revenueInfluenced: number;
  churnReduction: number;
  agentProductivity: number;
  retention: number;
  ticketsHandled: number;
  ticketsAiResolved: number;
  csat: number;
  trend: { month: string; savings: number; revenue: number }[];
}

export type WorkflowStatus = "draft" | "active" | "paused" | "archived";

export interface WorkflowItem {
  id: string;
  name: string;
  description: string;
  status: WorkflowStatus;
  trigger: string;
  nodes: number;
  runCount: number;
  lastRun: string;
}

export interface WorkflowRunItem {
  id: string;
  workflow: string;
  status: "succeeded" | "failed" | "running";
  steps: number;
  durationMs: number;
  createdAt: string;
}

export interface ExpertSource {
  title: string;
  kind: "faq" | "pricing" | "policy" | "product" | "kb";
}
