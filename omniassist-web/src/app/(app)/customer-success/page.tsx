"use client";

import { useState } from "react";
import { HeartPulse, ArrowDownRight, Sparkles } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { customerHealth } from "@/lib/ops-data";
import { useCustomerHealth } from "@/lib/api-hooks";
import { cn, formatCurrency, relativeTime } from "@/lib/utils";
import type { HealthCategory } from "@/types";

const categoryStyle: Record<HealthCategory, { label: string; cls: string; bar: string }> = {
  healthy: { label: "Healthy", cls: "bg-success/10 text-success", bar: "bg-success" },
  at_risk: { label: "At Risk", cls: "bg-amber-500/10 text-amber-500", bar: "bg-amber-500" },
  critical: { label: "Critical", cls: "bg-danger/10 text-danger", bar: "bg-danger" },
};

export default function CustomerSuccessPage() {
  const [filter, setFilter] = useState<HealthCategory | "all">("all");
  const { data } = useCustomerHealth();
  const all = data ?? customerHealth;
  const rows = all.filter((c) => filter === "all" || c.category === filter);

  const counts = {
    healthy: all.filter((c) => c.category === "healthy").length,
    at_risk: all.filter((c) => c.category === "at_risk").length,
    critical: all.filter((c) => c.category === "critical").length,
  };
  const mrrAtRisk = all
    .filter((c) => c.category !== "healthy")
    .reduce((s, c) => s + c.mrr, 0);
  const avgScore = all.length
    ? Math.round(all.reduce((s, c) => s + c.score, 0) / all.length)
    : 0;

  return (
    <div className="mx-auto max-w-[1100px] space-y-6 p-4 sm:p-6">
      <PageHeader
        title="Customer Health"
        description="AI-scored account health, churn risk and engagement actions."
      >
        <Select value={filter} onValueChange={(v) => setFilter(v as HealthCategory | "all")}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All accounts</SelectItem>
            <SelectItem value="healthy">Healthy</SelectItem>
            <SelectItem value="at_risk">At Risk</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
          </SelectContent>
        </Select>
      </PageHeader>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat label="Avg health" value={`${avgScore}`} icon={<HeartPulse className="h-4 w-4 text-success" />} />
        <Stat label="Healthy" value={`${counts.healthy}`} tone="success" />
        <Stat label="At risk" value={`${counts.at_risk}`} tone="amber" />
        <Stat label="MRR at risk" value={formatCurrency(mrrAtRisk)} icon={<ArrowDownRight className="h-4 w-4 text-danger" />} />
      </div>

      <Card className="overflow-hidden">
        <div className="grid grid-cols-12 gap-2 border-b border-border px-4 py-2.5 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
          <div className="col-span-4">Account</div>
          <div className="col-span-3">Health</div>
          <div className="col-span-2">Churn risk</div>
          <div className="col-span-2">Owner</div>
          <div className="col-span-1 text-right">Active</div>
        </div>
        <div className="divide-y divide-border">
          {rows.map((c) => {
            const style = categoryStyle[c.category];
            return (
              <div key={c.id} className="grid grid-cols-12 items-center gap-2 px-4 py-3 text-sm transition-colors hover:bg-accent/40">
                <div className="col-span-4 min-w-0">
                  <p className="truncate font-medium">{c.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {c.plan} · {formatCurrency(c.mrr)}/mo
                  </p>
                </div>
                <div className="col-span-3 flex items-center gap-2">
                  <Progress value={c.score} className="h-1.5" indicatorClassName={style.bar} />
                  <span className="w-7 text-right font-mono text-xs tabular-nums">{c.score}</span>
                </div>
                <div className="col-span-2">
                  <Badge className={cn("font-medium", style.cls)}>
                    {Math.round(c.churnRisk * 100)}% · {style.label}
                  </Badge>
                </div>
                <div className="col-span-2 truncate text-xs text-muted-foreground">{c.owner}</div>
                <div className="col-span-1 text-right text-xs tabular-nums text-muted-foreground">
                  {relativeTime(c.lastActive)}
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      <Card className="flex items-start gap-3 p-4">
        <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-ai" />
        <p className="text-sm text-muted-foreground">
          <span className="font-medium text-foreground">CS Agent recommendation:</span>{" "}
          {counts.critical} critical account{counts.critical === 1 ? "" : "s"} inactive &gt;14 days.
          Trigger the re-engagement playbook and schedule a CSM check-in this week.
        </p>
      </Card>
    </div>
  );
}

function Stat({
  label,
  value,
  icon,
  tone,
}: {
  label: string;
  value: string;
  icon?: React.ReactNode;
  tone?: "success" | "amber";
}) {
  return (
    <Card className="p-4">
      <div className="flex items-center justify-between">
        <span className="text-xs text-muted-foreground">{label}</span>
        {icon}
      </div>
      <p
        className={cn(
          "mt-1 font-mono text-xl font-medium tabular-nums",
          tone === "success" && "text-success",
          tone === "amber" && "text-amber-500"
        )}
      >
        {value}
      </p>
    </Card>
  );
}
