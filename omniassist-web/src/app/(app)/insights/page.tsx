"use client";

import {
  TrendingUp,
  TrendingDown,
  Sparkles,
  AlertTriangle,
  Lightbulb,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
} from "recharts";
import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { businessImpact, execInsights } from "@/lib/ops-data";
import { useImpact, useInsights } from "@/lib/api-hooks";
import { cn, formatCurrency, formatPercent, relativeTime } from "@/lib/utils";
import type { ExecInsight } from "@/types";

const severityStyle: Record<ExecInsight["severity"], string> = {
  positive: "bg-success/10 text-success",
  warning: "bg-warning/10 text-warning",
  critical: "bg-danger/10 text-danger",
  info: "bg-info/10 text-info",
};

function severityIcon(s: ExecInsight["severity"]) {
  if (s === "critical" || s === "warning") return <AlertTriangle className="h-4 w-4" />;
  if (s === "positive") return <TrendingUp className="h-4 w-4" />;
  return <Lightbulb className="h-4 w-4" />;
}

export default function InsightsPage() {
  const { data: impact } = useImpact();
  const { data: insightsData } = useInsights();
  const b = impact ?? businessImpact;
  const insights = insightsData ?? execInsights;
  const roi = [
    { label: "AI Resolution Rate", value: formatPercent(b.aiResolutionRate), up: true },
    { label: "Cost Savings", value: formatCurrency(b.costSavings), up: true },
    { label: "Revenue Influenced", value: formatCurrency(b.revenueInfluenced), up: true },
    { label: "Churn Reduction", value: formatPercent(b.churnReduction), up: true },
    { label: "Agent Productivity", value: `+${formatPercent(b.agentProductivity)}`, up: true },
    { label: "Customer Retention", value: formatPercent(b.retention), up: true },
  ];

  return (
    <div className="mx-auto max-w-[1100px] space-y-6 p-4 sm:p-6">
      <PageHeader
        title="Executive Insights"
        description="AI-generated business recommendations and ROI for leadership."
      />

      {/* ROI grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {roi.map((m) => (
          <Card key={m.label} className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">{m.label}</span>
              {m.up ? (
                <TrendingUp className="h-3.5 w-3.5 text-success" />
              ) : (
                <TrendingDown className="h-3.5 w-3.5 text-danger" />
              )}
            </div>
            <p className="mt-1 font-mono text-xl font-medium tabular-nums">{m.value}</p>
          </Card>
        ))}
      </div>

      {/* ROI trend */}
      <Card className="p-5">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold">Business impact trend</h2>
          <span className="text-xs text-muted-foreground">Cost savings vs revenue influenced (6 mo)</span>
        </div>
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={b.trend} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="g-savings" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="hsl(var(--success))" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="hsl(var(--success))" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="g-revenue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
              <XAxis dataKey="month" tickLine={false} axisLine={false} fontSize={11} stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  background: "hsl(var(--popover))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: 8,
                  fontSize: 12,
                }}
                formatter={(v: number) => formatCurrency(v)}
              />
              <Area type="monotone" dataKey="revenue" stroke="hsl(var(--primary))" strokeWidth={2} fill="url(#g-revenue)" />
              <Area type="monotone" dataKey="savings" stroke="hsl(var(--success))" strokeWidth={2} fill="url(#g-savings)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* AI insights */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-ai" />
          <h2 className="text-sm font-semibold">AI-powered recommendations</h2>
        </div>
        {insights.map((ins) => (
          <Card key={ins.id} className="p-4">
            <div className="flex items-start gap-3">
              <div className={cn("flex h-8 w-8 shrink-0 items-center justify-center rounded-md", severityStyle[ins.severity])}>
                {severityIcon(ins.severity)}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-sm font-medium">{ins.title}</p>
                  <Badge variant="outline" className="capitalize">{ins.kind.replace("_", " ")}</Badge>
                  <span className="text-xs text-muted-foreground">{relativeTime(ins.createdAt)}</span>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">{ins.summary}</p>
                {ins.recommendation && (
                  <p className="mt-1.5 text-sm">
                    <span className="font-medium">Recommendation: </span>
                    {ins.recommendation}
                  </p>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
