"""
AI-Powered Fitness Coach — Repetition Counting Package
"""

from typing import Optional
from app.ml.rep_counting.base import BaseRepCounter, MovementPhase, RepData
from app.ml.rep_counting.squat import SquatCounter
from app.ml.rep_counting.pushup import PushUpCounter
from app.ml.rep_counting.bicep_curl import BicepCurlCounter
from app.ml.rep_counting.shoulder_press import ShoulderPressCounter


def create_rep_counter(exercise_name: str) -> BaseRepCounter:
    """Factory function returning the corresponding exercise counter."""
    clean = exercise_name.lower().strip().replace("-", "_").replace(" ", "_")
    if "squat" in clean:
        return SquatCounter()
    elif "push" in clean:
        return PushUpCounter()
    elif "curl" in clean:
        return BicepCurlCounter()
    elif "shoulder" in clean or "press" in clean:
        return ShoulderPressCounter()
    else:
        # Default fallback
        return SquatCounter()


__all__ = [
    "BaseRepCounter",
    "MovementPhase",
    "RepData",
    "SquatCounter",
    "PushUpCounter",
    "BicepCurlCounter",
    "ShoulderPressCounter",
    "create_rep_counter",
]
