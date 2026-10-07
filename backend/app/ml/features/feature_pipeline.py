"""
AI-Powered Fitness Coach — End-to-End Feature Engineering Pipeline

Orchestrates landmark normalization, biomechanical angle calculations,
distance ratios, temporal kinematics, and form rule evaluation.
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import json
from pathlib import Path
import numpy as np

from app.ml.features.landmark_features import (
    normalize_landmarks,
    flatten_landmarks,
    extract_raw_landmark_array
)
from app.ml.features.angle_features import compute_all_joint_angles
from app.ml.features.distance_features import compute_distance_features
from app.ml.features.temporal_features import (
    compute_frame_deltas,
    compute_window_temporal_features
)
from app.ml.features.form_labels import generate_frame_form_label


class BiomechanicalFeaturePipeline:
    """
    Main feature extraction and engineering pipeline.
    Maintains temporal state for a live session or processes an entire video sequence.
    """

    def __init__(self, fps: float = 30.0, window_size: int = 15):
        self.fps = fps
        self.dt = 1.0 / fps if fps > 0 else 1.0 / 30.0
        self.window_size = window_size
        self.reset()

    def reset(self):
        """Reset internal sequence history (e.g. on new video/user stream)."""
        self.prev_angles: Optional[Dict[str, float]] = None
        self.angle_history: List[Dict[str, float]] = []
        self.landmark_history: List[np.ndarray] = []

    def extract_frame_features(
        self,
        raw_landmarks: Union[np.ndarray, List[Dict[str, float]]],
        exercise: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single frame:
        - raw_landmarks: (33, 4) array or list of 33 dicts with {'x', 'y', 'z', 'visibility'}
        - exercise: optional known exercise name for targeted form rule evaluation
        """
        if not isinstance(raw_landmarks, np.ndarray):
            landmarks_arr = extract_raw_landmark_array(raw_landmarks)
        else:
            landmarks_arr = raw_landmarks.copy()

        # 1. Normalization
        norm_landmarks, norm_meta = normalize_landmarks(landmarks_arr)

        # 2. Joint angles
        angles = compute_all_joint_angles(landmarks_arr)

        # 3. Distance features
        scale = norm_meta.get("scale_factor", 1.0)
        distances = compute_distance_features(landmarks_arr, scale_factor=scale)

        # 4. Instantaneous kinematic deltas
        deltas = compute_frame_deltas(angles, self.prev_angles, dt=self.dt)

        # 5. Sliding window temporal statistics
        self.angle_history.append(angles)
        self.landmark_history.append(norm_landmarks)
        if len(self.angle_history) > 60:
            self.angle_history.pop(0)
            self.landmark_history.pop(0)

        window_temporal = compute_window_temporal_features(
            self.angle_history, window_size=self.window_size, fps=self.fps,
            exercise=exercise
        )

        self.prev_angles = angles

        # 6. Form rule classification (if exercise is specified)
        form_label = "unknown"
        error_list: List[str] = []
        form_meta: Dict[str, Any] = {}
        if exercise:
            form_label, error_list, form_meta = generate_frame_form_label(exercise, angles, distances)

        # 7. Flattened landmark vectors
        flat_norm_coords = flatten_landmarks(norm_landmarks, include_visibility=False)  # 99 values

        # Construct flat feature dictionary for ML models
        features_dict: Dict[str, float] = {}
        for i, val in enumerate(flat_norm_coords):
            features_dict[f"lm_{i}"] = float(val)
        features_dict.update(angles)
        features_dict.update(distances)
        features_dict.update(deltas)
        features_dict.update(window_temporal)

        return {
            "features_dict": features_dict,
            "feature_vector": np.array(list(features_dict.values()), dtype=np.float32),
            "angles": angles,
            "distances": distances,
            "temporal": {**deltas, **window_temporal},
            "norm_landmarks": norm_landmarks,
            "form_label": form_label,
            "form_errors": error_list,
            "metadata": norm_meta,
        }

    def process_sequence(
        self,
        landmarks_seq: np.ndarray,
        valid_mask: Optional[np.ndarray] = None,
        exercise: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a full video landmark sequence (T, 33, 4).
        """
        self.reset()
        t_len = landmarks_seq.shape[0]
        vectors = []
        angles_seq = []
        form_labels = []

        for t in range(t_len):
            if valid_mask is not None and not valid_mask[t]:
                # If pose was lost, append zero/interpolated features
                vectors.append(vectors[-1] if vectors else np.zeros(144, dtype=np.float32))
                continue

            frame_res = self.extract_frame_features(landmarks_seq[t], exercise=exercise)
            vectors.append(frame_res["feature_vector"])
            angles_seq.append(frame_res["angles"])
            form_labels.append(frame_res["form_label"])

        return {
            "feature_matrix": np.array(vectors, dtype=np.float32),  # (T, num_features)
            "angles_history": angles_seq,
            "form_labels": form_labels,
        }


def export_feature_schema(output_path: Path):
    """
    Generates and saves feature_schema.json describing all engineered features.
    """
    pipeline = BiomechanicalFeaturePipeline()
    dummy_landmarks = np.zeros((33, 4), dtype=np.float32)
    dummy_res = pipeline.extract_frame_features(dummy_landmarks, exercise="squat")
    feat_dict = dummy_res["features_dict"]

    schema = {
        "num_features": len(feat_dict),
        "feature_names": list(feat_dict.keys()),
        "categories": {
            "normalized_landmarks": [k for k in feat_dict.keys() if k.startswith("lm_")],
            "joint_angles": [k for k in feat_dict.keys() if "angle" in k or "diff" in k and "depth" not in k],
            "distance_ratios": [k for k in feat_dict.keys() if "norm" in k],
            "temporal_kinematics": [k for k in feat_dict.keys() if "vel" in k or "rom" in k or "score" in k],
        },
        "description": "Comprehensive biomechanical feature schema for exercise recognition and form scoring."
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(schema, f, indent=2)
    print(f"Exported feature schema ({len(feat_dict)} features) to: {output_path}")


if __name__ == "__main__":
    export_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "reports" / "feature_schema.json"
    export_feature_schema(export_path)
