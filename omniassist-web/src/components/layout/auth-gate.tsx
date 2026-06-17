"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { apiConfigured } from "@/lib/api-hooks";

/**
 * Auth gate for the authenticated (app) route group. After mount (so the
 * persisted auth store has rehydrated and SSR matches), it requires a session
 * whenever a real backend is configured — unauthenticated visitors are
 * redirected to /login. In demo mode (no NEXT_PUBLIC_API_URL) the app is
 * intentionally open. Subsumes the old mount-only ClientGate.
 */
export function AuthGate({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);
  const router = useRouter();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const demo = !apiConfigured();

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (mounted && !demo && !isAuthenticated) {
      router.replace("/login");
    }
  }, [mounted, demo, isAuthenticated, router]);

  // Hold render until mounted, and (when a backend is configured) until a
  // session is confirmed — so protected pages never flash for logged-out users.
  if (!mounted || (!demo && !isAuthenticated)) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }
  return <>{children}</>;
}
