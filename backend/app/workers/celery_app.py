"""
AI-Powered Fitness Coach — Celery Worker & Async Task Queue
"""

import os
from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "fitness_coach_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
)


@celery_app.task(name="tasks.analyze_video", bind=True)
def analyze_video_task(self, video_id: str, exercise_override: str = None, model_type: str = "random_forest", user_id: str = "demo_user", analysis_id: str = None):
    """
    Async Celery task to run full computer vision and biomechanical analysis.
    """
    from app.services.analysis_service import AnalysisService

    def on_progress(prog):
        self.update_state(state="PROGRESS", meta=prog)

    result = AnalysisService.run_full_analysis(
        video_id=video_id,
        exercise_override=exercise_override,
        model_type=model_type,
        user_id=user_id,
        progress_callback=on_progress,
        analysis_id=analysis_id
    )
    return result
