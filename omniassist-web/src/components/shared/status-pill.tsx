import { Badge } from "@/components/ui/badge";
import type {
  ConversationStatus,
  Priority,
  Sentiment,
  TicketStatus,
  LeadStage,
} from "@/types";
import { cn } from "@/lib/utils";

const ticketStatusMap: Record<
  TicketStatus,
  { label: string; variant: React.ComponentProps<typeof Badge>["variant"] }
> = {
  open: { label: "Open", variant: "info" },
  in_progress: { label: "In Progress", variant: "default" },
  pending: { label: "Pending", variant: "warning" },
  resolved: { label: "Resolved", variant: "success" },
  closed: { label: "Closed", variant: "secondary" },
};

const convStatusMap: Record<
  ConversationStatus,
  { label: string; variant: React.ComponentProps<typeof Badge>["variant"] }
> = {
  open: { label: "Open", variant: "info" },
  pending: { label: "Pending", variant: "warning" },
  resolved: { label: "Resolved", variant: "success" },
  snoozed: { label: "Snoozed", variant: "secondary" },
};

const priorityMap: Record<Priority, { label: string; className: string; dot: string }> = {
  low: { label: "Low", className: "text-muted-foreground", dot: "bg-muted-foreground" },
  medium: { label: "Medium", className: "text-info", dot: "bg-info" },
  high: { label: "High", className: "text-warning", dot: "bg-warning" },
  urgent: { label: "Urgent", className: "text-danger", dot: "bg-danger" },
};

const stageMap: Record<LeadStage, { label: string; variant: React.ComponentProps<typeof Badge>["variant"] }> = {
  new: { label: "New", variant: "secondary" },
  qualified: { label: "Qualified", variant: "info" },
  demo: { label: "Demo", variant: "default" },
  proposal: { label: "Proposal", variant: "ai" },
  won: { label: "Won", variant: "success" },
  lost: { label: "Lost", variant: "danger" },
};

export function TicketStatusPill({ status }: { status: TicketStatus }) {
  const s = ticketStatusMap[status];
  return <Badge variant={s.variant}>{s.label}</Badge>;
}

export function ConversationStatusPill({ status }: { status: ConversationStatus }) {
  const s = convStatusMap[status];
  return <Badge variant={s.variant}>{s.label}</Badge>;
}

export function StagePill({ stage }: { stage: LeadStage }) {
  const s = stageMap[stage];
  return <Badge variant={s.variant}>{s.label}</Badge>;
}

export function PriorityPill({ priority }: { priority: Priority }) {
  const p = priorityMap[priority];
  return (
    <span className={cn("inline-flex items-center gap-1.5 text-xs font-medium", p.className)}>
      <span className={cn("h-1.5 w-1.5 rounded-full", p.dot)} />
      {p.label}
    </span>
  );
}

const sentimentMap: Record<Sentiment, { label: string; emoji: string; className: string }> = {
  positive: { label: "Positive", emoji: "😊", className: "text-success" },
  neutral: { label: "Neutral", emoji: "😐", className: "text-muted-foreground" },
  negative: { label: "Negative", emoji: "😠", className: "text-danger" },
};

export function SentimentPill({ sentiment }: { sentiment: Sentiment }) {
  const s = sentimentMap[sentiment];
  return (
    <span className={cn("inline-flex items-center gap-1 text-xs font-medium", s.className)}>
      <span>{s.emoji}</span>
      {s.label}
    </span>
  );
}
