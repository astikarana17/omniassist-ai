"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import type { Conversation, Channel } from "@/types";
import { ChannelIcon } from "@/components/shared/channel-icon";
import { UserAvatar } from "@/components/shared/user-avatar";
import { ConversationStatusPill } from "@/components/shared/status-pill";
import { Input } from "@/components/ui/input";
import { relativeTime, cn } from "@/lib/utils";

const filters: { key: Channel | "all"; label: string }[] = [
  { key: "all", label: "All" },
  { key: "web", label: "Web" },
  { key: "whatsapp", label: "WhatsApp" },
  { key: "email", label: "Email" },
  { key: "voice", label: "Voice" },
];

export function ConversationList({
  conversations,
  activeId,
  onSelect,
}: {
  conversations: Conversation[];
  activeId: string;
  onSelect: (id: string) => void;
}) {
  const [filter, setFilter] = useState<Channel | "all">("all");
  const [query, setQuery] = useState("");

  const filtered = conversations.filter((c) => {
    const matchChannel = filter === "all" || c.channel === filter;
    const matchQuery =
      !query ||
      c.contact.name.toLowerCase().includes(query.toLowerCase()) ||
      c.subject.toLowerCase().includes(query.toLowerCase());
    return matchChannel && matchQuery;
  });

  return (
    <div className="flex h-full w-full flex-col border-r border-border bg-subtle/30 md:w-80">
      <div className="space-y-3 border-b border-border p-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold">Inbox</h2>
        </div>
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search conversations…"
            className="h-8 pl-8 text-xs"
          />
        </div>
        <div className="flex gap-1 overflow-x-auto no-scrollbar">
          {filters.map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={cn(
                "shrink-0 rounded-full px-2.5 py-1 text-xs font-medium transition-colors",
                filter === f.key
                  ? "bg-primary/15 text-primary"
                  : "text-muted-foreground hover:bg-accent"
              )}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {filtered.map((c) => (
          <button
            key={c.id}
            onClick={() => onSelect(c.id)}
            className={cn(
              "flex w-full gap-3 border-b border-border/60 px-3 py-3 text-left transition-colors hover:bg-accent/40",
              activeId === c.id && "bg-accent/60",
              (c.status === "resolved" || c.status === "closed") && "opacity-60"
            )}
          >
            <div className="relative">
              <UserAvatar name={c.contact.name} src={c.contact.avatar} className="h-9 w-9" />
              <span className="absolute -bottom-1 -right-1">
                <ChannelIcon channel={c.channel} className="h-4 w-4 ring-2 ring-subtle" />
              </span>
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <p className="truncate text-sm font-medium">{c.contact.name}</p>
                <span className="shrink-0 text-[10px] text-muted-foreground">
                  {relativeTime(c.lastMessageAt)}
                </span>
              </div>
              <p className="truncate text-xs font-medium text-muted-foreground">{c.subject}</p>
              <div className="mt-1 flex items-center gap-2">
                <ConversationStatusPill status={c.status} />
                <p className="truncate text-xs text-muted-foreground/70">{c.preview}</p>
              </div>
            </div>
            {c.unread > 0 && (
              <span className="mt-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-primary px-1 text-[10px] font-semibold text-primary-foreground">
                {c.unread}
              </span>
            )}
          </button>
        ))}
        {filtered.length === 0 && (
          <p className="px-3 py-8 text-center text-sm text-muted-foreground">
            No conversations found.
          </p>
        )}
      </div>
    </div>
  );
}
