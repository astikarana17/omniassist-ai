"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  X,
  Send,
  FileText,
  Loader2,
  HelpCircle,
  CreditCard,
  ShieldCheck,
  Wand2,
  ArrowUpRight,
} from "lucide-react";
import { useUiStore } from "@/store/ui-store";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAskExpert, apiConfigured } from "@/lib/api-hooks";
import { cn } from "@/lib/utils";

interface CopilotMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  confidence?: number;
}

const suggestions = [
  { label: "What can OmniAssist do?", icon: HelpCircle },
  { label: "Explain the pricing plans", icon: CreditCard },
  { label: "How does human handoff work?", icon: Wand2 },
  { label: "Is customer data secure?", icon: ShieldCheck },
];

let counter = 0;
const nextId = () => `cp_${++counter}`;

export function CopilotPanel() {
  const { copilotOpen, setCopilotOpen } = useUiStore();
  const [messages, setMessages] = useState<CopilotMessage[]>([
    {
      id: nextId(),
      role: "assistant",
      content:
        "Hi! I'm your in-app copilot, grounded in this workspace's knowledge base. Ask me anything about the product, plans, setup, or policies.",
    },
  ]);
  const [input, setInput] = useState("");
  const askExpert = useAskExpert();
  const endRef = useRef<HTMLDivElement>(null);
  const busy = askExpert.isPending;

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  const send = (text: string) => {
    const q = text.trim();
    if (!q || busy) return;
    setMessages((m) => [...m, { id: nextId(), role: "user", content: q }]);
    setInput("");

    if (!apiConfigured()) {
      setMessages((m) => [
        ...m,
        {
          id: nextId(),
          role: "assistant",
          content: "Connect the backend (NEXT_PUBLIC_API_URL) to enable the live copilot.",
        },
      ]);
      return;
    }

    // Thread recent turns so follow-up questions keep context.
    const history = messages
      .slice(-6)
      .map((m) => `${m.role === "user" ? "User" : "Assistant"}: ${m.content}`)
      .join("\n");

    askExpert.mutate(
      { question: q, history },
      {
        onSuccess: (res) => {
          setMessages((m) => [
            ...m,
            {
              id: nextId(),
              role: "assistant",
              content: res.answer,
              sources: [...new Set((res.sources ?? []).map((s) => s.title ?? "Source"))].slice(0, 2),
              confidence: Math.round((res.confidence ?? 0) * 100),
            },
          ]);
        },
        onError: () => {
          setMessages((m) => [
            ...m,
            {
              id: nextId(),
              role: "assistant",
              content: "Sorry — I couldn't reach the AI right now. Please try again.",
            },
          ]);
        },
      }
    );
  };

  return (
    <AnimatePresence>
      {copilotOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setCopilotOpen(false)}
            className="fixed inset-0 z-[1190] bg-black/40 backdrop-blur-sm lg:hidden"
          />
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 320, damping: 34 }}
            className="fixed right-0 top-0 z-[1200] flex h-screen w-full flex-col border-l border-border bg-card shadow-xl sm:w-[400px]"
          >
            <div className="flex items-center justify-between border-b border-border px-4 py-3">
              <div className="flex items-center gap-2">
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-ai">
                  <Sparkles className="h-4 w-4 text-white" />
                </span>
                <div>
                  <p className="text-sm font-semibold">Copilot</p>
                  <p className="flex items-center gap-1 text-[11px] text-muted-foreground">
                    grounded in your knowledge base
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="icon-sm" onClick={() => setCopilotOpen(false)}>
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="flex flex-wrap gap-2 border-b border-border p-3">
              {suggestions.map((s) => (
                <button
                  key={s.label}
                  onClick={() => send(s.label)}
                  disabled={busy}
                  className="inline-flex items-center gap-1.5 rounded-full border border-border-strong bg-subtle px-3 py-1.5 text-xs font-medium transition-colors hover:border-ai/40 hover:text-ai disabled:opacity-50"
                >
                  <s.icon className="h-3.5 w-3.5" />
                  {s.label}
                </button>
              ))}
            </div>

            <div className="flex-1 space-y-4 overflow-y-auto p-4">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={cn(
                    "flex flex-col gap-1.5",
                    m.role === "user" ? "items-end" : "items-start"
                  )}
                >
                  <div
                    className={cn(
                      "max-w-[90%] whitespace-pre-wrap rounded-xl px-3.5 py-2.5 text-sm",
                      m.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "border border-border bg-subtle"
                    )}
                  >
                    {m.content}
                  </div>
                  {m.sources && m.sources.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5">
                      {m.sources.map((s, i) => (
                        <Badge key={`${s}-${i}`} variant="ai" className="gap-1">
                          <FileText className="h-3 w-3" />
                          {s}
                        </Badge>
                      ))}
                      {m.confidence != null && (
                        <span className="text-[11px] text-muted-foreground">
                          confidence {m.confidence}%
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))}
              {busy && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" /> thinking…
                </div>
              )}
              <div ref={endRef} />
            </div>

            <div className="border-t border-border p-3">
              <div className="flex items-end gap-2 rounded-lg border border-border-strong bg-background/50 p-2 focus-within:border-ai/50">
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
                  placeholder="Ask copilot…"
                  className="max-h-24 flex-1 resize-none bg-transparent px-1 py-1 text-sm outline-none placeholder:text-muted-foreground"
                />
                <Button
                  size="icon-sm"
                  variant="ai"
                  onClick={() => send(input)}
                  disabled={!input.trim() || busy}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <p className="mt-2 flex items-center gap-1 px-1 text-[11px] text-muted-foreground">
                <ArrowUpRight className="h-3 w-3" />
                Answers are grounded in your workspace knowledge base.
              </p>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
