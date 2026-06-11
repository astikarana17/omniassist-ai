"use client";

import type { TooltipProps } from "recharts";

export function ChartTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass rounded-lg px-3 py-2 text-xs shadow-lg">
      {label && <p className="mb-1 font-medium text-foreground">{label}</p>}
      <div className="space-y-0.5">
        {payload.map((entry) => (
          <div key={entry.dataKey as string} className="flex items-center gap-2">
            <span
              className="h-2 w-2 rounded-full"
              style={{ background: entry.color }}
            />
            <span className="capitalize text-muted-foreground">
              {entry.name ?? (entry.dataKey as string)}
            </span>
            <span className="ml-auto font-mono font-medium text-foreground">
              {typeof entry.value === "number"
                ? entry.value.toLocaleString()
                : entry.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
