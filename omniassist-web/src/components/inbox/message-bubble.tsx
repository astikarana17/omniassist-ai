"use client";

import { motion } from "framer-motion";
import {
  Sparkles,
  FileText,
  Check,
  CheckCheck,
  Paperclip,
  Play,
} from "lucide-react";
import type { Message } from "@/types";
import { UserAvatar } from "@/components/shared/user-avatar";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

function timeOf(iso: string) {
  return new Date(iso).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function MessageBubble({ message }: { message: Message }) {
  if (message.sender === "system") {
    return (
      <div className="my-2 flex items-center justify-center">
        <span className="rounded-full bg-secondary px-3 py-1 text-[11px] text-muted-foreground">
          {message.content}
        </span>
      </div>
    );
  }

  const isCustomer = message.sender === "contact";
  const isAi = message.sender === "ai";
  const align = isCustomer ? "justify-start" : "justify-end";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={cn("flex gap-2.5", align)}
    >
      {isCustomer && (
        <UserAvatar
          name={message.authorName ?? "Customer"}
          className="mt-1 h-7 w-7"
        />
      )}

      <div className={cn("flex max-w-[78%] flex-col gap-1", isCustomer ? "items-start" : "items-end")}>
        {(isAi || message.sender === "agent") && (
          <span className="flex items-center gap-1 px-1 text-[11px] font-medium">
            {isAi ? (
              <span className="flex items-center gap-1 text-ai">
                <Sparkles className="h-3 w-3" /> OmniAssist AI
              </span>
            ) : (
              <span className="text-muted-foreground">{message.authorName}</span>
            )}
          </span>
        )}

        <div
          className={cn(
            "rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed",
            isCustomer && "rounded-tl-sm border border-border bg-card",
            isAi && "rounded-tr-sm border border-ai/20 bg-ai/5",
            message.sender === "agent" && "rounded-tr-sm bg-primary text-primary-foreground"
          )}
        >
          {message.language && message.language !== "en" && (
            <span className="mb-1 block text-[10px] uppercase tracking-wide opacity-60">
              {message.language}
            </span>
          )}
          <p className="whitespace-pre-wrap">{message.content}</p>

          {message.attachments?.map((att) => (
            <div
              key={att.id}
              className="mt-2 flex items-center gap-2 rounded-lg border border-border/60 bg-background/40 px-2.5 py-2"
            >
              {att.type === "audio" ? (
                <>
                  <button className="flex h-7 w-7 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <Play className="h-3.5 w-3.5" />
                  </button>
                  <div className="h-1 flex-1 rounded-full bg-border">
                    <div className="h-full w-1/3 rounded-full bg-primary" />
                  </div>
                  <span className="text-[11px] text-muted-foreground">
                    {att.durationSec}s
                  </span>
                </>
              ) : (
                <>
                  <Paperclip className="h-3.5 w-3.5 text-muted-foreground" />
                  <span className="truncate text-xs">{att.name}</span>
                  {att.size && (
                    <span className="ml-auto text-[11px] text-muted-foreground">{att.size}</span>
                  )}
                </>
              )}
            </div>
          ))}
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5 px-1">
            {[...new Map(message.sources.map((s) => [s.title, s])).values()].map((s, si) => (
              <Badge key={`${s.title}-${si}`} variant="ai" className="gap-1">
                <FileText className="h-3 w-3" />
                {s.title}
              </Badge>
            ))}
            {message.confidence && (
              <span className="text-[11px] text-muted-foreground">
                {message.confidence}% confidence
              </span>
            )}
          </div>
        )}

        {message.reactions && message.reactions.length > 0 && (
          <div className="flex gap-1 px-1">
            {message.reactions.map((r) => (
              <span
                key={r.emoji}
                className="flex items-center gap-1 rounded-full border border-border bg-card px-1.5 py-0.5 text-[11px]"
              >
                {r.emoji} {r.count}
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center gap-1.5 px-1 text-[10px] text-muted-foreground">
          {timeOf(message.createdAt)}
          {message.sender === "agent" && message.status === "read" && (
            <CheckCheck className="h-3 w-3 text-info" />
          )}
          {message.sender === "agent" && message.status === "delivered" && (
            <Check className="h-3 w-3" />
          )}
        </div>
      </div>

      {!isCustomer && isAi && (
        <span className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-ai">
          <Sparkles className="h-3.5 w-3.5 text-white" />
        </span>
      )}
      {message.sender === "agent" && (
        <UserAvatar
          name={message.authorName ?? "Agent"}
          src={message.authorAvatar}
          className="mt-1 h-7 w-7"
        />
      )}
    </motion.div>
  );
}
