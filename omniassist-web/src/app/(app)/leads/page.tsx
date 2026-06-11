"use client";

import Link from "next/link";
import { Plus, Search, Target, TrendingUp, Trophy, Clock } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { UserAvatar } from "@/components/shared/user-avatar";
import { ChannelIcon } from "@/components/shared/channel-icon";
import { StagePill } from "@/components/shared/status-pill";
import { LeadScore } from "@/components/leads/lead-score";
import { leads as mockLeads } from "@/lib/data";
import { useLeads, useCreateLead, apiConfigured } from "@/lib/api-hooks";
import { formatCurrency, relativeTime } from "@/lib/utils";
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

export default function LeadsPage() {
  const [query, setQuery] = useState("");
  const { data } = useLeads();
  const leads = data ?? (apiConfigured() ? [] : mockLeads);
  const createLead = useCreateLead();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", company: "", email: "", value: "" });

  const submitLead = () => {
    if (!form.name.trim()) return;
    createLead.mutate(
      {
        name: form.name.trim(),
        company: form.company.trim() || undefined,
        email: form.email.trim() || undefined,
        value: Number(form.value) || 0,
      },
      {
        onSuccess: () => {
          toast.success("Lead added");
          setOpen(false);
          setForm({ name: "", company: "", email: "", value: "" });
        },
        onError: () => toast.error("Could not add the lead"),
      }
    );
  };
  const filtered = leads.filter(
    (l) =>
      !query ||
      l.name.toLowerCase().includes(query.toLowerCase()) ||
      l.company.toLowerCase().includes(query.toLowerCase())
  );

  const pipelineValue = leads
    .filter((l) => l.stage !== "lost" && l.stage !== "won")
    .reduce((sum, l) => sum + l.value, 0);
  const won = leads.filter((l) => l.stage === "won").length;
  const hot = leads.filter((l) => l.score >= 85).length;

  const stats = [
    { label: "Pipeline value", value: formatCurrency(pipelineValue), icon: TrendingUp, color: "text-primary bg-primary/10" },
    { label: "Hot leads", value: hot, icon: Target, color: "text-danger bg-danger/10" },
    { label: "Won this month", value: won, icon: Trophy, color: "text-success bg-success/10" },
    { label: "Avg response", value: "12m", icon: Clock, color: "text-ai bg-ai/10" },
  ];

  return (
    <div className="mx-auto max-w-[1400px] space-y-6 p-4 sm:p-6">
      <PageHeader title="Leads" description="Track, qualify and convert your sales pipeline.">
        <Button variant="secondary" asChild>
          <Link href="/leads/pipeline">Pipeline view</Link>
        </Button>
        <Button variant="gradient" onClick={() => setOpen(true)}>
          <Plus className="h-4 w-4" /> Add lead
        </Button>
      </PageHeader>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add a lead</DialogTitle>
            <DialogDescription>The AI will score and track it through your pipeline.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label htmlFor="lead-name">Name *</Label>
              <Input id="lead-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Jane Cooper" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="lead-company">Company</Label>
                <Input id="lead-company" value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} placeholder="Acme Inc" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lead-value">Deal value ($)</Label>
                <Input id="lead-value" type="number" value={form.value} onChange={(e) => setForm({ ...form, value: e.target.value })} placeholder="5000" />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="lead-email">Email</Label>
              <Input id="lead-email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="jane@acme.com" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="secondary" onClick={() => setOpen(false)}>Cancel</Button>
            <Button variant="gradient" onClick={submitLead} disabled={!form.name.trim()} loading={createLead.isPending}>
              Add lead
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

      <div className="relative sm:w-72">
        <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search leads…" className="pl-8" />
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-card">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[860px] text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs text-muted-foreground">
                <th className="px-4 py-3 font-medium">Lead</th>
                <th className="px-2 py-3 font-medium">Score</th>
                <th className="px-2 py-3 font-medium">Stage</th>
                <th className="px-2 py-3 font-medium">Value</th>
                <th className="px-2 py-3 font-medium">Owner</th>
                <th className="px-2 py-3 font-medium">Source</th>
                <th className="px-2 py-3 font-medium">Next action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((l) => (
                <tr key={l.id} className="group border-b border-border/60 transition-colors last:border-0 hover:bg-accent/40">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <UserAvatar name={l.name} src={l.avatar} className="h-8 w-8" />
                      <div>
                        <p className="font-medium group-hover:text-primary">{l.name}</p>
                        <p className="text-xs text-muted-foreground">{l.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-2 py-3"><LeadScore score={l.score} /></td>
                  <td className="px-2 py-3"><StagePill stage={l.stage} /></td>
                  <td className="px-2 py-3 font-mono text-sm tabular-nums">{formatCurrency(l.value)}</td>
                  <td className="px-2 py-3">
                    <div className="flex items-center gap-2">
                      <UserAvatar name={l.owner.name} src={l.owner.avatar} className="h-6 w-6" />
                      <span className="hidden text-xs lg:inline">{l.owner.name.split(" ")[0]}</span>
                    </div>
                  </td>
                  <td className="px-2 py-3"><ChannelIcon channel={l.source} /></td>
                  <td className="px-2 py-3">
                    <div className="flex flex-col">
                      <span className="text-xs font-medium">{l.nextAction}</span>
                      <span className="text-[11px] text-muted-foreground">{relativeTime(l.nextActionDue)}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filtered.length === 0 && (
          <p className="py-12 text-center text-sm text-muted-foreground">No leads found.</p>
        )}
      </div>

      <Badge variant="ai" className="gap-1">
        <Target className="h-3 w-3" /> AI captured & scored {leads.length} leads automatically
      </Badge>
    </div>
  );
}
