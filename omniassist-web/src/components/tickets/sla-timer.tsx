"use client";

import { useEffect, useState } from "react";
import { Clock, AlarmClockOff } from "lucide-react";
import { cn } from "@/lib/utils";

export function SlaTimer({ dueAt }: { dueAt: string | null }) {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);

  if (!dueAt) {
    return <span className="text-xs text-muted-foreground">—</span>;
  }

  const diff = new Date(dueAt).getTime() - now;
  const breached = diff <= 0;
  const mins = Math.floor(Math.abs(diff) / 60000);
  const secs = Math.floor((Math.abs(diff) % 60000) / 1000);
  const atRisk = !breached && diff < 5 * 60 * 1000;

  const label =
    mins >= 60
      ? `${Math.floor(mins / 60)}h ${mins % 60}m`
      : `${mins}m ${String(secs).padStart(2, "0")}s`;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-xs font-medium tabular-nums",
        breached && "text-danger",
        atRisk && "text-warning",
        !breached && !atRisk && "text-muted-foreground"
      )}
    >
      {breached ? (
        <>
          <AlarmClockOff className="h-3.5 w-3.5" />
          Breached {label} ago
        </>
      ) : (
        <>
          <Clock className={cn("h-3.5 w-3.5", atRisk && "animate-pulse")} />
          {label}
        </>
      )}
    </span>
  );
}
