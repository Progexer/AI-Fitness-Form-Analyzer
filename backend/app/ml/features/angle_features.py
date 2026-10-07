"""
AI-Powered Fitness Coach — Biomechanical Angle Features

Calculates exact 2D and 3D joint angles for exercise form evaluation.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np


def calculate_angle_3d(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """
    Calculate the 3D angle at vertex b between vectors ba and bc in degrees [0, 180].
    a, b, c are (3,) numpy arrays [x, y, z].
    """
    ba = a - b
    bc = c - b

    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)

    if norm_ba < 1e-6 or norm_bc < 1e-6:
        return 0.0

    cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
    # Clamp for numerical stability
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    angle = np.arccos(cosine_angle)
    return float(np.degrees(angle))


def calculate_angle_2d(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """
    Calculate 2D angle (x, y plane) at vertex b between rays ba and bc in degrees [0, 180].
    """
    ba = a[:2] - b[:2]
    bc = c[:2] - b[:2]

    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)

    if norm_ba < 1e-6 or norm_bc < 1e-6:
        return 0.0

    cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    angle = np.arccos(cosine_angle)
    return float(np.degrees(angle))


# Landmarks mapping indices:
# 11: left_shoulder, 12: right_shoulder
# 13: left_elbow,    14: right_elbow
# 15: left_wrist,    16: right_wrist
# 19: left_index,    20: right_index
# 23: left_hip,      24: right_hip
# 25: left_knee,     26: right_knee
# 27: left_ankle,    28: right_ankle
# 0:  nose


def compute_all_joint_angles(landmarks_33x4: np.ndarray) -> Dict[str, float]:
    """
    Computes all standard biomechanical joint angles from a (33, 4) landmark array.
    """
    pts = landmarks_33x4[:, :3]

    l_shoulder, r_shoulder = pts[11], pts[12]
    l_elbow, r_elbow = pts[13], pts[14]
    l_wrist, r_wrist = pts[15], pts[16]
    l_hip, r_hip = pts[23], pts[24]
    l_knee, r_knee = pts[25], pts[26]
    l_ankle, r_ankle = pts[27], pts[28]
    nose = pts[0]

    mid_shoulder = (l_shoulder + r_shoulder) / 2.0
    mid_hip = (l_hip + r_hip) / 2.0

    # 1. Elbow angles (forearm - upper arm)
    l_elbow_angle = calculate_angle_3d(l_shoulder, l_elbow, l_wrist)
    r_elbow_angle = calculate_angle_3d(r_shoulder, r_elbow, r_wrist)

    # 2. Knee angles (thigh - shank)
    l_knee_angle = calculate_angle_3d(l_hip, l_knee, l_ankle)
    r_knee_angle = calculate_angle_3d(r_hip, r_knee, r_ankle)

    # 3. Hip angles (torso - thigh)
    l_hip_angle = calculate_angle_3d(l_shoulder, l_hip, l_knee)
    r_hip_angle = calculate_angle_3d(r_shoulder, r_hip, r_knee)

    # 4. Shoulder angles (upper arm - torso)
    l_shoulder_angle = calculate_angle_3d(l_elbow, l_shoulder, l_hip)
    r_shoulder_angle = calculate_angle_3d(r_elbow, r_shoulder, r_hip)

    # 5. Trunk inclination / Spine angle relative to vertical [0, 1, 0]
    torso_vec = mid_shoulder - mid_hip
    norm_torso = np.linalg.norm(torso_vec)
    if norm_torso > 1e-6:
        # Vertical is along y (downwards in screen coordinates)
        # Cosine with negative y-axis (upward)
        up_vec = np.array([0.0, -1.0, 0.0])
        cos_trunk = np.dot(torso_vec, up_vec) / norm_torso
        trunk_angle = float(np.degrees(np.arccos(np.clip(cos_trunk, -1.0, 1.0))))
    else:
        trunk_angle = 0.0

    # 6. Neck angle (head to torso alignment)
    neck_angle = calculate_angle_3d(nose, mid_shoulder, mid_hip)

    # Bilateral symmetry metrics (absolute difference between left & right)
    elbow_symmetry_diff = abs(l_elbow_angle - r_elbow_angle)
    knee_symmetry_diff = abs(l_knee_angle - r_knee_angle)
    hip_symmetry_diff = abs(l_hip_angle - r_hip_angle)
    shoulder_symmetry_diff = abs(l_shoulder_angle - r_shoulder_angle)

    return {
        "left_elbow_angle": round(l_elbow_angle, 2),
        "right_elbow_angle": round(r_elbow_angle, 2),
        "avg_elbow_angle": round((l_elbow_angle + r_elbow_angle) / 2.0, 2),
        "left_knee_angle": round(l_knee_angle, 2),
        "right_knee_angle": round(r_knee_angle, 2),
        "avg_knee_angle": round((l_knee_angle + r_knee_angle) / 2.0, 2),
        "left_hip_angle": round(l_hip_angle, 2),
        "right_hip_angle": round(r_hip_angle, 2),
        "avg_hip_angle": round((l_hip_angle + r_hip_angle) / 2.0, 2),
        "left_shoulder_angle": round(l_shoulder_angle, 2),
        "right_shoulder_angle": round(r_shoulder_angle, 2),
        "avg_shoulder_angle": round((l_shoulder_angle + r_shoulder_angle) / 2.0, 2),
        "trunk_angle": round(trunk_angle, 2),
        "neck_angle": round(neck_angle, 2),
        "elbow_symmetry_diff": round(elbow_symmetry_diff, 2),
        "knee_symmetry_diff": round(knee_symmetry_diff, 2),
        "hip_symmetry_diff": round(hip_symmetry_diff, 2),
        "shoulder_symmetry_diff": round(shoulder_symmetry_diff, 2),
    }
