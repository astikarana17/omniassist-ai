import Link from "next/link";
import { Sparkles, ShieldCheck, Globe } from "lucide-react";
import { Logo } from "@/components/shared/logo";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* Brand panel */}
      <div className="relative hidden overflow-hidden border-r border-border bg-subtle lg:flex lg:flex-col lg:justify-between lg:p-12">
        <div className="pointer-events-none absolute inset-0 bg-gradient-mesh" />
        <div className="pointer-events-none absolute -left-20 top-1/3 h-72 w-72 rounded-full bg-primary/20 blur-[100px]" />
        <div className="pointer-events-none absolute right-0 top-0 h-72 w-72 rounded-full bg-ai/10 blur-[100px]" />

        <Link href="/" className="relative w-fit">
          <Logo />
        </Link>

        <div className="relative space-y-6">
          <h2 className="max-w-md text-3xl font-semibold leading-tight tracking-tight">
            Your customers always heard.{" "}
            <span className="text-gradient">Your team always ahead.</span>
          </h2>
          <p className="max-w-md text-muted-foreground">
            Deploy AI support and sales agents across every channel — grounded in
            your knowledge, escalating to humans when it matters.
          </p>
          <div className="flex flex-col gap-3 pt-2">
            {[
              { icon: Sparkles, text: "RAG-grounded answers with sources & confidence" },
              { icon: Globe, text: "Website, WhatsApp, Email & Voice in one inbox" },
              { icon: ShieldCheck, text: "Enterprise RBAC, audit logs & data isolation" },
            ].map((f) => (
              <div key={f.text} className="flex items-center gap-3 text-sm">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-card ring-1 ring-border">
                  <f.icon className="h-4 w-4 text-primary" />
                </span>
                {f.text}
              </div>
            ))}
          </div>
        </div>

        <div className="relative rounded-xl border border-border bg-card/60 p-4 backdrop-blur">
          <p className="text-sm italic text-muted-foreground">
            &ldquo;OmniAssist deflected 70% of our tickets in the first month — our
            team finally focuses on the conversations that matter.&rdquo;
          </p>
          <p className="mt-2 text-sm font-medium">— Head of CX, Acme Inc</p>
        </div>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center p-6">
        <div className="w-full max-w-sm">
          <div className="mb-8 lg:hidden">
            <Logo />
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
