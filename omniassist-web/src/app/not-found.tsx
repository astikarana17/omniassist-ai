import Link from "next/link";
import { Home, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/shared/logo";

export default function NotFound() {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-background p-6 text-center">
      <div className="pointer-events-none absolute inset-0 bg-gradient-mesh" />
      <div className="relative">
        <Logo />
      </div>
      <h1 className="relative mt-10 font-mono text-7xl font-semibold text-gradient">404</h1>
      <p className="relative mt-3 text-lg font-medium">Page not found</p>
      <p className="relative mt-1 max-w-sm text-sm text-muted-foreground">
        The page you&apos;re looking for doesn&apos;t exist or has been moved.
      </p>
      <div className="relative mt-8 flex gap-3">
        <Button variant="secondary" asChild>
          <Link href="/dashboard"><ArrowLeft className="h-4 w-4" /> Dashboard</Link>
        </Button>
        <Button variant="gradient" asChild>
          <Link href="/"><Home className="h-4 w-4" /> Home</Link>
        </Button>
      </div>
    </div>
  );
}
