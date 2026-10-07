"""
AI-Powered Fitness Coach — Landmark Normalization & Features

Transforms raw 33 MediaPipe body landmarks into scale-invariant,
torso-centered biomechanical representations.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np


# MediaPipe 33 Landmark indices
LANDMARK_NAMES = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear", "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow",
    "left_wrist", "right_wrist",
    "left_pinky", "right_pinky",
    "left_index", "right_index",
    "left_thumb", "right_thumb",
    "left_hip", "right_hip",
    "left_knee", "right_knee",
    "left_ankle", "right_ankle",
    "left_heel", "right_heel",
    "left_foot_index", "right_foot_index"
]

INDEX_MAP = {name: i for i, name in enumerate(LANDMARK_NAMES)}

# Key functional landmark groups for fitness
BODY_PARTS = {
    "upper_body": [11, 12, 13, 14, 15, 16],  # Shoulders, elbows, wrists
    "core": [11, 12, 23, 24],                 # Shoulders, hips
    "lower_body": [23, 24, 25, 26, 27, 28],  # Hips, knees, ankles
    "feet": [27, 28, 29, 30, 31, 32],        # Ankles, heels, feet
}


def extract_raw_landmark_array(landmarks_list: List[Dict[str, float]]) -> np.ndarray:
    """
    Convert a list of 33 dicts with {'x', 'y', 'z', 'visibility'}
    to a shape (33, 4) numpy array.
    """
    arr = np.zeros((33, 4), dtype=np.float32)
    for i in range(min(33, len(landmarks_list))):
        lm = landmarks_list[i]
        arr[i, 0] = lm.get("x", 0.0)
        arr[i, 1] = lm.get("y", 0.0)
        arr[i, 2] = lm.get("z", 0.0)
        arr[i, 3] = lm.get("visibility", 0.0)
    return arr


def normalize_landmarks(arr: np.ndarray) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Normalize 33 landmarks:
    1. Torso origin: midpoint between left_hip (23) and right_hip (24).
    2. Body scale factor: distance between shoulder midpoint and hip midpoint,
       or shoulder-to-shoulder width (whichever is larger/stable).
    3. Shift landmarks so origin = (0, 0, 0) at hip center.
    4. Scale x, y, z by body scale factor.

    Returns:
        norm_arr: (33, 4) with normalized x,y,z and preserved visibility.
        meta: dict containing scale factor, hip center, and mean visibility.
    """
    coords = arr[:, :3].copy()
    vis = arr[:, 3].copy()

    left_hip = coords[23]
    right_hip = coords[24]
    hip_center = (left_hip + right_hip) / 2.0

    left_shoulder = coords[11]
    right_shoulder = coords[12]
    shoulder_center = (left_shoulder + right_shoulder) / 2.0

    # Torso length
    torso_len = np.linalg.norm(shoulder_center - hip_center)
    # Shoulder width
    shoulder_width = np.linalg.norm(left_shoulder - right_shoulder)

    # Scale factor (use torso length if valid, else shoulder width, fallback 1.0)
    scale = torso_len if torso_len > 1e-4 else (shoulder_width if shoulder_width > 1e-4 else 1.0)

    # Centering and scaling
    norm_coords = (coords - hip_center) / scale

    norm_arr = np.column_stack([norm_coords, vis])

    meta = {
        "scale_factor": float(scale),
        "hip_center_x": float(hip_center[0]),
        "hip_center_y": float(hip_center[1]),
        "hip_center_z": float(hip_center[2]),
        "mean_visibility": float(np.mean(vis)),
        "upper_body_vis": float(np.mean(vis[BODY_PARTS["upper_body"]])),
        "lower_body_vis": float(np.mean(vis[BODY_PARTS["lower_body"]])),
    }
    return norm_arr, meta


def flatten_landmarks(norm_arr: np.ndarray, include_visibility: bool = True) -> np.ndarray:
    """
    Flatten (33, 4) to 1D vector (99 if no visibility, 132 if with visibility).
    """
    if include_visibility:
        return norm_arr.flatten()
    else:
        return norm_arr[:, :3].flatten()
