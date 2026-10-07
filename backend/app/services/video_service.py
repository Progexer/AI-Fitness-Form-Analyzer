"""
AI-Powered Fitness Coach — Video Upload & Management Service
"""

import os
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import cv2

from app.services.supabase_client import get_db
from app.core.config import get_settings
from app.core.security import sanitize_filename, validate_file_extension
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
UPLOAD_DIR = PROJECT_ROOT / "data" / "raw" / "uploads"


class VideoService:
    @staticmethod
    def save_uploaded_video(
        file_bytes: bytes,
        original_filename: str,
        user_id: str = "demo_user"
    ) -> Dict[str, Any]:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        clean_name = sanitize_filename(original_filename)
        validate_file_extension(clean_name, settings.ALLOWED_VIDEO_EXTENSIONS)

        video_id = f"vid_{uuid.uuid4().hex[:12]}"
        ext = Path(clean_name).suffix
        target_path = UPLOAD_DIR / f"{video_id}{ext}"

        with open(target_path, "wb") as f:
            f.write(file_bytes)

        file_size = target_path.stat().st_size

        # Extract video metadata via OpenCV
        cap = cv2.VideoCapture(str(target_path))
        fps = float(cap.get(cv2.CAP_PROP_FPS)) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = round(total_frames / fps, 2) if total_frames > 0 else 0.0
        cap.release()

        now_str = datetime.now(timezone.utc).isoformat()
        record = {
            "id": video_id,
            "user_id": user_id,
            "filename": clean_name,
            "file_path": str(target_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "file_size_bytes": file_size,
            "duration_sec": duration,
            "fps": round(fps, 2),
            "width": width,
            "height": height,
            "created_at": now_str
        }

        db = get_db()
        db.table("videos").insert(record)
        logger.info(f"Saved video {video_id} ({clean_name}, {duration}s)")
        return record

    @staticmethod
    def get_video_by_id(video_id: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        res = db.table("videos").eq("id", video_id).execute()
        if res.data:
            return res.data[0]
        return None

    @staticmethod
    def list_user_videos(user_id: str = "demo_user") -> List[Dict[str, Any]]:
        db = get_db()
        res = db.table("videos").eq("user_id", user_id).order("created_at", desc=True).execute()
        videos = res.data or []

        # Enrich with latest analysis info
        for vid in videos:
            a_res = db.table("analyses").eq("video_id", vid["id"]).order("created_at", desc=True).limit(1).execute()
            if a_res.data:
                latest = a_res.data[0]
                vid["has_analysis"] = True
                vid["latest_exercise"] = latest.get("exercise")
                vid["latest_score"] = latest.get("overall_score")
            else:
                vid["has_analysis"] = False
                vid["latest_exercise"] = None
                vid["latest_score"] = None

        return videos
