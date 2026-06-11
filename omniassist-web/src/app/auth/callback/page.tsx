"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, AlertCircle } from "lucide-react";
import { Logo } from "@/components/shared/logo";
import { Button } from "@/components/ui/button";
import { useOAuthCallback } from "@/lib/api-hooks";

function CallbackInner() {
  const params = useSearchParams();
  const router = useRouter();
  const oauth = useOAuthCallback();
  const [error, setError] = useState<string | null>(null);
  const ran = useRef(false);

  useEffect(() => {
    if (ran.current) return;
    ran.current = true;

    const code = params.get("code");
    const provider = params.get("state");
    if (params.get("error")) {
      setError("Sign-in was cancelled.");
      return;
    }
    if (!code || (provider !== "google" && provider !== "github")) {
      setError("Invalid sign-in callback.");
      return;
    }
    oauth.mutate(
      { provider, code },
      {
        onSuccess: () => router.replace("/dashboard"),
        onError: (e: unknown) =>
          setError(e instanceof Error ? e.message : "Sign-in failed. Please try again."),
      }
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 p-6 text-center">
      <Logo />
      {error ? (
        <>
          <AlertCircle className="h-8 w-8 text-danger" />
          <p className="text-sm text-muted-foreground">{error}</p>
          <Button variant="secondary" onClick={() => router.replace("/login")}>
            Back to login
          </Button>
        </>
      ) : (
        <>
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Signing you in…</p>
        </>
      )}
    </div>
  );
}

export default function OAuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      }
    >
      <CallbackInner />
    </Suspense>
  );
}
