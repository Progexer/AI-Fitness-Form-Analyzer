"""
AI-Powered Fitness Coach — XGBoost Form Fault Classifier Inference Engine
"""

from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import numpy as np
import joblib
import json

PROJECT_ROOT = Path(__file__).resolve().parents[4]
MODEL_DIR = PROJECT_ROOT / "models" / "xgboost"


class XGBoostFormClassifier:
    """Production inference wrapper for XGBoost form error detection."""

    def __init__(self, model_dir: Optional[Path] = None):
        self.model_dir = model_dir or MODEL_DIR
        self.model = None
        self.label_encoder = None
        self.feature_columns = None
        self._load()

    def _load(self):
        model_file = self.model_dir / "xgb_form_classifier.joblib"
        encoder_file = self.model_dir / "form_label_encoder.joblib"
        cols_file = self.model_dir / "form_feature_columns.json"

        if model_file.exists() and encoder_file.exists():
            self.model = joblib.load(model_file)
            self.label_encoder = joblib.load(encoder_file)
            if cols_file.exists():
                with open(cols_file, "r") as f:
                    self.feature_columns = json.load(f)

    @property
    def is_ready(self) -> bool:
        return self.model is not None and self.label_encoder is not None

    def predict(self, feature_dict_or_vector: Union[Dict[str, float], np.ndarray]) -> Dict[str, Any]:
        """
        Predict form fault and probabilities from a single frame's feature vector.
        """
        if not self.is_ready:
            return {
                "form_label": "good_form",
                "confidence": 0.8,
                "probabilities": {"good_form": 0.8}
            }

        if isinstance(feature_dict_or_vector, dict):
            if self.feature_columns:
                vec = [feature_dict_or_vector.get(c, 0.0) for c in self.feature_columns]
            else:
                vec = list(feature_dict_or_vector.values())
            x = np.array([vec], dtype=np.float32)
        else:
            x = np.array(feature_dict_or_vector, dtype=np.float32)
            if x.ndim == 1:
                x = x.reshape(1, -1)

        probs = self.model.predict_proba(x)[0]
        pred_idx = np.argmax(probs)
        pred_label = self.label_encoder.classes_[pred_idx]
        conf = float(probs[pred_idx])

        prob_dist = {
            cls_name: round(float(probs[i]), 4)
            for i, cls_name in enumerate(self.label_encoder.classes_)
        }

        return {
            "form_label": pred_label,
            "confidence": round(conf, 4),
            "probabilities": prob_dist,
            "is_error": pred_label != "good_form"
        }
