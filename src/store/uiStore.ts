import { create } from 'zustand';

interface UIState {
  sidebarCollapsed: boolean;
  jobInputModalOpen: boolean;

  toggleSidebar: () => void;
  openJobInput: () => void;
  closeJobInput: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarCollapsed: false,
  jobInputModalOpen: false,

  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  openJobInput: () => set({ jobInputModalOpen: true }),
  closeJobInput: () => set({ jobInputModalOpen: false }),
}));
