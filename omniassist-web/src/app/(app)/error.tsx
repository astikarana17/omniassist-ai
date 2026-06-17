"use client";

import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex h-full flex-col items-center justify-center gap-5 px-6 text-center">
      <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-danger/10 text-danger ring-1 ring-danger/20">
        <AlertTriangle className="h-6 w-6" />
      </span>
      <div className="space-y-1">
        <h2 className="text-lg font-semibold">This page hit an error</h2>
        <p className="max-w-sm text-sm text-muted-foreground">
          Something went wrong loading this section. Try again — the rest of the app is fine.
        </p>
      </div>
      <Button variant="gradient" onClick={reset}>Try again</Button>
    </div>
  );
}
