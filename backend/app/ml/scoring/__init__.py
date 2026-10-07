"""
AI-Powered Fitness Coach — Scoring & Feedback Package
"""

from app.ml.scoring.engine import BiomechanicalScoringEngine
from app.ml.scoring.feedback import FeedbackGenerator, INSTANT_CUES, CORRECTIVE_DRILLS

__all__ = [
    "BiomechanicalScoringEngine",
    "FeedbackGenerator",
    "INSTANT_CUES",
    "CORRECTIVE_DRILLS",
]
