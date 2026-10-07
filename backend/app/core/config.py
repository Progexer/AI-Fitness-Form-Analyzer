"""
AI-Powered Fitness Coach — Backend Configuration
"""

import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── Project Info ───────────────────────────────────────
    PROJECT_NAME: str = "AI-Powered Fitness Coach"
    ENVIRONMENT: str = "development"
    JWT_SECRET_KEY: str = "fitness-coach-jwt-secret-key-super-safe-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "*"]

    # ── Supabase ───────────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # ── Redis / Celery ─────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # ── API ────────────────────────────────────────────────
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = True
    API_CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    API_V1_PREFIX: str = "/api/v1"

    # ── ML Pipeline ────────────────────────────────────────
    MODEL_DIR: str = str(Path(__file__).resolve().parents[3] / "models")
    DATA_DIR: str = str(Path(__file__).resolve().parents[3] / "data")
    DATASET_DIR: str = str(Path(__file__).resolve().parents[3] / "Dataset")

    FRAME_SAMPLE_RATE: int = 3
    MIN_LANDMARK_VISIBILITY: float = 0.5
    EXERCISE_CONFIDENCE_THRESHOLD: float = 0.6
    LSTM_SEQUENCE_LENGTH: int = 30

    # ── Video Limits ───────────────────────────────────────
    MAX_VIDEO_SIZE_MB: int = 500
    ALLOWED_VIDEO_EXTENSIONS: str = ".mp4,.mov,.avi,.mkv,.webm"
    MAX_VIDEO_DURATION_SECONDS: int = 300

    # ── Rate Limiting ──────────────────────────────────────
    AUTH_RATE_LIMIT: str = "10/minute"
    UPLOAD_RATE_LIMIT: str = "5/hour"
    ANALYSIS_RATE_LIMIT: str = "10/day"

    # ── Logging ────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # ── Scoring Weights ────────────────────────────────────
    SCORE_WEIGHT_FORM: float = 0.35
    SCORE_WEIGHT_ROM: float = 0.25
    SCORE_WEIGHT_CONSISTENCY: float = 0.20
    SCORE_WEIGHT_COMPLETION: float = 0.20

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.API_CORS_ORIGINS.split(",")]

    @property
    def allowed_extensions(self) -> list[str]:
        return [e.strip() for e in self.ALLOWED_VIDEO_EXTENSIONS.split(",")]

    @property
    def max_video_size_bytes(self) -> int:
        return self.MAX_VIDEO_SIZE_MB * 1024 * 1024

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings singleton."""
    return Settings()
