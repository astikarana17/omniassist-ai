"use client";

import { useEffect } from "react";
import Link from "next/link";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Surface for monitoring; replace with Sentry.captureException in prod.
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-5 bg-background px-6 text-center">
      <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-danger/10 text-danger ring-1 ring-danger/20">
        <AlertTriangle className="h-7 w-7" />
      </span>
      <div className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">Something went wrong</h1>
        <p className="max-w-sm text-sm text-muted-foreground">
          An unexpected error occurred. You can try again, or head back to safety.
        </p>
      </div>
      <div className="flex gap-3">
        <Button variant="gradient" onClick={reset}>Try again</Button>
        <Button variant="secondary" asChild>
          <Link href="/dashboard">Go to dashboard</Link>
        </Button>
      </div>
    </div>
  );
}
