import Link from "next/link";
import { Logo } from "@/components/shared/logo";

export default function LegalLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border/60">
        <div className="mx-auto flex h-16 max-w-3xl items-center justify-between px-4">
          <Link href="/">
            <Logo />
          </Link>
          <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">
            ← Back to home
          </Link>
        </div>
      </header>
      <main className="mx-auto max-w-3xl px-4 py-12">
        <article className="prose-sm space-y-4 text-sm leading-relaxed text-muted-foreground [&_h1]:text-2xl [&_h1]:font-semibold [&_h1]:text-foreground [&_h2]:mt-8 [&_h2]:text-lg [&_h2]:font-semibold [&_h2]:text-foreground [&_p]:mt-2 [&_strong]:text-foreground">
          {children}
        </article>
      </main>
      <footer className="border-t border-border py-8 text-center text-xs text-muted-foreground">
        © 2026 OmniAssist Health. All rights reserved.
      </footer>
    </div>
  );
}
