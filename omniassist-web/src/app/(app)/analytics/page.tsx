"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Funnel,
  FunnelChart,
  LabelList,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Download, TrendingUp, Sparkles } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ChartTooltip } from "@/components/dashboard/chart-tooltip";
import { KpiCard } from "@/components/dashboard/kpi-card";
import {
  revenueTrend,
  conversionFunnel,
  sentimentByDay,
  csatTrend,
  resolutionHistogram,
  teamPerformance,
  dashboardKpis as mockKpis,
} from "@/lib/data";
import { useDashboardKpis } from "@/lib/api-hooks";

export default function AnalyticsPage() {
  const { data } = useDashboardKpis();
  const dashboardKpis = data ?? mockKpis;
  return (
    <div className="mx-auto max-w-[1400px] space-y-6 p-4 sm:p-6">
      <PageHeader title="Analytics" description="Measure deflection, satisfaction, revenue and team performance.">
        <Select defaultValue="30d">
          <SelectTrigger className="w-[130px]"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="7d">Last 7 days</SelectItem>
            <SelectItem value="30d">Last 30 days</SelectItem>
            <SelectItem value="90d">Last 90 days</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="secondary"><Download className="h-4 w-4" /> Export</Button>
      </PageHeader>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="conversations">Conversations</TabsTrigger>
          <TabsTrigger value="sales">Sales</TabsTrigger>
          <TabsTrigger value="ai">AI Performance</TabsTrigger>
        </TabsList>
      </Tabs>

      {/* KPI row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {dashboardKpis.slice(0, 4).map((m, i) => (
          <KpiCard key={m.id} metric={m} index={i} />
        ))}
      </div>

      {/* Revenue + Funnel */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <div>
              <CardTitle className="text-base">Revenue Influenced by AI</CardTitle>
              <p className="text-xs text-muted-foreground">Monthly · vs target</p>
            </div>
            <Badge variant="success" className="gap-1"><TrendingUp className="h-3 w-3" /> +12.8%</Badge>
          </CardHeader>
          <CardContent>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={revenueTrend} margin={{ top: 10, right: 8, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="rev" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#6366F1" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="#6366F1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                  <XAxis dataKey="month" tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} tickLine={false} axisLine={false} />
                  <YAxis tickFormatter={(v) => `$${v / 1000}k`} tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} tickLine={false} axisLine={false} width={48} />
                  <Tooltip content={<ChartTooltip />} />
                  <Area type="monotone" dataKey="revenue" stroke="#6366F1" strokeWidth={2.5} fill="url(#rev)" animationDuration={900} />
                  <Line type="monotone" dataKey="target" stroke="#8B5CF6" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">Conversion Funnel</CardTitle></CardHeader>
          <CardContent>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <FunnelChart>
                  <Tooltip content={<ChartTooltip />} />
                  <Funnel dataKey="value" data={conversionFunnel} isAnimationActive animationDuration={900}>
                    <LabelList position="right" fill="hsl(var(--foreground))" stroke="none" dataKey="stage" fontSize={11} />
                    {conversionFunnel.map((entry) => (
                      <Cell key={entry.stage} fill={entry.fill} />
                    ))}
                  </Funnel>
                </FunnelChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* CSAT + Resolution + Sentiment */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader><CardTitle className="text-base">CSAT Trend</CardTitle></CardHeader>
          <CardContent>
            <div className="h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={csatTrend} margin={{ top: 10, right: 8, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} tickLine={false} axisLine={false} interval={2} />
                  <YAxis domain={[3.5, 5]} tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} tickLine={false} axisLine={false} />
                  <Tooltip content={<ChartTooltip />} />
                  <Line type="monotone" dataKey="csat" stroke="#22C55E" strokeWidth={2.5} dot={{ r: 2, fill: "#22C55E" }} animationDuration={900} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">Resolution Time</CardTitle></CardHeader>
          <CardContent>
            <div className="h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={resolutionHistogram} margin={{ top: 10, right: 8, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                  <XAxis dataKey="bucket" tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} tickLine={false} axisLine={false} />
                  <Tooltip content={<ChartTooltip />} cursor={{ fill: "hsl(var(--accent))" }} />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]} animationDuration={900}>
                    {resolutionHistogram.map((_, i) => (
                      <Cell key={i} fill={i < 2 ? "#22C55E" : i < 4 ? "#6366F1" : "#F59E0B"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">Sentiment Breakdown</CardTitle></CardHeader>
          <CardContent>
            <div className="h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sentimentByDay} margin={{ top: 10, right: 8, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                  <XAxis dataKey="day" tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} tickLine={false} axisLine={false} />
                  <Tooltip content={<ChartTooltip />} cursor={{ fill: "hsl(var(--accent))" }} />
                  <Bar dataKey="positive" stackId="a" fill="#22C55E" radius={[0, 0, 0, 0]} />
                  <Bar dataKey="neutral" stackId="a" fill="#A1A1AA" />
                  <Bar dataKey="negative" stackId="a" fill="#EF4444" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Team performance */}
      <Card>
        <CardHeader className="flex-row items-center justify-between space-y-0">
          <CardTitle className="text-base">Team Performance</CardTitle>
          <Badge variant="ai" className="gap-1"><Sparkles className="h-3 w-3" /> AI-assisted resolutions counted</Badge>
        </CardHeader>
        <CardContent>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={teamPerformance} layout="vertical" margin={{ top: 0, right: 16, left: 8, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} tickLine={false} axisLine={false} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 12, fill: "hsl(var(--foreground))" }} tickLine={false} axisLine={false} width={70} />
                <Tooltip content={<ChartTooltip />} cursor={{ fill: "hsl(var(--accent))" }} />
                <Bar dataKey="resolved" fill="#6366F1" radius={[0, 6, 6, 0]} barSize={20} animationDuration={900}>
                  <LabelList dataKey="resolved" position="right" fontSize={11} fill="hsl(var(--muted-foreground))" />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
            {teamPerformance.map((m) => (
              <div key={m.name} className="rounded-lg border border-border bg-subtle/40 p-3">
                <p className="text-sm font-medium">{m.name}</p>
                <p className="font-mono text-lg font-semibold">{m.resolved}</p>
                <p className="text-[11px] text-muted-foreground">CSAT {m.csat} · {m.avgHandle.toFixed(1)}m avg handle</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
