"use client";

import { useEffect, useRef, useState } from "react";
import {
  ArrowRightLeft,
  CheckCircle2,
  User as UserIcon,
  Sparkles,
} from "lucide-react";
import type { Conversation, Message } from "@/types";
import { MessageBubble } from "@/components/inbox/message-bubble";
import { TypingIndicator } from "@/components/inbox/typing-indicator";
import { ChatComposer } from "@/components/inbox/chat-composer";
import { UserAvatar } from "@/components/shared/user-avatar";
import { ChannelIcon, channelLabel } from "@/components/shared/channel-icon";
import { ConversationStatusPill } from "@/components/shared/status-pill";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  useAgentReply,
  useConversationStatus,
  useCustomerMessage,
  useHandoff,
} from "@/lib/api-hooks";

type SendMode = "agent" | "customer";

export function ChatWindow({
  conversation,
  live = false,
}: {
  conversation: Conversation;
  live?: boolean;
}) {
  const [messages, setMessages] = useState<Message[]>(conversation.messages);
  const [typing, setTyping] = useState(false);
  const [mode, setMode] = useState<SendMode>("agent");
  const scrollRef = useRef<HTMLDivElement>(null);

  const customerMsg = useCustomerMessage(conversation.id);
  const agentReply = useAgentReply(conversation.id);
  const handoff = useHandoff(conversation.id);
  const status = useConversationStatus(conversation.id);

  // When the AI hands off (status pending), the human agent (you) should take over.
  const needsHuman = conversation.status === "pending";

  useEffect(() => {
    setMessages(conversation.messages);
  }, [conversation]);

  useEffect(() => {
    if (needsHuman) setMode("agent"); // auto-switch to human reply on handoff
  }, [needsHuman]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, typing]);

  const send = (text: string) => {
    if (live) {
      if (mode === "agent") {
        // Human agent reply — shows as an agent message, no AI reply.
        setMessages((m) => [
          ...m,
          {
            id: `tmp-${Date.now()}`,
            conversationId: conversation.id,
            sender: "agent",
            authorName: "You",
            content: text,
            createdAt: new Date().toISOString(),
            status: "delivered",
          },
        ]);
        agentReply.mutate(text);
        return;
      }
      // Customer test — inbound message; the AI agent replies (KB-grounded).
      setMessages((m) => [
        ...m,
        {
          id: `tmp-${Date.now()}`,
          conversationId: conversation.id,
          sender: "contact",
          content: text,
          createdAt: new Date().toISOString(),
        },
      ]);
      setTyping(true);
      customerMsg.mutate(text, { onSettled: () => setTyping(false) });
      return;
    }

    // Demo mode: simulated local reply.
    const agentMsg: Message = {
      id: `m-${Date.now()}`,
      conversationId: conversation.id,
      sender: "agent",
      authorName: "Priya Rao",
      content: text,
      createdAt: new Date().toISOString(),
      status: "delivered",
    };
    setMessages((m) => [...m, agentMsg]);
    setTyping(true);
    setTimeout(() => {
      setTyping(false);
      setMessages((m) => [
        ...m,
        {
          id: `ai-${Date.now()}`,
          conversationId: conversation.id,
          sender: "ai",
          content:
            "Got it — I've noted that and updated the customer's record. Anything else?",
          createdAt: new Date().toISOString(),
          confidence: 89,
        },
      ]);
    }, 1800);
  };

  return (
    <div className="flex h-full min-w-0 flex-1 flex-col">
      {/* Header */}
      <div className="flex items-center gap-3 border-b border-border bg-background/60 px-4 py-3 backdrop-blur">
        <UserAvatar name={conversation.contact.name} src={conversation.contact.avatar} status="online" className="h-9 w-9" />
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <p className="truncate text-sm font-semibold">{conversation.contact.name}</p>
            <ConversationStatusPill status={conversation.status} />
          </div>
          <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <ChannelIcon channel={conversation.channel} withBg={false} />
            {channelLabel(conversation.channel)} · {conversation.language}
          </p>
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="secondary"
            size="sm"
            className="hidden sm:inline-flex"
            disabled={!live || handoff.isPending}
            onClick={() => live && handoff.mutate()}
          >
            <ArrowRightLeft className="h-4 w-4" /> {handoff.isPending ? "…" : "Handoff"}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="hidden text-success sm:inline-flex"
            disabled={!live || status.isPending}
            onClick={() => live && status.mutate("resolved")}
          >
            <CheckCircle2 className="h-4 w-4" /> Resolve
          </Button>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto bg-gradient-mesh/[0.02] p-4">
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {typing && (
          <div className="flex justify-start pl-9">
            <TypingIndicator />
          </div>
        )}
      </div>

      {/* Handoff banner — a human (you) needs to take over */}
      {live && needsHuman && (
        <div className="flex items-center gap-2 border-t border-warning/30 bg-warning/10 px-3 py-2 text-xs text-warning">
          <span className="text-base leading-none">🙋</span>
          <span>
            Customer requested a human — <b>you’re the agent now</b>. Reply below to take over,
            or hit <b>Resolve</b> when done.
          </span>
        </div>
      )}

      {/* Send-as toggle (live only) */}
      {live && (
        <div className="flex items-center gap-2 border-t border-border bg-background/40 px-3 pt-2 text-xs">
          <span className="text-muted-foreground">Send as:</span>
          <button
            onClick={() => setMode("agent")}
            className={cn(
              "flex items-center gap-1 rounded-full px-2.5 py-1 transition-colors",
              mode === "agent" ? "bg-primary/15 text-primary" : "text-muted-foreground hover:bg-accent"
            )}
          >
            <UserIcon className="h-3 w-3" /> Agent (human)
          </button>
          <button
            onClick={() => setMode("customer")}
            className={cn(
              "flex items-center gap-1 rounded-full px-2.5 py-1 transition-colors",
              mode === "customer" ? "bg-ai/15 text-ai" : "text-muted-foreground hover:bg-accent"
            )}
          >
            <Sparkles className="h-3 w-3" /> Customer (test AI)
          </button>
        </div>
      )}

      {/* Composer */}
      <ChatComposer onSend={send} />
    </div>
  );
}
