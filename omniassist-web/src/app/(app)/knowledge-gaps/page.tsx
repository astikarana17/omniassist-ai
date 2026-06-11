"use client";

import { useState } from "react";
import { AlertTriangle, Sparkles, FilePlus2, Check } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { knowledgeGaps, gapCounts } from "@/lib/ops-data";
import { useGapDashboard, useKnowledgeGaps } from "@/lib/api-hooks";
import { cn, relativeTime } from "@/lib/utils";
import type { GapStatus } from "@/types";

const statusVariant: Record<GapStatus, "warning" | "info" | "success" | "secondary"> = {
  open: "warning",
  in_review: "info",
  resolved: "success",
  dismissed: "secondary",
};

export default function KnowledgeGapsPage() {
  const [resolved, setResolved] = useState<Set<string>>(new Set());
  const { data: gaps } = useKnowledgeGaps();
  const { data: counts } = useGapDashboard();
  const rows = gaps ?? knowledgeGaps;
  const dash = counts ?? gapCounts;

  return (
    <div className="mx-auto max-w-[1100px] space-y-6 p-4 sm:p-6">
      <PageHeader
        title="Knowledge Gaps"
        description="Questions the AI couldn't answer confidently — turn them into documentation."
      />

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <CountCard label="Open" value={dash.open} tone="warning" />
        <CountCard label="In review" value={dash.in_review} tone="info" />
        <CountCard label="Resolved" value={dash.resolved} tone="success" />
        <CountCard label="Dismissed" value={dash.dismissed} tone="muted" />
      </div>

      <Card className="overflow-hidden">
        <div className="flex items-center gap-2 border-b border-border px-4 py-3">
          <AlertTriangle className="h-4 w-4 text-warning" />
          <h2 className="text-sm font-semibold">Top gaps by frequency</h2>
        </div>
        <div className="divide-y divide-border">
          {rows.map((g) => {
            const isResolved = resolved.has(g.id) || g.status === "resolved";
            return (
              <div key={g.id} className="px-4 py-3.5">
                <div className="flex items-start gap-3">
                  <div className="flex h-9 w-9 shrink-0 flex-col items-center justify-center rounded-md bg-subtle font-mono text-sm font-semibold tabular-nums">
                    {g.occurrences}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">{g.question}</p>
                    <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                      <Badge variant={isResolved ? "success" : statusVariant[g.status]} className="capitalize">
                        {isResolved ? "resolved" : g.status.replace("_", " ")}
                      </Badge>
                      <span>avg confidence {Math.round(g.avgConfidence * 100)}%</span>
                      <span>· seen {relativeTime(g.lastSeen)}</span>
                    </div>
                    {g.suggestion && !isResolved && (
                      <p className="mt-1.5 flex items-start gap-1.5 text-xs text-ai">
                        <Sparkles className="mt-0.5 h-3 w-3 shrink-0" />
                        {g.suggestion}
                      </p>
                    )}
                  </div>
                  <div className="shrink-0">
                    {isResolved ? (
                      <span className="inline-flex items-center gap-1 text-xs text-success">
                        <Check className="h-3.5 w-3.5" /> Done
                      </span>
                    ) : (
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => setResolved((s) => new Set(s).add(g.id))}
                      >
                        <FilePlus2 className="h-3.5 w-3.5" /> Create doc
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}

function CountCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: "warning" | "info" | "success" | "muted";
}) {
  return (
    <Card className="p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p
        className={cn(
          "mt-1 font-mono text-2xl font-medium tabular-nums",
          tone === "warning" && "text-warning",
          tone === "info" && "text-info",
          tone === "success" && "text-success",
          tone === "muted" && "text-muted-foreground"
        )}
      >
        {value}
      </p>
    </Card>
  );
}
