"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { ArrowLeft, ArrowRight, KeyRound, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useResetPassword } from "@/lib/api-hooks";

function ResetInner() {
  const params = useSearchParams();
  const router = useRouter();
  const token = params.get("token") ?? "";
  const reset = useResetPassword();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password.length < 8) {
      toast.error("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirm) {
      toast.error("Passwords don't match.");
      return;
    }
    try {
      await reset.mutateAsync({ token, new_password: password });
      toast.success("Password updated. Please sign in.");
      router.replace("/login");
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "This reset link is invalid or has expired."
      );
    }
  };

  if (!token) {
    return (
      <div className="text-center">
        <h1 className="text-2xl font-semibold tracking-tight">Invalid reset link</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          This link is missing its token. Please request a new password reset.
        </p>
        <Button variant="secondary" className="mt-6 w-full" asChild>
          <Link href="/forgot-password">Request a new link</Link>
        </Button>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 space-y-1.5">
        <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary ring-1 ring-primary/20">
          <KeyRound className="h-6 w-6" />
        </div>
        <h1 className="text-2xl font-semibold tracking-tight">Set a new password</h1>
        <p className="text-sm text-muted-foreground">Choose a strong password for your account.</p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="password">New password</Label>
          <Input
            id="password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="confirm">Confirm password</Label>
          <Input
            id="confirm"
            type="password"
            placeholder="••••••••"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
          />
        </div>
        <Button type="submit" variant="gradient" className="w-full" loading={reset.isPending}>
          Update password <ArrowRight className="h-4 w-4" />
        </Button>
      </form>

      <Button variant="ghost" className="mt-4 w-full" asChild>
        <Link href="/login">
          <ArrowLeft className="h-4 w-4" /> Back to login
        </Link>
      </Button>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-[40vh] items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      }
    >
      <ResetInner />
    </Suspense>
  );
}
