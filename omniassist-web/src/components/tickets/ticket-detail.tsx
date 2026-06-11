"use client";

import Link from "next/link";
import {
  ChevronLeft,
  Sparkles,
  Send,
  ArrowRightLeft,
  CheckCircle2,
  Tag,
} from "lucide-react";
import type { Ticket } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  TicketStatusPill,
  PriorityPill,
  SentimentPill,
} from "@/components/shared/status-pill";
import { SlaTimer } from "@/components/tickets/sla-timer";
import { ChannelIcon, channelLabel } from "@/components/shared/channel-icon";
import { UserAvatar } from "@/components/shared/user-avatar";
import { MessageBubble } from "@/components/inbox/message-bubble";
import { conversations, users } from "@/lib/data";
import { relativeTime } from "@/lib/utils";
import { useUpdateTicket, apiConfigured } from "@/lib/api-hooks";
import { toast } from "sonner";

export function TicketDetail({ ticket }: { ticket: Ticket }) {
  const conversation = conversations.find((c) => c.contact.id === ticket.requester.id);
  const thread = conversation?.messages ?? [];
  const updateTicket = useUpdateTicket();

  const setStatus = (status: string) => {
    if (!apiConfigured()) {
      toast.success(`Ticket marked ${status}`);
      return;
    }
    updateTicket.mutate(
      { id: ticket.id, patch: { status } },
      {
        onSuccess: () => toast.success(`Ticket marked ${status}`),
        onError: () => toast.error("Could not update the ticket"),
      }
    );
  };

  return (
    <div className="mx-auto max-w-[1400px] p-4 sm:p-6">
      <Link
        href="/tickets"
        className="mb-4 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ChevronLeft className="h-4 w-4" /> Back to tickets
      </Link>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Main */}
        <div className="space-y-6 lg:col-span-2">
          <div className="flex flex-wrap items-center gap-3">
            <ChannelIcon channel={ticket.channel} />
            <h1 className="text-xl font-semibold">{ticket.subject}</h1>
            <span className="text-sm text-muted-foreground">#{ticket.number}</span>
            <TicketStatusPill status={ticket.status} />
          </div>

          {/* AI summary */}
          {ticket.aiSummary && (
            <Card className="border-ai/20 bg-ai/5">
              <CardHeader className="flex-row items-center gap-2 space-y-0 pb-2">
                <Sparkles className="h-4 w-4 text-ai" />
                <CardTitle className="text-sm">AI Summary</CardTitle>
                <Button size="sm" variant="ghost" className="ml-auto h-7 text-xs">Regenerate</Button>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-relaxed text-muted-foreground">{ticket.aiSummary}</p>
              </CardContent>
            </Card>
          )}

          {/* Conversation timeline */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Conversation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {thread.length > 0 ? (
                thread.map((m) => <MessageBubble key={m.id} message={m} />)
              ) : (
                <p className="text-sm text-muted-foreground">No messages on this ticket yet.</p>
              )}
            </CardContent>
          </Card>

          {/* Reply box */}
          <Card>
            <CardContent className="space-y-3 p-4">
              <Textarea placeholder="Write a reply…" rows={3} />
              <div className="flex items-center justify-between">
                <Button size="sm" variant="ai">
                  <Sparkles className="h-4 w-4" /> Draft with AI
                </Button>
                <div className="flex gap-2">
                  <Button size="sm" variant="secondary">Save draft</Button>
                  <Button size="sm" variant="gradient">
                    <Send className="h-4 w-4" /> Send reply
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3"><CardTitle className="text-sm">Properties</CardTitle></CardHeader>
            <CardContent className="space-y-4 text-sm">
              <Field label="Status">
                <Select defaultValue={ticket.status} onValueChange={setStatus}>
                  <SelectTrigger className="h-8 w-36"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="open">Open</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="resolved">Resolved</SelectItem>
                    <SelectItem value="closed">Closed</SelectItem>
                  </SelectContent>
                </Select>
              </Field>
              <Field label="Priority"><PriorityPill priority={ticket.priority} /></Field>
              <Field label="SLA"><SlaTimer dueAt={ticket.slaDueAt} /></Field>
              <Field label="Channel">
                <span className="flex items-center gap-1.5 text-xs">
                  <ChannelIcon channel={ticket.channel} withBg={false} />
                  {channelLabel(ticket.channel)}
                </span>
              </Field>
              <Field label="Sentiment"><SentimentPill sentiment={ticket.sentiment} /></Field>
              <Field label="Created">
                <span className="text-xs text-muted-foreground">{relativeTime(ticket.createdAt)}</span>
              </Field>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3"><CardTitle className="text-sm">Assignee</CardTitle></CardHeader>
            <CardContent>
              <Select defaultValue={ticket.assignee?.id ?? "unassigned"}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="unassigned">Unassigned</SelectItem>
                  {users.map((u) => (
                    <SelectItem key={u.id} value={u.id}>{u.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm">Tags</CardTitle>
              <button className="text-muted-foreground hover:text-foreground"><Tag className="h-4 w-4" /></button>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {ticket.tags.map((tag) => (
                <Badge key={tag} variant="secondary">{tag}</Badge>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3"><CardTitle className="text-sm">Requester</CardTitle></CardHeader>
            <CardContent className="flex items-center gap-3">
              <UserAvatar name={ticket.requester.name} src={ticket.requester.avatar} className="h-10 w-10" />
              <div className="min-w-0">
                <p className="truncate text-sm font-medium">{ticket.requester.name}</p>
                <p className="truncate text-xs text-muted-foreground">{ticket.requester.email}</p>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-2">
            <Button variant="ai" className="w-full" onClick={() => setStatus("pending")}>
              <ArrowRightLeft className="h-4 w-4" /> Hand off to human
            </Button>
            <Button
              variant="success"
              className="w-full"
              loading={updateTicket.isPending}
              onClick={() => setStatus("resolved")}
            >
              <CheckCircle2 className="h-4 w-4" /> Resolve ticket
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">{label}</span>
      {children}
    </div>
  );
}
