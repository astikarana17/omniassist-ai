import { Sidebar } from "@/components/layout/sidebar";
import { Navbar } from "@/components/layout/navbar";
import { CommandPalette } from "@/components/layout/command-palette";
import { BottomNav } from "@/components/layout/bottom-nav";
import { AuthGate } from "@/components/layout/auth-gate";
import { AuroraBackground } from "@/components/shared/aurora-background";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex h-screen overflow-hidden">
      <AuroraBackground />
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar />
        <main className="flex-1 overflow-y-auto pb-20 lg:pb-0">
          <AuthGate>{children}</AuthGate>
        </main>
      </div>
      <CommandPalette />
      <BottomNav />
    </div>
  );
}
