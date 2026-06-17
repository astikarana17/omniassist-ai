"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Pill, FlaskConical, MessageCircleHeart, CalendarClock, UsersRound, Stethoscope,
  ArrowRight, ArrowUpRight, Sparkles, TrendingUp, Wand2,
} from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { AssistantAvatar } from "@/components/shared/assistant-avatar";
import { AnimatedCounter } from "@/components/shared/animated-counter";
import { useReveal } from "@/components/shared/use-reveal";
import {
  useClinicOverview, useAppointments, apiConfigured,
} from "@/lib/api-hooks";

const sameDay = (a: Date, b: Date) =>
  a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

// Premium button: subtle indigo gradient + inset top highlight.
const btn = "inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-b from-primary to-primary-hover text-sm font-medium text-primary-foreground shadow-sm ring-1 ring-inset ring-white/15 transition-all hover:brightness-110";

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  const firstName = mounted ? (user?.fullName ?? "there").split(" ")[0] : "there";
  const greet = mounted ? greeting() : "Welcome";

  const overview = useClinicOverview();
  const appointments = useAppointments();
  const ov = overview.data;
  const appts = appointments.data;
  const hasError = overview.isError || appointments.isError;
  const retry = () => { overview.refetch(); appointments.refetch(); };
  const reveal = useReveal<HTMLDivElement>();

  const upcoming = useMemo(
    () => {
      const now = Date.now();
      return (appts ?? [])
        .filter((a) => a.status === "scheduled" && new Date(a.scheduled_at).getTime() >= now)
        .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at))
        .slice(0, 4);
    },
    [appts]
  );

  const week = useMemo(() => {
    const days = Array.from({ length: 7 }, (_, i) => {
      const d = new Date(); d.setDate(d.getDate() - (6 - i)); d.setHours(0, 0, 0, 0); return d;
    });
    return days.map((d) => ({
      label: d.toLocaleDateString(undefined, { weekday: "short" }).slice(0, 1),
      full: d.toLocaleDateString(undefined, { weekday: "short" }),
      count: (appts ?? []).filter((a) => sameDay(new Date(a.scheduled_at), d)).length,
    }));
  }, [appts]);
  const weekMax = Math.max(1, ...week.map((w) => w.count));

  // Full literal class strings so Tailwind's JIT picks them up (no interpolation).
  const stats = [
    { label: "Patients", value: ov?.patients, icon: UsersRound, href: "/patients",
      glow: "from-indigo-500/25", iconCx: "from-indigo-500/25 to-indigo-500/5 text-indigo-400 ring-indigo-500/20" },
    { label: "Doctors", value: ov?.doctors, icon: Stethoscope, href: "/doctors",
      glow: "from-sky-500/25", iconCx: "from-sky-500/25 to-sky-500/5 text-sky-400 ring-sky-500/20" },
    { label: "Today", value: ov?.appointments_today, icon: CalendarClock, href: "/appointments",
      glow: "from-emerald-500/25", iconCx: "from-emerald-500/25 to-emerald-500/5 text-emerald-400 ring-emerald-500/20" },
    { label: "Prescriptions", value: ov?.prescriptions, icon: Pill, href: "/prescriptions",
      glow: "from-indigo-500/25", iconCx: "from-indigo-500/25 to-indigo-500/5 text-indigo-400 ring-indigo-500/20" },
    { label: "Reports", value: ov?.reports, icon: FlaskConical, href: "/reports",
      glow: "from-violet-500/25", iconCx: "from-violet-500/25 to-violet-500/5 text-violet-400 ring-violet-500/20" },
  ];

  const recommendations = useMemo(() => {
    const r: { icon: typeof Pill; text: string; href: string }[] = [];
    if ((ov?.appointments_upcoming ?? 0) > 0)
      r.push({ icon: CalendarClock, text: `${ov!.appointments_upcoming} upcoming appointment${ov!.appointments_upcoming === 1 ? "" : "s"} to prepare for.`, href: "/appointments" });
    if ((ov?.patients ?? 0) === 0)
      r.push({ icon: UsersRound, text: "Add your first patient to start booking visits.", href: "/patients" });
    if ((ov?.doctors ?? 0) === 0)
      r.push({ icon: Stethoscope, text: "Add the doctors in your clinic to assign appointments.", href: "/doctors" });
    r.push({ icon: Pill, text: "Upload a prescription — AI explains every medicine instantly.", href: "/prescriptions" });
    r.push({ icon: FlaskConical, text: "Analyze a lab report to flag abnormal values automatically.", href: "/reports" });
    return r.slice(0, 4);
  }, [ov]);

  const analyzed = (ov?.prescriptions ?? 0) + (ov?.reports ?? 0);

  return (
    <div ref={reveal} className="mx-auto max-w-[1320px] space-y-6 p-4 sm:p-6 lg:p-8">
      {/* Header */}
      <div data-reveal>
        <h1 className="text-[26px] font-semibold tracking-tight sm:text-[28px]">
          {greet}, <span className="text-gradient">{firstName}</span>
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">Here&apos;s your clinic, intelligently summarised.</p>
      </div>

      {hasError && (
        <div data-reveal className="flex flex-col items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm sm:flex-row sm:items-center sm:justify-between">
          <span className="text-muted-foreground">
            We couldn&apos;t load your live clinic data. Some numbers may be unavailable.
          </span>
          <button onClick={retry} className="font-medium text-danger hover:underline">Retry</button>
        </div>
      )}

      {!apiConfigured() && (
        <div data-reveal className="rounded-lg border border-warning/30 bg-warning/5 px-4 py-3 text-sm text-muted-foreground">
          Demo mode — set <code className="rounded bg-secondary px-1">NEXT_PUBLIC_API_URL</code> to see live clinic data.
        </div>
      )}

      {/* Hero + assistant */}
      <div data-reveal className="grid gap-5 lg:grid-cols-3">
        {/* Hero — subtle gradient edge + glow wash */}
        <div className="relative rounded-2xl bg-gradient-to-br from-primary/30 via-border/40 to-ai/20 p-px lg:col-span-2">
          <div className="relative h-full overflow-hidden rounded-2xl bg-card">
            <div className="pointer-events-none absolute -right-16 -top-20 h-60 w-60 rounded-full bg-primary/10 blur-3xl" />
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-primary/[0.05] via-transparent to-ai/[0.04]" />
            <div className="relative flex flex-col gap-5 p-6 sm:flex-row sm:items-center sm:p-7">
              <AssistantAvatar size={84} />
              <div className="flex-1">
                <span className="inline-flex items-center gap-1.5 rounded-md border border-border bg-secondary/60 px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
                  <Sparkles className="h-3 w-3 text-primary" /> AI Insight
                </span>
                <h2 className="mt-2.5 text-xl font-semibold tracking-tight sm:text-2xl">Your clinic is running smoothly.</h2>
                <p className="mt-1 max-w-xl text-sm text-muted-foreground">
                  {analyzed > 0 ? `${analyzed} document${analyzed === 1 ? "" : "s"} analysed by AI` : "Upload a prescription or report to see AI analysis"}
                  {upcoming.length > 0 ? ` · ${upcoming.length} upcoming appointment${upcoming.length === 1 ? "" : "s"}.` : "."}
                </p>
                <Link href="/health-assistant" className={`group mt-5 px-4 py-2 ${btn}`}>
                  Ask the AI assistant <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Assistant */}
        <div className="surface flex flex-col rounded-2xl p-5">
          <div className="flex items-center gap-3">
            <AssistantAvatar size={48} />
            <div>
              <p className="text-sm font-semibold">Aanya · Health AI</p>
              <p className="flex items-center gap-1.5 text-xs text-muted-foreground"><span className="h-1.5 w-1.5 rounded-full bg-success" /> Online</p>
            </div>
          </div>
          <div className="mt-4 space-y-1.5">
            {["Explain my prescription", "What is a normal sugar level?", "Side effects of Metformin?"].map((p, i) => (
              <Link key={i} href="/health-assistant" className="group flex items-center justify-between rounded-lg border border-border bg-secondary/40 px-3 py-2 text-xs text-muted-foreground transition-colors hover:border-primary/30 hover:text-foreground">
                {p} <ArrowUpRight className="h-3 w-3 opacity-0 transition-opacity group-hover:opacity-100" />
              </Link>
            ))}
          </div>
          <Link href="/health-assistant" className={`mt-4 w-full py-2.5 ${btn}`}>
            <MessageCircleHeart className="h-4 w-4" /> Start a conversation
          </Link>
        </div>
      </div>

      {/* Stat tiles */}
      <div data-reveal className="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-5">
        {stats.map((s) => (
          <Link key={s.label} href={s.href} className="group relative block">
            <div className={`absolute -inset-px rounded-2xl bg-gradient-to-b ${s.glow} to-transparent opacity-0 blur-[2px] transition-opacity duration-300 group-hover:opacity-100`} />
            <div className="surface relative rounded-2xl p-4 transition-transform duration-200 group-hover:-translate-y-[3px]">
              <span className={`flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br ring-1 ${s.iconCx}`}>
                <s.icon className="h-4 w-4" />
              </span>
              <p className="mt-3 text-[28px] font-semibold leading-none tabular-nums tracking-tight">
                <AnimatedCounter value={s.value} />
              </p>
              <p className="mt-1.5 text-xs text-muted-foreground">{s.label}</p>
            </div>
          </Link>
        ))}
      </div>

      {/* Analytics + recommendations */}
      <div data-reveal className="grid gap-5 lg:grid-cols-3">
        <div className="surface rounded-2xl p-5 lg:col-span-2">
          <div className="mb-5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-md bg-primary/10 text-primary"><TrendingUp className="h-3.5 w-3.5" /></span>
              <h2 className="text-sm font-semibold">Appointment activity</h2>
            </div>
            <span className="text-xs text-muted-foreground">Last 7 days</span>
          </div>
          <div className="flex h-36 items-end justify-between gap-3 sm:gap-5">
            {week.map((d, i) => (
              <div key={i} className="flex flex-1 flex-col items-center gap-2">
                <div className="flex w-full flex-1 items-end">
                  <motion.div
                    initial={{ height: 0 }} animate={{ height: `${(d.count / weekMax) * 100}%` }}
                    transition={{ delay: 0.25 + i * 0.05, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
                    className="w-full rounded-md bg-gradient-to-t from-primary/50 to-primary"
                    style={{ minHeight: d.count ? 6 : 2 }}
                    title={`${d.full}: ${d.count}`}
                  />
                </div>
                <span className="text-[10px] text-muted-foreground">{d.label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="surface rounded-2xl p-5">
          <div className="mb-3 flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-md bg-primary/10 text-primary"><Wand2 className="h-3.5 w-3.5" /></span>
            <h2 className="text-sm font-semibold">Recommendations</h2>
          </div>
          <div className="space-y-0.5">
            {recommendations.map((r, i) => (
              <Link key={i} href={r.href} className="group flex items-start gap-3 rounded-lg px-2 py-2 transition-colors hover:bg-secondary/60">
                <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
                  <r.icon className="h-3.5 w-3.5" />
                </span>
                <p className="flex-1 text-xs text-muted-foreground">{r.text}</p>
                <ArrowUpRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground/50 transition-all group-hover:translate-x-0.5 group-hover:text-primary" />
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Quick actions */}
      <div data-reveal className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { href: "/prescriptions", icon: Pill, title: "Prescription AI", desc: "Explain medicines" },
          { href: "/reports", icon: FlaskConical, title: "Report Analyzer", desc: "Flag abnormalities" },
          { href: "/health-assistant", icon: MessageCircleHeart, title: "Health Assistant", desc: "Ask anything" },
          { href: "/appointments", icon: CalendarClock, title: "Appointments", desc: "Book & manage" },
        ].map((q) => (
          <Link key={q.href} href={q.href} className="surface group flex items-center gap-3 rounded-2xl p-4 transition-all duration-200 hover:-translate-y-[3px] hover:border-primary/20">
            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-primary/25 to-primary/5 text-primary ring-1 ring-primary/20">
              <q.icon className="h-5 w-5" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium">{q.title}</p>
              <p className="text-xs text-muted-foreground">{q.desc}</p>
            </div>
            <ArrowRight className="h-4 w-4 text-muted-foreground/50 transition-all group-hover:translate-x-0.5 group-hover:text-primary" />
          </Link>
        ))}
      </div>

      {/* Upcoming */}
      <div data-reveal className="surface rounded-2xl p-5">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold">Upcoming appointments</h2>
          <Link href="/appointments" className="text-xs font-medium text-primary hover:underline">View all</Link>
        </div>
        {upcoming.length === 0 ? (
          <p className="py-6 text-center text-sm text-muted-foreground">No upcoming appointments.</p>
        ) : (
          <div className="grid gap-2 sm:grid-cols-2">
            {upcoming.map((a) => (
              <div key={a.id} className="flex items-center gap-3 rounded-lg border border-border bg-secondary/30 p-3 transition-colors hover:border-primary/20">
                <span className="flex h-10 w-10 shrink-0 flex-col items-center justify-center rounded-md bg-gradient-to-br from-primary/25 to-primary/5 text-primary ring-1 ring-primary/15">
                  <span className="text-xs font-bold leading-none">{new Date(a.scheduled_at).toLocaleDateString(undefined, { day: "2-digit" })}</span>
                  <span className="text-[8px] uppercase leading-none">{new Date(a.scheduled_at).toLocaleDateString(undefined, { month: "short" })}</span>
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">{a.patient_name || "Patient"}</p>
                  <p className="text-xs text-muted-foreground">
                    {a.doctor_name ? `Dr. ${a.doctor_name} · ` : ""}
                    {new Date(a.scheduled_at).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
