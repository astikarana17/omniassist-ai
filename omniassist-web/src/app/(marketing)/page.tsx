"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Sparkles,
  Pill,
  FlaskConical,
  MessageCircleHeart,
  Database,
  ShieldCheck,
  Stethoscope,
  HeartPulse,
  Check,
  Zap,
} from "lucide-react";
import { Logo } from "@/components/shared/logo";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ThemeToggle } from "@/components/shared/theme-toggle";
import { LiveDemo } from "@/components/marketing/live-demo";
import { StackCard, FadeIn } from "@/components/marketing/stacking-cards";

const capabilities = [
  { icon: Pill, label: "Prescription AI" },
  { icon: FlaskConical, label: "Report Analyzer" },
  { icon: MessageCircleHeart, label: "Health Assistant" },
  { icon: Database, label: "Medicine Intelligence" },
];

const features = [
  { icon: Pill, title: "Prescription Intelligence", desc: "Upload a prescription photo — every medicine explained simply: what it's for, how it works, side effects, timing and food notes.", illo: "/illustrations/prescriptions.svg", tag: "Prescriptions" },
  { icon: FlaskConical, title: "Medical Report Analyzer", desc: "CBC, thyroid, sugar, lipid — values extracted, abnormalities flagged, explained in plain words.", illo: "/illustrations/reports.svg", tag: "Lab reports" },
  { icon: MessageCircleHeart, title: "AI Health Assistant", desc: "Ask about a medicine, symptom or result — clear answers, never a diagnosis.", illo: "/illustrations/assistant.svg", tag: "Assistant" },
  { icon: Database, title: "Medicine Intelligence", desc: "Brand → composition intelligence grounds every answer, so Azithral is understood as Azithromycin automatically.", illo: "/illustrations/doctors.svg", tag: "Knowledge base" },
];

const stats = [
  { value: "Free", label: "for patients — no card needed" },
  { value: "Minutes", label: "to understand a prescription or report" },
  { value: "3", label: "AI tools: Rx · Reports · Assistant" },
  { value: "24/7", label: "health answers, anytime" },
];

const plans = [
  { name: "Patient", price: "Free", period: "", desc: "Understand your own care.", features: ["Prescription AI", "Medical Report Analyzer", "AI Health Assistant", "10 uploads / month"], cta: "Start free", highlight: false },
  { name: "Clinic", price: "$99", period: "/mo", desc: "For clinics & individual doctors.", features: ["Everything in Patient", "Patient & doctor management", "Appointment booking", "Unlimited uploads", "Priority support"], cta: "Start free trial", highlight: true },
  { name: "Hospital", price: "Custom", period: "", desc: "For hospitals & networks.", features: ["Multi-department & branches", "SSO + RBAC + audit logs", "Dedicated success manager", "SLA & onboarding"], cta: "Contact sales", highlight: false },
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
            <a href="#capabilities" className="transition-colors hover:text-foreground">Capabilities</a>
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
        <video
          autoPlay
          loop
          muted
          playsInline
          className="pointer-events-none absolute inset-0 h-full w-full object-cover"
        >
          <source src="/hero_section_video.mp4" type="video/mp4" />
        </video>
        {/* no tint over the video — keep its true colors; only a thin bottom fade to blend into the page */}
        <div className="pointer-events-none absolute inset-x-0 bottom-0 h-24 bg-gradient-to-b from-transparent to-background" />
        <div className="relative mx-auto max-w-4xl px-4 pb-20 pt-24 text-center">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <Badge variant="ai" className="mb-6 gap-1.5 px-3 py-1">
              <HeartPulse className="h-3.5 w-3.5" />
              Healthcare AI Copilot · Powered by Claude
            </Badge>
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.05 }}
            className="text-balance text-4xl font-semibold tracking-tight text-white drop-shadow-[0_2px_14px_rgba(0,0,0,0.9)] sm:text-6xl"
          >
            Understand your health,{" "}
            <span className="text-gradient">in plain language</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.12 }}
            className="mx-auto mt-6 max-w-2xl text-pretty text-lg text-white drop-shadow-[0_1px_10px_rgba(0,0,0,0.95)]"
          >
            Upload a prescription or lab report and get a clear, simple explanation of every
            medicine and result — plus an AI assistant for your health questions.
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
                <Stethoscope className="h-4 w-4" /> View live demo
              </Link>
            </Button>
          </motion.div>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="mx-auto mt-4 flex items-center justify-center gap-1.5 text-xs text-white/75 drop-shadow-[0_1px_8px_rgba(0,0,0,0.55)]"
          >
            <ShieldCheck className="h-3.5 w-3.5" /> AI-powered health information — not a diagnosis. Always consult a qualified doctor.
          </motion.p>

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

      {/* Capabilities */}
      <section id="capabilities" className="mx-auto max-w-5xl px-4 py-20 text-center">
        <h2 className="text-3xl font-semibold tracking-tight">One copilot for your whole health journey</h2>
        <p className="mx-auto mt-3 max-w-xl text-muted-foreground">
          From the pharmacy counter to your lab results — clear, grounded answers, instantly.
        </p>
        <div className="mt-10 grid grid-cols-2 gap-4 md:grid-cols-4">
          {capabilities.map((c, i) => (
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

      {/* Features — sticky-stacking deck (scroll to stack the cards) */}
      <section id="features" className="mx-auto max-w-5xl px-4 py-20">
        <div className="text-center">
          <h2 className="text-3xl font-semibold tracking-tight">Everything to understand your care</h2>
          <p className="mx-auto mt-3 max-w-xl text-muted-foreground">From prescription to report to question — explained simply.</p>
        </div>
        <div className="mt-14 space-y-8 pb-[18vh]">
          {features.map((f, i) => (
            <StackCard
              key={f.title}
              index={i}
              total={features.length}
              className="relative mx-auto flex min-h-[74vh] max-w-5xl flex-col justify-between gap-8 overflow-hidden rounded-[44px] border-2 border-border-strong/70 bg-card p-9 shadow-[0_30px_80px_-30px_hsl(222_47%_2%/0.7)] sm:p-12 lg:flex-row lg:items-center lg:gap-10"
            >
              {/* subtle brand wash so stacked cards read with depth */}
              <div aria-hidden className="pointer-events-none absolute -left-16 -top-16 h-64 w-64 rounded-full bg-gradient-brand opacity-[0.07] blur-3xl" />
              {/* left — copy */}
              <FadeIn className="relative lg:max-w-md">
                <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-gradient-brand/10 px-3 py-1 text-xs font-medium text-primary">
                  <f.icon className="h-3.5 w-3.5" /> {f.tag}
                </span>
                <h3 className="mt-6 text-3xl font-semibold tracking-tight sm:text-4xl">{f.title}</h3>
                <p className="mt-4 text-lg text-muted-foreground">{f.desc}</p>
                <div className="mt-7">
                  <Button variant="secondary" size="lg" asChild>
                    <Link href="/signup">
                      Try it free <ArrowRight className="h-4 w-4" />
                    </Link>
                  </Button>
                </div>
              </FadeIn>
              {/* right — illustration */}
              <FadeIn delay={0.12} className="relative flex flex-1 items-center justify-center">
                <div aria-hidden className="absolute inset-0 m-auto h-3/4 w-3/4 rounded-full bg-gradient-brand opacity-[0.06] blur-3xl" />
                <img
                  src={f.illo}
                  alt=""
                  aria-hidden
                  draggable={false}
                  className="relative max-h-[40vh] w-auto select-none object-contain drop-shadow-[0_18px_40px_rgba(79,70,229,0.18)]"
                />
              </FadeIn>
            </StackCard>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="mx-auto max-w-5xl px-4 py-20">
        <div className="text-center">
          <h2 className="text-3xl font-semibold tracking-tight">Simple, scalable pricing</h2>
          <p className="mx-auto mt-3 max-w-xl text-muted-foreground">Free for patients. Plans for clinics and hospitals.</p>
        </div>
        <div className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-3">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative rounded-2xl border p-7 ${
                plan.highlight ? "border-primary/40 bg-card shadow-glow-brand" : "border-border bg-card"
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
              <Button variant={plan.highlight ? "gradient" : "secondary"} className="mt-7 w-full" asChild>
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
          <h2 className="relative text-3xl font-semibold text-white">Ready to make healthcare simple?</h2>
          <p className="relative mx-auto mt-3 max-w-lg text-white/80">
            Understand your prescriptions and reports in seconds. No credit card required.
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
          <p className="text-center text-xs text-muted-foreground sm:text-sm">
            © 2026 OmniAssist Health · Not a substitute for professional medical advice.
          </p>
          <div className="flex gap-6 text-sm text-muted-foreground">
            <Link href="/legal/privacy" className="hover:text-foreground">Privacy</Link>
            <Link href="/legal/terms" className="hover:text-foreground">Terms</Link>
            <a href="mailto:hello@omniassist.health" className="hover:text-foreground">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
