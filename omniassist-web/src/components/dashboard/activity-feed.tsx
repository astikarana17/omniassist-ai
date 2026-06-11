"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  CheckCircle2,
  ArrowRightLeft,
  Target,
  UserPlus,
  Ticket as TicketIcon,
  Star,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChannelIcon } from "@/components/shared/channel-icon";
import { activityFeed } from "@/lib/data";
import type { ActivityEvent } from "@/types";
import { relativeTime, cn } from "@/lib/utils";

const iconFor: Record<ActivityEvent["type"], { icon: typeof CheckCircle2; color: string }> = {
  ai_resolved: { icon: CheckCircle2, color: "text-success bg-success/10" },
  handoff: { icon: ArrowRightLeft, color: "text-info bg-info/10" },
  lead: { icon: Target, color: "text-ai bg-ai/10" },
  joined: { icon: UserPlus, color: "text-primary bg-primary/10" },
  ticket: { icon: TicketIcon, color: "text-warning bg-warning/10" },
  csat: { icon: Star, color: "text-warning bg-warning/10" },
};

const liveCandidates: ActivityEvent[] = [
  { id: "live1", type: "ai_resolved", text: "AI resolved #1045 — Password reset", createdAt: new Date().toISOString(), channel: "web" },
  { id: "live2", type: "lead", text: "New lead captured: Nimbus Cloud", createdAt: new Date().toISOString() },
  { id: "live3", type: "csat", text: "CSAT 5★ on WhatsApp conversation", createdAt: new Date().toISOString(), channel: "whatsapp" },
  { id: "live4", type: "handoff", text: "Handoff resolved by Arjun K.", createdAt: new Date().toISOString(), channel: "email" },
];

export function ActivityFeed() {
  const [events, setEvents] = useState<ActivityEvent[]>(activityFeed);

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      const base = liveCandidates[i % liveCandidates.length];
      const next: ActivityEvent = {
        ...base,
        id: `live-${Date.now()}`,
        createdAt: new Date().toISOString(),
      };
      setEvents((cur) => [next, ...cur].slice(0, 9));
      i += 1;
    }, 6000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="flex h-full flex-col">
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle className="text-base">Live Activity</CardTitle>
        <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-success" />
          </span>
          Live
        </span>
      </CardHeader>
      <CardContent className="flex-1">
        <div className="space-y-1">
          <AnimatePresence initial={false}>
            {events.map((e) => {
              const cfg = iconFor[e.type];
              const Icon = cfg.icon;
              return (
                <motion.div
                  key={e.id}
                  layout
                  initial={{ opacity: 0, y: -8, height: 0 }}
                  animate={{ opacity: 1, y: 0, height: "auto" }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="flex items-center gap-3 rounded-md px-2 py-2 transition-colors hover:bg-accent/40"
                >
                  <span className={cn("flex h-7 w-7 shrink-0 items-center justify-center rounded-lg", cfg.color)}>
                    <Icon className="h-3.5 w-3.5" />
                  </span>
                  <p className="min-w-0 flex-1 truncate text-sm">{e.text}</p>
                  {e.channel && <ChannelIcon channel={e.channel} withBg={false} className="text-muted-foreground" />}
                  <span className="shrink-0 text-[11px] tabular-nums text-muted-foreground">
                    {relativeTime(e.createdAt)}
                  </span>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      </CardContent>
    </Card>
  );
}
