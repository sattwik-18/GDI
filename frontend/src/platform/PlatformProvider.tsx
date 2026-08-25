'use client';

/**
 * GDI Platform v2 - PlatformProvider
 *
 * Root context provider for the Evidence-Centric architecture.
 * Wraps the entire application. Initializes health polling and
 * migrates page-level state into Zustand stores.
 *
 * Usage: wrap <body> or top-level layout with <PlatformProvider>
 */

import React, { useEffect, useRef } from 'react';
import { GDIClient } from '@/services/api';
import { useSystemStore } from '@/state/system.store';

interface PlatformProviderProps {
  children: React.ReactNode;
}

export const PlatformProvider: React.FC<PlatformProviderProps> = ({ children }) => {
  const setHealth = useSystemStore((s) => s.setHealth);
  const isMounted = useRef(true);

  useEffect(() => {
    isMounted.current = true;

    const checkBackend = async () => {
      const start = performance.now();
      try {
        const health = await GDIClient.getHealth();
        const latency = Math.max(1, Math.round(performance.now() - start));
        if (!isMounted.current) return;

        const status =
          health.status === 'healthy' || health.status === 'degraded'
            ? (health.status as 'healthy' | 'degraded')
            : 'offline';

        const cpu =
          typeof health.components?.api?.details?.cpu_percent === 'number'
            ? health.components.api.details.cpu_percent
            : undefined;
        const mem =
          typeof health.components?.api?.details?.memory_mb === 'number'
            ? health.components.api.details.memory_mb
            : undefined;

        setHealth(status, latency, cpu, mem);
      } catch {
        if (!isMounted.current) return;
        setHealth('offline', null);
      }
    };

    checkBackend();
    const id = setInterval(checkBackend, 3000);

    return () => {
      isMounted.current = false;
      clearInterval(id);
    };
  }, [setHealth]);

  return <>{children}</>;
};
