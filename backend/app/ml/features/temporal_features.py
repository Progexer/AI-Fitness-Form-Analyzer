"""
AI-Powered Fitness Coach — Temporal Kinematic Features

Computes velocities, accelerations, jerk, and sliding-window Range of Motion (ROM)
across consecutive frames for dynamic movement analysis and rep phase segmentation.
"""

from typing import Dict, List, Any, Optional
import numpy as np


def compute_frame_deltas(
    current_angles: Dict[str, float],
    previous_angles: Optional[Dict[str, float]],
    dt: float = 1.0 / 30.0
) -> Dict[str, float]:
    """
    Compute 1st-order derivatives (angular velocities in deg/s) between two consecutive frames.
    """
    if previous_angles is None or dt <= 0:
        return {
            "elbow_angular_vel": 0.0,
            "knee_angular_vel": 0.0,
            "hip_angular_vel": 0.0,
            "shoulder_angular_vel": 0.0,
            "trunk_angular_vel": 0.0,
        }

    d_elbow = (current_angles.get("avg_elbow_angle", 0.0) - previous_angles.get("avg_elbow_angle", 0.0)) / dt
    d_knee = (current_angles.get("avg_knee_angle", 0.0) - previous_angles.get("avg_knee_angle", 0.0)) / dt
    d_hip = (current_angles.get("avg_hip_angle", 0.0) - previous_angles.get("avg_hip_angle", 0.0)) / dt
    d_shoulder = (current_angles.get("avg_shoulder_angle", 0.0) - previous_angles.get("avg_shoulder_angle", 0.0)) / dt
    d_trunk = (current_angles.get("trunk_angle", 0.0) - previous_angles.get("trunk_angle", 0.0)) / dt

    return {
        "elbow_angular_vel": round(float(d_elbow), 2),
        "knee_angular_vel": round(float(d_knee), 2),
        "hip_angular_vel": round(float(d_hip), 2),
        "shoulder_angular_vel": round(float(d_shoulder), 2),
        "trunk_angular_vel": round(float(d_trunk), 2),
    }


def compute_window_temporal_features(
    angle_history: List[Dict[str, float]],
    window_size: int = 15,
    fps: float = 30.0,
    exercise: Optional[str] = None
) -> Dict[str, float]:
    """
    Computes statistical and kinematic features over a sliding time window:
    - Min, Max, Range of Motion (ROM)
    - Mean velocity
    - Acceleration / Jerk (smoothness)

    Smoothness is measured on the exercise's primary joint (knee for squat,
    elbow otherwise) after a short moving-average filter, so the metric
    reflects real movement jerk rather than per-frame pose-estimation jitter.
    Score mapping is saturating: 100 / (1 + jerk / J0), J0 = 800 deg/s².
    """
    if not angle_history:
        return {
            "window_elbow_rom": 0.0,
            "window_knee_rom": 0.0,
            "window_hip_rom": 0.0,
            "window_shoulder_rom": 0.0,
            "elbow_velocity_std": 0.0,
            "knee_velocity_std": 0.0,
            "smoothness_score": 100.0,
        }

    primary_key = "avg_knee_angle" if (exercise or "").lower() == "squat" else "avg_elbow_angle"

    recent = angle_history[-window_size:]
    elbow_vals = [f.get("avg_elbow_angle", 0.0) for f in recent]
    knee_vals = [f.get("avg_knee_angle", 0.0) for f in recent]
    hip_vals = [f.get("avg_hip_angle", 0.0) for f in recent]
    shoulder_vals = [f.get("avg_shoulder_angle", 0.0) for f in recent]
    primary_vals = [f.get(primary_key, 0.0) for f in recent]

    dt = 1.0 / (fps if fps > 0 else 30.0)

    # ROM = max - min
    elbow_rom = float(np.ptp(elbow_vals)) if len(elbow_vals) > 1 else 0.0
    knee_rom = float(np.ptp(knee_vals)) if len(knee_vals) > 1 else 0.0
    hip_rom = float(np.ptp(hip_vals)) if len(hip_vals) > 1 else 0.0
    shoulder_rom = float(np.ptp(shoulder_vals)) if len(shoulder_vals) > 1 else 0.0

    # Velocity variances + jerk-based smoothness on the smoothed primary joint
    if len(primary_vals) > 4:
        kernel = min(5, len(primary_vals))
        smoothed = np.convolve(primary_vals, np.ones(kernel) / kernel, mode="valid")
        vels = np.diff(smoothed) / dt
        accels = np.diff(vels) / dt
        jerk_val = float(np.mean(np.abs(accels))) if len(accels) > 0 else 0.0
        smoothness = max(0.0, min(100.0, 100.0 / (1.0 + jerk_val / 800.0)))
    else:
        smoothness = 100.0

    elbow_vel_std = float(np.std(np.diff(elbow_vals) / dt)) if len(elbow_vals) > 2 else 0.0
    knee_vel_std = float(np.std(np.diff(knee_vals) / dt)) if len(knee_vals) > 2 else 0.0

    return {
        "window_elbow_rom": round(elbow_rom, 2),
        "window_knee_rom": round(knee_rom, 2),
        "window_hip_rom": round(hip_rom, 2),
        "window_shoulder_rom": round(shoulder_rom, 2),
        "elbow_velocity_std": round(elbow_vel_std, 2),
        "knee_velocity_std": round(knee_vel_std, 2),
        "smoothness_score": round(smoothness, 2),
    }
