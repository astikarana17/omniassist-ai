"use client";

import { motion } from "framer-motion";
import { Sparkles, TrendingUp, AlertTriangle, Lightbulb, ArrowRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { aiInsights } from "@/lib/data";
import type { AiInsight } from "@/types";
import { cn } from "@/lib/utils";

const kindConfig: Record<
  AiInsight["kind"],
  { icon: typeof TrendingUp; color: string; ring: string }
> = {
  trend: { icon: TrendingUp, color: "text-info", ring: "border-l-info" },
  risk: { icon: AlertTriangle, color: "text-danger", ring: "border-l-danger" },
  opportunity: { icon: Lightbulb, color: "text-ai", ring: "border-l-ai" },
};

export function AiInsights() {
  return (
    <Card className="relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-gradient-mesh opacity-40" />
      <CardHeader className="relative flex-row items-center gap-2 space-y-0">
        <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-ai">
          <Sparkles className="h-4 w-4 text-white" />
        </span>
        <CardTitle className="text-base">AI Insights</CardTitle>
      </CardHeader>
      <CardContent className="relative space-y-3">
        {aiInsights.map((insight, i) => {
          const cfg = kindConfig[insight.kind];
          const Icon = cfg.icon;
          return (
            <motion.div
              key={insight.id}
              initial={{ opacity: 0, x: 8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.15 + i * 0.1 }}
              className={cn(
                "rounded-lg border border-border border-l-2 bg-subtle/60 p-3",
                cfg.ring
              )}
            >
              <div className="flex items-start gap-2.5">
                <Icon className={cn("mt-0.5 h-4 w-4 shrink-0", cfg.color)} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium leading-snug">{insight.title}</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {insight.recommendation}
                  </p>
                  <button className={cn("mt-2 inline-flex items-center gap-1 text-xs font-medium", cfg.color)}>
                    {insight.actionLabel}
                    <ArrowRight className="h-3 w-3" />
                  </button>
                </div>
              </div>
            </motion.div>
          );
        })}
      </CardContent>
    </Card>
  );
}
