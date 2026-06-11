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
  Check,
  ExternalLink,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const sections = [
  { key: "general", label: "General", icon: Settings2 },
  { key: "channels", label: "Channels", icon: Radio },
  { key: "ai", label: "AI Configuration", icon: Sparkles },
  { key: "notifications", label: "Notifications", icon: Bell },
  { key: "api", label: "API Keys", icon: KeyRound },
  { key: "billing", label: "Billing & Plan", icon: CreditCard },
  { key: "security", label: "Security", icon: ShieldCheck },
] as const;

type SectionKey = (typeof sections)[number]["key"];

export default function SettingsPage() {
  const [active, setActive] = useState<SectionKey>("general");

  return (
    <div className="mx-auto max-w-[1200px] space-y-6 p-4 sm:p-6">
      <PageHeader title="Settings" description="Configure your workspace, channels and security." />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[220px_1fr]">
        {/* Section nav */}
        <nav className="flex gap-1 overflow-x-auto no-scrollbar lg:flex-col">
          {sections.map((s) => (
            <button
              key={s.key}
              onClick={() => setActive(s.key)}
              className={cn(
                "flex shrink-0 items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                active === s.key ? "bg-primary/10 text-foreground ring-1 ring-primary/20" : "text-muted-foreground hover:bg-accent hover:text-foreground"
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

        {/* Content */}
        <div className="space-y-4">
          {active === "general" && <GeneralSection />}
          {active === "channels" && <ChannelsSection />}
          {active === "ai" && <AiSection />}
          {active === "notifications" && <NotificationsSection />}
          {active === "api" && <ApiSection />}
          {active === "billing" && <BillingSection />}
          {active === "security" && <SecuritySection />}
        </div>
      </div>
    </div>
  );
}

function GeneralSection() {
  return (
    <Card>
      <CardHeader><CardTitle className="text-base">Workspace</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label>Workspace name</Label>
          <Input defaultValue="Acme Inc" />
        </div>
        <div className="space-y-2">
          <Label>Workspace URL</Label>
          <div className="flex items-center">
            <span className="rounded-l-md border border-r-0 border-border-strong bg-secondary px-3 py-2 text-sm text-muted-foreground">omniassist.ai/</span>
            <Input defaultValue="acme" className="rounded-l-none" />
          </div>
        </div>
        <div className="space-y-2">
          <Label>Brand color</Label>
          <div className="flex gap-2">
            {["#6366F1", "#8B5CF6", "#22C55E", "#F59E0B", "#EF4444", "#22D3EE"].map((c, i) => (
              <button key={c} className={cn("h-8 w-8 rounded-full ring-2 ring-offset-2 ring-offset-background", i === 0 ? "ring-foreground" : "ring-transparent")} style={{ background: c }} />
            ))}
          </div>
        </div>
        <div className="flex justify-end">
          <Button variant="gradient" onClick={() => toast.success("Workspace saved")}>Save</Button>
        </div>
      </CardContent>
    </Card>
  );
}

const channels = [
  { key: "web", icon: Globe, label: "Website Chat", status: "connected", detail: "Widget installed" },
  { key: "whatsapp", icon: MessageCircle, label: "WhatsApp", status: "connected", detail: "+1 415 555 0132" },
  { key: "email", icon: Mail, label: "Email", status: "setup", detail: "Connect Gmail" },
  { key: "voice", icon: Phone, label: "Voice", status: "connected", detail: "+1 415 555 0199" },
];

function ChannelsSection() {
  return (
    <Card>
      <CardHeader><CardTitle className="text-base">Channels</CardTitle></CardHeader>
      <CardContent className="space-y-3">
        {channels.map((c) => (
          <div key={c.key} className="flex items-center gap-3 rounded-lg border border-border p-4">
            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
              <c.icon className="h-5 w-5" />
            </span>
            <div className="flex-1">
              <p className="text-sm font-medium">{c.label}</p>
              <p className="text-xs text-muted-foreground">{c.detail}</p>
            </div>
            {c.status === "connected" ? (
              <>
                <Badge variant="success" className="gap-1"><Check className="h-3 w-3" /> Connected</Badge>
                <Button size="sm" variant="secondary">Configure</Button>
              </>
            ) : (
              <>
                <Badge variant="warning">Setup needed</Badge>
                <Button size="sm" variant="gradient">Connect</Button>
              </>
            )}
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
      <CardContent className="space-y-1">
        {[
          { label: "Auto-respond on website chat", desc: "AI answers instantly before a human is needed.", on: true },
          { label: "Auto-send email replies", desc: "Send AI drafts without manual approval.", on: false },
          { label: "Cite knowledge sources", desc: "Always attach sources to factual answers.", on: true },
          { label: "Multi-language auto-detect", desc: "Reply in the customer's language.", on: true },
          { label: "Sentiment-based escalation", desc: "Escalate angry customers automatically.", on: true },
        ].map((o) => (
          <div key={o.label} className="flex items-center justify-between rounded-md px-2 py-3">
            <div>
              <p className="text-sm font-medium">{o.label}</p>
              <p className="text-xs text-muted-foreground">{o.desc}</p>
            </div>
            <Switch defaultChecked={o.on} />
          </div>
        ))}
        <div className="pt-2">
          <Button variant="ai" asChild><Link href="/agents/support"><Sparkles className="h-4 w-4" /> Open agent config</Link></Button>
        </div>
      </CardContent>
    </Card>
  );
}

function NotificationsSection() {
  return (
    <Card>
      <CardHeader><CardTitle className="text-base">Slack Notifications</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-3 rounded-lg border border-border p-4">
          <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary text-xl">💬</span>
          <div className="flex-1">
            <p className="text-sm font-medium">Slack workspace</p>
            <p className="text-xs text-muted-foreground">Connected to acme.slack.com · #support</p>
          </div>
          <Badge variant="success" className="gap-1"><Check className="h-3 w-3" /> Connected</Badge>
        </div>
        {[
          { label: "New handoff request", on: true },
          { label: "SLA breach warning", on: true },
          { label: "Low CSAT (≤ 2★)", on: true },
          { label: "New hot lead", on: true },
          { label: "Daily summary digest", on: false },
        ].map((o) => (
          <div key={o.label} className="flex items-center justify-between rounded-md px-2 py-1.5">
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

function SecuritySection() {
  return (
    <Card>
      <CardHeader><CardTitle className="text-base">Security</CardTitle></CardHeader>
      <CardContent className="space-y-1">
        {[
          { label: "Require 2FA for all members", desc: "Enforce two-factor across the workspace.", on: false },
          { label: "SSO / SAML", desc: "Single sign-on for enterprise.", on: false },
          { label: "Session timeout", desc: "Auto sign-out after 30 min idle.", on: true },
          { label: "IP allowlist", desc: "Restrict access to known IPs.", on: false },
          { label: "PII redaction in logs", desc: "Mask sensitive data before logging.", on: true },
        ].map((o) => (
          <div key={o.label} className="flex items-center justify-between rounded-md px-2 py-3">
            <div>
              <p className="text-sm font-medium">{o.label}</p>
              <p className="text-xs text-muted-foreground">{o.desc}</p>
            </div>
            <Switch defaultChecked={o.on} />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
