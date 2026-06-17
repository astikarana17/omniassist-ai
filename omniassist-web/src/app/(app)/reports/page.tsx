"use client";

import { useRef, useState, type DragEvent } from "react";
import { motion } from "framer-motion";
import {
  Upload,
  FlaskConical,
  Loader2,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  TrendingDown,
  Minus,
  Sparkles,
  FileText,
  ShieldAlert,
  Stethoscope,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Breadcrumb } from "@/components/shared/breadcrumb";
import { IllustratedEmpty } from "@/components/shared/illustrated-empty";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { relativeTime } from "@/lib/utils";
import { toast } from "sonner";
import {
  useReports,
  useReport,
  useUploadReport,
  apiConfigured,
  type MedicalReportDTO,
  type ReportValueDTO,
} from "@/lib/api-hooks";

const MAX_MB = 15;

const statusCfg: Record<
  string,
  { label: string; variant: React.ComponentProps<typeof Badge>["variant"]; icon: typeof Minus }
> = {
  normal: { label: "Normal", variant: "success", icon: CheckCircle2 },
  high: { label: "High", variant: "danger", icon: TrendingUp },
  low: { label: "Low", variant: "warning", icon: TrendingDown },
  borderline: { label: "Borderline", variant: "warning", icon: AlertTriangle },
  unknown: { label: "—", variant: "secondary", icon: Minus },
};

const listStatus = {
  ready: { label: "Ready", variant: "success" as const, icon: CheckCircle2 },
  processing: { label: "Analyzing", variant: "warning" as const, icon: Loader2 },
  failed: { label: "Failed", variant: "danger" as const, icon: AlertCircle },
};

export default function ReportsPage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  const upload = useUploadReport();
  const detail = useReport(activeId);
  const { data: history } = useReports();

  const active: MedicalReportDTO | null =
    detail.data && detail.data.id === activeId
      ? detail.data
      : upload.data && upload.data.id === activeId
        ? upload.data
        : null;

  const handleFile = (file?: File | null) => {
    if (!file) return;
    if (!apiConfigured()) {
      toast.error("Connect the backend (NEXT_PUBLIC_API_URL) to analyze reports.");
      return;
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      toast.error(`File too large — max ${MAX_MB}MB.`);
      return;
    }
    upload.mutate(file, {
      onSuccess: (res) => {
        setActiveId(res.id);
        if (res.status === "ready") toast.success("Report analyzed");
        else if (res.status === "failed") toast.error(res.error ?? "Could not analyze this report");
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
      <Breadcrumb items={[{ label: "Dashboard", href: "/dashboard" }, { label: "Report Analyzer" }]} />
      <PageHeader
        title="Medical Report Analyzer"
        description="Upload a lab report — our AI reads the values, flags what's off, and explains it simply."
      />

      {!apiConfigured() && (
        <Card className="border-warning/30 bg-warning/5">
          <CardContent className="flex items-center gap-3 p-4 text-sm">
            <AlertTriangle className="h-4 w-4 text-warning" />
            Demo mode — set <code className="rounded bg-secondary px-1">NEXT_PUBLIC_API_URL</code> to analyze real reports.
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.6fr_1fr]">
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
              {upload.isPending ? "Reading your report…" : "Drop a lab report or click to upload"}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">CBC, thyroid, sugar, lipid… · JPG, PNG or PDF · up to {MAX_MB}MB</p>
            {upload.isPending && (
              <p className="mt-3 text-xs text-ai">OCR + range check + plain-language explanation…</p>
            )}
          </div>

          {active && <ReportResult report={active} />}
          {!active && !upload.isPending && (
            <IllustratedEmpty
              src="/illustrations/reports.svg"
              size="sm"
              title="Your analysis will appear here"
              description="Upload a lab report above and the values, ranges and abnormalities will be explained."
            />
          )}
        </div>

        {/* History */}
        <div className="space-y-3">
          <h2 className="text-sm font-semibold">Recent reports</h2>
          {!history || history.length === 0 ? (
            <Card className="border-dashed">
              <CardContent className="p-6 text-center text-xs text-muted-foreground">
                No reports yet.
              </CardContent>
            </Card>
          ) : (
            history.map((h, i) => {
              const sb = listStatus[h.status];
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
                          <p className="truncate text-sm font-medium">{h.report_type || "Lab report"}</p>
                          <p className="text-[11px] text-muted-foreground">
                            {h.value_count} values · {h.abnormal_count} flagged · {relativeTime(h.created_at)}
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

function ReportResult({ report }: { report: MedicalReportDTO }) {
  if (report.status === "failed") {
    return (
      <Card className="border-danger/30 bg-danger/5">
        <CardContent className="flex items-start gap-3 p-5">
          <AlertCircle className="mt-0.5 h-5 w-5 text-danger" />
          <div>
            <p className="text-sm font-medium">Couldn&apos;t analyze this report</p>
            <p className="mt-1 text-xs text-muted-foreground">{report.error || "Please try a clearer photo."}</p>
          </div>
        </CardContent>
      </Card>
    );
  }
  if (report.status === "processing") {
    return (
      <Card>
        <CardContent className="flex items-center gap-2 p-6 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Still analyzing…
        </CardContent>
      </Card>
    );
  }

  const abnormal = report.values.filter((v) => ["high", "low", "borderline"].includes(v.status));

  return (
    <div className="space-y-4">
      {/* Header + summary */}
      <Card>
        <CardContent className="space-y-3 p-5">
          <div className="flex flex-wrap items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-ai">
              <FlaskConical className="h-5 w-5 text-white" />
            </span>
            <span className="text-base font-semibold">{report.report_type || "Lab Report"}</span>
            <Badge variant={abnormal.length ? "danger" : "success"} className="ml-auto gap-1">
              {abnormal.length ? `${abnormal.length} flagged` : "All normal"}
            </Badge>
          </div>
          {report.summary && (
            <p className="flex gap-2 rounded-lg bg-ai/5 p-3 text-sm">
              <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-ai" /> {report.summary}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Values table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-muted-foreground">
                  <th className="px-4 py-2.5 font-medium">Test</th>
                  <th className="px-4 py-2.5 font-medium">Result</th>
                  <th className="px-4 py-2.5 font-medium">Reference</th>
                  <th className="px-4 py-2.5 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {report.values.map((v, i) => (
                  <ValueRow key={`${v.test_name}-${i}`} v={v} />
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Findings for abnormal values */}
      {report.analysis.length > 0 && (
        <div className="space-y-3">
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <Stethoscope className="h-4 w-4 text-ai" /> What these mean
          </h3>
          {report.analysis.map((f, i) => {
            const cfg = statusCfg[f.status] ?? statusCfg.unknown;
            return (
              <motion.div
                key={`${f.test_name}-${i}`}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <Card>
                  <CardContent className="space-y-2 p-4">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold">{f.test_name}</span>
                      <Badge variant={cfg.variant} className="gap-1">
                        <cfg.icon className="h-3 w-3" /> {cfg.label}
                      </Badge>
                    </div>
                    {f.meaning && <p className="text-sm">{f.meaning}</p>}
                    {f.advice && (
                      <p className="flex items-start gap-2 rounded-lg bg-subtle/50 p-2 text-xs text-muted-foreground">
                        <Stethoscope className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {f.advice}
                      </p>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
      )}

      <p className="flex items-start gap-2 rounded-lg border border-border bg-subtle/50 p-3 text-xs text-muted-foreground">
        <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0" /> {report.disclaimer}
      </p>
    </div>
  );
}

function ValueRow({ v }: { v: ReportValueDTO }) {
  const cfg = statusCfg[v.status] ?? statusCfg.unknown;
  const abnormal = ["high", "low", "borderline"].includes(v.status);
  return (
    <tr className={`border-b border-border/60 last:border-0 ${abnormal ? "bg-danger/[0.03]" : ""}`}>
      <td className="px-4 py-2.5 font-medium">{v.test_name}</td>
      <td className="px-4 py-2.5">
        <span className={abnormal ? "font-semibold" : ""}>
          {v.value} {v.unit}
        </span>
      </td>
      <td className="px-4 py-2.5 text-muted-foreground">{v.reference_range || "—"}</td>
      <td className="px-4 py-2.5">
        <Badge variant={cfg.variant} className="gap-1">
          <cfg.icon className="h-3 w-3" /> {cfg.label}
        </Badge>
      </td>
    </tr>
  );
}
