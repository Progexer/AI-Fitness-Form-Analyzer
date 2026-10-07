export interface VideoItem {
  id: string;
  filename: string;
  file_size_bytes: number;
  duration_sec: number;
  uploaded_at: string;
  has_analysis?: boolean;
  latest_exercise?: string;
  latest_score?: number;
}

export interface RepTelemetry {
  rep_number: number;
  duration_sec: number;
  eccentric_duration_sec: number;
  concentric_duration_sec: number;
  min_angle: number;
  max_angle: number;
  rom: number;
  form_errors: string[];
  score: number;
}

export interface CoachingFeedback {
  exercise: string;
  overall_score: number;
  grade: string;
  summary: string;
  strengths: string[];
  improvements: Array<{
    fault: string;
    frequency: number;
    coaching_cue: string;
  }>;
  recommended_drills: Array<{
    drill: string;
    description: string;
  }>;
}

export interface AnalysisResult {
  id: string;
  video_id: string;
  exercise: string;
  model_used: string;
  status: string;
  overall_score: number;
  grade: string;
  total_reps: number;
  reps: RepTelemetry[];
  metrics_breakdown: {
    form_accuracy: number;
    range_of_motion: number;
    tempo_smoothness: number;
    bilateral_symmetry: number;
    movement_consistency?: number;
    rep_completion?: number;
  };
  coaching_feedback?: CoachingFeedback;
  created_at: string;
  processing_time_sec: number;
}

export interface AnalysisProgress {
  analysis_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress_percent: number;
  current_frame: number;
  total_frames: number;
  current_rep: number;
  current_phase: string;
  current_angle: number;
  latest_cue: string;
  error_message?: string;
  result?: AnalysisResult;
}

export interface ModelInfo {
  id: string;
  name: string;
  type: string;
  task: string;
  is_active: boolean;
  accuracy?: number;
  macro_f1?: number;
  latency_ms?: number;
  fps?: number;
  description: string;
}

export interface UserStats {
  total_workouts: number;
  total_reps: number;
  average_form_score: number;
  favorite_exercise: string;
  weekly_workout_counts: Record<string, number>;
  exercise_breakdown: Record<string, number>;
}
