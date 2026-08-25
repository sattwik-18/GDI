export interface GenomeSeal {
  feature_count: number;
  sha256_of_features: string;
  sealed_at: string;
  seal_type: string;
}

export interface ManifestStep {
  step_name: string;
  version: string;
  start_timestamp: string;
  finish_timestamp: string;
  duration_ms: number;
  status: string;
  parameters: Record<string, any>;
  configuration: Record<string, any>;
  input_summary: Record<string, any>;
  output_summary: Record<string, any>;
  cpu_percent: number;
  memory_rss_mb: number;
  peak_memory_mb: number;
  retry_count: number;
  warnings: string[];
  exception: string | null;
}

export interface ProcessingManifest {
  id: string;
  job_id: string;
  total_duration_ms: number;
  step_count: number;
  steps: ManifestStep[];
  created_at: string;
}

export interface PageMetadata {
  page_number: number;
  width_px: number;
  height_px: number;
  dpi: number;
  skew_angle_deg: number;
  color_space: string;
}

export interface GenomeResponse {
  genome_id: string;
  job_id: string;
  document_id: string;
  schema_version: string;
  pipeline_version: string;
  feature_version: string;
  processing_version: string;
  config_fingerprint?: string;
  document_hash_sha256: string;
  document_hash_sha3_256: string;
  extraction_timestamp: string;
  processing_duration_ms: number;
  page_count: number;
  feature_vector: number[];
  genome_seal: GenomeSeal;
  pages: Array<Record<string, any>>;
  processing_manifest: ProcessingManifest;
}

export interface DebugInspectionResponse {
  request_id: string;
  job_id: string;
  original_filename: string;
  file_size_bytes: number;
  metadata: {
    mime_type: string | null;
    page_count: number;
    hash_sha256: string | null;
  };
  rendered_pages: Array<{
    page_number: number;
    width_px: number;
    height_px: number;
    dpi: number;
  }>;
  normalized_pages: Array<{
    page_number: number;
    skew_angle_deg: number;
    color_space: string;
  }>;
  page_quality_reports: Array<{
    page_id: string;
    blur_score: number;
    sharpness_score: number;
    contrast_score: number;
    noise_score: number;
    metrics: Record<string, any>;
  }>;
  ocr_results: Array<{
    page_number: number;
    element_count: number;
    total_words: number;
    mean_confidence: number;
    elements: Array<{
      id: string;
      text: string;
      confidence: number;
      bbox: number[][];
      page_number: number;
    }>;
  }>;
  layout_results: Array<{
    page_number: number;
    region_count: number;
    reading_order_len: number;
  }>;
  feature_groups: Array<{
    name: string;
    version: string;
    feature_count: number;
    extraction_time_ms: number;
    features: Record<string, any>;
  }>;
  processing_manifest: ProcessingManifest | null;
  warnings: string[];
  errors: string[];
}

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  timestamp: string;
  components: Record<string, {
    status: string;
    latency_ms: number;
    details: Record<string, any>;
  }>;
  build_info?: {
    app_version: string;
    git_commit: string;
    build_date: string;
    python_version: string;
    schema_version: string;
    feature_version: string;
    pipeline_version: string;
  };
}

export type ActiveWorkspace = 'analysis' | 'comparison' | 'manifest' | 'datasets' | 'reports' | 'debug' | 'settings';
