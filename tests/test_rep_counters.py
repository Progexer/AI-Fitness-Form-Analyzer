"""
Tests for Exercise Repetition Counters & State Machines
"""

import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.rep_counting.squat import SquatCounter
from app.ml.rep_counting.pushup import PushUpCounter
from app.ml.rep_counting.bicep_curl import BicepCurlCounter
from app.ml.rep_counting.shoulder_press import ShoulderPressCounter


def test_squat_counter_full_rep():
    counter = SquatCounter()
    angles_sequence = [170.0, 150.0, 130.0, 110.0, 90.0, 85.0, 95.0, 120.0, 145.0, 165.0]

    for i, angle in enumerate(angles_sequence):
        t = i * 0.15  # Total time ~ 1.5s (exceeds min_rep_duration 0.8s)
        state = counter.update(
            angles={"avg_knee_angle": angle},
            distances={"ankle_distance_norm": 0.4},
            timestamp=t,
            detected_errors=[]
        )

    assert counter.rep_count == 1
    summary = counter.get_summary()
    assert summary["total_reps"] == 1
    assert summary["average_rep_score"] >= 90.0


def test_squat_counter_partial_lockout_still_counts():
    """Real-world MediaPipe knee angles often peak at ~150°, never reaching
    the absolute 160° lockout threshold. A rep that returns to its start
    reference with sufficient ROM must still count."""
    counter = SquatCounter()
    # Upright reference ~148°, deep descent to 60°, back to ~145°
    angles_sequence = [148.0, 140.0, 120.0, 95.0, 70.0, 60.0, 75.0, 100.0, 125.0, 145.0]

    for i, angle in enumerate(angles_sequence):
        t = i * 0.2  # Total time ~ 2.0s
        counter.update(
            angles={"avg_knee_angle": angle},
            distances={},
            timestamp=t,
            detected_errors=[]
        )

    assert counter.rep_count == 1
    summary = counter.get_summary()
    assert summary["total_reps"] == 1
    assert summary["average_rom"] >= 25.0


def test_pushup_counter_full_rep():
    counter = PushUpCounter()
    angles_sequence = [160.0, 140.0, 115.0, 90.0, 85.0, 95.0, 120.0, 155.0]

    for i, angle in enumerate(angles_sequence):
        t = i * 0.15
        counter.update(
            angles={"avg_elbow_angle": angle, "avg_hip_angle": 170.0},
            distances={},
            timestamp=t,
            detected_errors=[]
        )

    assert counter.rep_count == 1


def test_bicep_curl_counter_full_rep():
    counter = BicepCurlCounter()
    # Curl up from 155 down to 50, then back to 150
    angles_sequence = [155.0, 135.0, 110.0, 80.0, 50.0, 48.0, 75.0, 110.0, 148.0]

    for i, angle in enumerate(angles_sequence):
        t = i * 0.15
        counter.update(
            angles={"avg_elbow_angle": angle},
            distances={},
            timestamp=t,
            detected_errors=[]
        )

    assert counter.rep_count == 1


def test_shoulder_press_counter_full_rep():
    counter = ShoulderPressCounter()
    # Press overhead from 90 up to 170, then back down to 90
    angles_sequence = [90.0, 110.0, 135.0, 165.0, 172.0, 150.0, 120.0, 90.0]

    for i, angle in enumerate(angles_sequence):
        t = i * 0.15
        counter.update(
            angles={"avg_elbow_angle": angle},
            distances={"hand_elevation_l_norm": 0.5, "hand_elevation_r_norm": 0.5},
            timestamp=t,
            detected_errors=[]
        )

    assert counter.rep_count == 1
