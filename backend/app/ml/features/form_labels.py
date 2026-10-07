"""
AI-Powered Fitness Coach — Biomechanical Form Rule Engine & Weak Label Generator

Generates rule-based biomechanical form classifications and specific error labels
for each of the 4 target exercises.

NOTE: All generated labels from this module are formally tagged as
'RULE_GENERATED_WEAK_LABEL' to adhere to scientific ML rigor.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np


LABEL_TYPE = "RULE_GENERATED_WEAK_LABEL"

EXERCISE_ERROR_TYPES = {
    "squat": [
        "good_form",
        "knee_valgus",              # Knees caving inward
        "shallow_squat",            # Incomplete depth (knee angle > 105°)
        "excessive_forward_lean",   # Torso leaning too far forward (> 45°)
        "asymmetric_weight_shift",  # Uneven knee loading (> 15° diff)
    ],
    "push_up": [
        "good_form",
        "elbow_flare",              # Elbows flared too wide (> 75° shoulder abduction)
        "sagging_hips",             # Hyperextended lumbar / hips drooping (< 155° hip angle)
        "raised_hips",              # Piking hips upward (< 155° inverted)
        "shallow_depth",            # Incomplete descent (elbows > 95° at bottom)
    ],
    "bicep_curl": [
        "good_form",
        "elbow_drift",              # Elbows moving away from ribs / swinging
        "incomplete_rom",           # Incomplete peak contraction or bottom extension
        "trunk_sway",               # Cheating with back momentum
        "asymmetric_curl",          # Unequal left/right arm flexion
    ],
    "shoulder_press": [
        "good_form",
        "excessive_arch",           # Leaning back / hyperextending spine
        "incomplete_lockout",       # Elbows failing to extend overhead (< 160°)
        "uneven_press",             # One arm pressing higher or faster than the other
        "flare_misalignment",       # Arms drifting outside optimal pressing groove
    ],
}


def evaluate_squat_form(angles: Dict[str, float], distances: Dict[str, float]) -> Tuple[str, List[str], Dict[str, Any]]:
    """Evaluate squat form from instantaneous and bottom-position biomechanics."""
    errors = []
    knee_angle = angles.get("avg_knee_angle", 180.0)
    trunk_angle = angles.get("trunk_angle", 0.0)
    knee_diff = angles.get("knee_symmetry_diff", 0.0)
    ankle_dist = distances.get("ankle_distance_norm", 0.5)
    
    # We estimate knee distance from landmarks if available, else from angle/distance proxy
    # In full squat descent (knee angle < 120°):
    if knee_angle < 120.0:
        # Check depth
        if knee_angle > 105.0:
            errors.append("shallow_squat")
        
        # Check forward lean
        if trunk_angle > 45.0:
            errors.append("excessive_forward_lean")
            
        # Check symmetry
        if knee_diff > 18.0:
            errors.append("asymmetric_weight_shift")

    primary_label = errors[0] if errors else "good_form"
    return primary_label, errors, {
        "knee_angle": knee_angle,
        "trunk_angle": trunk_angle,
        "knee_diff": knee_diff,
        "label_source": LABEL_TYPE
    }


def evaluate_pushup_form(angles: Dict[str, float], distances: Dict[str, float]) -> Tuple[str, List[str], Dict[str, Any]]:
    """Evaluate push-up form."""
    errors = []
    elbow_angle = angles.get("avg_elbow_angle", 180.0)
    hip_angle = angles.get("avg_hip_angle", 180.0)
    shoulder_angle = angles.get("avg_shoulder_angle", 90.0)

    # In bottom phase:
    if elbow_angle < 130.0:
        if elbow_angle > 95.0:
            errors.append("shallow_depth")
        if shoulder_angle > 75.0:
            errors.append("elbow_flare")

    # Core alignment (plank stability)
    if hip_angle < 155.0:
        errors.append("sagging_hips")

    primary_label = errors[0] if errors else "good_form"
    return primary_label, errors, {
        "elbow_angle": elbow_angle,
        "hip_angle": hip_angle,
        "shoulder_angle": shoulder_angle,
        "label_source": LABEL_TYPE
    }


def evaluate_bicep_curl_form(angles: Dict[str, float], distances: Dict[str, float]) -> Tuple[str, List[str], Dict[str, Any]]:
    """Evaluate bicep curl form."""
    errors = []
    elbow_angle = angles.get("avg_elbow_angle", 180.0)
    shoulder_angle = angles.get("avg_shoulder_angle", 0.0)
    trunk_angle = angles.get("trunk_angle", 0.0)
    elbow_diff = angles.get("elbow_symmetry_diff", 0.0)

    # Elbow drift: upper arm swinging forward (shoulder angle > 30° during curl)
    if shoulder_angle > 30.0:
        errors.append("elbow_drift")

    # Back swing / torso momentum
    if trunk_angle > 18.0:
        errors.append("trunk_sway")

    # Bilateral asymmetry
    if elbow_diff > 22.0:
        errors.append("asymmetric_curl")

    primary_label = errors[0] if errors else "good_form"
    return primary_label, errors, {
        "elbow_angle": elbow_angle,
        "shoulder_angle": shoulder_angle,
        "trunk_angle": trunk_angle,
        "elbow_diff": elbow_diff,
        "label_source": LABEL_TYPE
    }


def evaluate_shoulder_press_form(angles: Dict[str, float], distances: Dict[str, float]) -> Tuple[str, List[str], Dict[str, Any]]:
    """Evaluate overhead shoulder press form."""
    errors = []
    elbow_angle = angles.get("avg_elbow_angle", 90.0)
    trunk_angle = angles.get("trunk_angle", 0.0)
    hand_elev_diff = abs(distances.get("hand_elevation_l_norm", 0.0) - distances.get("hand_elevation_r_norm", 0.0))

    # Spine hyperextension (arching back excessively)
    if trunk_angle > 20.0:
        errors.append("excessive_arch")

    # Uneven lockout or pressing path
    if hand_elev_diff > 0.15:
        errors.append("uneven_press")

    primary_label = errors[0] if errors else "good_form"
    return primary_label, errors, {
        "elbow_angle": elbow_angle,
        "trunk_angle": trunk_angle,
        "hand_elev_diff": hand_elev_diff,
        "label_source": LABEL_TYPE
    }


def generate_frame_form_label(
    exercise: str,
    angles: Dict[str, float],
    distances: Dict[str, float]
) -> Tuple[str, List[str], Dict[str, Any]]:
    """Dispatch form evaluation based on exercise type."""
    if exercise == "squat":
        return evaluate_squat_form(angles, distances)
    elif exercise == "push_up":
        return evaluate_pushup_form(angles, distances)
    elif exercise == "bicep_curl":
        return evaluate_bicep_curl_form(angles, distances)
    elif exercise == "shoulder_press":
        return evaluate_shoulder_press_form(angles, distances)
    else:
        return "good_form", [], {"label_source": LABEL_TYPE}
