"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { ChevronLeft } from "lucide-react";
import { tickets as mockTickets } from "@/lib/data";
import { useTickets, apiConfigured } from "@/lib/api-hooks";
import { TicketDetail } from "@/components/tickets/ticket-detail";
import { PageLoader } from "@/components/shared/page-loader";

export default function TicketDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useTickets();
  const tickets = data ?? (apiConfigured() ? [] : mockTickets);

  if (apiConfigured() && isLoading) return <PageLoader />;
  const ticket = tickets.find((t) => t.id === id);

  if (!ticket) {
    return (
      <div className="mx-auto max-w-2xl p-8 text-center">
        <Link
          href="/tickets"
          className="mb-4 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <ChevronLeft className="h-4 w-4" /> Back to tickets
        </Link>
        <p className="mt-8 text-sm text-muted-foreground">
          This ticket couldn&apos;t be found. It may have been resolved or removed.
        </p>
      </div>
    );
  }
  return <TicketDetail ticket={ticket} />;
}
