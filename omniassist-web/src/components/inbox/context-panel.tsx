"use client";

import {
  FileText,
  Sparkles,
  Mail,
  Phone,
  Building2,
  History,
  ArrowRightLeft,
} from "lucide-react";
import type { Conversation } from "@/types";
import { UserAvatar } from "@/components/shared/user-avatar";
import { SentimentPill } from "@/components/shared/status-pill";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export function ContextPanel({ conversation }: { conversation: Conversation }) {
  const confidence =
    conversation.messages.find((m) => m.sender === "ai" && m.confidence)?.confidence ?? 0;

  return (
    <div className="hidden w-80 shrink-0 flex-col gap-4 overflow-y-auto border-l border-border bg-subtle/30 p-4 xl:flex">
      {/* Contact */}
      <div className="rounded-xl border border-border bg-card p-4">
        <div className="flex flex-col items-center text-center">
          <UserAvatar name={conversation.contact.name} src={conversation.contact.avatar} className="h-14 w-14" />
          <p className="mt-2 font-semibold">{conversation.contact.name}</p>
          <p className="text-xs text-muted-foreground">{conversation.contact.company}</p>
        </div>
        <div className="mt-4 space-y-2 text-sm">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Mail className="h-3.5 w-3.5" />
            <span className="truncate">{conversation.contact.email}</span>
          </div>
          {conversation.contact.phone && (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Phone className="h-3.5 w-3.5" />
              <span>{conversation.contact.phone}</span>
            </div>
          )}
          <div className="flex items-center gap-2 text-muted-foreground">
            <Building2 className="h-3.5 w-3.5" />
            <span>{conversation.language} speaker</span>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <History className="h-3.5 w-3.5" />
            <span>{conversation.contact.pastConversations} past conversations</span>
          </div>
        </div>
      </div>

      {/* AI summary */}
      <div className="rounded-xl border border-ai/20 bg-ai/5 p-4">
        <div className="mb-2 flex items-center gap-1.5 text-sm font-medium text-ai">
          <Sparkles className="h-4 w-4" /> AI Summary
        </div>
        <p className="text-xs leading-relaxed text-muted-foreground">
          Customer raised an issue about &ldquo;{conversation.subject}&rdquo;. AI engaged,
          provided a grounded answer, and the conversation is now {conversation.status}.
        </p>
      </div>

      {/* Sentiment + confidence */}
      <div className="rounded-xl border border-border bg-card p-4">
        <p className="mb-3 text-xs font-medium text-muted-foreground">Signals</p>
        <div className="flex items-center justify-between">
          <span className="text-sm">Sentiment</span>
          <SentimentPill sentiment={conversation.sentiment} />
        </div>
        <div className="mt-3">
          <div className="flex items-center justify-between text-sm">
            <span>AI confidence</span>
            <span className="font-mono text-xs">{confidence}%</span>
          </div>
          <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-secondary">
            <div
              className="h-full rounded-full bg-gradient-brand transition-all"
              style={{ width: `${confidence}%` }}
            />
          </div>
        </div>
      </div>

      {/* KB sources */}
      <div className="rounded-xl border border-border bg-card p-4">
        <p className="mb-2 text-xs font-medium text-muted-foreground">Matched knowledge</p>
        <div className="space-y-2">
          {["Billing & Refund Policy", "Shipping FAQ"].map((s) => (
            <button
              key={s}
              className="flex w-full items-center gap-2 rounded-md border border-border p-2 text-left text-xs transition-colors hover:border-ai/40"
            >
              <FileText className="h-3.5 w-3.5 text-ai" />
              <span className="truncate">{s}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="space-y-2">
        <Button variant="ai" className="w-full">
          <ArrowRightLeft className="h-4 w-4" /> Hand off to human
        </Button>
        <div className="flex gap-2">
          <Badge variant="outline" className="flex-1 justify-center py-1.5">Snooze</Badge>
          <Badge variant="success" className="flex-1 justify-center py-1.5">Resolve</Badge>
        </div>
      </div>
    </div>
  );
}
