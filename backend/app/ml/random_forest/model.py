"""
AI-Powered Fitness Coach — Random Forest Exercise Classifier Inference Engine
"""

from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import numpy as np
import joblib
import json

PROJECT_ROOT = Path(__file__).resolve().parents[4]
MODEL_DIR = PROJECT_ROOT / "models" / "random_forest"


class RandomForestExerciseClassifier:
    """Production inference wrapper for exercise recognition."""

    def __init__(self, model_dir: Optional[Path] = None):
        self.model_dir = model_dir or MODEL_DIR
        self.model = None
        self.label_encoder = None
        self.feature_columns = None
        self._load()

    def _load(self):
        model_file = self.model_dir / "rf_exercise_classifier.joblib"
        encoder_file = self.model_dir / "label_encoder.joblib"
        cols_file = self.model_dir / "feature_columns.json"

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
        Predict exercise class from a feature dictionary or 1D array.
        """
        if not self.is_ready:
            # Fallback if model not yet trained
            return {
                "exercise": "squat",
                "confidence": 0.5,
                "probabilities": {"squat": 0.5, "push_up": 0.2, "bicep_curl": 0.15, "shoulder_press": 0.15}
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
            "exercise": pred_label,
            "confidence": round(conf, 4),
            "probabilities": prob_dist
        }

    def predict_majority_from_sequence(self, feature_matrix: np.ndarray) -> Dict[str, Any]:
        """
        Predict overall exercise for a full video sequence via voting.
        """
        if not self.is_ready or len(feature_matrix) == 0:
            return {
                "exercise": "unknown",
                "confidence": 0.0,
                "votes": {}
            }

        probs = self.model.predict_proba(feature_matrix)
        avg_probs = np.mean(probs, axis=0)
        best_idx = np.argmax(avg_probs)
        best_label = self.label_encoder.classes_[best_idx]

        return {
            "exercise": best_label,
            "confidence": round(float(avg_probs[best_idx]), 4),
            "probabilities": {
                cls_name: round(float(avg_probs[i]), 4)
                for i, cls_name in enumerate(self.label_encoder.classes_)
            }
        }
