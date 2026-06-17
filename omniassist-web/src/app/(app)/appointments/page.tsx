"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  CalendarPlus, CalendarClock, CalendarDays, User, Stethoscope, Clock, UserPlus,
  Search, ChevronLeft, ChevronRight, CheckCircle2, XCircle, RotateCcw, UserX, List as ListIcon,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Breadcrumb } from "@/components/shared/breadcrumb";
import { IllustratedEmpty } from "@/components/shared/illustrated-empty";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Field, DemoNote } from "@/components/shared/form-bits";
import { ErrorState } from "@/components/shared/error-state";
import {
  useAppointments, useCreateAppointment, useUpdateAppointment,
  usePatients, useDoctors, apiConfigured, type AppointmentDTO,
} from "@/lib/api-hooks";
import { toast } from "sonner";

// ---------- status ----------
type Variant = React.ComponentProps<typeof Badge>["variant"];
const STATUS: Record<string, { label: string; variant: Variant; icon: typeof CheckCircle2 }> = {
  scheduled: { label: "Scheduled", variant: "info", icon: CalendarClock },
  completed: { label: "Completed", variant: "success", icon: CheckCircle2 },
  cancelled: { label: "Cancelled", variant: "danger", icon: XCircle },
  rescheduled: { label: "Rescheduled", variant: "warning", icon: RotateCcw },
  no_show: { label: "No-show", variant: "secondary", icon: UserX },
};
const STATUS_OPTS = ["scheduled", "completed", "cancelled", "rescheduled", "no_show"];

function StatusBadge({ status }: { status: string }) {
  const c = STATUS[status] ?? STATUS.scheduled;
  return (
    <Badge variant={c.variant} className="gap-1 shrink-0">
      <c.icon className="h-3 w-3" /> {c.label}
    </Badge>
  );
}

// ---------- date helpers ----------
const D = (iso: string) => new Date(iso);
const fmtDateTime = (iso: string) =>
  D(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
const fmtTime = (iso: string) => D(iso).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
const startOfDay = (d: Date) => { const x = new Date(d); x.setHours(0, 0, 0, 0); return x; };
const addDays = (d: Date, n: number) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
const sameDay = (a: Date, b: Date) =>
  a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
const toLocalInput = (iso: string) => {
  const d = D(iso); const p = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
};
const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export default function AppointmentsPage() {
  const { data: appts, isLoading, isError, refetch } = useAppointments();
  const update = useUpdateAppointment();

  const [bookOpen, setBookOpen] = useState(false);
  const [view, setView] = useState<"list" | "calendar">("list");
  const [calMode, setCalMode] = useState<"month" | "week" | "day">("month");
  const [cursor, setCursor] = useState<Date>(() => new Date());
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [dateFilter, setDateFilter] = useState("");
  const [reschedule, setReschedule] = useState<AppointmentDTO | null>(null);

  const list = appts ?? [];

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return list.filter((a) => {
      if (statusFilter !== "all" && a.status !== statusFilter) return false;
      if (dateFilter && !sameDay(D(a.scheduled_at), new Date(dateFilter + "T00:00"))) return false;
      if (q) {
        const hay = `${a.patient_name ?? ""} ${a.doctor_name ?? ""} ${a.id}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [list, query, statusFilter, dateFilter]);

  const upcoming = useMemo(
    () =>
      list
        .filter((a) => a.status === "scheduled" && D(a.scheduled_at).getTime() >= Date.now())
        .sort((a, b) => +D(a.scheduled_at) - +D(b.scheduled_at))
        .slice(0, 6),
    [list]
  );

  const hasFilters = query || statusFilter !== "all" || dateFilter;

  return (
    <div className="mx-auto max-w-[1400px] space-y-5 p-4 sm:p-6">
      <Breadcrumb items={[{ label: "Dashboard", href: "/dashboard" }, { label: "Appointments" }]} />

      <PageHeader title="Appointments" description="Book, track and reschedule patient appointments.">
        <Button variant="gradient" className="gap-2" onClick={() => setBookOpen(true)}>
          <CalendarPlus className="h-4 w-4" /> Book Appointment
        </Button>
      </PageHeader>

      {!apiConfigured() && <DemoNote />}

      {/* Toolbar */}
      <Card>
        <CardContent className="flex flex-col gap-3 p-3 lg:flex-row lg:items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search patient, doctor or appointment ID…"
              className="pl-9"
            />
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="h-9 w-[150px]"><SelectValue placeholder="Status" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All statuses</SelectItem>
                {STATUS_OPTS.map((s) => (
                  <SelectItem key={s} value={s} className="capitalize">{STATUS[s].label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="h-9 w-[150px]"
            />
            {hasFilters && (
              <Button variant="ghost" size="sm" onClick={() => { setQuery(""); setStatusFilter("all"); setDateFilter(""); }}>
                Clear
              </Button>
            )}
            {/* View toggle */}
            <div className="flex items-center rounded-lg border border-border-strong p-0.5">
              <ToggleBtn active={view === "list"} onClick={() => setView("list")} icon={ListIcon} label="List" />
              <ToggleBtn active={view === "calendar"} onClick={() => setView("calendar")} icon={CalendarDays} label="Calendar" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Content */}
      {isError ? (
        <ErrorState
          title="Couldn't load appointments"
          description="We couldn't reach your appointment schedule. Check your connection and try again."
          onRetry={() => refetch()}
        />
      ) : isLoading ? (
        view === "calendar" ? <CalendarSkeleton /> : <ListSkeleton />
      ) : list.length === 0 ? (
        <EmptyAppointments onBook={() => setBookOpen(true)} />
      ) : view === "calendar" ? (
        <CalendarView
          mode={calMode} setMode={setCalMode} cursor={cursor} setCursor={setCursor}
          items={list} onReschedule={setReschedule}
        />
      ) : (
        <div className="space-y-6">
          {upcoming.length > 0 && !hasFilters && (
            <UpcomingStrip items={upcoming} onReschedule={setReschedule} />
          )}
          <div>
            <h2 className="mb-3 text-sm font-semibold">
              {hasFilters ? `Results (${filtered.length})` : `All appointments (${filtered.length})`}
            </h2>
            {filtered.length === 0 ? (
              <Card className="border-dashed">
                <CardContent className="p-8 text-center text-sm text-muted-foreground">
                  No appointments match your filters.
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-3">
                {filtered.map((a, i) => (
                  <AppointmentRow
                    key={a.id} a={a} index={i}
                    onReschedule={() => setReschedule(a)}
                    onStatus={(s) => update.mutate({ id: a.id, status: s }, { onSuccess: () => toast.success("Updated"), onError: (e: Error) => toast.error(e.message || "Could not update status") })}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      <RescheduleDialog appt={reschedule} onClose={() => setReschedule(null)} />
      <BookDialog open={bookOpen} onOpenChange={setBookOpen} />
    </div>
  );
}

function ToggleBtn({ active, onClick, icon: Icon, label }: { active: boolean; onClick: () => void; icon: typeof ListIcon; label: string }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors ${
        active ? "bg-primary/15 text-primary" : "text-muted-foreground hover:text-foreground"
      }`}
    >
      <Icon className="h-3.5 w-3.5" /> <span className="hidden sm:inline">{label}</span>
    </button>
  );
}

// ---------- Upcoming cards ----------
function UpcomingStrip({ items, onReschedule }: { items: AppointmentDTO[]; onReschedule: (a: AppointmentDTO) => void }) {
  return (
    <div>
      <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold">
        <CalendarClock className="h-4 w-4 text-ai" /> Upcoming
      </h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {items.map((a, i) => (
          <motion.div key={a.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}>
            <Card interactive className="p-4">
              <div className="flex items-start justify-between gap-2">
                <span className="flex items-center gap-2">
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-ai">
                    <CalendarClock className="h-4 w-4 text-white" />
                  </span>
                  <span>
                    <p className="text-sm font-semibold leading-tight">{a.patient_name || "Patient"}</p>
                    <p className="text-xs text-muted-foreground">{fmtDateTime(a.scheduled_at)}</p>
                  </span>
                </span>
                <StatusBadge status={a.status} />
              </div>
              <div className="mt-3 flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Stethoscope className="h-3.5 w-3.5" /> {a.doctor_name ? `Dr. ${a.doctor_name}` : "Unassigned"}
                </span>
                <Button variant="secondary" size="sm" className="h-7 gap-1 text-xs" onClick={() => onReschedule(a)}>
                  <RotateCcw className="h-3 w-3" /> Reschedule
                </Button>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

// ---------- List row ----------
function AppointmentRow({ a, index, onReschedule, onStatus }: {
  a: AppointmentDTO; index: number; onReschedule: () => void; onStatus: (s: string) => void;
}) {
  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: Math.min(index * 0.03, 0.3) }}>
      <Card className="p-4">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
          <span className="flex items-center gap-2 font-medium">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-ai">
              <CalendarClock className="h-4 w-4 text-white" />
            </span>
            {fmtDateTime(a.scheduled_at)}
          </span>
          <span className="flex items-center gap-1.5 text-sm"><User className="h-4 w-4 text-muted-foreground" /> {a.patient_name || "Patient"}</span>
          <span className="flex items-center gap-1.5 text-sm"><Stethoscope className="h-4 w-4 text-muted-foreground" /> {a.doctor_name ? `Dr. ${a.doctor_name}` : "Unassigned"}</span>
          <span className="flex items-center gap-1.5 text-xs text-muted-foreground"><Clock className="h-3.5 w-3.5" /> {a.duration_min} min</span>
          <div className="ml-auto flex items-center gap-2">
            <StatusBadge status={a.status} />
            <Button variant="secondary" size="sm" className="h-8 gap-1 text-xs" onClick={onReschedule}>
              <RotateCcw className="h-3 w-3" /> Reschedule
            </Button>
            <Select value={STATUS[a.status] ? a.status : "scheduled"} onValueChange={onStatus}>
              <SelectTrigger className="h-8 w-[130px] text-xs"><SelectValue /></SelectTrigger>
              <SelectContent>
                {STATUS_OPTS.map((s) => <SelectItem key={s} value={s}>{STATUS[s].label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>
        {a.reason && <p className="mt-2 pl-11 text-sm text-muted-foreground">{a.reason}</p>}
      </Card>
    </motion.div>
  );
}

// ---------- Calendar ----------
function CalendarView({ mode, setMode, cursor, setCursor, items, onReschedule }: {
  mode: "month" | "week" | "day"; setMode: (m: "month" | "week" | "day") => void;
  cursor: Date; setCursor: (d: Date) => void; items: AppointmentDTO[]; onReschedule: (a: AppointmentDTO) => void;
}) {
  const onDay = (d: Date) =>
    items.filter((a) => sameDay(D(a.scheduled_at), d)).sort((a, b) => +D(a.scheduled_at) - +D(b.scheduled_at));

  const shift = (dir: number) => {
    if (mode === "month") setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + dir, 1));
    else if (mode === "week") setCursor(addDays(cursor, dir * 7));
    else setCursor(addDays(cursor, dir));
  };

  const label =
    mode === "day"
      ? cursor.toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long", year: "numeric" })
      : cursor.toLocaleDateString(undefined, { month: "long", year: "numeric" });

  return (
    <Card>
      <CardContent className="p-4">
        {/* Calendar header */}
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => shift(-1)}><ChevronLeft className="h-4 w-4" /></Button>
            <Button variant="ghost" size="sm" className="h-8" onClick={() => setCursor(new Date())}>Today</Button>
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => shift(1)}><ChevronRight className="h-4 w-4" /></Button>
            <span className="ml-2 text-sm font-semibold">{label}</span>
          </div>
          <div className="flex items-center rounded-lg border border-border-strong p-0.5">
            {(["month", "week", "day"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`rounded-md px-3 py-1.5 text-xs font-medium capitalize transition-colors ${
                  mode === m ? "bg-primary/15 text-primary" : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {m}
              </button>
            ))}
          </div>
        </div>

        {mode === "month" && <MonthGrid cursor={cursor} onDay={onDay} onReschedule={onReschedule} />}
        {mode === "week" && <WeekView cursor={cursor} onDay={onDay} onReschedule={onReschedule} />}
        {mode === "day" && <DayView cursor={cursor} onDay={onDay} onReschedule={onReschedule} />}
      </CardContent>
    </Card>
  );
}

function MonthGrid({ cursor, onDay, onReschedule }: { cursor: Date; onDay: (d: Date) => AppointmentDTO[]; onReschedule: (a: AppointmentDTO) => void }) {
  const first = new Date(cursor.getFullYear(), cursor.getMonth(), 1);
  const start = addDays(first, -first.getDay());
  const days = Array.from({ length: 42 }, (_, i) => addDays(start, i));
  const today = new Date();
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <div className="grid grid-cols-7 border-b border-border bg-subtle/40 text-center text-[11px] font-medium text-muted-foreground">
        {WEEKDAYS.map((d) => <div key={d} className="py-2">{d}</div>)}
      </div>
      <div className="grid grid-cols-7">
        {days.map((d, i) => {
          const inMonth = d.getMonth() === cursor.getMonth();
          const appts = onDay(d);
          const isToday = sameDay(d, today);
          return (
            <div key={i} className={`min-h-[84px] border-b border-r border-border p-1.5 last:border-r-0 ${inMonth ? "" : "bg-subtle/30"}`}>
              <div className={`mb-1 flex h-5 w-5 items-center justify-center rounded-full text-[11px] ${isToday ? "bg-primary font-semibold text-primary-foreground" : inMonth ? "text-foreground" : "text-muted-foreground"}`}>
                {d.getDate()}
              </div>
              <div className="space-y-1">
                {appts.slice(0, 2).map((a) => (
                  <button
                    key={a.id} onClick={() => onReschedule(a)}
                    className="block w-full truncate rounded bg-ai/10 px-1.5 py-0.5 text-left text-[10px] text-ai hover:bg-ai/20"
                  >
                    {fmtTime(a.scheduled_at)} {a.patient_name || "Patient"}
                  </button>
                ))}
                {appts.length > 2 && <p className="px-1 text-[10px] text-muted-foreground">+{appts.length - 2} more</p>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function WeekView({ cursor, onDay, onReschedule }: { cursor: Date; onDay: (d: Date) => AppointmentDTO[]; onReschedule: (a: AppointmentDTO) => void }) {
  const start = addDays(startOfDay(cursor), -cursor.getDay());
  const days = Array.from({ length: 7 }, (_, i) => addDays(start, i));
  const today = new Date();
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-7">
      {days.map((d, i) => {
        const appts = onDay(d);
        const isToday = sameDay(d, today);
        return (
          <div key={i} className="rounded-lg border border-border">
            <div className={`border-b border-border px-2 py-1.5 text-center text-xs font-medium ${isToday ? "text-primary" : "text-muted-foreground"}`}>
              {WEEKDAYS[d.getDay()]} {d.getDate()}
            </div>
            <div className="min-h-[60px] space-y-1 p-1.5">
              {appts.length === 0 ? (
                <p className="py-2 text-center text-[10px] text-muted-foreground">—</p>
              ) : appts.map((a) => (
                <button
                  key={a.id} onClick={() => onReschedule(a)}
                  className="block w-full truncate rounded bg-ai/10 px-1.5 py-1 text-left text-[10px] text-ai hover:bg-ai/20"
                >
                  {fmtTime(a.scheduled_at)} · {a.patient_name || "Patient"}
                </button>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function DayView({ cursor, onDay, onReschedule }: { cursor: Date; onDay: (d: Date) => AppointmentDTO[]; onReschedule: (a: AppointmentDTO) => void }) {
  const appts = onDay(cursor);
  if (appts.length === 0) {
    return <p className="py-12 text-center text-sm text-muted-foreground">No appointments on this day.</p>;
  }
  return (
    <div className="space-y-2">
      {appts.map((a) => (
        <div key={a.id} className="flex items-center gap-4 rounded-lg border border-border bg-subtle/40 p-3">
          <span className="w-16 shrink-0 text-sm font-semibold">{fmtTime(a.scheduled_at)}</span>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{a.patient_name || "Patient"}</p>
            <p className="text-xs text-muted-foreground">{a.doctor_name ? `Dr. ${a.doctor_name}` : "Unassigned"} · {a.duration_min} min</p>
          </div>
          <StatusBadge status={a.status} />
          <Button variant="secondary" size="sm" className="h-7 gap-1 text-xs" onClick={() => onReschedule(a)}>
            <RotateCcw className="h-3 w-3" /> Reschedule
          </Button>
        </div>
      ))}
    </div>
  );
}

// ---------- Reschedule ----------
function RescheduleDialog({ appt, onClose }: { appt: AppointmentDTO | null; onClose: () => void }) {
  const update = useUpdateAppointment();
  const [when, setWhen] = useState("");
  useEffect(() => { if (appt) setWhen(toLocalInput(appt.scheduled_at)); }, [appt]);

  const submit = () => {
    if (!appt) return;
    if (!when) return toast.error("Pick a new date & time");
    update.mutate(
      { id: appt.id, scheduled_at: new Date(when).toISOString(), status: "rescheduled" },
      { onSuccess: () => { toast.success("Appointment rescheduled"); onClose(); }, onError: (e: Error) => toast.error(e.message) }
    );
  };

  return (
    <Dialog open={!!appt} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader><DialogTitle>Reschedule appointment</DialogTitle></DialogHeader>
        {appt && (
          <div className="space-y-3">
            <div className="rounded-lg border border-border bg-subtle/40 p-3 text-sm">
              <p className="font-medium">{appt.patient_name || "Patient"}</p>
              <p className="text-xs text-muted-foreground">
                Current: {fmtDateTime(appt.scheduled_at)}{appt.doctor_name ? ` · Dr. ${appt.doctor_name}` : ""}
              </p>
            </div>
            <Field label="New date & time">
              <Input type="datetime-local" value={when} onChange={(e) => setWhen(e.target.value)} />
            </Field>
          </div>
        )}
        <DialogFooter>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button variant="gradient" onClick={submit} loading={update.isPending}>Reschedule</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// ---------- Empty state ----------
function EmptyAppointments({ onBook }: { onBook: () => void }) {
  return (
    <IllustratedEmpty
      src="/illustrations/appointments.svg"
      title="No appointments yet"
      description="Schedule your first appointment — pick a patient and doctor, choose a time, and you're set."
    >
      <Button variant="gradient" className="gap-2" onClick={onBook}>
        <CalendarPlus className="h-4 w-4" /> Book Appointment
      </Button>
    </IllustratedEmpty>
  );
}

// ---------- Skeletons ----------
function ListSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <Card key={i} className="p-4">
          <div className="flex items-center gap-4">
            <Skeleton className="h-9 w-9 rounded-lg" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-3.5 w-44" />
              <Skeleton className="h-3 w-60" />
            </div>
            <Skeleton className="h-6 w-24 rounded-full" />
            <Skeleton className="h-8 w-28 rounded-md" />
          </div>
        </Card>
      ))}
    </div>
  );
}

function CalendarSkeleton() {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="mb-4 flex items-center justify-between">
          <Skeleton className="h-8 w-44" />
          <Skeleton className="h-8 w-40" />
        </div>
        <div className="grid grid-cols-7 gap-px">
          {Array.from({ length: 42 }).map((_, i) => <Skeleton key={i} className="h-20 rounded-none" />)}
        </div>
      </CardContent>
    </Card>
  );
}

// ---------- Book dialog (controlled) ----------
function BookDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (o: boolean) => void }) {
  const create = useCreateAppointment();
  const { data: patients } = usePatients();
  const { data: doctors } = useDoctors();
  const [patientId, setPatientId] = useState("");
  const [doctorId, setDoctorId] = useState("");
  const [when, setWhen] = useState("");
  const [duration, setDuration] = useState("30");
  const [reason, setReason] = useState("");

  const submit = () => {
    if (!patientId) return toast.error("Select a patient");
    if (!when) return toast.error("Pick a date & time");
    create.mutate(
      {
        patient_id: patientId, doctor_id: doctorId || null,
        scheduled_at: new Date(when).toISOString(),
        duration_min: Number(duration) || 30, reason: reason || null,
      },
      {
        onSuccess: () => {
          toast.success("Appointment booked");
          setPatientId(""); setDoctorId(""); setWhen(""); setReason("");
          onOpenChange(false);
        },
        onError: (e: Error) => toast.error(e.message || "Could not book"),
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader><DialogTitle>Book Appointment</DialogTitle></DialogHeader>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Patient *" className="col-span-2">
            <Select value={patientId} onValueChange={setPatientId}>
              <SelectTrigger><SelectValue placeholder={patients?.length ? "Select patient" : "No patients yet"} /></SelectTrigger>
              <SelectContent>
                {(patients ?? []).map((p) => <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>)}
              </SelectContent>
            </Select>
            <Link href="/patients" className="mt-1 inline-flex items-center gap-1 text-xs text-ai hover:underline">
              <UserPlus className="h-3.5 w-3.5" /> {patients?.length ? "Add a new patient" : "No patients — add your first patient"}
            </Link>
          </Field>
          <Field label="Doctor" className="col-span-2">
            <Select value={doctorId} onValueChange={setDoctorId}>
              <SelectTrigger><SelectValue placeholder="Select doctor (optional)" /></SelectTrigger>
              <SelectContent>
                {(doctors ?? []).map((d) => <SelectItem key={d.id} value={d.id}>Dr. {d.name}{d.specialty ? ` · ${d.specialty}` : ""}</SelectItem>)}
              </SelectContent>
            </Select>
          </Field>
          <Field label="Date & time *">
            <Input type="datetime-local" value={when} onChange={(e) => setWhen(e.target.value)} />
          </Field>
          <Field label="Duration (min)">
            <Input type="number" min={5} step={5} value={duration} onChange={(e) => setDuration(e.target.value)} />
          </Field>
          <Field label="Reason / notes" className="col-span-2">
            <Textarea rows={2} value={reason} onChange={(e) => setReason(e.target.value)} placeholder="e.g. Follow-up for blood pressure" />
          </Field>
        </div>
        <DialogFooter>
          <Button variant="secondary" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button variant="gradient" onClick={submit} loading={create.isPending}>Book</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
