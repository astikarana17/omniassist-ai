"use client";

import { Check, CreditCard, Sparkles, Zap, Building2 } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useBilling, useBillingPortal, useCheckout } from "@/lib/api-hooks";
import { cn } from "@/lib/utils";

const PLANS = [
  {
    id: "starter", name: "Starter", price: "$49", icon: Zap,
    blurb: "For small teams getting started.",
    features: ["1 AI Support Agent", "Website chat", "1,000 conversations/mo", "Knowledge base (100 docs)", "Email support"],
  },
  {
    id: "growth", name: "Growth", price: "$199", icon: Sparkles, highlight: true,
    blurb: "For growing teams.",
    features: ["All AI agents", "Web + WhatsApp + Email", "10,000 conversations/mo", "Ticketing + workflows", "Full analytics", "Up to 10 seats"],
  },
  {
    id: "enterprise", name: "Enterprise", price: "Custom", icon: Building2,
    blurb: "For large orgs.",
    features: ["All channels incl. Voice", "Unlimited conversations + seats", "SSO/SAML + audit logs", "Data residency", "Dedicated CSM + SLA"],
  },
];

export default function BillingPage() {
  const { data } = useBilling();
  const checkout = useCheckout();
  const portal = useBillingPortal();
  const plan = data?.plan ?? "free";
  const convoLimit = data?.limits.conversations ?? 100;
  const convoUsed = data?.usage.conversations ?? 0;
  const pct = convoLimit > 0 ? Math.min(100, Math.round((convoUsed / convoLimit) * 100)) : 0;

  return (
    <div className="mx-auto max-w-[1100px] space-y-6 p-4 sm:p-6">
      <PageHeader title="Billing & Plans" description="Manage your subscription and usage.">
        {data?.configured && plan !== "free" && (
          <Button variant="secondary" onClick={() => portal.mutate()} loading={portal.isPending}>
            <CreditCard className="h-4 w-4" /> Manage billing
          </Button>
        )}
      </PageHeader>

      {/* Current plan + usage */}
      <Card className="p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs text-muted-foreground">Current plan</p>
            <p className="mt-0.5 text-xl font-semibold capitalize">
              {plan} <Badge variant="ai" className="ml-1 align-middle">active</Badge>
            </p>
          </div>
          <div className="min-w-[220px] flex-1 sm:max-w-xs">
            <div className="mb-1 flex justify-between text-xs text-muted-foreground">
              <span>AI conversations this month</span>
              <span className="tabular-nums">
                {convoUsed.toLocaleString()} / {convoLimit < 0 ? "∞" : convoLimit.toLocaleString()}
              </span>
            </div>
            <Progress value={pct} className="h-2" />
          </div>
        </div>
        {!data?.configured && (
          <p className="mt-3 text-xs text-warning">
            ⚠ Stripe is not configured yet — set STRIPE_SECRET_KEY + price IDs to enable checkout.
          </p>
        )}
      </Card>

      {/* Plans */}
      <div className="grid gap-4 md:grid-cols-3">
        {PLANS.map((p) => {
          const current = p.id === plan;
          const Icon = p.icon;
          return (
            <Card
              key={p.id}
              className={cn("flex flex-col p-5", p.highlight && "border-primary/40 ring-1 ring-primary/20")}
            >
              <div className="flex items-center gap-2">
                <span className={cn("flex h-8 w-8 items-center justify-center rounded-md",
                  p.highlight ? "bg-gradient-brand text-white" : "bg-subtle")}>
                  <Icon className="h-4 w-4" />
                </span>
                <p className="font-semibold">{p.name}</p>
                {p.highlight && <Badge variant="default" className="ml-auto">Popular</Badge>}
              </div>
              <p className="mt-3 font-mono text-2xl font-medium">
                {p.price}
                {p.price !== "Custom" && <span className="text-sm text-muted-foreground">/mo</span>}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">{p.blurb}</p>
              <ul className="mt-4 flex-1 space-y-1.5 text-sm">
                {p.features.map((f) => (
                  <li key={f} className="flex items-start gap-2">
                    <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-success" /> {f}
                  </li>
                ))}
              </ul>
              <div className="mt-4">
                {current ? (
                  <Button variant="secondary" className="w-full" disabled>Current plan</Button>
                ) : p.id === "enterprise" ? (
                  <Button variant="secondary" className="w-full" asChild>
                    <a href="mailto:sales@omniassist.ai?subject=Enterprise%20plan">Contact sales</a>
                  </Button>
                ) : (
                  <Button
                    variant={p.highlight ? "gradient" : "secondary"}
                    className="w-full"
                    onClick={() => checkout.mutate(p.id)}
                    loading={checkout.isPending}
                  >
                    Upgrade to {p.name}
                  </Button>
                )}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
