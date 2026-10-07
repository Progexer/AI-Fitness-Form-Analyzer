"""
AI-Powered Fitness Coach — Models & AI Governance API Router
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter

from app.schemas.model import ModelInfo, SwitchActiveModelRequest

router = APIRouter(prefix="/models", tags=["Models"])
PROJECT_ROOT = Path(__file__).resolve().parents[4]
REPORTS_DIR = PROJECT_ROOT / "reports" / "model_evaluation"

ACTIVE_MODEL_STATE = {
    "active_exercise_model": "random_forest",
    "active_form_model": "xgboost"
}


@router.get("/", response_model=List[ModelInfo])
def list_models():
    # Load measured evaluation metrics if available.
    # Missing metrics are returned as None ("evaluation not available yet")
    # — never fabricated.
    comp_file = REPORTS_DIR / "model_comparison.json"
    comp_data = {}
    if comp_file.exists():
        try:
            with open(comp_file, "r") as f:
                comp_data = json.load(f)
        except Exception:
            pass

    rf_metrics = comp_data.get("random_forest", {})
    xgb_metrics = comp_data.get("xgboost", {})
    lstm_metrics = comp_data.get("bilstm", {})

    return [
        ModelInfo(
            id="random_forest",
            name="Random Forest Classifier",
            type="random_forest",
            task="Exercise Recognition (Squat, Push-up, Bicep Curl, Shoulder Press)",
            is_active=ACTIVE_MODEL_STATE["active_exercise_model"] == "random_forest",
            accuracy=rf_metrics.get("test_accuracy"),
            macro_f1=rf_metrics.get("macro_f1"),
            latency_ms=rf_metrics.get("latency_ms"),
            fps=rf_metrics.get("fps"),
            description="Ensemble of decision trees trained on normalized 3D joint angles, limb vectors, and kinematic deltas."
        ),
        ModelInfo(
            id="xgboost",
            name="XGBoost Gradient Boosted Trees",
            type="xgboost",
            task="Biomechanical Form Error Detection (Knee Valgus, Sagging Hips, Elbow Flare, etc.)",
            is_active=ACTIVE_MODEL_STATE["active_form_model"] == "xgboost",
            accuracy=xgb_metrics.get("test_accuracy"),
            macro_f1=xgb_metrics.get("macro_f1"),
            latency_ms=xgb_metrics.get("latency_ms"),
            fps=xgb_metrics.get("fps"),
            description="Gradient boosting model optimized for detecting nuanced biomechanical breakdown and posture faults."
        ),
        ModelInfo(
            id="lstm",
            name="Bidirectional LSTM with Attention",
            type="lstm",
            task="Temporal Sequence Classification & Trajectory Modeling",
            is_active=ACTIVE_MODEL_STATE["active_exercise_model"] == "lstm",
            accuracy=lstm_metrics.get("test_accuracy", lstm_metrics.get("val_accuracy")),
            macro_f1=lstm_metrics.get("macro_f1", lstm_metrics.get("val_f1")),
            latency_ms=lstm_metrics.get("latency_ms"),
            fps=lstm_metrics.get("fps"),
            description="PyTorch 2-layer Bi-LSTM with temporal attention pooling across 30-frame sequential windows."
        )
    ]


@router.get("/metrics")
def get_model_metrics():
    comp_file = REPORTS_DIR / "model_comparison.json"
    if comp_file.exists():
        with open(comp_file, "r") as f:
            return json.load(f)

    # No measured metrics available yet — return honest empty state,
    # never fabricated numbers.
    return {
        "status": "evaluation_not_available_yet",
        "message": "Models have not been evaluated on the holdout test set yet. Run scripts/evaluate_models.py to generate measured metrics.",
        "random_forest": None,
        "xgboost": None,
        "bilstm": None
    }


@router.post("/active")
def set_active_model(req: SwitchActiveModelRequest):
    if req.model_id in ["random_forest", "lstm"]:
        ACTIVE_MODEL_STATE["active_exercise_model"] = req.model_id
    elif req.model_id == "xgboost":
        ACTIVE_MODEL_STATE["active_form_model"] = req.model_id
    return {"status": "success", "active_models": ACTIVE_MODEL_STATE}


@router.get("/{model_id}", response_model=ModelInfo)
def get_model_by_id(model_id: str):
    from fastapi import HTTPException
    for m in list_models():
        if m.id == model_id or m.type == model_id:
            return m
    raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
