"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, ArrowRight, MailCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function ForgotPasswordPage() {
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setSent(true);
    }, 900);
  };

  if (sent) {
    return (
      <div className="text-center">
        <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-success/10 text-success ring-1 ring-success/20">
          <MailCheck className="h-6 w-6" />
        </div>
        <h1 className="text-2xl font-semibold tracking-tight">Check your email</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          We sent a password reset link to{" "}
          <span className="font-medium text-foreground">{email || "your email"}</span>.
        </p>
        <Button variant="secondary" className="mt-6 w-full" asChild>
          <Link href="/login">
            <ArrowLeft className="h-4 w-4" /> Back to login
          </Link>
        </Button>
        <button
          onClick={() => setSent(false)}
          className="mt-4 text-sm text-primary hover:underline"
        >
          Didn&apos;t get it? Resend
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">Reset password</h1>
        <p className="text-sm text-muted-foreground">
          Enter your email and we&apos;ll send you a reset link.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="priya@acme.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <Button type="submit" variant="gradient" className="w-full" loading={loading}>
          Send reset link <ArrowRight className="h-4 w-4" />
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
