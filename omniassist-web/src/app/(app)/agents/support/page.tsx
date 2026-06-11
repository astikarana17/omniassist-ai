import { PageHeader } from "@/components/shared/page-header";
import { AgentConfig } from "@/components/agents/agent-config";

export default function SupportAgentPage() {
  return (
    <div className="mx-auto max-w-[1400px] space-y-6 p-4 sm:p-6">
      <PageHeader
        title="AI Support Agent"
        description="Configure how your support agent answers, escalates and uses tools."
      />
      <AgentConfig
        type="support"
        name="Support Agent"
        defaultPrompt={`You are OmniAssist, the AI customer support agent for Acme Inc.

- Always ground answers in the knowledge base and cite sources.
- Be warm, concise and empathetic.
- If confidence is low or the customer asks for a human, hand off gracefully.
- Never invent policies. When unsure, say so and escalate.
- Detect the customer's language and reply in it.`}
        tools={[
          { key: "kb_search", label: "Search knowledge base", enabled: true },
          { key: "create_ticket", label: "Create ticket", enabled: true },
          { key: "lookup_order", label: "Look up order", enabled: true },
          { key: "process_refund", label: "Process refund", enabled: false },
          { key: "escalate", label: "Escalate to human", enabled: true },
        ]}
        starterReply="I'm sorry for the trouble! I can see your order in our system. Based on our Billing Policy, I've initiated a refund — it'll reflect in 3–5 business days. Would you like a confirmation email?"
      />
    </div>
  );
}
