"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Sparkles,
  Send,
  Save,
  Wand2,
  Wrench,
  Languages,
  Gauge,
  RotateCcw,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TypingIndicator } from "@/components/inbox/typing-indicator";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { useAgents, useUpdateAgent, useTestAgent, apiConfigured } from "@/lib/api-hooks";

interface AgentConfigProps {
  type: "support" | "sales";
  name: string;
  defaultPrompt: string;
  tools: { key: string; label: string; enabled: boolean }[];
  starterReply: string;
}

interface SandboxMsg {
  id: string;
  role: "user" | "ai";
  text: string;
  confidence?: number;
  intent?: string;
  handoff?: boolean;
  sources?: { title?: string }[];
}

export function AgentConfig({ type, name, defaultPrompt, tools, starterReply }: AgentConfigProps) {
  const { data: agents } = useAgents();
  const liveAgent = agents?.find((a) => a.type === type || a.type === `${type}_agent`);
  const updateAgent = useUpdateAgent();
  const testAgent = useTestAgent(liveAgent?.id ?? "");

  const [prompt, setPrompt] = useState(defaultPrompt);
  const [temperature, setTemperature] = useState(0.3);
  const [threshold, setThreshold] = useState(70);
  const [toolState, setToolState] = useState(tools);
  const [messages, setMessages] = useState<SandboxMsg[]>([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  // Hydrate the form from the live agent record once it loads.
  useEffect(() => {
    if (liveAgent) {
      setPrompt(liveAgent.system_prompt || defaultPrompt);
      setTemperature(liveAgent.temperature ?? 0.3);
      setThreshold(liveAgent.confidence_threshold ?? 70);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [liveAgent?.id]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const saveConfig = () => {
    if (!apiConfigured() || !liveAgent) {
      toast.success(`${name} saved`);
      return;
    }
    updateAgent.mutate(
      {
        id: liveAgent.id,
        patch: { system_prompt: prompt, temperature, confidence_threshold: threshold },
      },
      {
        onSuccess: () => toast.success(`${name} saved`),
        onError: () => toast.error("Could not save the agent"),
      }
    );
  };

  const send = (text: string) => {
    const q = text.trim();
    if (!q || typing) return;
    setMessages((m) => [...m, { id: `u${Date.now()}`, role: "user", text: q }]);
    setInput("");
    setTyping(true);

    if (!apiConfigured() || !liveAgent) {
      // Demo fallback when no live agent is available.
      setTimeout(() => {
        setTyping(false);
        setMessages((m) => [
          ...m,
          { id: `a${Date.now()}`, role: "ai", text: starterReply, confidence: 88 },
        ]);
      }, 1200);
      return;
    }

    testAgent.mutate(q, {
      onSettled: () => setTyping(false),
      onSuccess: (r) => {
        setMessages((m) => [
          ...m,
          {
            id: `a${Date.now()}`,
            role: "ai",
            text: r.reply,
            confidence: Math.round((r.confidence ?? 0) * 100),
            intent: r.intent,
            handoff: r.handoff,
            sources: r.sources,
          },
        ]);
      },
      onError: () => {
        setMessages((m) => [
          ...m,
          { id: `a${Date.now()}`, role: "ai", text: "Sorry — the agent couldn't respond. Try again." },
        ]);
      },
    });
  };

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
      {/* Config */}
      <div className="space-y-4 lg:col-span-3">
        <Card>
          <CardHeader className="flex-row items-center gap-2 space-y-0">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-ai">
              <Sparkles className="h-4 w-4 text-white" />
            </span>
            <div>
              <CardTitle className="text-base">{name}</CardTitle>
              <p className="text-xs text-muted-foreground capitalize">{type} agent configuration</p>
            </div>
            <Badge variant="success" className="ml-auto">Active</Badge>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>System prompt</Label>
                <Button size="sm" variant="ghost" className="h-7 text-xs">
                  <Wand2 className="h-3.5 w-3.5" /> Improve with AI
                </Button>
              </div>
              <Textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={7}
                className="font-mono text-xs"
              />
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Model</Label>
                <Select defaultValue="claude-opus">
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="claude-opus">Claude Opus 4.8</SelectItem>
                    <SelectItem value="claude-sonnet">Claude Sonnet 4.6</SelectItem>
                    <SelectItem value="claude-haiku">Claude Haiku 4.5</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Tone</Label>
                <Select defaultValue={type === "sales" ? "persuasive" : "friendly"}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="friendly">Friendly & warm</SelectItem>
                    <SelectItem value="professional">Professional</SelectItem>
                    <SelectItem value="persuasive">Persuasive</SelectItem>
                    <SelectItem value="concise">Concise</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <div className="flex items-center justify-between text-sm">
                  <Label className="flex items-center gap-1.5"><Gauge className="h-3.5 w-3.5" /> Temperature</Label>
                  <span className="font-mono text-xs">{temperature.toFixed(2)}</span>
                </div>
                <input
                  type="range" min={0} max={1} step={0.05} value={temperature}
                  onChange={(e) => setTemperature(Number(e.target.value))}
                  className="mt-2 w-full accent-[hsl(var(--primary))]"
                />
              </div>
              <div>
                <div className="flex items-center justify-between text-sm">
                  <Label>Auto-handoff below confidence</Label>
                  <span className="font-mono text-xs">{threshold}%</span>
                </div>
                <input
                  type="range" min={0} max={100} step={5} value={threshold}
                  onChange={(e) => setThreshold(Number(e.target.value))}
                  className="mt-2 w-full accent-[hsl(var(--primary))]"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-sm"><Wrench className="h-4 w-4" /> Tools</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            {toolState.map((tool) => (
              <div key={tool.key} className="flex items-center justify-between rounded-md px-2 py-2 hover:bg-accent/40">
                <span className="text-sm">{tool.label}</span>
                <Switch
                  checked={tool.enabled}
                  onCheckedChange={(v) =>
                    setToolState((s) => s.map((t) => (t.key === tool.key ? { ...t, enabled: v } : t)))
                  }
                />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-sm"><Languages className="h-4 w-4" /> Languages</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {["English", "Spanish", "German", "French", "Hindi", "Arabic", "Portuguese"].map((lang, i) => (
              <Badge key={lang} variant={i < 5 ? "default" : "outline"}>{lang}</Badge>
            ))}
            <Badge variant="ai" className="gap-1"><Sparkles className="h-3 w-3" /> Auto-detect</Badge>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-2">
          <Button
            variant="secondary"
            onClick={() => {
              setPrompt(liveAgent?.system_prompt || defaultPrompt);
              setTemperature(liveAgent?.temperature ?? 0.3);
              setThreshold(liveAgent?.confidence_threshold ?? 70);
              setToolState(tools);
            }}
          >
            <RotateCcw className="h-4 w-4" /> Reset
          </Button>
          <Button variant="gradient" onClick={saveConfig} loading={updateAgent.isPending}>
            <Save className="h-4 w-4" /> Save changes
          </Button>
        </div>
      </div>

      {/* Sandbox */}
      <div className="lg:col-span-2">
        <Card className="sticky top-20 flex h-[640px] flex-col">
          <CardHeader className="flex-row items-center justify-between space-y-0 border-b border-border pb-3">
            <CardTitle className="flex items-center gap-2 text-sm">
              <Sparkles className="h-4 w-4 text-ai" /> Test Sandbox
            </CardTitle>
            <Badge variant={liveAgent ? "ai" : "secondary"}>
              {liveAgent ? "Live AI" : "Demo"}
            </Badge>
          </CardHeader>
          <CardContent className="flex-1 space-y-3 overflow-y-auto p-4">
            {messages.length === 0 && (
              <div className="flex h-full flex-col items-center justify-center text-center text-sm text-muted-foreground">
                <Sparkles className="mb-2 h-8 w-8 text-ai/40" />
                Chat with your agent to test the prompt & tools live.
              </div>
            )}
            {messages.map((m) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn("flex", m.role === "user" ? "justify-end" : "justify-start")}
              >
                <div
                  className={cn(
                    "max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm",
                    m.role === "user" ? "bg-primary text-primary-foreground" : "border border-ai/20 bg-ai/5"
                  )}
                >
                  <p className="whitespace-pre-wrap">{m.text}</p>
                  {m.role === "ai" && (m.confidence != null || m.intent || m.handoff) && (
                    <div className="mt-1.5 flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
                      {m.confidence != null && <span>confidence {m.confidence}%</span>}
                      {m.intent && <span>· intent: {m.intent}</span>}
                      {m.sources?.[0]?.title && <span>· 📎 {m.sources[0].title}</span>}
                      {m.handoff && (
                        <span className="rounded-full bg-warning/15 px-1.5 py-0.5 font-medium text-warning">
                          → human handoff
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
            {typing && <TypingIndicator />}
            <div ref={endRef} />
          </CardContent>
          <div className="border-t border-border p-3">
            <div className="flex items-end gap-2 rounded-lg border border-border-strong bg-background/50 p-2">
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
                placeholder="Try a customer message…"
                className="max-h-20 flex-1 resize-none bg-transparent px-1 py-1 text-sm outline-none placeholder:text-muted-foreground"
              />
              <Button size="icon-sm" variant="ai" onClick={() => send(input)} disabled={!input.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
