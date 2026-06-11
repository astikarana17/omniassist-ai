"use client";

import { useRef, useState } from "react";
import { Bot, Send, Sparkles, User, FileText } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { expertCanned } from "@/lib/ops-data";
import { apiConfigured, useAskExpert } from "@/lib/api-hooks";
import { cn } from "@/lib/utils";
import type { ExpertSource } from "@/types";

interface ChatMsg {
  id: string;
  role: "user" | "expert";
  text: string;
  confidence?: number;
  sources?: ExpertSource[];
}

const SUGGESTIONS = [
  "What does OmniAssist do?",
  "What's included in the Growth plan?",
  "How do you compare to competitors?",
  "Do you support SSO?",
];

let counter = 0;
const nextId = () => `m_${++counter}`;

export default function ProductExpertPage() {
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const askExpert = useAskExpert();

  async function ask(question: string) {
    const q = question.trim();
    if (!q || thinking) return;
    setMessages((m) => [...m, { id: nextId(), role: "user", text: q }]);
    setInput("");
    setThinking(true);

    // Live mode: call the Product Expert agent on the backend, passing the recent
    // turns so it remembers the conversation (memory).
    if (apiConfigured()) {
      try {
        const history = messages
          .slice(-6)
          .map((mm) => `${mm.role === "user" ? "Customer" : "Expert"}: ${mm.text}`)
          .join("\n");
        const res = await askExpert.mutateAsync({ question: q, history });
        setMessages((m) => [
          ...m,
          {
            id: nextId(),
            role: "expert",
            text: res.answer,
            confidence: res.confidence,
            sources: (res.sources ?? []).map((s) => ({
              title: s.title ?? "Source",
              kind: "kb" as const,
            })),
          },
        ]);
      } catch {
        setMessages((m) => [
          ...m,
          { id: nextId(), role: "expert", text: "Sorry — I couldn't reach the Product Expert just now." },
        ]);
      } finally {
        setThinking(false);
      }
      return;
    }

    // Demo mode: canned answers.
    const canned = /pric|cost|plan|\$/i.test(q) ? expertCanned.pricing : expertCanned.default;
    timer.current = setTimeout(() => {
      setMessages((m) => [
        ...m,
        {
          id: nextId(),
          role: "expert",
          text: canned.answer,
          confidence: canned.confidence,
          sources: canned.sources,
        },
      ]);
      setThinking(false);
    }, 650);
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-4rem)] max-w-[860px] flex-col gap-4 p-4 sm:p-6">
      <PageHeader
        title="AI Product Expert"
        description="Ask anything about the company — grounded in products, pricing, FAQs & policies."
      />

      <Card className="flex min-h-0 flex-1 flex-col overflow-hidden">
        <div className="flex-1 space-y-4 overflow-y-auto p-4">
          {messages.length === 0 && (
            <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-ai/10 text-ai">
                <Bot className="h-6 w-6" />
              </div>
              <div className="space-y-1">
                <p className="font-medium">Your AI Product Expert</p>
                <p className="text-sm text-muted-foreground">Ask about pricing, features, integrations or competitors.</p>
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => ask(s)}
                    className="rounded-full border border-border-strong px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-accent/50 hover:text-foreground"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m) => (
            <div key={m.id} className={cn("flex gap-3", m.role === "user" && "flex-row-reverse")}>
              <div
                className={cn(
                  "flex h-8 w-8 shrink-0 items-center justify-center rounded-md",
                  m.role === "expert" ? "bg-ai/10 text-ai" : "bg-secondary text-secondary-foreground"
                )}
              >
                {m.role === "expert" ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
              </div>
              <div className={cn("max-w-[80%] space-y-2", m.role === "user" && "items-end text-right")}>
                <div
                  className={cn(
                    "inline-block rounded-2xl px-3.5 py-2 text-sm",
                    m.role === "expert"
                      ? "bg-subtle text-foreground"
                      : "bg-primary text-primary-foreground"
                  )}
                >
                  {m.text}
                </div>
                {m.role === "expert" && (
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="ai" className="gap-1">
                      <Sparkles className="h-3 w-3" />
                      {Math.round((m.confidence ?? 0) * 100)}% confident
                    </Badge>
                    {m.sources?.map((s, si) => (
                      <Badge key={`${s.title}-${si}`} variant="outline" className="gap-1 font-normal">
                        <FileText className="h-3 w-3" />
                        {s.title}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {thinking && (
            <div className="flex gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-ai/10 text-ai">
                <Bot className="h-4 w-4" />
              </div>
              <div className="flex items-center gap-1 rounded-2xl bg-subtle px-3.5 py-3">
                <Dot /> <Dot delay={0.15} /> <Dot delay={0.3} />
              </div>
            </div>
          )}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            ask(input);
          }}
          className="flex items-center gap-2 border-t border-border p-3"
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask the Product Expert…"
            className="flex-1"
          />
          <Button type="submit" disabled={!input.trim() || thinking}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </Card>
    </div>
  );
}

function Dot({ delay = 0 }: { delay?: number }) {
  return (
    <span
      className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground/60"
      style={{ animationDelay: `${delay}s` }}
    />
  );
}
