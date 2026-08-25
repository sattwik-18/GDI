import { GenomeResponse, DebugInspectionResponse, HealthResponse } from '@/types/gdi';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class GDIClient {
  static async getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) {
      throw new Error(`Health check failed: ${res.statusText}`);
    }
    return res.json();
  }

  static async generateGenome(file: File): Promise<GenomeResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE_URL}/genome`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const errText = await res.text();
      let msg = res.statusText;
      try {
        const jsonErr = JSON.parse(errText);
        msg = jsonErr.error?.message || jsonErr.detail || msg;
      } catch {
        msg = errText || msg;
      }
      throw new Error(`Genome generation failed: ${msg}`);
    }

    return res.json();
  }

  static async getGenomeById(genomeId: string): Promise<GenomeResponse> {
    const res = await fetch(`${API_BASE_URL}/genome/${genomeId}`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });

    if (!res.ok) {
      throw new Error(`Genome ${genomeId} not found (${res.status})`);
    }

    return res.json();
  }

  static async inspectDebugPipeline(file: File): Promise<DebugInspectionResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE_URL}/genome/debug`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      throw new Error(`Debug inspection failed (${res.status})`);
    }

    return res.json();
  }
}
