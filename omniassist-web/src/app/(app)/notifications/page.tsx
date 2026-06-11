"use client";

import { useEffect, useState } from "react";
import {
  Bell,
  ArrowRightLeft,
  AlarmClock,
  AtSign,
  Target,
  Settings2,
  Star,
  CheckCheck,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { notifications as seed } from "@/lib/data";
import type { NotificationItem } from "@/types";
import { relativeTime, cn } from "@/lib/utils";
import { useNotificationsList, useMarkAllNotificationsRead, apiConfigured } from "@/lib/api-hooks";

const iconFor: Record<NotificationItem["type"], typeof Bell> = {
  handoff: ArrowRightLeft,
  sla: AlarmClock,
  mention: AtSign,
  lead: Target,
  system: Settings2,
  csat: Star,
};
const colorFor: Record<NotificationItem["type"], string> = {
  handoff: "text-info bg-info/10",
  sla: "text-danger bg-danger/10",
  mention: "text-primary bg-primary/10",
  lead: "text-ai bg-ai/10",
  system: "text-muted-foreground bg-secondary",
  csat: "text-warning bg-warning/10",
};

const tabs = ["All", "Unread", "Handoffs", "SLA", "Mentions"] as const;

export default function NotificationsPage() {
  const { data } = useNotificationsList();
  const markAllRead = useMarkAllNotificationsRead();
  const [items, setItems] = useState<NotificationItem[]>(seed);
  const [tab, setTab] = useState<(typeof tabs)[number]>("All");

  useEffect(() => {
    if (!data) return;
    setItems(
      data.map((n) => ({
        id: n.id,
        type: (iconFor[n.type as NotificationItem["type"]] ? n.type : "system") as NotificationItem["type"],
        title: n.title,
        body: n.body ?? "",
        createdAt: n.created_at,
        read: n.read,
      }))
    );
  }, [data]);

  const filtered = items.filter((n) => {
    if (tab === "All") return true;
    if (tab === "Unread") return !n.read;
    if (tab === "Handoffs") return n.type === "handoff";
    if (tab === "SLA") return n.type === "sla";
    if (tab === "Mentions") return n.type === "mention";
    return true;
  });

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-4 sm:p-6">
      <PageHeader title="Notifications" description="Stay on top of handoffs, SLAs and mentions.">
        <Button
          variant="secondary"
          loading={markAllRead.isPending}
          onClick={() => {
            setItems((c) => c.map((n) => ({ ...n, read: true })));
            if (apiConfigured()) markAllRead.mutate();
          }}
        >
          <CheckCheck className="h-4 w-4" /> Mark all read
        </Button>
      </PageHeader>

      <div className="flex gap-1 overflow-x-auto no-scrollbar rounded-lg border border-border bg-subtle p-1">
        {tabs.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              "shrink-0 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
              tab === t ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
            )}
          >
            {t}
          </button>
        ))}
      </div>

      <Card className="overflow-hidden">
        <div className="divide-y divide-border">
          {filtered.map((n) => {
            const Icon = iconFor[n.type];
            return (
              <button
                key={n.id}
                onClick={() => setItems((c) => c.map((x) => (x.id === n.id ? { ...x, read: true } : x)))}
                className={cn("flex w-full gap-3 px-4 py-4 text-left transition-colors hover:bg-accent/40", !n.read && "bg-primary/[0.03]")}
              >
                <span className={cn("flex h-9 w-9 shrink-0 items-center justify-center rounded-lg", colorFor[n.type])}>
                  <Icon className="h-4 w-4" />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="flex items-center gap-2 text-sm font-medium">
                    {n.title}
                    {!n.read && <span className="h-1.5 w-1.5 rounded-full bg-primary" />}
                  </p>
                  <p className="text-sm text-muted-foreground">{n.body}</p>
                  <p className="mt-0.5 text-[11px] text-muted-foreground/70">{relativeTime(n.createdAt)}</p>
                </div>
              </button>
            );
          })}
          {filtered.length === 0 && (
            <p className="py-12 text-center text-sm text-muted-foreground">You&apos;re all caught up 🎉</p>
          )}
        </div>
      </Card>
    </div>
  );
}
