"""
AI-Powered Fitness Coach — User Profile & Stats Schemas
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    fitness_goal: Optional[str] = None
    experience_level: Optional[str] = None  # beginner, intermediate, advanced


class UserStatsResponse(BaseModel):
    total_workouts: int = 0
    total_reps: int = 0
    average_form_score: float = 0.0
    favorite_exercise: str = "squat"
    weekly_workout_counts: Dict[str, int] = {}
    exercise_breakdown: Dict[str, int] = {}
