// React Query hooks bridging the UI to the omniassist-api backend.
//
// Every data hook gracefully falls back to local mock data when the API is not
// configured (NEXT_PUBLIC_API_URL unset) so the app runs in demo mode. When the
// API URL is set, hooks fetch live and map snake_case DTOs to the UI types.

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiConfigured, apiFetch } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import {
  businessImpact,
  customerHealth,
  execInsights,
  gapCounts,
  knowledgeGaps,
  workflowRuns,
  workflows,
} from "@/lib/ops-data";
import type {
  BusinessImpact,
  CustomerHealth,
  ExecInsight,
  GapStatus,
  HealthCategory,
  KnowledgeGapItem,
  WorkflowItem,
  WorkflowStatus,
} from "@/types";

interface Page<T> {
  items: T[];
  meta: { total: number; limit: number; offset: number; has_more: boolean };
}

// ---------------- Auth ----------------
interface AuthResponseDTO {
  user: { id: string; email: string; full_name: string; avatar_url?: string | null; title?: string | null };
  organization: { id: string; name: string; slug: string; role: string };
  tokens: { access_token: string; refresh_token: string; expires_in: number };
}

function applySession(res: AuthResponseDTO) {
  useAuthStore.getState().setSession({
    accessToken: res.tokens.access_token,
    refreshToken: res.tokens.refresh_token,
    user: {
      id: res.user.id,
      email: res.user.email,
      fullName: res.user.full_name,
      avatarUrl: res.user.avatar_url,
      title: res.user.title,
    },
    org: res.organization,
  });
}

export function useLogin() {
  return useMutation({
    mutationFn: (vars: { email: string; password: string }) =>
      apiFetch<AuthResponseDTO>("/auth/login", { method: "POST", body: vars, auth: false }),
    onSuccess: applySession,
  });
}

export function useSignup() {
  return useMutation({
    mutationFn: (vars: {
      full_name: string;
      email: string;
      password: string;
      workspace_name: string;
    }) => apiFetch<AuthResponseDTO>("/auth/signup", { method: "POST", body: vars, auth: false }),
    onSuccess: applySession,
  });
}

export function useOAuthCallback() {
  return useMutation({
    mutationFn: (vars: { provider: "google" | "github"; code: string }) =>
      apiFetch<AuthResponseDTO>(`/auth/${vars.provider}/callback`, {
        method: "POST",
        body: { code: vars.code },
        auth: false,
      }),
    onSuccess: applySession,
  });
}

export function useLogout() {
  return useMutation({
    mutationFn: async () => {
      const rt = useAuthStore.getState().refreshToken;
      if (apiConfigured() && rt) {
        try {
          await apiFetch("/auth/logout", { method: "POST", body: { refresh_token: rt } });
        } catch {
          /* ignore — clear locally regardless */
        }
      }
    },
    onSuccess: () => useAuthStore.getState().clear(),
  });
}

// ---------------- Customer health ----------------
interface CustomerAccountDTO {
  id: string;
  name: string;
  plan: string | null;
  mrr: number;
  status: string;
  owner_id: string | null;
  last_active_at: string | null;
}

// Derive a health view from the real account status until a joined
// accounts+latest-health endpoint exists on the backend.
function statusToHealth(status: string): { score: number; category: HealthCategory; churn: number } {
  const map: Record<string, { score: number; category: HealthCategory }> = {
    active: { score: 85, category: "healthy" },
    trial: { score: 60, category: "at_risk" },
    paused: { score: 45, category: "at_risk" },
    churned: { score: 25, category: "critical" },
  };
  const h = map[status] ?? { score: 55, category: "at_risk" as HealthCategory };
  return { ...h, churn: Math.round((1 - h.score / 100) * 100) / 100 };
}

export function useCustomerHealth() {
  return useQuery<CustomerHealth[]>({
    queryKey: ["customer-health"],
    queryFn: async () => {
      if (!apiConfigured()) return customerHealth;
      const page = await apiFetch<Page<CustomerAccountDTO>>("/customer-success/accounts?limit=100");
      return page.items.map((a) => {
        const h = statusToHealth(a.status);
        return {
          id: a.id,
          name: a.name,
          plan: a.plan ?? "—",
          mrr: a.mrr,
          score: h.score,
          category: h.category,
          churnRisk: h.churn,
          usage: h.score,
          engagement: h.score,
          support: h.score,
          satisfaction: h.score,
          adoption: h.score,
          owner: a.owner_id ?? "—",
          lastActive: a.last_active_at ?? a.id,
        };
      });
    },
  });
}

// ---------------- Knowledge gaps ----------------
interface GapDTO {
  id: string;
  question: string;
  occurrences: number;
  avg_confidence: number | null;
  suggestion: string | null;
  status: GapStatus;
  last_seen_at: string;
}

export function useKnowledgeGaps() {
  return useQuery<KnowledgeGapItem[]>({
    queryKey: ["knowledge-gaps"],
    queryFn: async () => {
      if (!apiConfigured()) return knowledgeGaps;
      const page = await apiFetch<Page<GapDTO>>("/knowledge-gaps?limit=50");
      return page.items.map((g) => ({
        id: g.id,
        question: g.question,
        occurrences: g.occurrences,
        avgConfidence: g.avg_confidence ?? 0,
        suggestion: g.suggestion ?? undefined,
        status: g.status,
        lastSeen: g.last_seen_at,
      }));
    },
  });
}

export function useGapDashboard() {
  return useQuery({
    queryKey: ["gap-dashboard"],
    queryFn: async () => {
      if (!apiConfigured()) return gapCounts;
      const d = await apiFetch<{ open: number; in_review: number; resolved: number; dismissed: number }>(
        "/knowledge-gaps/dashboard"
      );
      return { open: d.open, in_review: d.in_review, resolved: d.resolved, dismissed: d.dismissed };
    },
  });
}

// ---------------- Executive insights + impact ----------------
interface InsightDTO {
  id: string;
  kind: ExecInsight["kind"];
  title: string;
  summary: string;
  recommendation: string | null;
  severity: ExecInsight["severity"];
  created_at: string;
}

export function useInsights() {
  return useQuery<ExecInsight[]>({
    queryKey: ["exec-insights"],
    queryFn: async () => {
      if (!apiConfigured()) return execInsights;
      const page = await apiFetch<Page<InsightDTO>>("/insights?limit=20");
      return page.items.map((i) => ({
        id: i.id,
        kind: i.kind,
        title: i.title,
        summary: i.summary,
        recommendation: i.recommendation ?? undefined,
        severity: i.severity,
        createdAt: i.created_at,
      }));
    },
  });
}

interface ImpactDTO {
  ai_resolution_rate: number | null;
  cost_savings_usd: number | null;
  revenue_influenced_usd: number | null;
  churn_reduction_pct: number | null;
  agent_productivity: number | null;
  customer_retention_pct: number | null;
  tickets_handled: number | null;
  tickets_ai_resolved: number | null;
  csat_avg: number | null;
}

export function useImpact() {
  return useQuery<BusinessImpact>({
    queryKey: ["business-impact"],
    queryFn: async () => {
      if (!apiConfigured()) return businessImpact;
      const page = await apiFetch<Page<ImpactDTO>>("/insights/impact?limit=1");
      const m = page.items[0];
      if (!m) return businessImpact;
      return {
        aiResolutionRate: m.ai_resolution_rate ?? 0,
        costSavings: m.cost_savings_usd ?? 0,
        revenueInfluenced: m.revenue_influenced_usd ?? 0,
        churnReduction: m.churn_reduction_pct ?? 0,
        agentProductivity: m.agent_productivity ?? 0,
        retention: m.customer_retention_pct ?? 0,
        ticketsHandled: m.tickets_handled ?? 0,
        ticketsAiResolved: m.tickets_ai_resolved ?? 0,
        csat: m.csat_avg ?? 0,
        trend: businessImpact.trend, // trend chart keeps the curated series
      };
    },
  });
}

// ---------------- Workflows ----------------
interface WorkflowDTO {
  id: string;
  name: string;
  description: string | null;
  status: WorkflowStatus;
  trigger_type: string;
  definition: { nodes?: unknown[] };
  run_count: number;
  last_run_at: string | null;
}

export function useWorkflows() {
  return useQuery<WorkflowItem[]>({
    queryKey: ["workflows"],
    queryFn: async () => {
      if (!apiConfigured()) return workflows;
      const page = await apiFetch<Page<WorkflowDTO>>("/workflows?limit=50");
      return page.items.map((w) => ({
        id: w.id,
        name: w.name,
        description: w.description ?? "",
        status: w.status,
        trigger: w.trigger_type,
        nodes: w.definition?.nodes?.length ?? 0,
        runCount: w.run_count,
        lastRun: w.last_run_at ?? "",
      }));
    },
  });
}

// No global runs endpoint yet (runs are per-workflow) — demo panel uses mock.
export function useWorkflowRuns() {
  return useQuery({
    queryKey: ["workflow-runs"],
    queryFn: async () => workflowRuns,
  });
}

// ---------------- Product Expert ----------------
interface AskResponseDTO {
  answer: string;
  confidence: number;
  sources: { title?: string }[];
  knowledge_gap_recorded: boolean;
}

export function useAskExpert() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { question: string; history?: string }) =>
      apiFetch<AskResponseDTO>("/company/ask", {
        method: "POST",
        body: { question: vars.question, history: vars.history },
      }),
    onSuccess: (res) => {
      // A newly recorded gap should refresh the gaps views.
      if (res.knowledge_gap_recorded) {
        qc.invalidateQueries({ queryKey: ["knowledge-gaps"] });
        qc.invalidateQueries({ queryKey: ["gap-dashboard"] });
      }
    },
  });
}

// ---------------- Inbox / conversations ----------------
import type {
  Channel as UIChannel,
  Conversation as UIConversation,
  Message as UIMessage,
  SenderType,
} from "@/types";

interface MessageDTO {
  id: string;
  sender_type: string;
  author_name?: string | null;
  content: string;
  confidence?: number | null;
  sources?: { title?: string; text?: string }[];
  language?: string | null;
  created_at: string;
}
interface ContactDTO {
  id: string;
  name: string;
  email?: string | null;
  phone?: string | null;
  company?: string | null;
  avatar_url?: string | null;
}
interface ConvDTO {
  id: string;
  channel: string;
  status: string;
  subject?: string | null;
  language?: string | null;
  sentiment?: string | null;
  ai_handled: boolean;
  unread_count: number;
  last_message_at?: string | null;
  contact: ContactDTO;
  messages?: MessageDTO[];
}

function mapMessage(m: MessageDTO): UIMessage {
  const sender = (["contact", "ai", "agent", "system"].includes(m.sender_type)
    ? m.sender_type
    : "system") as SenderType;
  return {
    id: m.id,
    conversationId: "",
    sender,
    authorName: m.author_name ?? undefined,
    content: m.content,
    createdAt: m.created_at,
    confidence: m.confidence ?? undefined,
    sources: (m.sources ?? []).map((s) => ({ title: s.title ?? "Source", chunk: s.text ?? "" })),
  };
}

function mapConversation(c: ConvDTO): UIConversation {
  const messages = (c.messages ?? []).map(mapMessage);
  const last = messages[messages.length - 1];
  const sentiment = (["positive", "neutral", "negative"].includes(c.sentiment ?? "")
    ? c.sentiment
    : "neutral") as UIConversation["sentiment"];
  return {
    id: c.id,
    channel: c.channel as UIChannel,
    status: c.status as UIConversation["status"],
    subject: c.subject ?? "",
    preview: last?.content ?? c.subject ?? "",
    unread: c.unread_count ?? 0,
    sentiment,
    assignee: null,
    aiHandled: c.ai_handled,
    lastMessageAt: c.last_message_at ?? new Date().toISOString(),
    language: c.language ?? "English",
    contact: {
      id: c.contact?.id ?? "",
      name: c.contact?.name ?? "Customer",
      email: c.contact?.email ?? "",
      phone: c.contact?.phone ?? undefined,
      avatar: c.contact?.avatar_url ?? "",
      company: c.contact?.company ?? undefined,
      pastConversations: 0,
    },
    messages,
  };
}

export function useConversations(channel?: string) {
  return useQuery<UIConversation[] | null>({
    queryKey: ["conversations", channel ?? "all"],
    queryFn: async () => {
      if (!apiConfigured()) return null; // null → page uses mock data
      const q = channel ? `?channel=${channel}&limit=50` : "?limit=50";
      const page = await apiFetch<Page<ConvDTO>>(`/conversations${q}`);
      return page.items.map(mapConversation);
    },
  });
}

export function useConversation(id?: string) {
  return useQuery<UIConversation | null>({
    queryKey: ["conversation", id],
    enabled: !!id && apiConfigured(),
    queryFn: async () => mapConversation(await apiFetch<ConvDTO>(`/conversations/${id}`)),
  });
}

export function useCustomerMessage(conversationId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (content: string) =>
      apiFetch<ConvDTO>(`/conversations/${conversationId}/customer`, {
        method: "POST",
        body: { content },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["conversation", conversationId] });
      qc.invalidateQueries({ queryKey: ["conversations"] });
    },
  });
}

function invalidateConversation(qc: ReturnType<typeof useQueryClient>, id: string) {
  qc.invalidateQueries({ queryKey: ["conversation", id] });
  qc.invalidateQueries({ queryKey: ["conversations"] });
}

/** Human agent reply (message shows as `agent`, not AI). */
export function useAgentReply(conversationId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (content: string) =>
      apiFetch(`/conversations/${conversationId}/messages`, { method: "POST", body: { content } }),
    onSuccess: () => invalidateConversation(qc, conversationId),
  });
}

/** Take over / hand off the conversation to a human (status → pending). */
export function useHandoff(conversationId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => apiFetch(`/conversations/${conversationId}/handoff`, { method: "POST" }),
    onSuccess: () => invalidateConversation(qc, conversationId),
  });
}

/** Change conversation status (e.g. "resolved", "open"). */
export function useConversationStatus(conversationId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (status: string) =>
      apiFetch(`/conversations/${conversationId}/status`, { method: "POST", body: { status } }),
    onSuccess: () => invalidateConversation(qc, conversationId),
  });
}

// ---------------- Tickets ----------------
import type { Ticket as UITicket, Lead as UILead, KpiMetric } from "@/types";
import { dashboardKpis } from "@/lib/data";

interface TicketDTO {
  id: string; number: number; subject: string; status: string; priority: string;
  channel: string; sentiment?: string | null; tags?: string[];
  requester_id?: string | null; sla_due_at?: string | null; sla_breached: boolean;
  created_at: string; updated_at: string;
}

function mapTicket(t: TicketDTO): UITicket {
  return {
    id: t.id, number: t.number, subject: t.subject,
    status: t.status as UITicket["status"], priority: t.priority as UITicket["priority"],
    channel: t.channel as UITicket["channel"],
    sentiment: (["positive", "neutral", "negative"].includes(t.sentiment ?? "")
      ? t.sentiment : "neutral") as UITicket["sentiment"],
    assignee: null,
    requester: { id: t.requester_id ?? "", name: "Customer", email: "", avatar: "", pastConversations: 0 },
    tags: t.tags ?? [], slaDueAt: t.sla_due_at ?? null,
    createdAt: t.created_at, updatedAt: t.updated_at,
  };
}

export function useTickets() {
  return useQuery<UITicket[] | null>({
    queryKey: ["tickets"],
    queryFn: async () => {
      if (!apiConfigured()) return null;
      const page = await apiFetch<Page<TicketDTO>>("/tickets?limit=100");
      return page.items.map(mapTicket);
    },
  });
}

// ---------------- Leads ----------------
interface LeadDTO {
  id: string; name: string; company?: string | null; email?: string | null;
  stage: string; score: number; value: number; source: string;
  next_action?: string | null; next_action_due?: string | null; created_at: string;
}

function mapLead(l: LeadDTO): UILead {
  return {
    id: l.id, name: l.name, company: l.company ?? "", email: l.email ?? "", avatar: "",
    value: l.value, score: l.score, stage: l.stage as UILead["stage"],
    owner: { id: "", name: "Unassigned", email: "", avatar: "", role: "agent",
             title: "", status: "offline", lastSeen: "" },
    source: l.source as UILead["source"],
    nextAction: l.next_action ?? "—", nextActionDue: l.next_action_due ?? l.created_at,
    createdAt: l.created_at,
  };
}

export function useLeads() {
  return useQuery<UILead[] | null>({
    queryKey: ["leads"],
    queryFn: async () => {
      if (!apiConfigured()) return null;
      const page = await apiFetch<Page<LeadDTO>>("/leads?limit=100");
      return page.items.map(mapLead);
    },
  });
}

// ---------------- Dashboard KPIs (live analytics) ----------------
interface OverviewDTO {
  deflection_rate: number; csat: number; avg_first_response_seconds: number;
  open_conversations: number; tickets_open: number; tickets_resolved: number;
  hot_leads: number; revenue_influenced: number;
}

export function useDashboardKpis() {
  return useQuery<KpiMetric[] | null>({
    queryKey: ["dashboard-kpis"],
    queryFn: async () => {
      if (!apiConfigured()) return null;
      const o = await apiFetch<OverviewDTO>("/analytics/overview?days=30");
      // Map live values onto the existing card shapes (keep sparkline visuals).
      const live: Record<string, number> = {
        deflection: o.deflection_rate, csat: o.csat,
        frt: o.avg_first_response_seconds, revenue: o.revenue_influenced,
        open: o.open_conversations, leads: o.hot_leads, tickets: o.tickets_open,
      };
      const pick = (m: KpiMetric): number => {
        const l = m.label.toLowerCase();
        if (l.includes("deflect")) return live.deflection;
        if (l.includes("csat") || l.includes("satisf")) return live.csat;
        if (l.includes("response")) return live.frt;
        if (l.includes("revenue")) return live.revenue;
        if (l.includes("open") || l.includes("conversation")) return live.open;
        if (l.includes("lead")) return live.leads;
        if (l.includes("ticket")) return live.tickets;
        return m.value;
      };
      return dashboardKpis.map((m) => ({ ...m, value: pick(m), delta: 0 }));
    },
  });
}

// ---------------- AI Agents (config + sandbox) ----------------
export interface AgentDTO {
  id: string; type: string; name: string; system_prompt: string; model: string;
  temperature: number; tone: string; confidence_threshold: number;
  tools: unknown[]; languages: unknown[]; enabled: boolean;
}
export function useAgents() {
  return useQuery<AgentDTO[] | null>({
    queryKey: ["agents"],
    queryFn: async () => (apiConfigured() ? apiFetch<AgentDTO[]>("/agents") : null),
  });
}
export function useUpdateAgent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { id: string; patch: Partial<AgentDTO> }) =>
      apiFetch<AgentDTO>(`/agents/${vars.id}`, { method: "PATCH", body: vars.patch }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["agents"] }),
  });
}
export interface AgentTestResult {
  reply: string; confidence: number; handoff: boolean; intent?: string;
  language?: string; sources?: { title?: string }[]; sentiment?: unknown;
}
export function useTestAgent(agentId: string) {
  return useMutation({
    mutationFn: (message: string) =>
      apiFetch<{ data: AgentTestResult }>(`/agents/${agentId}/test`, {
        method: "POST",
        body: { message },
      }).then((r) => r.data),
  });
}

// ---------------- Audit logs ----------------
interface AuditDTO {
  id: string; actor_name?: string | null; action: string; resource_type: string;
  resource_id?: string | null; detail?: string | null; ip_address?: string | null;
  created_at: string;
}
export interface UIAuditEntry {
  id: string; actor: { name: string; avatar: string }; action: string;
  resource: string; resourceType: string; detail: string; ip: string; createdAt: string;
}
export function useAuditLogs() {
  return useQuery<UIAuditEntry[] | null>({
    queryKey: ["audit-logs"],
    queryFn: async () => {
      if (!apiConfigured()) return null;
      const page = await apiFetch<Page<AuditDTO>>("/audit-logs?limit=100");
      return page.items.map((a) => ({
        id: a.id,
        actor: { name: a.actor_name ?? "System", avatar: "" },
        action: a.action,
        resource: a.resource_id ?? "—",
        resourceType: a.resource_type,
        detail: a.detail ?? "",
        ip: a.ip_address ?? "—",
        createdAt: a.created_at,
      }));
    },
  });
}

// ---------------- Create / action mutations ----------------
export function useCreateTicket() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { subject: string; priority: string; channel?: string }) =>
      apiFetch<TicketDTO>("/tickets", {
        method: "POST",
        body: { subject: vars.subject, priority: vars.priority, channel: vars.channel ?? "web" },
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tickets"] }),
  });
}

export function useUpdateTicket() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { id: string; patch: { status?: string; priority?: string } }) =>
      apiFetch(`/tickets/${vars.id}`, { method: "PATCH", body: vars.patch }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tickets"] }),
  });
}

export function useCreateLead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { name: string; company?: string; email?: string; value?: number }) =>
      apiFetch<LeadDTO>("/leads", {
        method: "POST",
        body: { name: vars.name, company: vars.company, email: vars.email || undefined, value: vars.value ?? 0 },
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["leads"] }),
  });
}

export function useInviteMember() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { email: string; role: string }) =>
      apiFetch("/members/invite", { method: "POST", body: vars }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["members"] }),
  });
}

export function useMarkAllNotificationsRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => apiFetch("/notifications/read-all", { method: "POST" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications-list"] });
      qc.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}

export function useKbCrawl() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (url: string) =>
      apiFetch("/knowledge-base/crawl", { method: "POST", body: { url } }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["kb-docs"] }),
  });
}

// ---------------- Billing ----------------
export interface BillingInfo {
  plan: string;
  limits: { conversations: number; seats: number; channels: string[]; features: string[] };
  usage: { conversations: number; seats: number };
  configured: boolean;
}

export function useBilling() {
  return useQuery<BillingInfo | null>({
    queryKey: ["billing"],
    queryFn: async () => (apiConfigured() ? apiFetch<BillingInfo>("/billing") : null),
  });
}

export function useCheckout() {
  return useMutation({
    mutationFn: (plan: string) =>
      apiFetch<{ url: string }>("/billing/checkout", { method: "POST", body: { plan } }),
    onSuccess: (res) => {
      if (res?.url) window.location.href = res.url;
    },
  });
}

export function useBillingPortal() {
  return useMutation({
    mutationFn: () => apiFetch<{ url: string }>("/billing/portal", { method: "POST" }),
    onSuccess: (res) => {
      if (res?.url) window.location.href = res.url;
    },
  });
}

// ---------------- Knowledge Base ----------------
interface KbDocDTO {
  id: string; title: string; source_type: string; status: string;
  chunk_count: number; size_bytes: number; updated_at: string;
}
function fmtBytes(n: number): string {
  if (!n) return "—";
  const u = ["B", "KB", "MB", "GB"];
  let v = n, i = 0;
  while (v >= 1024 && i < u.length - 1) { v /= 1024; i++; }
  return `${v.toFixed(v < 10 && i > 0 ? 1 : 0)} ${u[i]}`;
}
export interface UIKbDoc {
  id: string; title: string; sourceType: "upload" | "crawl" | "faq";
  status: "ready" | "processing" | "failed"; sizeLabel: string;
  chunks: number; updatedAt: string; progress?: number | null;
}
export function useKbDocuments() {
  return useQuery<UIKbDoc[] | null>({
    queryKey: ["kb-docs"],
    queryFn: async () => {
      if (!apiConfigured()) return null;
      const page = await apiFetch<Page<KbDocDTO>>("/knowledge-base/documents?limit=100");
      return page.items.map((d) => ({
        id: d.id, title: d.title,
        sourceType: (["upload", "crawl", "faq"].includes(d.source_type) ? d.source_type : "upload") as UIKbDoc["sourceType"],
        status: (["ready", "processing", "failed"].includes(d.status) ? d.status : "ready") as UIKbDoc["status"],
        sizeLabel: fmtBytes(d.size_bytes), chunks: d.chunk_count, updatedAt: d.updated_at,
      }));
    },
  });
}
export interface KbChunk { title: string; text: string; score: number }
export function useKbSearch() {
  return useMutation({
    mutationFn: (query: string) =>
      apiFetch<KbChunk[]>("/knowledge-base/search", { method: "POST", body: { query, top_k: 4 } }),
  });
}

// ---------------- Team members ----------------
interface MemberDTO {
  id: string; user_id: string; role: string; status: string;
  name?: string | null; email?: string | null; avatar_url?: string | null; created_at: string;
}
export interface UIMember {
  id: string; name: string; email: string; avatar: string;
  role: string; status: "online" | "away" | "offline"; lastSeen: string;
}
export function useMembers() {
  return useQuery<UIMember[] | null>({
    queryKey: ["members"],
    queryFn: async () => {
      if (!apiConfigured()) return null;
      const rows = await apiFetch<MemberDTO[]>("/members");
      const roleMap: Record<string, string> = {
        super_admin: "owner", admin: "admin", manager: "admin",
        support_agent: "agent", sales_agent: "agent", viewer: "viewer",
      };
      return rows.map((m) => ({
        id: m.id, name: m.name ?? "Member", email: m.email ?? "", avatar: m.avatar_url ?? "",
        role: roleMap[m.role] ?? "agent",
        status: "offline" as const, lastSeen: m.created_at,
      }));
    },
  });
}

// ---------------- Notifications (page list) ----------------
interface NotifDTO {
  id: string; type: string; title: string; body?: string | null; read: boolean; created_at: string;
}
export function useNotificationsList() {
  return useQuery<NotifDTO[] | null>({
    queryKey: ["notifications-list"],
    queryFn: async () => {
      if (!apiConfigured()) return null;
      const page = await apiFetch<Page<NotifDTO>>("/notifications?limit=50");
      return page.items;
    },
  });
}

// ---------------- Analytics overview (raw) ----------------
export interface AnalyticsOverview {
  deflection_rate: number; csat: number; avg_first_response_seconds: number;
  open_conversations: number; tickets_open: number; tickets_resolved: number;
  hot_leads: number; revenue_influenced: number;
}
export function useAnalyticsOverview() {
  return useQuery<AnalyticsOverview | null>({
    queryKey: ["analytics-overview"],
    queryFn: async () =>
      apiConfigured() ? apiFetch<AnalyticsOverview>("/analytics/overview?days=30") : null,
  });
}

export { apiConfigured };
