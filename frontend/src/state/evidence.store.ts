import { create } from 'zustand';
import type { EvidenceDef, EvidenceDomain, EvidenceStatus, ForensicImportance, EvidenceFilter } from '@/core/domain/types';

export interface IngestedEvidence {
  def: EvidenceDef;
  value: number | string | null;
  normalizedValue: number; // 0.0 to 1.0
  formattedValue: string;
  isImpossible: boolean;
  computedStatus: EvidenceStatus;
}

interface EvidenceState {
  evidenceMap: Record<string, IngestedEvidence>; // key: feature id
  evidenceList: IngestedEvidence[];
  activeEvidenceId: string | null;
  filter: EvidenceFilter;
  searchQuery: string;
  selectedDomain: EvidenceDomain | 'all';

  // Actions
  setIngestedEvidence: (list: IngestedEvidence[]) => void;
  setActiveEvidenceId: (id: string | null) => void;
  setFilter: (filter: EvidenceFilter) => void;
  setSearchQuery: (query: string) => void;
  setSelectedDomain: (domain: EvidenceDomain | 'all') => void;
  clearEvidence: () => void;
}

export const useEvidenceStore = create<EvidenceState>((set) => ({
  evidenceMap: {},
  evidenceList: [],
  activeEvidenceId: null,
  filter: {},
  searchQuery: '',
  selectedDomain: 'all',

  setIngestedEvidence: (list) => {
    const map: Record<string, IngestedEvidence> = {};
    for (const item of list) {
      map[item.def.id] = item;
    }
    set({ evidenceList: list, evidenceMap: map });
  },

  setActiveEvidenceId: (id) => set({ activeEvidenceId: id }),

  setFilter: (filter) => set({ filter }),

  setSearchQuery: (query) => set({ searchQuery: query }),

  setSelectedDomain: (domain) => set({ selectedDomain: domain }),

  clearEvidence: () => set({ evidenceList: [], evidenceMap: {}, activeEvidenceId: null }),
}));
