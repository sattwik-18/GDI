import { create } from 'zustand';
import type { InspectorMode } from '@/core/domain/types';

interface InspectorHistoryEntry {
  objectId: string;
  objectType: string;
  label: string;
  workspace: string;
}

interface InspectorStore {
  mode: InspectorMode;
  selectedObjectId: string | null;
  history: InspectorHistoryEntry[];
  bookmarkedIds: Set<string>;
  setMode: (mode: InspectorMode) => void;
  selectObject: (entry: InspectorHistoryEntry) => void;
  goBack: () => void;
  toggleBookmark: (id: string, label: string, type: string) => void;
  isBookmarked: (id: string) => boolean;
}

export const useInspectorStore = create<InspectorStore>((set, get) => ({
  mode: 'analyst',
  selectedObjectId: null,
  history: [],
  bookmarkedIds: new Set(),
  setMode: (mode) => set({ mode }),
  selectObject: (entry) =>
    set((s) => ({
      selectedObjectId: entry.objectId,
      history: [entry, ...s.history.filter((h) => h.objectId !== entry.objectId)].slice(0, 50),
    })),
  goBack: () =>
    set((s) => {
      const [, ...rest] = s.history;
      return { selectedObjectId: rest[0]?.objectId ?? null, history: rest };
    }),
  toggleBookmark: (id, label, type) =>
    set((s) => {
      const next = new Set(s.bookmarkedIds);
      if (next.has(id)) { next.delete(id); } else { next.add(id); }
      return { bookmarkedIds: next };
    }),
  isBookmarked: (id) => get().bookmarkedIds.has(id),
}));
