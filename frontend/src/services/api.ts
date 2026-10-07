import { VideoItem, AnalysisResult, AnalysisProgress, ModelInfo, UserStats } from '../types';

const API_BASE = '/api/v1';

function authHeaders(): Record<string, string> {
  try {
    const token = localStorage.getItem('fitness_coach_token');
    if (token) return { Authorization: `Bearer ${token}` };
  } catch {
    /* storage unavailable */
  }
  return {};
}

export const api = {
  // ── Videos ────────────────────────────────────────────────────────
  async uploadVideo(file: File): Promise<VideoItem> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/videos/upload`, {
      method: 'POST',
      headers: { ...authHeaders() },
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async listVideos(): Promise<VideoItem[]> {
    const res = await fetch(`${API_BASE}/videos/`, { headers: { ...authHeaders() } });
    if (!res.ok) throw new Error('Failed to load videos');
    return res.json();
  },

  getVideoStreamUrl(videoId: string): string {
    return `${API_BASE}/videos/${videoId}/stream`;
  },

  // ── Analysis ──────────────────────────────────────────────────────
  async startAnalysis(
    videoId: string,
    exerciseOverride?: string,
    modelType: string = 'random_forest'
  ): Promise<{ analysis_id: string; message: string }> {
    const res = await fetch(`${API_BASE}/analysis/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({
        video_id: videoId,
        exercise_override: exerciseOverride || null,
        model_type: modelType,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to start analysis' }));
      throw new Error(err.detail || 'Failed to start analysis');
    }
    return res.json();
  },

  subscribeAnalysisProgress(
    analysisId: string,
    onUpdate: (progress: AnalysisProgress) => void,
    onComplete: (result: AnalysisResult) => void,
    onError: (err: any) => void
  ): () => void {
    const eventSource = new EventSource(`${API_BASE}/analysis/${analysisId}/stream`);

    eventSource.onmessage = (event) => {
      try {
        const data: AnalysisProgress = JSON.parse(event.data);
        onUpdate(data);

        if (data.status === 'completed') {
          eventSource.close();
          if (data.result) {
            onComplete(data.result);
          } else {
            api.getAnalysisResult(analysisId).then(onComplete).catch(onError);
          }
        } else if (data.status === 'failed') {
          eventSource.close();
          onError(new Error(data.error_message || 'Analysis processing failed'));
        }
      } catch (e) {
        console.error('SSE JSON parse error', e);
      }
    };

    eventSource.onerror = (e) => {
      console.warn('SSE connection closed or errored', e);
      eventSource.close();
      // Polling fallback check
      api.getAnalysisResult(analysisId)
        .then(onComplete)
        .catch(() => {});
    };

    return () => {
      eventSource.close();
    };
  },

  async getAnalysisResult(analysisId: string): Promise<AnalysisResult> {
    const res = await fetch(`${API_BASE}/analysis/${analysisId}`, { headers: { ...authHeaders() } });
    if (!res.ok) throw new Error('Analysis not found');
    return res.json();
  },

  async listAnalyses(): Promise<AnalysisResult[]> {
    const res = await fetch(`${API_BASE}/analysis/`, { headers: { ...authHeaders() } });
    if (!res.ok) throw new Error('Failed to load analyses');
    return res.json();
  },

  // ── Reports & Models ──────────────────────────────────────────────
  async downloadPdfReport(analysisId: string, filename: string = 'workout_report.pdf'): Promise<void> {
    const res = await fetch(`${API_BASE}/reports/${analysisId}/pdf`, { headers: { ...authHeaders() } });
    if (!res.ok) throw new Error('Failed to generate PDF report');
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  },

  async listModels(): Promise<ModelInfo[]> {
    const res = await fetch(`${API_BASE}/models/`, { headers: { ...authHeaders() } });
    if (!res.ok) throw new Error('Failed to load models');
    return res.json();
  },

  async getUserStats(): Promise<UserStats> {
    const res = await fetch(`${API_BASE}/users/stats`, { headers: { ...authHeaders() } });
    if (!res.ok) throw new Error('Failed to load user stats');
    return res.json();
  },
};
