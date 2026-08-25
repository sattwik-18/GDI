/**
 * GDI Platform v2 — Master Domain Type System
 *
 * Single source of truth for all domain types.
 * Every workspace, service, store, and component imports from here.
 */

// --- PRIMITIVES -----------------------------------------------
export type UUID = string;
export type ISO8601 = string;
export type SemVer = string;

// --- OBJECT TYPE REGISTRY -------------------------------------
export type GDIObjectType =
  | 'document' | 'document_version' | 'page' | 'image_layer'
  | 'layout_region' | 'text_region' | 'table_region' | 'image_region' | 'bounding_box'
  | 'ocr_observation' | 'ocr_line' | 'ocr_word'
  | 'genome' | 'genome_feature' | 'genome_seal' | 'feature_domain' | 'feature_vector'
  | 'pipeline_run' | 'pipeline_stage' | 'stage_input' | 'stage_output'
  | 'stage_resource' | 'stage_warning' | 'stage_exception'
  | 'comparison_session' | 'document_pair' | 'feature_delta' | 'similarity_score' | 'comparison_finding'
  | 'hash_record' | 'seal_record' | 'validation_record' | 'integrity_record'
  | 'case' | 'analysis_session' | 'workspace_snapshot' | 'investigation_timeline'
  | 'annotation' | 'note' | 'bookmark' | 'flag' | 'tag' | 'review_status' | 'evidence_collection'
  | 'report' | 'report_section' | 'report_finding' | 'evidence_reference' | 'chain_of_custody_record'
  | 'dataset' | 'corpus' | 'corpus_entry' | 'corpus_statistics'
  | 'health_record' | 'system_component' | 'audit_event' | 'diagnostics_snapshot';

// --- RELATIONSHIP TYPES ---------------------------------------
export type RelationshipType =
  | 'derived_from' | 'belongs_to' | 'depends_on' | 'references' | 'correlates_with'
  | 'generated_by' | 'validated_by' | 'compared_to' | 'linked_to' | 'used_by'
  | 'supports' | 'contradicts' | 'spatially_contains' | 'temporally_precedes'
  | 'extracted_from' | 'has_page' | 'has_region' | 'has_observation'
  | 'has_feature' | 'has_stage' | 'produced' | 'processed';

export interface Relationship {
  id: UUID;
  type: RelationshipType;
  source_id: UUID;
  target_id: UUID;
  target_type: GDIObjectType;
  target_label: string;
  strength: number | null;
  metadata: Record<string, unknown>;
}

// --- EVIDENCE DOMAIN TAXONOMY ---------------------------------
export type EvidenceDomain =
  | 'geometry' | 'typography' | 'ocr' | 'texture'
  | 'frequency' | 'statistics' | 'layout' | 'metadata' | 'security';

export const EVIDENCE_DOMAIN_LABELS: Record<EvidenceDomain, string> = {
  geometry: 'Geometry', typography: 'Typography', ocr: 'OCR Intelligence',
  texture: 'Texture Analysis', frequency: 'Frequency Domain',
  statistics: 'Statistical Profile', layout: 'Layout Structure',
  metadata: 'Document Metadata', security: 'Security & Integrity',
};

export const EVIDENCE_DOMAIN_COLORS: Record<EvidenceDomain, string> = {
  geometry: '#3b82f6', typography: '#f97316', ocr: '#10b981',
  texture: '#8b5cf6', frequency: '#6366f1', statistics: '#6b7280',
  layout: '#14b8a6', metadata: '#6366f1', security: '#ef4444',
};

// --- STATUS & IMPORTANCE --------------------------------------
export type EvidenceStatus =
  | 'measured' | 'calculated' | 'derived' | 'estimated'
  | 'interpolated' | 'unavailable' | 'experimental' | 'deprecated';

export type ForensicImportance = 'critical' | 'high' | 'medium' | 'low';
export type DeterminismLevel = 'deterministic' | 'probabilistic' | 'stochastic';
export type InspectorMode = 'analyst' | 'research' | 'developer';

// --- VISUALIZATION HINTS --------------------------------------
export type VizType =
  | 'scalar_bar' | 'confidence_ring' | 'angle_dial' | 'binary'
  | 'raw' | 'sparkline' | 'heatmap_cell' | 'count_badge';

// --- PROVENANCE -----------------------------------------------
export interface ProvenanceDependency {
  name: string;
  version: string;
  type: 'library' | 'model' | 'dataset' | 'service';
}

export interface Provenance {
  origin: string;
  pipeline_stage: string;
  algorithm: string;
  configuration: Record<string, unknown>;
  version: string;
  schema_version: string;
  processing_context: string;
  config_fingerprint: string | null;
  runtime_ms: number;
  random_seed: number | null;
  timestamp: ISO8601;
  dependencies: ProvenanceDependency[];
}

// --- CONFIDENCE -----------------------------------------------
export interface ConfidenceFactor {
  name: string;
  description: string;
  impact: 'positive' | 'negative' | 'neutral';
  weight: number;
}

export interface Confidence {
  score: number;
  method: string;
  factors: ConfidenceFactor[];
  degraded_by: string[];
}

// --- INTEGRITY ------------------------------------------------
export interface Anomaly {
  id: string;
  severity: 'warning' | 'error' | 'info';
  description: string;
  field: string | null;
}

export interface IntegrityRecord {
  schema_valid: boolean;
  checksum_verified: boolean;
  seal_verified: boolean | null;
  pipeline_complete: boolean;
  normalization_applied: boolean;
  validation_passed: boolean;
  anomalies: Anomaly[];
}

// --- ANNOTATIONS ----------------------------------------------
export interface Annotation {
  id: UUID;
  type: 'note' | 'flag' | 'tag' | 'review_status';
  content: string;
  author: string;
  created_at: ISO8601;
  updated_at: ISO8601;
}

export interface Bookmark {
  id: UUID;
  object_id: UUID;
  object_label: string;
  object_type: GDIObjectType;
  created_at: ISO8601;
  note: string | null;
}

// --- HISTORY --------------------------------------------------
export type HistoryEventType =
  | 'created' | 'modified' | 'processed' | 'validated'
  | 'compared' | 'exported' | 'inspected' | 'annotated' | 'bookmarked';

export interface HistoryEvent {
  id: UUID;
  type: HistoryEventType;
  timestamp: ISO8601;
  actor: string;
  description: string;
  metadata: Record<string, unknown>;
}

// --- VALIDATION -----------------------------------------------
export interface ValidationResult {
  passed: boolean;
  checks: Array<{ name: string; passed: boolean; message: string | null }>;
  timestamp: ISO8601;
}

// --- REPORTING ------------------------------------------------
export interface ReportFragment {
  human_summary: string;
  technical_summary: string;
  machine_key: string;
  evidence_refs: string[];
}

// --- EVIDENCE VALUE -------------------------------------------
export type EvidenceValue = number | string | boolean | null | number[] | Record<string, unknown>;

// --- UNIVERSAL BASE OBJECT ------------------------------------
export interface GDIObject {
  id: UUID;
  type: GDIObjectType;
  label: string;
  schema_version: string;
  created_at: ISO8601;
  updated_at: ISO8601;
  lifecycle_state: 'active' | 'archived' | 'deleted';
  provenance: Provenance;
  integrity: IntegrityRecord;
  relationships: Relationship[];
  metadata: Record<string, unknown>;
  annotations: Annotation[];
  bookmarks: Bookmark[];
  history: HistoryEvent[];
  report_fragment: ReportFragment;
  validation: ValidationResult;
}

// --- EVIDENCE DEFINITION (static registry entry) -------------
export interface EvidenceDef {
  id: string;
  vectorIndex: number | undefined;
  featureKey?: string;
  label: string;
  domain: EvidenceDomain;
  extractor: string;
  pipelineStage: string;
  unit: string;
  dataType: string;
  description: string;
  purpose: string;
  calculationMethod: string;
  interpretation: string;
  typicalRange: [number, number] | null;
  forensicImportance: ForensicImportance;
  determinism: DeterminismLevel;
  status: EvidenceStatus;
  vizType: VizType;
  tags: string[];
  relatedIds: string[];
  derivedFrom: string[];
  knownLimitations: string;
  edgeCases: string;
}

export interface EvidenceDomainDef {
  id: EvidenceDomain;
  label: string;
  description: string;
  color: string;
  features: EvidenceDef[];
}

// --- NAVIGATION -----------------------------------------------
export type WorkspaceId =
  | 'analysis' | 'comparison' | 'manifest'
  | 'datasets' | 'reports' | 'debug' | 'settings';

export interface NavigationEvent {
  object_id: UUID;
  object_type: GDIObjectType;
  source_workspace: WorkspaceId;
  action: 'inspect' | 'highlight' | 'scroll_to' | 'compare';
  metadata?: Record<string, unknown>;
}

// --- SEARCH ---------------------------------------------------
export interface SearchResult {
  object_id: UUID;
  object_type: GDIObjectType;
  object_label: string;
  score: number;
  match_field: string;
  match_excerpt: string;
  workspace: WorkspaceId;
}

export interface StructuredQuery {
  text?: string;
  domain?: EvidenceDomain;
  type?: GDIObjectType;
  importance?: ForensicImportance;
  status?: EvidenceStatus;
  tags?: string[];
}

// --- FILTER ---------------------------------------------------
export interface EvidenceFilter {
  domain?: EvidenceDomain[];
  importance?: ForensicImportance[];
  status?: EvidenceStatus[];
  tags?: string[];
  text?: string;
}
