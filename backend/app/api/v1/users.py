"""
AI-Powered Fitness Coach — Users & Analytics API Router
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from app.schemas.user import UserProfileUpdate, UserStatsResponse
from app.schemas.auth import UserResponse
from app.api.v1.auth import get_current_user
from app.services.supabase_client import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/stats", response_model=UserStatsResponse)
def get_user_stats(user: UserResponse = Depends(get_current_user)):
    db = get_db()
    res = db.table("analyses").eq("user_id", user.id).execute()
    analyses = res.data or []

    total_workouts = len(analyses)
    total_reps = sum(a.get("total_reps", 0) for a in analyses)
    avg_score = float(sum(a.get("overall_score", 0.0) for a in analyses) / total_workouts) if total_workouts > 0 else 0.0

    exercise_counts: Dict[str, int] = {}
    for a in analyses:
        ex = a.get("exercise", "squat")
        exercise_counts[ex] = exercise_counts.get(ex, 0) + 1

    fav_exercise = max(exercise_counts.items(), key=lambda x: x[1])[0] if exercise_counts else "squat"

    # Real weekday buckets derived from each analysis' created_at timestamp.
    weekly = {"Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0}
    day_keys = list(weekly.keys())
    for a in analyses:
        created = a.get("created_at")
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
            weekly[day_keys[dt.weekday() if dt.weekday() < 7 else 0]] += 1
            # Python weekday(): Mon=0..Sun=6 matches day_keys order
        except Exception:
            continue

    return UserStatsResponse(
        total_workouts=total_workouts,
        total_reps=total_reps,
        average_form_score=round(avg_score, 1),
        favorite_exercise=fav_exercise,
        weekly_workout_counts=weekly,
        exercise_breakdown=exercise_counts
    )


@router.get("/profile")
def get_user_profile(user: UserResponse = Depends(get_current_user)):
    db = get_db()
    res = db.table("profiles").eq("id", user.id).execute()
    if res.data:
        return res.data[0]
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "fitness_goal": "Hypertrophy & Form Perfection",
        "experience_level": "intermediate"
    }


@router.put("/profile")
def update_user_profile(req: UserProfileUpdate, user: UserResponse = Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    db.table("profiles").eq("id", user.id).update(update_data)
    return {"status": "success", "updated": update_data}
