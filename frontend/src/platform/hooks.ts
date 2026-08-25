/**
 * GDI Platform v2 - Platform Hooks
 *
 * Convenience hooks for consuming platform services and stores.
 * Components should import from here, not directly from store files.
 */

export { useSystemStore } from '@/state/system.store';
export { useSessionStore } from '@/state/session.store';
export { useInspectorStore } from '@/state/inspector.store';
export { useUIStore } from '@/state/ui.store';
export { useAnnotationStore } from '@/state/annotation.store';

// Re-export frequently used types
export type { InspectorMode, WorkspaceId, EvidenceDomain, ForensicImportance } from '@/core/domain/types';
export { EVIDENCE_DOMAIN_COLORS, EVIDENCE_DOMAIN_LABELS } from '@/core/domain/types';
