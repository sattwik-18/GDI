import { create } from 'zustand';
import type { GenomeResponse, DebugInspectionResponse } from '@/types/gdi';
import { GenomeIngester } from '@/core/ingestion/GenomeIngester';
import { useEvidenceStore } from '@/state/evidence.store';

interface SessionStore {
  activeGenome: GenomeResponse | null;
  debugData: DebugInspectionResponse | null;
  uploadedFile: File | null;
  
  // Secondary comparison document state
  secondaryGenome: GenomeResponse | null;
  secondaryFile: File | null;
  isProcessingSecondary: boolean;
  secondaryError: string | null;

  recentGenomes: GenomeResponse[];
  isProcessing: boolean;
  processingError: string | null;

  setActiveGenome: (genome: GenomeResponse | null, debug: DebugInspectionResponse | null) => void;
  setUploadedFile: (file: File | null) => void;
  setSecondaryGenome: (genome: GenomeResponse | null, file?: File | null) => void;
  setSecondaryFile: (file: File | null) => void;
  setProcessingSecondary: (v: boolean) => void;
  setSecondaryError: (msg: string | null) => void;
  setProcessing: (v: boolean) => void;
  setError: (msg: string | null) => void;
  addRecentGenome: (genome: GenomeResponse) => void;
}

export const useSessionStore = create<SessionStore>((set) => ({
  activeGenome: null,
  debugData: null,
  uploadedFile: null,

  secondaryGenome: null,
  secondaryFile: null,
  isProcessingSecondary: false,
  secondaryError: null,

  recentGenomes: [],
  isProcessing: false,
  processingError: null,

  setActiveGenome: (genome, debug) => {
    set({ activeGenome: genome, debugData: debug });
    if (genome) {
      const items = GenomeIngester.ingest(genome, debug);
      useEvidenceStore.getState().setIngestedEvidence(items);
    } else {
      useEvidenceStore.getState().clearEvidence();
    }
  },
  setUploadedFile: (file) => set({ uploadedFile: file }),

  setSecondaryGenome: (genome, file) =>
    set((s) => ({
      secondaryGenome: genome,
      secondaryFile: file !== undefined ? file : s.secondaryFile,
    })),
  setSecondaryFile: (file) => set({ secondaryFile: file }),
  setProcessingSecondary: (v) => set({ isProcessingSecondary: v }),
  setSecondaryError: (msg) => set({ secondaryError: msg }),

  setProcessing: (v) => set({ isProcessing: v }),
  setError: (msg) => set({ processingError: msg }),
  addRecentGenome: (genome) =>
    set((s) => ({
      recentGenomes: [genome, ...s.recentGenomes.filter((g) => g.genome_id !== genome.genome_id)].slice(0, 20),
    })),
}));
