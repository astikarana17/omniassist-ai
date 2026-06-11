"use client";

import { useState } from "react";
import { Download, Search, ShieldCheck, ChevronRight } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { UserAvatar } from "@/components/shared/user-avatar";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { auditLog as mockAudit } from "@/lib/data";
import { useAuditLogs, apiConfigured } from "@/lib/api-hooks";
import { relativeTime, cn } from "@/lib/utils";

export default function AuditLogsPage() {
  const [query, setQuery] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);
  const { data } = useAuditLogs();
  const auditLog = data ?? (apiConfigured() ? [] : mockAudit);

  const filtered = auditLog.filter(
    (e) =>
      !query ||
      e.action.toLowerCase().includes(query.toLowerCase()) ||
      e.resource.toLowerCase().includes(query.toLowerCase()) ||
      e.actor.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="mx-auto max-w-[1100px] space-y-6 p-4 sm:p-6">
      <PageHeader title="Audit Logs" description="Immutable record of security and data actions.">
        <Button
          variant="secondary"
          onClick={() => {
            const esc = (v: string) => `"${String(v).replace(/"/g, '""')}"`;
            const rows = [
              ["Timestamp", "Actor", "Action", "Resource type", "Resource", "Detail", "IP"],
              ...filtered.map((e) => [e.createdAt, e.actor.name, e.action, e.resourceType, e.resource, e.detail, e.ip]),
            ];
            const csv = rows.map((r) => r.map(esc).join(",")).join("\n");
            const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
            const a = document.createElement("a");
            a.href = url;
            a.download = "audit-logs.csv";
            a.click();
            URL.revokeObjectURL(url);
          }}
        >
          <Download className="h-4 w-4" /> Export CSV
        </Button>
      </PageHeader>

      <div className="flex flex-col gap-2 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search actions, resources, actors…" className="pl-8" />
        </div>
        <Select defaultValue="all">
          <SelectTrigger className="sm:w-40"><SelectValue placeholder="Resource" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All resources</SelectItem>
            <SelectItem value="user">Users</SelectItem>
            <SelectItem value="ticket">Tickets</SelectItem>
            <SelectItem value="knowledge_base">Knowledge base</SelectItem>
            <SelectItem value="security">Security</SelectItem>
          </SelectContent>
        </Select>
        <Select defaultValue="7d">
          <SelectTrigger className="sm:w-36"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="24h">Last 24h</SelectItem>
            <SelectItem value="7d">Last 7 days</SelectItem>
            <SelectItem value="30d">Last 30 days</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Card className="overflow-hidden">
        <div className="divide-y divide-border">
          {filtered.map((entry) => (
            <div key={entry.id}>
              <button
                onClick={() => setExpanded((e) => (e === entry.id ? null : entry.id))}
                className="flex w-full items-center gap-3 px-4 py-3.5 text-left transition-colors hover:bg-accent/40"
              >
                <UserAvatar name={entry.actor.name} src={entry.actor.avatar} className="h-8 w-8" />
                <div className="min-w-0 flex-1">
                  <p className="text-sm">
                    <span className="font-medium">{entry.actor.name}</span>{" "}
                    <span className="text-muted-foreground">{entry.action}</span>{" "}
                    <span className="font-medium">{entry.resource}</span>
                  </p>
                  <p className="text-xs text-muted-foreground">{entry.detail}</p>
                </div>
                <Badge variant="outline" className="hidden capitalize sm:inline-flex">
                  {entry.resourceType.replace("_", " ")}
                </Badge>
                <span className="shrink-0 text-xs tabular-nums text-muted-foreground">{relativeTime(entry.createdAt)}</span>
                <ChevronRight className={cn("h-4 w-4 text-muted-foreground transition-transform", expanded === entry.id && "rotate-90")} />
              </button>
              {expanded === entry.id && (
                <div className="space-y-1.5 border-t border-border bg-subtle/40 px-4 py-3 text-xs">
                  <Row label="Actor" value={entry.actor.name} />
                  <Row label="Action" value={entry.action} />
                  <Row label="Resource" value={`${entry.resourceType} · ${entry.resource}`} />
                  <Row label="Change" value={entry.detail} />
                  <Row label="IP address" value={entry.ip} mono />
                  <Row label="Timestamp" value={new Date(entry.createdAt).toLocaleString()} mono />
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      <p className="flex items-center justify-center gap-1.5 text-xs text-muted-foreground">
        <ShieldCheck className="h-3.5 w-3.5 text-success" />
        Audit logs are append-only and cannot be modified or deleted.
      </p>
    </div>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex gap-3">
      <span className="w-24 shrink-0 text-muted-foreground">{label}</span>
      <span className={mono ? "font-mono" : ""}>{value}</span>
    </div>
  );
}
