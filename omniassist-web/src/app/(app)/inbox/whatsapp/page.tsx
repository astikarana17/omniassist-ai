"use client";

import { InboxView } from "@/components/inbox/inbox-view";
import { PageLoader } from "@/components/shared/page-loader";
import { conversations as mockConversations } from "@/lib/data";
import { useConversations, apiConfigured } from "@/lib/api-hooks";

export default function WhatsAppInboxPage() {
  const { data, isLoading } = useConversations("whatsapp");
  if (apiConfigured() && isLoading) return <PageLoader />;
  return (
    <InboxView
      conversations={data ?? (apiConfigured() ? [] : mockConversations)}
      channel="whatsapp"
      live={!!data}
    />
  );
}
