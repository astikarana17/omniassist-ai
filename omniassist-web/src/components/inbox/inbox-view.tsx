"use client";

import { useEffect, useState } from "react";
import { Inbox as InboxIcon, Loader2 } from "lucide-react";
import type { Channel, Conversation } from "@/types";
import { ConversationList } from "@/components/inbox/conversation-list";
import { ChatWindow } from "@/components/inbox/chat-window";
import { ContextPanel } from "@/components/inbox/context-panel";
import { EmptyState } from "@/components/shared/empty-state";
import { useConversation } from "@/lib/api-hooks";

export function InboxView({
  conversations,
  channel,
  initialId,
  live = false,
}: {
  conversations: Conversation[];
  channel?: Channel;
  initialId?: string;
  live?: boolean;
}) {
  const pool = channel
    ? conversations.filter((c) => c.channel === channel)
    : conversations;
  const [activeId, setActiveId] = useState<string>(
    initialId && pool.some((c) => c.id === initialId) ? initialId : pool[0]?.id ?? ""
  );
  const fromList = pool.find((c) => c.id === activeId) ?? pool[0];

  // In live mode, fetch the full conversation (with messages) for the active one.
  const { data: detail } = useConversation(live ? fromList?.id : undefined);
  const active = live && detail ? detail : fromList;

  // The inbox renders locale/time-based text (message times, "8s ago") that differs
  // between server and client — render only after mount to avoid hydration mismatch.
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) {
    return (
      <div className="flex h-[calc(100vh-3.5rem)] items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-3.5rem)] overflow-hidden">
      <ConversationList
        conversations={pool}
        activeId={active?.id ?? ""}
        onSelect={setActiveId}
      />
      {active ? (
        <>
          <ChatWindow conversation={active} live={live} />
          <ContextPanel conversation={active} />
        </>
      ) : (
        <div className="flex flex-1 items-center justify-center p-8">
          <EmptyState
            icon={InboxIcon}
            title="No conversations yet"
            description="When customers reach out on this channel, they'll appear here."
          />
        </div>
      )}
    </div>
  );
}
