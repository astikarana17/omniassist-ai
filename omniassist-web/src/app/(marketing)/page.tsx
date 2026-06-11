"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight,
  MessageSquare,
  Sparkles,
  Globe,
  Mail,
  Phone,
  MessageCircle,
  BookOpen,
  BarChart3,
  ShieldCheck,
  Zap,
  Check,
} from "lucide-react";
import { Logo } from "@/components/shared/logo";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ThemeToggle } from "@/components/shared/theme-toggle";
import { LiveDemo } from "@/components/marketing/live-demo";

const channels = [
  { icon: Globe, label: "Website Chat" },
  { icon: MessageCircle, label: "WhatsApp" },
  { icon: Mail, label: "Email" },
  { icon: Phone, label: "Voice" },
];

const features = [
  { icon: Sparkles, title: "AI Support & Sales Agents", desc: "RAG-grounded answers with sources and confidence, plus a sales agent that qualifies and books demos.", span: "lg:col-span-2" },
  { icon: BookOpen, title: "RAG Knowledge Base", desc: "Upload docs, crawl your site, sync FAQs — instantly searchable.", span: "" },
  { icon: ShieldCheck, title: "Human Handoff", desc: "Seamless AI → human with full context and presence.", span: "" },
  { icon: BarChart3, title: "Analytics", desc: "Deflection, CSAT, response time, revenue and sentiment in one place.", span: "lg:col-span-2" },
];

const stats = [
  { value: "70%+", label: "of questions resolvable by AI" },
  { value: "<5s", label: "typical first response" },
  { value: "4", label: "channels, one AI brain" },
  { value: "30+", label: "languages supported" },
];

const plans = [
  { name: "Starter", price: "$49", period: "/mo", desc: "For small teams getting started.", features: ["1 AI Support Agent", "Website chat", "1,000 conversations/mo", "Knowledge base (100 docs)", "Email support"], cta: "Start free trial", highlight: false },
  { name: "Growth", price: "$199", period: "/mo", desc: "For scaling support & sales.", features: ["Support + Sales agents", "Web + WhatsApp + Email", "10k conversations/mo", "Ticketing + workflows", "Full analytics + handoff"], cta: "Start free trial", highlight: true },
  { name: "Enterprise", price: "Custom", period: "", desc: "For large orgs with SLAs.", features: ["All channels incl. Voice", "Unlimited conversations", "SSO + RBAC + audit logs", "Dedicated CSM + SLA"], cta: "Contact sales", highlight: false },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <header className="sticky top-0 z-50 border-b border-border/60 bg-background/70 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
          <Logo />
          <nav className="hidden items-center gap-8 text-sm text-muted-foreground md:flex">
            <a href="#features" className="transition-colors hover:text-foreground">Features</a>
            <a href="#channels" className="transition-colors hover:text-foreground">Channels</a>
            <a href="#pricing" className="transition-colors hover:text-foreground">Pricing</a>
          </nav>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Button variant="ghost" size="sm" asChild>
              <Link href="/login">Login</Link>
            </Button>
            <Button variant="gradient" size="sm" asChild>
              <Link href="/signup">Start free</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        {/* Background video (behind the heading) — clear, full opacity */}
        <video
          autoPlay
          loop
          muted
          playsInline
          className="pointer-events-none absolute inset-0 h-full w-full object-cover"
        >
          <source src="/hero.mp4" type="video/mp4" />
        </video>
        {/* Light overlay just for heading readability */}
        <div className="pointer-events-none absolute inset-0 bg-background/45" />
        <div className="relative mx-auto max-w-4xl px-4 pb-20 pt-24 text-center">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <Badge variant="ai" className="mb-6 gap-1.5 px-3 py-1">
              <Sparkles className="h-3.5 w-3.5" />
              Powered by Claude + RAG
            </Badge>
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.05 }}
            className="text-balance text-4xl font-semibold tracking-tight sm:text-6xl"
          >
            The AI workforce for{" "}
            <span className="text-gradient">customer support & sales</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.12 }}
            className="mx-auto mt-6 max-w-2xl text-pretty text-lg text-muted-foreground"
          >
            One AI brain across chat, WhatsApp, email and voice — grounded in your
            knowledge, escalates to humans when it matters.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.18 }}
            className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row"
          >
            <Button variant="gradient" size="xl" asChild>
              <Link href="/signup">
                Start free <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button variant="secondary" size="xl" asChild>
              <Link href="/dashboard">
                <MessageSquare className="h-4 w-4" /> View live demo
              </Link>
            </Button>
          </motion.div>

          {/* Live product demo — real AI, no login */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.25 }}
            className="mx-auto mt-16 max-w-4xl"
          >
            <LiveDemo />
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-border bg-subtle/40">
        <div className="mx-auto grid max-w-5xl grid-cols-2 gap-8 px-4 py-12 md:grid-cols-4">
          {stats.map((s) => (
            <div key={s.label} className="text-center">
              <div className="font-mono text-3xl font-semibold text-gradient">{s.value}</div>
              <div className="mt-1 text-sm text-muted-foreground">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Channels */}
      <section id="channels" className="mx-auto max-w-5xl px-4 py-20 text-center">
        <h2 className="text-3xl font-semibold tracking-tight">Every channel. One brain.</h2>
        <p className="mx-auto mt-3 max-w-xl text-muted-foreground">
          Your customers reach you anywhere — OmniAssist answers everywhere, with the same knowledge and tone.
        </p>
        <div className="mt-10 grid grid-cols-2 gap-4 md:grid-cols-4">
          {channels.map((c, i) => (
            <motion.div
              key={c.label}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="rounded-xl border border-border bg-card p-6 transition-all hover:-translate-y-1 hover:border-primary/30 hover:shadow-glow-brand"
            >
              <c.icon className="mx-auto h-8 w-8 text-primary" />
              <p className="mt-3 text-sm font-medium">{c.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Features bento */}
      <section id="features" className="mx-auto max-w-5xl px-4 py-20">
        <div className="text-center">
          <h2 className="text-3xl font-semibold tracking-tight">Everything you need to scale</h2>
          <p className="mx-auto mt-3 max-w-xl text-muted-foreground">From first message to closed ticket and won deal.</p>
        </div>
        <div className="mt-12 grid grid-cols-1 gap-4 lg:grid-cols-3">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className={`group relative overflow-hidden rounded-2xl border border-border bg-card p-7 transition-colors hover:border-primary/30 ${f.span}`}
            >
              <div className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-gradient-brand opacity-0 blur-3xl transition-opacity group-hover:opacity-10" />
              <span className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-brand/10 text-primary ring-1 ring-primary/20">
                <f.icon className="h-5 w-5" />
              </span>
              <h3 className="mt-4 text-lg font-semibold">{f.title}</h3>
              <p className="mt-1.5 text-sm text-muted-foreground">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="mx-auto max-w-5xl px-4 py-20">
        <div className="text-center">
          <h2 className="text-3xl font-semibold tracking-tight">Simple, scalable pricing</h2>
          <p className="mx-auto mt-3 max-w-xl text-muted-foreground">Start free. Upgrade when you grow.</p>
        </div>
        <div className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-3">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative rounded-2xl border p-7 ${
                plan.highlight
                  ? "border-primary/40 bg-card shadow-glow-brand"
                  : "border-border bg-card"
              }`}
            >
              {plan.highlight && (
                <Badge variant="default" className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Zap className="h-3 w-3" /> Most popular
                </Badge>
              )}
              <h3 className="text-lg font-semibold">{plan.name}</h3>
              <p className="mt-1 text-sm text-muted-foreground">{plan.desc}</p>
              <div className="mt-4 flex items-end gap-1">
                <span className="font-mono text-4xl font-semibold">{plan.price}</span>
                <span className="mb-1 text-sm text-muted-foreground">{plan.period}</span>
              </div>
              <ul className="mt-6 space-y-2.5">
                {plan.features.map((feat) => (
                  <li key={feat} className="flex items-center gap-2 text-sm">
                    <Check className="h-4 w-4 text-success" />
                    {feat}
                  </li>
                ))}
              </ul>
              <Button
                variant={plan.highlight ? "gradient" : "secondary"}
                className="mt-7 w-full"
                asChild
              >
                <Link href="/signup">{plan.cta}</Link>
              </Button>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-5xl px-4 pb-24">
        <div className="relative overflow-hidden rounded-3xl border border-border-strong bg-gradient-brand p-12 text-center">
          <div className="pointer-events-none absolute inset-0 bg-gradient-mesh opacity-30" />
          <h2 className="relative text-3xl font-semibold text-white">Ready to deploy your AI workforce?</h2>
          <p className="relative mx-auto mt-3 max-w-lg text-white/80">
            Set up in minutes. No credit card required.
          </p>
          <Button variant="secondary" size="xl" className="relative mt-6 border-0" asChild>
            <Link href="/signup">
              Start free <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 py-8 sm:flex-row">
          <Logo />
          <p className="text-sm text-muted-foreground">© 2026 OmniAssist AI. All rights reserved.</p>
          <div className="flex gap-6 text-sm text-muted-foreground">
            <Link href="/legal/privacy" className="hover:text-foreground">Privacy</Link>
            <Link href="/legal/terms" className="hover:text-foreground">Terms</Link>
            <a href="mailto:sales@omniassist.ai" className="hover:text-foreground">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

