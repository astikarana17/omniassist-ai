"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Settings2,
  Radio,
  Sparkles,
  Bell,
  KeyRound,
  CreditCard,
  ShieldCheck,
  Globe,
  MessageCircle,
  Mail,
  Phone,
  Plus,
  ExternalLink,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { useAuthStore } from "@/store/auth-store";
import { cn } from "@/lib/utils";

const sections = [
  { key: "general", label: "General", icon: Settings2 },
  { key: "channels", label: "Channels", icon: Radio },
  { key: "ai", label: "AI Configuration", icon: Sparkles },
  { key: "notifications", label: "Notifications", icon: Bell },
  { key: "api", label: "API Keys", icon: KeyRound },
  { key: "billing", label: "Billing & Plan", icon: CreditCard },
] as const;

type SectionKey = (typeof sections)[number]["key"];

export default function SettingsPage() {
  const [active, setActive] = useState<SectionKey>("general");

  return (
    <div className="mx-auto max-w-[1200px] space-y-6 p-4 sm:p-6">
      <PageHeader title="Settings" description="Configure your workspace, channels and AI." />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[220px_1fr]">
        <nav className="flex gap-1 overflow-x-auto no-scrollbar lg:flex-col">
          {sections.map((s) => (
            <button
              key={s.key}
              onClick={() => setActive(s.key)}
              className={cn(
                "flex shrink-0 items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                active === s.key
                  ? "bg-primary/10 text-foreground ring-1 ring-primary/20"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )}
            >
              <s.icon className={cn("h-4 w-4", active === s.key && "text-primary")} />
              {s.label}
            </button>
          ))}
          <Link
            href="/audit-logs"
            className="flex shrink-0 items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
          >
            <ShieldCheck className="h-4 w-4" /> Audit Logs
            <ExternalLink className="ml-auto h-3 w-3" />
          </Link>
        </nav>

        <div className="space-y-4">
          {active === "general" && <GeneralSection />}
          {active === "channels" && <ChannelsSection />}
          {active === "ai" && <AiSection />}
          {active === "notifications" && <NotificationsSection />}
          {active === "api" && <ApiSection />}
          {active === "billing" && <BillingSection />}
        </div>
      </div>
    </div>
  );
}

function GeneralSection() {
  const { org } = useAuthStore();
  return (
    <Card>
      <CardHeader><CardTitle className="text-base">Workspace</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label>Workspace name</Label>
          <Input defaultValue={org?.name ?? ""} readOnly />
        </div>
        <div className="space-y-2">
          <Label>Workspace URL</Label>
          <div className="flex items-center">
            <span className="rounded-l-md border border-r-0 border-border-strong bg-secondary px-3 py-2 text-sm text-muted-foreground">
              omniassist.ai/
            </span>
            <Input defaultValue={org?.slug ?? ""} readOnly className="rounded-l-none" />
          </div>
        </div>
        <div className="space-y-2">
          <Label>Plan</Label>
          <p className="text-sm capitalize text-muted-foreground">
            {org?.role === "super_admin" ? "Owner" : org?.role} ·{" "}
            <Link href="/billing" className="text-primary hover:underline">manage plan →</Link>
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

const channels = [
  { key: "web", icon: Globe, label: "Website Chat", detail: "Embed the widget on your site — always available." },
  { key: "whatsapp", icon: MessageCircle, label: "WhatsApp", detail: "Connect via Twilio (Growth & Enterprise plans)." },
  { key: "email", icon: Mail, label: "Email", detail: "Connect a support inbox (Gmail / SMTP)." },
  { key: "voice", icon: Phone, label: "Voice", detail: "Phone support via Twilio Voice (Enterprise)." },
];

function ChannelsSection() {
  return (
    <Card>
      <CardHeader><CardTitle className="text-base">Channels</CardTitle></CardHeader>
      <CardContent className="space-y-3">
        <p className="text-xs text-muted-foreground">
          Connect channels by configuring their provider credentials in the backend environment.
          Need help wiring a channel? Reach out and we&apos;ll get you set up.
        </p>
        {channels.map((c) => (
          <div key={c.key} className="flex items-center gap-3 rounded-lg border border-border p-4">
            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
              <c.icon className="h-5 w-5" />
            </span>
            <div className="flex-1">
              <p className="text-sm font-medium">{c.label}</p>
              <p className="text-xs text-muted-foreground">{c.detail}</p>
            </div>
            <Button size="sm" variant="secondary" asChild>
              <a href={`mailto:sales@omniassist.ai?subject=Connect%20${c.label}`}>Set up</a>
            </Button>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

function AiSection() {
  return (
    <Card>
      <CardHeader><CardTitle className="text-base">AI Configuration</CardTitle></CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground">
          Configure your AI agents — system prompt, tools, auto-handoff confidence threshold, and
          a live test sandbox — on the dedicated agent pages.
        </p>
        <div className="flex flex-wrap gap-2">
          <Button variant="ai" asChild>
            <Link href="/agents/support"><Sparkles className="h-4 w-4" /> Support Agent</Link>
          </Button>
          <Button variant="secondary" asChild>
            <Link href="/agents/sales"><Sparkles className="h-4 w-4" /> Sales Agent</Link>
          </Button>
          <Button variant="secondary" asChild>
            <Link href="/knowledge-base">Knowledge Base</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function NotificationsSection() {
  return (
    <Card>
      <CardHeader><CardTitle className="text-base">Notification preferences</CardTitle></CardHeader>
      <CardContent className="space-y-1">
        <p className="px-2 pb-2 text-xs text-muted-foreground">
          Choose which events appear in your in-app notifications.
        </p>
        {[
          { label: "New handoff request", on: true },
          { label: "SLA breach warning", on: true },
          { label: "New ticket created", on: true },
          { label: "New hot lead", on: true },
          { label: "Daily summary digest", on: false },
        ].map((o) => (
          <div key={o.label} className="flex items-center justify-between rounded-md px-2 py-2.5">
            <p className="text-sm">{o.label}</p>
            <Switch defaultChecked={o.on} />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

function ApiSection() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">API Keys</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-center gap-2 py-10 text-center">
        <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-subtle">
          <Plus className="h-5 w-5 text-muted-foreground" />
        </span>
        <p className="text-sm font-medium">Programmatic API access</p>
        <p className="max-w-sm text-xs text-muted-foreground">
          Generate scoped API keys to integrate OmniAssist with your own systems. Available on the
          Enterprise plan — contact us to enable it for your workspace.
        </p>
        <Button size="sm" variant="secondary" asChild className="mt-2">
          <a href="mailto:sales@omniassist.ai?subject=API%20access">Request API access</a>
        </Button>
      </CardContent>
    </Card>
  );
}

function BillingSection() {
  return (
    <Card>
      <CardContent className="flex flex-col items-center justify-center gap-3 py-12 text-center">
        <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-subtle">
          <CreditCard className="h-5 w-5 text-muted-foreground" />
        </span>
        <p className="text-sm font-medium">Billing &amp; subscription</p>
        <p className="max-w-sm text-xs text-muted-foreground">
          Manage your plan, usage, and payment method on the dedicated billing page.
        </p>
        <Button variant="gradient" asChild>
          <Link href="/billing">Go to Billing</Link>
        </Button>
      </CardContent>
    </Card>
  );
}
