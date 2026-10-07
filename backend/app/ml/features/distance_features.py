"""
AI-Powered Fitness Coach — Biomechanical Distance Features

Calculates normalized 3D and planar distances between key joints to capture
body posture, stance width, grip width, and limb extensions.
"""

from typing import Dict, List, Any, Optional
import numpy as np


def compute_distance_features(landmarks_33x4: np.ndarray, scale_factor: float = 1.0) -> Dict[str, float]:
    """
    Computes key body distances normalized by body scale factor (torso length).
    landmarks_33x4: (33, 4) array [x, y, z, visibility]
    scale_factor: normalization scale factor (ensures distance is scale-invariant).
    """
    pts = landmarks_33x4[:, :3]
    scale = scale_factor if scale_factor > 1e-4 else 1.0

    l_shoulder, r_shoulder = pts[11], pts[12]
    l_elbow, r_elbow = pts[13], pts[14]
    l_wrist, r_wrist = pts[15], pts[16]
    l_hip, r_hip = pts[23], pts[24]
    l_knee, r_knee = pts[25], pts[26]
    l_ankle, r_ankle = pts[27], pts[28]

    # Stance and grip
    ankle_distance = float(np.linalg.norm(l_ankle - r_ankle) / scale)
    wrist_distance = float(np.linalg.norm(l_wrist - r_wrist) / scale)
    shoulder_distance = float(np.linalg.norm(l_shoulder - r_shoulder) / scale)
    hip_distance = float(np.linalg.norm(l_hip - r_hip) / scale)

    # Wrist to shoulder (critical for curls and presses)
    wrist_shoulder_l = float(np.linalg.norm(l_wrist - l_shoulder) / scale)
    wrist_shoulder_r = float(np.linalg.norm(r_wrist - r_shoulder) / scale)

    # Wrist to hip (starting position for curls/presses)
    wrist_hip_l = float(np.linalg.norm(l_wrist - l_hip) / scale)
    wrist_hip_r = float(np.linalg.norm(r_wrist - r_hip) / scale)

    # Hip height relative to ankles (squat depth)
    hip_y = (l_hip[1] + r_hip[1]) / 2.0
    knee_y = (l_knee[1] + r_knee[1]) / 2.0
    ankle_y = (l_ankle[1] + r_ankle[1]) / 2.0

    # In image coordinates, y increases downwards:
    # higher hip_depth_ratio means hips are deeper down towards knees
    hip_depth_diff = float((hip_y - knee_y) / scale)

    # Vertical hand elevation above shoulders (for shoulder press lockouts)
    hand_elevation_l = float((l_shoulder[1] - l_wrist[1]) / scale)  # Positive when wrist is above shoulder
    hand_elevation_r = float((r_shoulder[1] - r_wrist[1]) / scale)

    return {
        "ankle_distance_norm": round(ankle_distance, 4),
        "wrist_distance_norm": round(wrist_distance, 4),
        "shoulder_distance_norm": round(shoulder_distance, 4),
        "hip_distance_norm": round(hip_distance, 4),
        "wrist_to_shoulder_l_norm": round(wrist_shoulder_l, 4),
        "wrist_to_shoulder_r_norm": round(wrist_shoulder_r, 4),
        "avg_wrist_to_shoulder_norm": round((wrist_shoulder_l + wrist_shoulder_r) / 2.0, 4),
        "wrist_to_hip_l_norm": round(wrist_hip_l, 4),
        "wrist_to_hip_r_norm": round(wrist_hip_r, 4),
        "hip_depth_diff_norm": round(hip_depth_diff, 4),
        "hand_elevation_l_norm": round(hand_elevation_l, 4),
        "hand_elevation_r_norm": round(hand_elevation_r, 4),
        "avg_hand_elevation_norm": round((hand_elevation_l + hand_elevation_r) / 2.0, 4),
    }
