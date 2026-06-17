"use client";

import { useRef, useState, type DragEvent } from "react";
import { motion } from "framer-motion";
import {
  Upload,
  Pill,
  Loader2,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Stethoscope,
  Building2,
  CalendarDays,
  Clock,
  Utensils,
  ShieldAlert,
  Sparkles,
  FileText,
  ShieldCheck,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { relativeTime } from "@/lib/utils";
import { Breadcrumb } from "@/components/shared/breadcrumb";
import { IllustratedEmpty } from "@/components/shared/illustrated-empty";
import { toast } from "sonner";
import {
  usePrescriptions,
  usePrescription,
  useUploadPrescription,
  apiConfigured,
  type PrescriptionDTO,
  type RxExplanation,
} from "@/lib/api-hooks";

const MAX_MB = 15;

const statusBadge = {
  ready: { label: "Ready", variant: "success" as const, icon: CheckCircle2 },
  processing: { label: "Analyzing", variant: "warning" as const, icon: Loader2 },
  failed: { label: "Failed", variant: "danger" as const, icon: AlertCircle },
};

export default function PrescriptionsPage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  const upload = useUploadPrescription();
  const detail = usePrescription(activeId);
  const { data: history } = usePrescriptions();

  const active: PrescriptionDTO | null =
    detail.data && detail.data.id === activeId
      ? detail.data
      : upload.data && upload.data.id === activeId
        ? upload.data
        : null;

  const handleFile = (file?: File | null) => {
    if (!file) return;
    if (!apiConfigured()) {
      toast.error("Connect the backend (NEXT_PUBLIC_API_URL) to analyze prescriptions.");
      return;
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      toast.error(`File too large — max ${MAX_MB}MB.`);
      return;
    }
    upload.mutate(file, {
      onSuccess: (res) => {
        setActiveId(res.id);
        if (res.status === "ready") toast.success("Prescription analyzed");
        else if (res.status === "failed") toast.error(res.error ?? "Could not analyze this image");
      },
      onError: (e: Error) => toast.error(e.message || "Upload failed"),
    });
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files?.[0]);
  };

  return (
    <div className="mx-auto max-w-[1400px] space-y-5 p-4 sm:p-6">
      <Breadcrumb items={[{ label: "Dashboard", href: "/dashboard" }, { label: "Prescription AI" }]} />
      <PageHeader
        title="Prescription Intelligence"
        description="Upload a prescription — our AI reads it and explains every medicine in simple language."
      />

      {!apiConfigured() && (
        <Card className="border-warning/30 bg-warning/5">
          <CardContent className="flex items-center gap-3 p-4 text-sm">
            <AlertTriangle className="h-4 w-4 text-warning" />
            Demo mode — set <code className="rounded bg-secondary px-1">NEXT_PUBLIC_API_URL</code> to analyze real prescriptions.
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.6fr_1fr]">
        {/* Left: upload + result */}
        <div className="space-y-6">
          {/* Dropzone */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
            className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-10 text-center transition-colors ${
              dragging ? "border-ai bg-ai/5" : "border-border-strong bg-subtle/40 hover:border-ai/40"
            }`}
          >
            <input
              ref={inputRef}
              type="file"
              accept="image/png,image/jpeg,image/webp,application/pdf"
              className="hidden"
              onChange={(e) => handleFile(e.target.files?.[0])}
            />
            <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-ai">
              {upload.isPending ? (
                <Loader2 className="h-7 w-7 animate-spin text-white" />
              ) : (
                <Upload className="h-7 w-7 text-white" />
              )}
            </span>
            <p className="mt-4 text-sm font-medium">
              {upload.isPending ? "Reading your prescription…" : "Drop a prescription image or click to upload"}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">JPG, PNG, WEBP or PDF · up to {MAX_MB}MB</p>
            {upload.isPending && (
              <p className="mt-3 text-xs text-ai">OCR + medicine lookup + AI explanation — a few seconds…</p>
            )}
          </div>

          {/* Result */}
          {active && <PrescriptionResult rx={active} loading={detail.isFetching && !active} />}
          {!active && !upload.isPending && (
            <IllustratedEmpty
              src="/illustrations/prescriptions.svg"
              size="sm"
              title="Your analysis will appear here"
              description="Upload a prescription above and every medicine will be explained in simple language."
            />
          )}
        </div>

        {/* Right: history */}
        <div className="space-y-3">
          <h2 className="text-sm font-semibold">Recent prescriptions</h2>
          {!history || history.length === 0 ? (
            <Card className="border-dashed">
              <CardContent className="p-6 text-center text-xs text-muted-foreground">
                No prescriptions yet.
              </CardContent>
            </Card>
          ) : (
            history.map((h, i) => {
              const sb = statusBadge[h.status];
              const SIcon = sb.icon;
              return (
                <motion.div
                  key={h.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04 }}
                >
                  <Card
                    interactive
                    className={`p-3 ${activeId === h.id ? "ring-1 ring-ai" : ""}`}
                    onClick={() => setActiveId(h.id)}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="flex min-w-0 items-center gap-2">
                        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary">
                          <FileText className="h-4 w-4" />
                        </span>
                        <span className="min-w-0">
                          <p className="truncate text-sm font-medium">
                            {h.doctor_name || h.hospital_name || "Prescription"}
                          </p>
                          <p className="text-[11px] text-muted-foreground">
                            {h.medicine_count} medicine{h.medicine_count === 1 ? "" : "s"} · {relativeTime(h.created_at)}
                          </p>
                        </span>
                      </span>
                      <Badge variant={sb.variant} className="gap-1 shrink-0">
                        <SIcon className={`h-3 w-3 ${h.status === "processing" ? "animate-spin" : ""}`} />
                        {sb.label}
                      </Badge>
                    </div>
                  </Card>
                </motion.div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

function PrescriptionResult({ rx, loading }: { rx: PrescriptionDTO; loading: boolean }) {
  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center gap-2 p-6 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading…
        </CardContent>
      </Card>
    );
  }

  if (rx.status === "failed") {
    return (
      <Card className="border-danger/30 bg-danger/5">
        <CardContent className="flex items-start gap-3 p-5">
          <AlertCircle className="mt-0.5 h-5 w-5 text-danger" />
          <div>
            <p className="text-sm font-medium">Couldn&apos;t analyze this prescription</p>
            <p className="mt-1 text-xs text-muted-foreground">{rx.error || "Please try a clearer photo."}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (rx.status === "processing") {
    return (
      <Card>
        <CardContent className="flex items-center gap-2 p-6 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Still analyzing…
        </CardContent>
      </Card>
    );
  }

  const dosageFor = (name: string) =>
    rx.medicines.find((m) => m.name.toLowerCase() === name.toLowerCase());

  return (
    <div className="space-y-4">
      {/* Header */}
      <Card>
        <CardContent className="flex flex-wrap items-center gap-x-6 gap-y-2 p-4 text-sm">
          {rx.doctor_name && (
            <span className="flex items-center gap-1.5">
              <Stethoscope className="h-4 w-4 text-ai" /> {rx.doctor_name}
            </span>
          )}
          {rx.hospital_name && (
            <span className="flex items-center gap-1.5">
              <Building2 className="h-4 w-4 text-info" /> {rx.hospital_name}
            </span>
          )}
          {rx.prescribed_date && (
            <span className="flex items-center gap-1.5">
              <CalendarDays className="h-4 w-4 text-muted-foreground" /> {rx.prescribed_date}
            </span>
          )}
          <Badge variant="success" className="ml-auto gap-1">
            <CheckCircle2 className="h-3 w-3" /> {rx.analysis.length} medicine{rx.analysis.length === 1 ? "" : "s"} explained
          </Badge>
        </CardContent>
      </Card>

      {/* Medicines */}
      {rx.analysis.map((m, i) => (
        <MedicineCard key={`${m.name}-${i}`} m={m} dosage={dosageFor(m.name)} index={i} />
      ))}

      {/* Possible conditions */}
      {rx.possible_conditions.length > 0 && (
        <Card className="border-ai/20 bg-ai/5">
          <CardContent className="space-y-3 p-5">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-ai" />
              <h3 className="text-sm font-semibold">Possible conditions this may relate to</h3>
            </div>
            <p className="rounded-lg bg-warning/10 px-3 py-2 text-xs text-warning">
              <AlertTriangle className="mr-1 inline h-3.5 w-3.5" />
              This is an AI interpretation and <strong>not a medical diagnosis</strong>. Only your doctor can diagnose you.
            </p>
            {rx.possible_conditions.map((c, i) => (
              <div key={i} className="rounded-lg border border-border bg-card p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{c.condition}</span>
                  <span className="text-xs text-muted-foreground">{Math.round(c.confidence * 100)}% confidence</span>
                </div>
                <Progress value={Math.round(c.confidence * 100)} className="mt-2 h-1.5" />
                {c.explanation && <p className="mt-2 text-xs text-muted-foreground">{c.explanation}</p>}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Disclaimer */}
      <p className="flex items-start gap-2 rounded-lg border border-border bg-subtle/50 p-3 text-xs text-muted-foreground">
        <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0" />
        {rx.disclaimer}
      </p>
    </div>
  );
}

function Field({ icon: Icon, label, value }: { icon: typeof Clock; label: string; value?: string | null }) {
  if (!value) return null;
  return (
    <div className="flex items-start gap-2">
      <Icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
      <div>
        <p className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
        <p className="text-sm">{value}</p>
      </div>
    </div>
  );
}

function MedicineCard({
  m,
  dosage,
  index,
}: {
  m: RxExplanation;
  dosage?: { dosage?: string | null; frequency?: string | null; duration?: string | null; notes?: string | null };
  index: number;
}) {
  const dose = [dosage?.dosage, dosage?.frequency, dosage?.duration].filter(Boolean).join(" · ");
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.05 }}>
      <Card>
        <CardContent className="space-y-4 p-5">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-ai">
                <Pill className="h-5 w-5 text-white" />
              </span>
              <div>
                <p className="text-base font-semibold leading-tight">{m.name}</p>
                {m.generic_name && <p className="text-xs text-muted-foreground">{m.generic_name}</p>}
              </div>
            </div>
            {m.grounded ? (
              <Badge variant="success" className="gap-1">
                <ShieldCheck className="h-3 w-3" /> Verified
              </Badge>
            ) : (
              <Badge variant="secondary">General info</Badge>
            )}
          </div>

          {dose && (
            <p className="rounded-lg bg-ai/5 px-3 py-2 text-xs font-medium text-ai">As prescribed: {dose}</p>
          )}

          {m.what_it_is && <p className="text-sm">{m.what_it_is}</p>}

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Field icon={Sparkles} label="Why it's prescribed" value={m.why_prescribed} />
            <Field icon={Pill} label="How it works" value={m.how_it_works} />
            <Field icon={Clock} label="When to take" value={m.timing} />
            <Field icon={Utensils} label="Food" value={m.food_instructions} />
          </div>

          {m.side_effects && (
            <div className="rounded-lg border border-border bg-subtle/40 p-3">
              <p className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">Common side effects</p>
              <p className="mt-1 text-sm">{m.side_effects}</p>
            </div>
          )}

          {m.warnings && (
            <div className="flex items-start gap-2 rounded-lg border border-warning/30 bg-warning/5 p-3">
              <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-warning" />
              <p className="text-sm">{m.warnings}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
