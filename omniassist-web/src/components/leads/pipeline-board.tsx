"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Plus, MoreHorizontal, Calendar } from "lucide-react";
import { toast } from "sonner";
import type { Lead, LeadStage } from "@/types";
import { UserAvatar } from "@/components/shared/user-avatar";
import { ChannelIcon } from "@/components/shared/channel-icon";
import { LeadScore } from "@/components/leads/lead-score";
import { formatCurrency, relativeTime, cn } from "@/lib/utils";

const columns: { key: LeadStage; label: string; accent: string }[] = [
  { key: "new", label: "New", accent: "bg-muted-foreground" },
  { key: "qualified", label: "Qualified", accent: "bg-info" },
  { key: "demo", label: "Demo", accent: "bg-primary" },
  { key: "proposal", label: "Proposal", accent: "bg-ai" },
  { key: "won", label: "Won", accent: "bg-success" },
  { key: "lost", label: "Lost", accent: "bg-danger" },
];

export function PipelineBoard({ initialLeads }: { initialLeads: Lead[] }) {
  const [leads, setLeads] = useState(initialLeads);
  const [dragId, setDragId] = useState<string | null>(null);
  const [overCol, setOverCol] = useState<LeadStage | null>(null);

  const move = (id: string, stage: LeadStage) => {
    setLeads((cur) => {
      const lead = cur.find((l) => l.id === id);
      if (lead && lead.stage !== stage) {
        toast.success(`${lead.name} moved to ${columns.find((c) => c.key === stage)?.label}`);
      }
      return cur.map((l) => (l.id === id ? { ...l, stage } : l));
    });
  };

  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {columns.map((col) => {
        const items = leads.filter((l) => l.stage === col.key);
        const total = items.reduce((s, l) => s + l.value, 0);
        return (
          <div
            key={col.key}
            onDragOver={(e) => {
              e.preventDefault();
              setOverCol(col.key);
            }}
            onDragLeave={() => setOverCol((c) => (c === col.key ? null : c))}
            onDrop={(e) => {
              e.preventDefault();
              if (dragId) move(dragId, col.key);
              setDragId(null);
              setOverCol(null);
            }}
            className={cn(
              "flex w-72 shrink-0 flex-col rounded-xl border border-border bg-subtle/40 transition-colors",
              overCol === col.key && "border-primary/50 bg-primary/5"
            )}
          >
            <div className="flex items-center justify-between border-b border-border px-3 py-2.5">
              <div className="flex items-center gap-2">
                <span className={cn("h-2 w-2 rounded-full", col.accent)} />
                <span className="text-sm font-medium">{col.label}</span>
                <span className="rounded-full bg-secondary px-1.5 py-0.5 text-[10px] text-muted-foreground">
                  {items.length}
                </span>
              </div>
              <button className="text-muted-foreground hover:text-foreground">
                <Plus className="h-4 w-4" />
              </button>
            </div>
            <div className="px-3 py-1.5 text-[11px] text-muted-foreground">
              {formatCurrency(total)} total
            </div>

            <div className="flex-1 space-y-2 overflow-y-auto p-2">
              {items.map((lead) => (
                <motion.div
                  layout
                  key={lead.id}
                  draggable
                  onDragStart={() => setDragId(lead.id)}
                  onDragEnd={() => setDragId(null)}
                  whileDrag={{ scale: 1.03, rotate: 1 }}
                  className={cn(
                    "cursor-grab rounded-lg border border-border bg-card p-3 shadow-sm transition-shadow hover:shadow-md active:cursor-grabbing",
                    dragId === lead.id && "opacity-50"
                  )}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <UserAvatar name={lead.name} src={lead.avatar} className="h-7 w-7" />
                      <div>
                        <p className="text-sm font-medium leading-tight">{lead.name}</p>
                        <p className="text-[11px] text-muted-foreground">{lead.company}</p>
                      </div>
                    </div>
                    <button className="text-muted-foreground hover:text-foreground">
                      <MoreHorizontal className="h-3.5 w-3.5" />
                    </button>
                  </div>

                  <div className="mt-2.5 flex items-center justify-between">
                    <span className="font-mono text-sm font-semibold tabular-nums">
                      {formatCurrency(lead.value)}
                    </span>
                    <LeadScore score={lead.score} />
                  </div>

                  <div className="mt-2.5 flex items-center justify-between border-t border-border pt-2">
                    <span className="flex items-center gap-1 text-[11px] text-muted-foreground">
                      <Calendar className="h-3 w-3" />
                      {relativeTime(lead.nextActionDue)}
                    </span>
                    <div className="flex items-center gap-1.5">
                      <ChannelIcon channel={lead.source} withBg={false} className="text-muted-foreground" />
                      <UserAvatar name={lead.owner.name} src={lead.owner.avatar} className="h-5 w-5" />
                    </div>
                  </div>
                </motion.div>
              ))}
              {items.length === 0 && (
                <div className="rounded-lg border border-dashed border-border py-6 text-center text-[11px] text-muted-foreground">
                  Drop leads here
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
