import { PageHeader } from "@/components/shared/page-header";
import { AgentConfig } from "@/components/agents/agent-config";

export default function SalesAgentPage() {
  return (
    <div className="mx-auto max-w-[1400px] space-y-6 p-4 sm:p-6">
      <PageHeader
        title="AI Sales Agent"
        description="Configure how your sales agent qualifies leads and books demos."
      />
      <AgentConfig
        type="sales"
        name="Sales Agent"
        defaultPrompt={`You are OmniAssist Sales, the AI sales development agent for Acme Inc.

- Engage visitors warmly and qualify using BANT (Budget, Authority, Need, Timeline).
- Answer product & pricing questions grounded in the knowledge base.
- Book demos when intent is high; capture contact details.
- Hand hot leads to the sales team and schedule follow-ups for the rest.
- Be persuasive but never pushy.`}
        tools={[
          { key: "kb_search", label: "Search product knowledge", enabled: true },
          { key: "qualify_lead", label: "Qualify lead (BANT)", enabled: true },
          { key: "book_demo", label: "Book a demo", enabled: true },
          { key: "create_lead", label: "Create lead in pipeline", enabled: true },
          { key: "schedule_followup", label: "Schedule follow-up", enabled: true },
        ]}
        starterReply="Great question! Our Growth plan includes both Support & Sales agents across every channel with 10k conversations/mo. Based on what you've shared, it sounds like a strong fit — would you like me to book a 20-minute demo this week?"
      />
    </div>
  );
}
