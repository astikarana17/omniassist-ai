"use client";

import { AlertTriangle, RotateCw } from "lucide-react";
import { Button } from "@/components/ui/button";

/** Inline "failed to load" state with a retry — use when a data query errors so
 *  a fetch failure isn't misrepresented as an empty list. */
export function ErrorState({
  title = "Couldn't load this",
  description = "Something went wrong fetching your data. Please try again.",
  onRetry,
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-border bg-card px-6 py-14 text-center">
      <span className="flex h-12 w-12 items-center justify-center rounded-full bg-danger/10 text-danger ring-1 ring-danger/20">
        <AlertTriangle className="h-6 w-6" />
      </span>
      <div>
        <p className="font-medium">{title}</p>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">{description}</p>
      </div>
      {onRetry && (
        <Button variant="secondary" onClick={onRetry}>
          <RotateCw className="h-4 w-4" /> Retry
        </Button>
      )}
    </div>
  );
}
