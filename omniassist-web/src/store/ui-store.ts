import { create } from "zustand";
import { persist } from "zustand/middleware";

interface UiState {
  sidebarCollapsed: boolean;
  commandOpen: boolean;
  copilotOpen: boolean;
  notificationsOpen: boolean;
  toggleSidebar: () => void;
  setSidebar: (v: boolean) => void;
  setCommandOpen: (v: boolean) => void;
  toggleCommand: () => void;
  setCopilotOpen: (v: boolean) => void;
  toggleCopilot: () => void;
  setNotificationsOpen: (v: boolean) => void;
}

export const useUiStore = create<UiState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      commandOpen: false,
      copilotOpen: false,
      notificationsOpen: false,
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
      setSidebar: (v) => set({ sidebarCollapsed: v }),
      setCommandOpen: (v) => set({ commandOpen: v }),
      toggleCommand: () => set((s) => ({ commandOpen: !s.commandOpen })),
      setCopilotOpen: (v) => set({ copilotOpen: v }),
      toggleCopilot: () => set((s) => ({ copilotOpen: !s.copilotOpen })),
      setNotificationsOpen: (v) => set({ notificationsOpen: v }),
    }),
    {
      name: "omniassist-ui",
      partialize: (s) => ({ sidebarCollapsed: s.sidebarCollapsed }),
    }
  )
);
