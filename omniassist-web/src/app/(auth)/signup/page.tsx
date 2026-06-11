"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, Check } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { OAuthButtons, OrDivider } from "@/components/auth/oauth-buttons";
import { apiConfigured, useSignup } from "@/lib/api-hooks";
import { cn } from "@/lib/utils";

function passwordStrength(pw: string) {
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return score;
}

const strengthLabel = ["Too weak", "Weak", "Fair", "Good", "Strong"];
const strengthColor = ["bg-danger", "bg-danger", "bg-warning", "bg-info", "bg-success"];

export default function SignupPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [workspace, setWorkspace] = useState("");
  const signup = useSignup();
  const strength = useMemo(() => passwordStrength(password), [password]);
  const slug = workspace.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiConfigured()) {
      toast.success("Workspace created! Welcome to OmniAssist.");
      router.push("/dashboard");
      return;
    }
    try {
      await signup.mutateAsync({
        full_name: name,
        email,
        password,
        workspace_name: workspace,
      });
      toast.success("Workspace created! Welcome to OmniAssist.");
      router.push("/dashboard");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Sign up failed.");
    }
  };

  return (
    <div>
      <div className="mb-6 space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">Create your workspace</h1>
        <p className="text-sm text-muted-foreground">Start your free trial — no card required.</p>
      </div>

      <OAuthButtons />
      <OrDivider />

      <form onSubmit={onSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label htmlFor="name">Full name</Label>
            <Input id="name" placeholder="Priya Rao" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Work email</Label>
            <Input id="email" type="email" placeholder="priya@acme.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="workspace">Workspace name</Label>
          <Input
            id="workspace"
            placeholder="Acme Inc"
            value={workspace}
            onChange={(e) => setWorkspace(e.target.value)}
            required
          />
          {slug && (
            <p className="text-xs text-muted-foreground">
              omniassist.ai/<span className="text-foreground">{slug}</span>
            </p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {password && (
            <div className="space-y-1.5">
              <div className="flex gap-1">
                {[0, 1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className={cn(
                      "h-1 flex-1 rounded-full transition-colors",
                      i < strength ? strengthColor[strength] : "bg-secondary"
                    )}
                  />
                ))}
              </div>
              <p className="text-xs text-muted-foreground">{strengthLabel[strength]}</p>
            </div>
          )}
        </div>

        <label className="flex items-start gap-2 text-xs text-muted-foreground">
          <input type="checkbox" required className="mt-0.5 accent-[hsl(var(--primary))]" />
          I agree to the{" "}
          <Link href="/legal/terms" className="text-primary hover:underline">Terms</Link> and{" "}
          <Link href="/legal/privacy" className="text-primary hover:underline">Privacy Policy</Link>.
        </label>

        <Button type="submit" variant="gradient" className="w-full" loading={signup.isPending}>
          Create workspace <ArrowRight className="h-4 w-4" />
        </Button>
      </form>

      <div className="mt-5 flex items-center justify-center gap-4 text-xs text-muted-foreground">
        <span className="flex items-center gap-1"><Check className="h-3 w-3 text-success" /> Free 14-day trial</span>
        <span className="flex items-center gap-1"><Check className="h-3 w-3 text-success" /> No credit card</span>
      </div>

      <p className="mt-6 text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-primary hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
