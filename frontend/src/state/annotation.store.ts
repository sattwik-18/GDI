import { create } from 'zustand';

export interface AnnotationEntry {
  id: string;
  objectId: string;
  objectLabel: string;
  note: string | null;
  createdAt: string;
}

interface AnnotationStore {
  bookmarks: AnnotationEntry[];
  notes: Map<string, string>;
  addBookmark: (entry: Omit<AnnotationEntry, 'id' | 'createdAt'>) => void;
  removeBookmark: (objectId: string) => void;
  isBookmarked: (objectId: string) => boolean;
  setNote: (objectId: string, note: string) => void;
  getNote: (objectId: string) => string | undefined;
}

export const useAnnotationStore = create<AnnotationStore>((set, get) => ({
  bookmarks: [],
  notes: new Map(),
  addBookmark: (entry) =>
    set((s) => ({
      bookmarks: [
        { ...entry, id: crypto.randomUUID(), createdAt: new Date().toISOString() },
        ...s.bookmarks.filter((b) => b.objectId !== entry.objectId),
      ],
    })),
  removeBookmark: (objectId) =>
    set((s) => ({ bookmarks: s.bookmarks.filter((b) => b.objectId !== objectId) })),
  isBookmarked: (objectId) => get().bookmarks.some((b) => b.objectId === objectId),
  setNote: (objectId, note) =>
    set((s) => { const m = new Map(s.notes); m.set(objectId, note); return { notes: m }; }),
  getNote: (objectId) => get().notes.get(objectId),
}));
