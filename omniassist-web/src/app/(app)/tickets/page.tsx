"use client";

import { useState } from "react";
import { Plus, Ticket as TicketIcon, AlertTriangle, CheckCircle2, Clock } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { TicketsTable } from "@/components/tickets/tickets-table";
import { tickets as mockTickets } from "@/lib/data";
import { useTickets, useCreateTicket, apiConfigured } from "@/lib/api-hooks";

export default function TicketsPage() {
  const { data } = useTickets();
  const tickets = data ?? (apiConfigured() ? [] : mockTickets);
  const createTicket = useCreateTicket();
  const [open, setOpen] = useState(false);
  const [subject, setSubject] = useState("");
  const [priority, setPriority] = useState("medium");

  const open_ = tickets.filter((t) => t.status === "open" || t.status === "in_progress").length;
  const atRisk = tickets.filter(
    (t) => t.slaDueAt && new Date(t.slaDueAt).getTime() - Date.now() < 30 * 60 * 1000 && t.status !== "resolved" && t.status !== "closed"
  ).length;
  const resolved = tickets.filter((t) => t.status === "resolved" || t.status === "closed").length;

  const submit = () => {
    if (!subject.trim()) return;
    createTicket.mutate(
      { subject: subject.trim(), priority },
      {
        onSuccess: () => {
          toast.success("Ticket created");
          setOpen(false);
          setSubject("");
        },
        onError: () => toast.error("Could not create the ticket"),
      }
    );
  };

  const stats = [
    { label: "Open tickets", value: open_, icon: TicketIcon, color: "text-info bg-info/10" },
    { label: "SLA at risk", value: atRisk, icon: AlertTriangle, color: "text-danger bg-danger/10" },
    { label: "Resolved", value: resolved, icon: CheckCircle2, color: "text-success bg-success/10" },
    { label: "Total", value: tickets.length, icon: Clock, color: "text-ai bg-ai/10" },
  ];

  return (
    <div className="mx-auto max-w-[1400px] space-y-6 p-4 sm:p-6">
      <PageHeader title="Tickets" description="Manage support tickets, SLAs and assignments.">
        <Button variant="gradient" onClick={() => setOpen(true)}>
          <Plus className="h-4 w-4" /> New ticket
        </Button>
      </PageHeader>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create a ticket</DialogTitle>
            <DialogDescription>It will appear in the queue with an SLA timer.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label htmlFor="ticket-subject">Subject</Label>
              <Input
                id="ticket-subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && submit()}
                placeholder="e.g. Customer can't access invoices"
              />
            </div>
            <div className="space-y-2">
              <Label>Priority</Label>
              <Select value={priority} onValueChange={setPriority}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="urgent">Urgent</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="secondary" onClick={() => setOpen(false)}>Cancel</Button>
            <Button
              variant="gradient"
              onClick={submit}
              disabled={!subject.trim()}
              loading={createTicket.isPending}
            >
              Create ticket
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {stats.map((s) => (
          <Card key={s.label} interactive className="flex items-center gap-3 p-4">
            <span className={`flex h-10 w-10 items-center justify-center rounded-lg ${s.color}`}>
              <s.icon className="h-5 w-5" />
            </span>
            <div>
              <p className="font-mono text-xl font-semibold tabular-nums">{s.value}</p>
              <p className="text-xs text-muted-foreground">{s.label}</p>
            </div>
          </Card>
        ))}
      </div>

      <TicketsTable tickets={tickets} />
    </div>
  );
}
