import { Sidebar } from "@/components/layout/sidebar";
import { Navbar } from "@/components/layout/navbar";
import { CommandPalette } from "@/components/layout/command-palette";
import { CopilotPanel } from "@/components/layout/copilot-panel";
import { BottomNav } from "@/components/layout/bottom-nav";
import { ClientGate } from "@/components/layout/client-gate";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar />
        <main className="flex-1 overflow-y-auto pb-20 lg:pb-0">
          <ClientGate>{children}</ClientGate>
        </main>
      </div>
      <CommandPalette />
      <CopilotPanel />
      <BottomNav />
    </div>
  );
}
