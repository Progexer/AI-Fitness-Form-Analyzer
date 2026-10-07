"""
AI-Powered Fitness Coach — Video Schemas
"""

from typing import Optional, List
from pydantic import BaseModel


class VideoUploadResponse(BaseModel):
    id: str
    filename: str
    file_path: str
    file_size_bytes: int
    duration_sec: float
    fps: float
    width: int
    height: int
    uploaded_at: str


class VideoListItem(BaseModel):
    id: str
    filename: str
    file_size_bytes: int
    duration_sec: float
    uploaded_at: str
    has_analysis: bool = False
    latest_exercise: Optional[str] = None
    latest_score: Optional[float] = None
