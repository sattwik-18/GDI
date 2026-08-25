import { create } from 'zustand';

type BackendStatus = 'healthy' | 'degraded' | 'offline';

interface SystemStore {
  status: BackendStatus;
  isHealthy: boolean;
  latencyMs: number | null;
  cpuPercent: number | undefined;
  memoryMb: number | undefined;
  setHealth: (status: BackendStatus, latencyMs: number | null, cpu?: number, mem?: number) => void;
}

export const useSystemStore = create<SystemStore>((set) => ({
  status: 'healthy',
  isHealthy: true,
  latencyMs: null,
  cpuPercent: undefined,
  memoryMb: undefined,
  setHealth: (status, latencyMs, cpu, mem) =>
    set({ status, isHealthy: status !== 'offline', latencyMs, cpuPercent: cpu, memoryMb: mem }),
}));
