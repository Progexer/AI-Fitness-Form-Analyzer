"""
AI-Powered Fitness Coach — Model Metadata & Metrics Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ModelInfo(BaseModel):
    model_config = {"protected_namespaces": ()}
    id: str
    name: str
    type: str  # random_forest, xgboost, lstm
    task: str  # exercise_recognition, form_fault_detection, sequence_classification
    is_active: bool
    accuracy: Optional[float] = None
    macro_f1: Optional[float] = None
    latency_ms: Optional[float] = None
    fps: Optional[float] = None
    description: str


class SwitchActiveModelRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    model_id: str
