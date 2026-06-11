"use client";

import { useState } from "react";
import {
  Bell,
  ArrowRightLeft,
  AlarmClock,
  AtSign,
  Target,
  Settings2,
  Star,
} from "lucide-react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { notifications as seed } from "@/lib/data";
import type { NotificationItem } from "@/types";
import { relativeTime, cn } from "@/lib/utils";

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

export function NotificationsPopover() {
  const [items, setItems] = useState<NotificationItem[]>(seed);
  const unread = items.filter((n) => !n.read).length;

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative" aria-label="Notifications">
          <Bell className="h-4 w-4" />
          {unread > 0 && (
            <span className="absolute right-1.5 top-1.5 flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-danger opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-danger" />
            </span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-[380px] p-0">
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <p className="text-sm font-semibold">Notifications</p>
          <button
            onClick={() => setItems((cur) => cur.map((n) => ({ ...n, read: true })))}
            className="text-xs text-primary hover:underline"
          >
            Mark all read
          </button>
        </div>
        <ScrollArea className="max-h-[420px]">
          <div className="divide-y divide-border">
            {items.map((n) => {
              const Icon = iconFor[n.type];
              return (
                <button
                  key={n.id}
                  onClick={() =>
                    setItems((cur) =>
                      cur.map((x) => (x.id === n.id ? { ...x, read: true } : x))
                    )
                  }
                  className="flex w-full gap-3 px-4 py-3 text-left transition-colors hover:bg-accent/50"
                >
                  <span
                    className={cn(
                      "mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg",
                      colorFor[n.type]
                    )}
                  >
                    <Icon className="h-4 w-4" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="flex items-center gap-2 text-sm font-medium">
                      {n.title}
                      {!n.read && (
                        <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                      )}
                    </p>
                    <p className="truncate text-xs text-muted-foreground">
                      {n.body}
                    </p>
                    <p className="mt-0.5 text-[11px] text-muted-foreground/70">
                      {relativeTime(n.createdAt)}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </ScrollArea>
        <div className="border-t border-border p-2">
          <Button variant="ghost" className="w-full text-sm" size="sm">
            View all notifications
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  );
}
