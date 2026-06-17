"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Send, Sparkles, User, ShieldAlert, Loader2 } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Illustration } from "@/components/shared/illustrated-empty";
import { MarkdownMessage } from "@/components/shared/markdown-message";
import { Button } from "@/components/ui/button";
import { useHealthChat, apiConfigured, type HealthChatMsg } from "@/lib/api-hooks";
import { toast } from "sonner";

const SUGGESTIONS = [
  "What is a normal blood sugar level?",
  "Explain what Metformin does",
  "What do high cholesterol results mean?",
  "Tips for a mild headache?",
];

const DISCLAIMER =
  "AI Health Assistant gives general information only — not a diagnosis. For emergencies, contact local emergency services. Always consult a doctor for personal advice.";

export default function HealthAssistantPage() {
  const [messages, setMessages] = useState<HealthChatMsg[]>([]);
  const [input, setInput] = useState("");
  const chat = useHealthChat();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, chat.isPending]);

  const send = (text: string) => {
    const content = text.trim();
    if (!content || chat.isPending) return;
    if (!apiConfigured()) {
      toast.error("Connect the backend (NEXT_PUBLIC_API_URL) to chat.");
      return;
    }
    const next = [...messages, { role: "user" as const, content }];
    setMessages(next);
    setInput("");
    chat.mutate(next, {
      onSuccess: (res) =>
        setMessages((m) => [...m, { role: "assistant", content: res.reply }]),
      onError: (e: Error) => {
        toast.error(e.message || "Could not get a reply");
        setMessages((m) => m.slice(0, -1)); // roll back the user msg on failure
        setInput(content);
      },
    });
  };

  return (
    <div className="mx-auto flex h-[calc(100vh-5.5rem)] max-w-3xl flex-col p-4 sm:p-6">
      <PageHeader
        title="AI Health Assistant"
        description="Ask about medicines, symptoms or lab results — explained simply. Not a diagnosis."
      />

      {/* Chat surface */}
      <div className="mt-4 flex flex-1 flex-col overflow-hidden rounded-2xl border border-border bg-card">
        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4 sm:p-6">
          {messages.length === 0 && (
            <div className="flex min-h-full flex-col items-center justify-center py-6 text-center">
              <Illustration src="/illustrations/assistant.svg" size="sm" />
              <h3 className="mt-3 text-lg font-semibold">How can I help with your health today?</h3>
              <p className="mt-1 max-w-sm text-sm text-muted-foreground">
                I explain medicines, symptoms and reports in simple language. I can&apos;t diagnose — always consult your doctor.
              </p>
              <div className="mt-4 grid w-full max-w-md grid-cols-1 gap-2 sm:grid-cols-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="rounded-xl border border-border bg-subtle/50 px-3 py-2.5 text-left text-sm transition-colors hover:border-ai/40 hover:bg-ai/5"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, i) => (
            <Bubble key={i} role={m.role} content={m.content} />
          ))}

          {chat.isPending && (
            <div className="flex items-center gap-3">
              <Avatar role="assistant" />
              <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm bg-secondary px-4 py-3">
                <span className="h-2 w-2 animate-pulse-dot rounded-full bg-ai" />
                <span className="h-2 w-2 animate-pulse-dot rounded-full bg-ai [animation-delay:0.2s]" />
                <span className="h-2 w-2 animate-pulse-dot rounded-full bg-ai [animation-delay:0.4s]" />
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-border p-3 sm:p-4">
          <div className="flex items-end gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send(input);
                }
              }}
              rows={1}
              placeholder="Ask about a medicine, symptom or report…"
              className="max-h-32 flex-1 resize-none rounded-xl border border-input bg-background px-3.5 py-2.5 text-sm outline-none ring-ring transition-shadow placeholder:text-muted-foreground focus:ring-2"
            />
            <Button
              size="icon"
              variant="gradient"
              className="h-11 w-11 shrink-0"
              onClick={() => send(input)}
              disabled={chat.isPending || !input.trim()}
            >
              {chat.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </div>
          <p className="mt-2 flex items-center gap-1.5 text-[11px] text-muted-foreground">
            <ShieldAlert className="h-3 w-3" /> {DISCLAIMER}
          </p>
        </div>
      </div>
    </div>
  );
}

function Avatar({ role }: { role: "user" | "assistant" }) {
  return role === "assistant" ? (
    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-ai">
      <Sparkles className="h-4 w-4 text-white" />
    </span>
  ) : (
    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary">
      <User className="h-4 w-4" />
    </span>
  );
}

function Bubble({ role, content }: { role: "user" | "assistant"; content: string }) {
  const isUser = role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : ""}`}
    >
      <Avatar role={role} />
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${
          isUser
            ? "whitespace-pre-wrap rounded-tr-sm bg-primary text-primary-foreground"
            : "rounded-tl-sm bg-secondary text-secondary-foreground"
        }`}
      >
        {isUser ? content : <MarkdownMessage content={content} />}
      </div>
    </motion.div>
  );
}
