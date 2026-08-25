import { create } from 'zustand';
import type { WorkspaceId } from '@/core/domain/types';

interface UIStore {
  activeWorkspace: WorkspaceId;
  isLeftCollapsed: boolean;
  isRightCollapsed: boolean;
  isCommandPaletteOpen: boolean;
  isGlobalSearchOpen: boolean;
  zoomLevel: number;
  cursorPos: { x: number; y: number };
  highlightedTextIndex: number | null;
  setActiveWorkspace: (ws: WorkspaceId) => void;
  setLeftCollapsed: (v: boolean) => void;
  setRightCollapsed: (v: boolean) => void;
  setCommandPaletteOpen: (v: boolean) => void;
  setGlobalSearchOpen: (v: boolean) => void;
  setZoomLevel: (v: number | ((prev: number) => number)) => void;
  setCursorPos: (pos: { x: number; y: number }) => void;
  setHighlightedTextIndex: (idx: number | null) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  activeWorkspace: 'analysis',
  isLeftCollapsed: false,
  isRightCollapsed: false,
  isCommandPaletteOpen: false,
  isGlobalSearchOpen: false,
  zoomLevel: 100,
  cursorPos: { x: 0, y: 0 },
  highlightedTextIndex: null,
  setActiveWorkspace: (ws) => set({ activeWorkspace: ws }),
  setLeftCollapsed: (v) => set({ isLeftCollapsed: v }),
  setRightCollapsed: (v) => set({ isRightCollapsed: v }),
  setCommandPaletteOpen: (v) => set({ isCommandPaletteOpen: v }),
  setGlobalSearchOpen: (v) => set({ isGlobalSearchOpen: v }),
  setZoomLevel: (v) => set((s) => ({ zoomLevel: typeof v === 'function' ? v(s.zoomLevel) : v })),

  setCursorPos: (pos) => set({ cursorPos: pos }),
  setHighlightedTextIndex: (idx) => set({ highlightedTextIndex: idx }),
}));
