"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Search, ArrowUpDown, MoreHorizontal } from "lucide-react";
import type { Ticket, TicketStatus } from "@/types";
import { TicketStatusPill, PriorityPill } from "@/components/shared/status-pill";
import { SlaTimer } from "@/components/tickets/sla-timer";
import { ChannelIcon } from "@/components/shared/channel-icon";
import { UserAvatar } from "@/components/shared/user-avatar";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { relativeTime, cn } from "@/lib/utils";

const tabs: { key: TicketStatus | "all"; label: string }[] = [
  { key: "all", label: "All" },
  { key: "open", label: "Open" },
  { key: "in_progress", label: "In Progress" },
  { key: "pending", label: "Pending" },
  { key: "resolved", label: "Resolved" },
];

export function TicketsTable({ tickets }: { tickets: Ticket[] }) {
  const [tab, setTab] = useState<TicketStatus | "all">("all");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());

  const filtered = tickets.filter((t) => {
    const matchTab = tab === "all" || t.status === tab;
    const matchQuery =
      !query ||
      t.subject.toLowerCase().includes(query.toLowerCase()) ||
      String(t.number).includes(query);
    return matchTab && matchQuery;
  });

  const toggle = (id: string) =>
    setSelected((s) => {
      const next = new Set(s);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex gap-1 overflow-x-auto no-scrollbar rounded-lg border border-border bg-subtle p-1">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={cn(
                "shrink-0 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                tab === t.key
                  ? "bg-card text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div className="relative sm:w-64">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search tickets…"
            className="pl-8"
          />
        </div>
      </div>

      {selected.size > 0 && (
        <div className="flex items-center gap-2 rounded-lg border border-primary/30 bg-primary/5 px-4 py-2 text-sm">
          <span className="font-medium">{selected.size} selected</span>
          <div className="ml-auto flex gap-2">
            <Button size="sm" variant="secondary">Assign</Button>
            <Button size="sm" variant="secondary">Tag</Button>
            <Button size="sm" variant="success">Resolve</Button>
          </div>
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-border bg-card">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[820px] text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs text-muted-foreground">
                <th className="w-10 px-4 py-3">
                  <input
                    type="checkbox"
                    className="accent-[hsl(var(--primary))]"
                    checked={selected.size === filtered.length && filtered.length > 0}
                    onChange={(e) =>
                      setSelected(e.target.checked ? new Set(filtered.map((t) => t.id)) : new Set())
                    }
                  />
                </th>
                <th className="px-2 py-3 font-medium">
                  <span className="inline-flex items-center gap-1">Ticket <ArrowUpDown className="h-3 w-3" /></span>
                </th>
                <th className="px-2 py-3 font-medium">Status</th>
                <th className="px-2 py-3 font-medium">Priority</th>
                <th className="px-2 py-3 font-medium">SLA</th>
                <th className="px-2 py-3 font-medium">Requester</th>
                <th className="px-2 py-3 font-medium">Assignee</th>
                <th className="px-2 py-3 font-medium">Updated</th>
                <th className="w-10 px-2 py-3" />
              </tr>
            </thead>
            <tbody>
              {filtered.map((t, i) => (
                <motion.tr
                  key={t.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.03 }}
                  className="group border-b border-border/60 transition-colors last:border-0 hover:bg-accent/40"
                >
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      className="accent-[hsl(var(--primary))]"
                      checked={selected.has(t.id)}
                      onChange={() => toggle(t.id)}
                    />
                  </td>
                  <td className="px-2 py-3">
                    <Link href={`/tickets/${t.id}`} className="block">
                      <div className="flex items-center gap-2">
                        <ChannelIcon channel={t.channel} />
                        <div className="min-w-0">
                          <p className="truncate font-medium group-hover:text-primary">
                            {t.subject}
                          </p>
                          <p className="text-xs text-muted-foreground">#{t.number}</p>
                        </div>
                      </div>
                    </Link>
                  </td>
                  <td className="px-2 py-3"><TicketStatusPill status={t.status} /></td>
                  <td className="px-2 py-3"><PriorityPill priority={t.priority} /></td>
                  <td className="px-2 py-3"><SlaTimer dueAt={t.slaDueAt} /></td>
                  <td className="px-2 py-3">
                    <div className="flex items-center gap-2">
                      <UserAvatar name={t.requester.name} src={t.requester.avatar} className="h-6 w-6" />
                      <span className="hidden truncate text-xs lg:inline">{t.requester.name}</span>
                    </div>
                  </td>
                  <td className="px-2 py-3">
                    {t.assignee ? (
                      <div className="flex items-center gap-2">
                        <UserAvatar name={t.assignee.name} src={t.assignee.avatar} className="h-6 w-6" />
                        <span className="hidden truncate text-xs lg:inline">{t.assignee.name.split(" ")[0]}</span>
                      </div>
                    ) : (
                      <Badge variant="outline" className="text-[10px]">Unassigned</Badge>
                    )}
                  </td>
                  <td className="px-2 py-3 text-xs text-muted-foreground">{relativeTime(t.updatedAt)}</td>
                  <td className="px-2 py-3">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <button className="text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100">
                          <MoreHorizontal className="h-4 w-4" />
                        </button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem>Assign to me</DropdownMenuItem>
                        <DropdownMenuItem>Change priority</DropdownMenuItem>
                        <DropdownMenuItem>Add tag</DropdownMenuItem>
                        <DropdownMenuItem className="text-success">Resolve</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
        {filtered.length === 0 && (
          <p className="py-12 text-center text-sm text-muted-foreground">No tickets match your filters.</p>
        )}
      </div>
    </div>
  );
}
