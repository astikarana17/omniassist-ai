import Link from "next/link";
import { Plus } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { PipelineBoard } from "@/components/leads/pipeline-board";
import { leads } from "@/lib/data";

export default function PipelinePage() {
  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col p-4 sm:p-6">
      <PageHeader
        title="CRM Pipeline"
        description="Drag leads across stages. AI suggests the next best action for each."
        className="mb-6"
      >
        <Button variant="secondary" asChild>
          <Link href="/leads">List view</Link>
        </Button>
        <Button variant="gradient"><Plus className="h-4 w-4" /> Add lead</Button>
      </PageHeader>
      <div className="min-h-0 flex-1">
        <PipelineBoard initialLeads={leads} />
      </div>
    </div>
  );
}
