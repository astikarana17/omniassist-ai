"use client";

import { Workflow as WorkflowIcon, Plus, Play, Check, X, Loader2 } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { workflows as mockWorkflows, workflowRuns as mockRuns } from "@/lib/ops-data";
import { useWorkflowRuns, useWorkflows } from "@/lib/api-hooks";
import { cn, relativeTime } from "@/lib/utils";
import type { WorkflowRunItem, WorkflowStatus } from "@/types";

const statusVariant: Record<WorkflowStatus, "success" | "warning" | "secondary"> = {
  active: "success",
  paused: "warning",
  draft: "secondary",
  archived: "secondary",
};

function runIcon(status: WorkflowRunItem["status"]) {
  if (status === "succeeded") return <Check className="h-3.5 w-3.5 text-success" />;
  if (status === "failed") return <X className="h-3.5 w-3.5 text-danger" />;
  return <Loader2 className="h-3.5 w-3.5 animate-spin text-info" />;
}

export default function WorkflowsPage() {
  const { data: wfData } = useWorkflows();
  const { data: runData } = useWorkflowRuns();
  const workflows = wfData ?? mockWorkflows;
  const workflowRuns = runData ?? mockRuns;
  return (
    <div className="mx-auto max-w-[1100px] space-y-6 p-4 sm:p-6">
      <PageHeader
        title="Workflow Automation"
        description="No-code automations across support, sales and finance."
      >
        <Button>
          <Plus className="h-4 w-4" /> New workflow
        </Button>
      </PageHeader>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-3 lg:col-span-2">
          {workflows.map((wf) => (
            <Card key={wf.id} interactive className="p-4">
              <div className="flex items-start gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
                  <WorkflowIcon className="h-4 w-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-sm font-semibold">{wf.name}</p>
                    <Badge variant={statusVariant[wf.status]} className="capitalize">{wf.status}</Badge>
                  </div>
                  <p className="mt-0.5 text-xs text-muted-foreground">{wf.description}</p>
                  <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                    <span className="font-mono">{wf.trigger}</span>
                    <span>· {wf.nodes} steps</span>
                    <span>· {wf.runCount} runs</span>
                    {wf.lastRun && <span>· last {relativeTime(wf.lastRun)}</span>}
                  </div>
                </div>
                <Button size="sm" variant="secondary" disabled={wf.status === "draft"}>
                  <Play className="h-3.5 w-3.5" /> Run
                </Button>
              </div>
            </Card>
          ))}
        </div>

        <div>
          <Card className="overflow-hidden">
            <div className="border-b border-border px-4 py-3">
              <h2 className="text-sm font-semibold">Recent runs</h2>
            </div>
            <div className="divide-y divide-border">
              {workflowRuns.map((r) => (
                <div key={r.id} className="flex items-center gap-2.5 px-4 py-3 text-sm">
                  {runIcon(r.status)}
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium">{r.workflow}</p>
                    <p className="text-xs text-muted-foreground">
                      {r.steps} step{r.steps === 1 ? "" : "s"}
                      {r.status !== "running" && ` · ${r.durationMs}ms`}
                    </p>
                  </div>
                  <span className={cn(
                    "shrink-0 text-xs tabular-nums text-muted-foreground"
                  )}>
                    {relativeTime(r.createdAt)}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
