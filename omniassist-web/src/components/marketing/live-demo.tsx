"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Loader2, Send, Sparkles } from "lucide-react";

/**
 * Live, no-login demo chat on the landing page — talks to the REAL Health
 * Assistant brain via the public /health-demo/chat endpoint, so visitors get
 * genuine medical answers (not a canned reply) before signing up.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

interface DemoMsg {
  id: string;
  who: "customer" | "ai";
  text: string;
}

const SUGGESTIONS = [
  "What can this Health Copilot do?",
  "How does prescription analysis work?",
  "Can it read lab reports?",
  "Is my health data private?",
];

let nextId = 0;
const mid = () => `dm_${++nextId}`;

export function LiveDemo() {
  const [messages, setMessages] = useState<DemoMsg[]>([
    {
      id: mid(),
      who: "ai",
      text: "Hi! I'm your Healthcare AI Copilot. Ask me about the product or how it helps you understand your care. 👋",
    },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  const ask = async (text: string) => {
    const q = text.trim();
    if (!q || busy) return;
    setInput("");
    const history = [...messages, { id: mid(), who: "customer" as const, text: q }];
    setMessages(history);
    setBusy(true);
    try {
      // send the running transcript to the real Health Assistant brain
      const payloadMessages = history.map((m) => ({
        role: m.who === "ai" ? "assistant" : "user",
        content: m.text,
      }));
      const res = await fetch(`${API_URL}/api/v1/public/health-demo/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: payloadMessages }),
      });
      const json = await res.json();
      const reply = json?.data?.reply ?? json?.reply;
      setMessages((m) => [
        ...m,
        {
          id: mid(),
          who: "ai",
          text: reply ?? "Sorry, I couldn't generate a response. Please try rephrasing.",
        },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          id: mid(),
          who: "ai",
          text: "Hmm, I couldn't reach the demo server. Try again in a moment!",
        },
      ]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="glass overflow-hidden rounded-2xl border border-border-strong p-2 text-left shadow-xl">
      <div className="rounded-xl border border-border bg-card">
        {/* Browser chrome */}
        <div className="flex items-center gap-1.5 border-b border-border px-4 py-3">
          <span className="h-3 w-3 rounded-full bg-danger/60" />
          <span className="h-3 w-3 rounded-full bg-warning/60" />
          <span className="h-3 w-3 rounded-full bg-success/60" />
          <span className="ml-3 text-xs text-muted-foreground">
            Healthcare AI Copilot
          </span>
          <span className="ml-auto inline-flex items-center gap-1 rounded-full bg-ai/10 px-2 py-0.5 text-[10px] font-semibold text-ai">
            <span className="relative flex h-1.5 w-1.5">
              <span className="absolute h-full w-full animate-ping rounded-full bg-ai opacity-70" />
              <span className="relative h-1.5 w-1.5 rounded-full bg-ai" />
            </span>
            LIVE AI — try it
          </span>
        </div>

        {/* Messages */}
        <div ref={scrollRef} className="h-72 space-y-3 overflow-y-auto p-5">
          {messages.map((m) => (
            <motion.div
              key={m.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${m.who === "ai" ? "justify-start" : "justify-end"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${
                  m.who === "ai"
                    ? "border border-border bg-subtle"
                    : "bg-primary text-primary-foreground"
                }`}
              >
                {m.who === "ai" && (
                  <span className="mb-1 flex items-center gap-1 text-xs font-medium text-ai">
                    <Sparkles className="h-3 w-3" /> Health Copilot
                  </span>
                )}
                <p className="whitespace-pre-wrap">{m.text}</p>
              </div>
            </motion.div>
          ))}
          {busy && (
            <div className="flex justify-start">
              <div className="flex items-center gap-2 rounded-2xl border border-border bg-subtle px-4 py-2.5 text-sm text-muted-foreground">
                <Loader2 className="h-3.5 w-3.5 animate-spin" /> thinking…
              </div>
            </div>
          )}
        </div>

        {/* Suggestions */}
        <div className="flex flex-wrap gap-2 px-5 pb-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => ask(s)}
              disabled={busy}
              className="rounded-full border border-border-strong bg-subtle px-3 py-1 text-xs transition-colors hover:border-ai/40 hover:text-ai disabled:opacity-50"
            >
              {s}
            </button>
          ))}
        </div>

        {/* Input */}
        <div className="border-t border-border p-3">
          <div className="flex items-center gap-2 rounded-xl border border-border-strong bg-background/50 px-3 py-1.5 focus-within:border-ai/50">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && ask(input)}
              placeholder="Ask the Health Copilot anything…"
              className="flex-1 bg-transparent py-1.5 text-sm outline-none placeholder:text-muted-foreground"
            />
            <button
              onClick={() => ask(input)}
              disabled={!input.trim() || busy}
              className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-ai text-white transition-opacity disabled:opacity-40"
              aria-label="Send"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
