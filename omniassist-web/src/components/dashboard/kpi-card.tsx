"use client";

import { motion } from "framer-motion";
import { ArrowDownRight, ArrowUpRight, Sparkles } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer } from "recharts";
import { Card } from "@/components/ui/card";
import { useCountUp } from "@/hooks/use-count-up";
import type { KpiMetric } from "@/types";
import { cn, formatCompact, formatCurrency } from "@/lib/utils";

function formatValue(value: number, format: KpiMetric["format"]) {
  switch (format) {
    case "currency":
      return formatCurrency(value);
    case "percent":
      return `${value.toFixed(1)}%`;
    case "duration":
      return `${value.toFixed(1)}s`;
    default:
      return value >= 1000 ? formatCompact(value) : value.toFixed(value % 1 === 0 ? 0 : 1);
  }
}

export function KpiCard({ metric, index = 0 }: { metric: KpiMetric; index?: number }) {
  const animated = useCountUp(metric.value, 1100);
  const positive = metric.delta >= 0;
  const data = metric.spark.map((v, i) => ({ i, v }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.06, ease: [0.2, 0.8, 0.2, 1] }}
    >
      <Card interactive className="relative overflow-hidden p-5">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-medium text-muted-foreground">
              {metric.label}
            </span>
            {metric.ai && <Sparkles className="h-3 w-3 text-ai" />}
          </div>
          <span
            className={cn(
              "inline-flex items-center gap-0.5 rounded-full px-1.5 py-0.5 text-[11px] font-semibold",
              positive ? "bg-success/10 text-success" : "bg-danger/10 text-danger"
            )}
          >
            {positive ? (
              <ArrowUpRight className="h-3 w-3" />
            ) : (
              <ArrowDownRight className="h-3 w-3" />
            )}
            {Math.abs(metric.delta).toFixed(1)}%
          </span>
        </div>

        <div className="mt-2 font-mono text-[28px] font-medium leading-none tracking-tight tabular-nums">
          {formatValue(animated, metric.format)}
        </div>

        <div className="mt-3 h-10">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 4, right: 0, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id={`spark-${metric.id}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="v"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                fill={`url(#spark-${metric.id})`}
                isAnimationActive
                animationDuration={900}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </motion.div>
  );
}
