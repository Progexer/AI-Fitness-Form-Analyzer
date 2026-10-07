"""
AI-Powered Fitness Coach — Analysis & Workout Telemetry Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class StartAnalysisRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    video_id: str
    exercise_override: Optional[str] = Field(None, description="Optional forced exercise class (squat, push_up, bicep_curl, shoulder_press)")
    model_type: Optional[str] = Field("random_forest", description="Model for exercise/form classification: random_forest, xgboost, lstm")


class RepTelemetry(BaseModel):
    rep_number: int
    duration_sec: float
    eccentric_duration_sec: float
    concentric_duration_sec: float
    min_angle: float
    max_angle: float
    rom: float
    form_errors: List[str]
    score: float


class CoachingFeedback(BaseModel):
    exercise: str
    overall_score: float
    grade: str
    summary: str
    strengths: List[str]
    improvements: List[Dict[str, Any]]
    recommended_drills: List[Dict[str, str]]


class AnalysisResultResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    id: str
    video_id: str
    exercise: str
    model_used: str
    status: str  # pending, processing, completed, failed
    overall_score: float
    grade: str
    total_reps: int
    reps: List[RepTelemetry] = []
    metrics_breakdown: Dict[str, float] = {}
    coaching_feedback: Optional[CoachingFeedback] = None
    created_at: str
    processing_time_sec: float = 0.0


class AnalysisProgressUpdate(BaseModel):
    analysis_id: str
    status: str
    progress_percent: float
    current_frame: int
    total_frames: int
    current_rep: int = 0
    current_phase: str = "IDLE"
    current_angle: float = 0.0
    latest_cue: str = ""
    error_message: Optional[str] = None
