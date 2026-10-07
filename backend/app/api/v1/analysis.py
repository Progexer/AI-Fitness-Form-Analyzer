"""
AI-Powered Fitness Coach — Analysis & SSE Progress API Router
"""

import asyncio
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse

from app.schemas.analysis import (
    StartAnalysisRequest,
    AnalysisResultResponse,
    AnalysisProgressUpdate
)
from app.schemas.auth import UserResponse
from app.api.v1.auth import get_current_user
from app.services.analysis_service import AnalysisService, ACTIVE_PROGRESS

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/start")
async def start_analysis(
    req: StartAnalysisRequest,
    background_tasks: BackgroundTasks,
    user: UserResponse = Depends(get_current_user)
):
    """
    Launch computer vision analysis in background task.
    Returns analysis_id immediately so frontend can listen to SSE progress.
    """
    # Quick pre-validation
    from app.services.video_service import VideoService
    vid = VideoService.get_video_by_id(req.video_id)
    if not vid:
        raise HTTPException(status_code=404, detail="Video not found")

    import uuid
    analysis_id = f"anl_{uuid.uuid4().hex[:12]}"

    # Initialize progress entry
    ACTIVE_PROGRESS[analysis_id] = {
        "analysis_id": analysis_id,
        "status": "queued",
        "progress_percent": 0.0,
        "current_frame": 0,
        "total_frames": 100,
        "current_rep": 0,
        "current_phase": "IDLE",
        "current_angle": 0.0,
        "latest_cue": "Video queued for AI processing...",
    }

    def run_worker():
        try:
            AnalysisService.run_full_analysis(
                video_id=req.video_id,
                exercise_override=req.exercise_override,
                model_type=req.model_type or "random_forest",
                user_id=user.id,
                analysis_id=analysis_id
            )
        except Exception as e:
            ACTIVE_PROGRESS[analysis_id] = {
                "analysis_id": analysis_id,
                "status": "failed",
                "progress_percent": 0.0,
                "error_message": str(e),
                "latest_cue": f"Analysis failed: {e}",
            }

    background_tasks.add_task(run_worker)

    return {
        "analysis_id": analysis_id,
        "video_id": req.video_id,
        "status": "queued",
        "message": "Analysis started in background. Connect to /stream for live SSE updates."
    }


@router.get("/{analysis_id}/progress")
def get_analysis_progress(analysis_id: str):
    prog = AnalysisService.get_analysis_progress(analysis_id)
    if not prog:
        # Check if already completed in DB
        res = AnalysisService.get_analysis_by_id(analysis_id)
        if res:
            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "progress_percent": 100.0,
                "total_reps": res.get("total_reps", 0),
                "overall_score": res.get("overall_score", 0.0)
            }
        raise HTTPException(status_code=404, detail="Analysis session not found")
    return prog


@router.get("/{analysis_id}/stream")
async def stream_analysis_progress(analysis_id: str):
    """
    Server-Sent Events (SSE) live progress endpoint.
    Streams JSON updates as frames are processed by OpenCV & MediaPipe.
    """
    async def event_generator():
        while True:
            prog = ACTIVE_PROGRESS.get(analysis_id)
            if prog:
                yield f"data: {json.dumps(prog)}\n\n"
                if prog.get("status") in ["completed", "failed"]:
                    break
            else:
                # Check DB
                res = AnalysisService.get_analysis_by_id(analysis_id)
                if res:
                    yield f"data: {json.dumps({'status': 'completed', 'progress_percent': 100.0, 'analysis_id': analysis_id})}\n\n"
                    break
                yield f"data: {json.dumps({'status': 'waiting', 'progress_percent': 0.0})}\n\n"

            await asyncio.sleep(0.3)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/{analysis_id}")
def get_analysis_result(analysis_id: str):
    res = AnalysisService.get_analysis_by_id(analysis_id)
    if not res:
        # Check active progress if still running
        prog = ACTIVE_PROGRESS.get(analysis_id)
        if prog and prog.get("status") == "processing":
            return {"id": analysis_id, "status": "processing", "progress": prog}
        raise HTTPException(status_code=404, detail="Analysis not found")
    return res


@router.get("/")
def list_analyses(user: UserResponse = Depends(get_current_user)):
    return AnalysisService.list_user_analyses(user.id)
