"""
AI-Powered Fitness Coach — Video Upload & Streaming API Router
"""

import os
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse

from app.schemas.video import VideoUploadResponse, VideoListItem
from app.schemas.auth import UserResponse
from app.api.v1.auth import get_current_user
from app.services.video_service import VideoService

router = APIRouter(prefix="/videos", tags=["Videos"])
PROJECT_ROOT = Path(__file__).resolve().parents[4]


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    user: UserResponse = Depends(get_current_user)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        record = VideoService.save_uploaded_video(
            file_bytes=content,
            original_filename=file.filename,
            user_id=user.id
        )
        return VideoUploadResponse(
            id=record["id"],
            filename=record["filename"],
            file_path=record["file_path"],
            file_size_bytes=record["file_size_bytes"],
            duration_sec=record["duration_sec"],
            fps=record["fps"],
            width=record["width"],
            height=record["height"],
            uploaded_at=record["created_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[VideoListItem])
def list_videos(user: UserResponse = Depends(get_current_user)):
    videos = VideoService.list_user_videos(user.id)
    return [
        VideoListItem(
            id=v["id"],
            filename=v["filename"],
            file_size_bytes=v["file_size_bytes"],
            duration_sec=v["duration_sec"],
            uploaded_at=v["created_at"],
            has_analysis=v.get("has_analysis", False),
            latest_exercise=v.get("latest_exercise"),
            latest_score=v.get("latest_score")
        )
        for v in videos
    ]


@router.get("/{video_id}")
def get_video_metadata(video_id: str, user: UserResponse = Depends(get_current_user)):
    vid = VideoService.get_video_by_id(video_id)
    if not vid:
        raise HTTPException(status_code=404, detail="Video not found")
    return vid


@router.get("/{video_id}/stream")
def stream_video(video_id: str):
    vid = VideoService.get_video_by_id(video_id)
    if not vid:
        raise HTTPException(status_code=404, detail="Video not found")

    file_path = PROJECT_ROOT / vid["file_path"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video file on disk not found")

    return FileResponse(str(file_path), media_type="video/mp4")


@router.delete("/{video_id}")
def delete_video(video_id: str, user: UserResponse = Depends(get_current_user)):
    from app.services.supabase_client import get_db
    db = get_db()
    vid = VideoService.get_video_by_id(video_id)
    if not vid:
        raise HTTPException(status_code=404, detail="Video not found")
    if vid.get("user_id") not in (user.id, "demo_user"):
        raise HTTPException(status_code=403, detail="Not authorized to delete this video")
    try:
        file_path = PROJECT_ROOT / vid["file_path"]
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass
    # Delete dependent analyses first (SQLite fallback has no cascades)
    try:
        analyses_res = db.table("analyses").eq("video_id", video_id).execute()
        for a in (analyses_res.data or []):
            db.table("reps").eq("analysis_id", a["id"]).delete()
            db.table("analyses").eq("id", a["id"]).delete()
        db.table("videos").eq("id", video_id).delete()
    except AttributeError:
        # Real Supabase client: delete() chains before filters + execute()
        for a in (db.table("analyses").select("*").eq("video_id", video_id).execute().data or []):
            db.table("reps").delete().eq("analysis_id", a["id"]).execute()
            db.table("analyses").delete().eq("id", a["id"]).execute()
        db.table("videos").delete().eq("id", video_id).execute()
    return {"status": "deleted", "video_id": video_id}


@router.post("/{video_id}/analyze")
def analyze_video(video_id: str, user: UserResponse = Depends(get_current_user)):
    """Spec-compliant alias: queue analysis for an uploaded video."""
    from fastapi import BackgroundTasks
    from app.services.analysis_service import AnalysisService, ACTIVE_PROGRESS
    import uuid
    vid = VideoService.get_video_by_id(video_id)
    if not vid:
        raise HTTPException(status_code=404, detail="Video not found")
    analysis_id = f"anl_{uuid.uuid4().hex[:12]}"
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
                video_id=video_id, user_id=user.id, analysis_id=analysis_id
            )
        except Exception as e:
            ACTIVE_PROGRESS[analysis_id] = {
                "analysis_id": analysis_id,
                "status": "failed",
                "progress_percent": 0.0,
                "error_message": str(e),
                "latest_cue": f"Analysis failed: {e}",
            }

    import threading
    threading.Thread(target=run_worker, daemon=True).start()
    return {"analysis_id": analysis_id, "video_id": video_id, "status": "queued"}
