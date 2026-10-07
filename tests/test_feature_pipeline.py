"""
Tests for Biomechanical Feature Engineering Pipeline
"""

import pytest
import numpy as np
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.features.landmark_features import normalize_landmarks, flatten_landmarks
from app.ml.features.angle_features import calculate_angle_3d, compute_all_joint_angles
from app.ml.features.distance_features import compute_distance_features
from app.ml.features.temporal_features import compute_frame_deltas
from app.ml.features.feature_pipeline import BiomechanicalFeaturePipeline


def test_angle_3d_calculation():
    # Right angle: (1, 0, 0) - (0, 0, 0) - (0, 1, 0)
    a = np.array([1.0, 0.0, 0.0])
    b = np.array([0.0, 0.0, 0.0])
    c = np.array([0.0, 1.0, 0.0])
    angle = calculate_angle_3d(a, b, c)
    assert abs(angle - 90.0) < 1e-4

    # Straight line: (-1, 0, 0) - (0, 0, 0) - (1, 0, 0)
    d = np.array([-1.0, 0.0, 0.0])
    e = np.array([0.0, 0.0, 0.0])
    f = np.array([1.0, 0.0, 0.0])
    angle_straight = calculate_angle_3d(d, e, f)
    assert abs(angle_straight - 180.0) < 1e-4


def test_landmark_normalization():
    raw = np.zeros((33, 4), dtype=np.float32)
    # Set left hip and right hip
    raw[23] = [0.4, 0.6, 0.0, 0.9]
    raw[24] = [0.6, 0.6, 0.0, 0.9]
    # Shoulders
    raw[11] = [0.4, 0.3, 0.0, 0.9]
    raw[12] = [0.6, 0.3, 0.0, 0.9]

    norm_arr, meta = normalize_landmarks(raw)
    assert norm_arr.shape == (33, 4)
    assert meta["scale_factor"] > 0
    # Midpoint between hips should be centered near (0, 0, 0)
    hip_mid = (norm_arr[23, :3] + norm_arr[24, :3]) / 2.0
    assert np.allclose(hip_mid, [0, 0, 0], atol=1e-5)


def test_feature_pipeline_output_shape():
    pipeline = BiomechanicalFeaturePipeline(fps=30.0)
    raw = np.random.rand(33, 4).astype(np.float32)
    res = pipeline.extract_frame_features(raw, exercise="squat")

    assert "features_dict" in res
    assert "feature_vector" in res
    assert len(res["feature_vector"]) == 142
    assert "angles" in res
    assert "distances" in res
    assert "form_label" in res
