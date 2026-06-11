"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Calendar, Download, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { VolumeChart } from "@/components/dashboard/volume-chart";
import { AiInsights } from "@/components/dashboard/ai-insights";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import {
  AiVsHumanDonut,
  DeflectionGauge,
  TeamPresence,
} from "@/components/dashboard/side-widgets";
import { dashboardKpis as mockKpis, currentUser } from "@/lib/data";
import { useAuthStore } from "@/store/auth-store";
import { useDashboardKpis } from "@/lib/api-hooks";

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  // Time + persisted user differ between server and first client paint, so render
  // a stable placeholder until mounted to avoid hydration mismatch.
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  const firstName = mounted ? (user?.fullName ?? currentUser.name).split(" ")[0] : "there";
  const greet = mounted ? greeting() : "Welcome";
  const { data: kpiData } = useDashboardKpis();
  const dashboardKpis = kpiData ?? mockKpis;
  return (
    <div className="mx-auto max-w-[1400px] space-y-6 p-4 sm:p-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {greet}, {firstName} 👋
          </h1>
          <p className="text-sm text-muted-foreground">
            Here&apos;s what&apos;s happening across your channels today.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select defaultValue="30d">
            <SelectTrigger className="w-[140px]">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="today">Today</SelectItem>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="secondary" size="default">
            <Download className="h-4 w-4" />
            <span className="hidden sm:inline">Export</span>
          </Button>
          <Button variant="gradient">
            <Plus className="h-4 w-4" />
            <span className="hidden sm:inline">New</span>
          </Button>
        </div>
      </div>

      {/* KPI strip */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {dashboardKpis.map((metric, i) => (
          <KpiCard key={metric.id} metric={metric} index={i} />
        ))}
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <VolumeChart />
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <AiInsights />
        </motion.div>
      </div>

      {/* Secondary grid */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-4">
        <DeflectionGauge />
        <AiVsHumanDonut />
        <div className="lg:col-span-2 xl:col-span-2">
          <ActivityFeed />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <TeamPresence />
      </div>
    </div>
  );
}
