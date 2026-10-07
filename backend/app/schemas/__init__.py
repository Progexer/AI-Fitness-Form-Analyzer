"""
AI-Powered Fitness Coach — Pydantic Schemas Package
"""

from app.schemas.auth import UserLogin, UserRegister, TokenResponse, UserResponse
from app.schemas.user import UserProfileUpdate, UserStatsResponse
from app.schemas.video import VideoUploadResponse, VideoListItem
from app.schemas.analysis import (
    StartAnalysisRequest,
    AnalysisResultResponse,
    AnalysisProgressUpdate,
    RepTelemetry,
    CoachingFeedback,
)
from app.schemas.model import ModelInfo, SwitchActiveModelRequest

__all__ = [
    "UserLogin",
    "UserRegister",
    "TokenResponse",
    "UserResponse",
    "UserProfileUpdate",
    "UserStatsResponse",
    "VideoUploadResponse",
    "VideoListItem",
    "StartAnalysisRequest",
    "AnalysisResultResponse",
    "AnalysisProgressUpdate",
    "RepTelemetry",
    "CoachingFeedback",
    "ModelInfo",
    "SwitchActiveModelRequest",
]
