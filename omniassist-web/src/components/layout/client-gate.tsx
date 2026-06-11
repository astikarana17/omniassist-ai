"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

/**
 * Renders children only after the client has mounted. The authenticated app is
 * fully client-driven (auth store, live data, locale/relative times), so SSR of
 * page content only causes hydration mismatches with no SEO benefit. Gating once
 * here fixes every app page; after the first mount it stays mounted across
 * client-side navigation, so there is no per-navigation flash.
 */
export function ClientGate({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  if (!mounted) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }
  return <>{children}</>;
}
