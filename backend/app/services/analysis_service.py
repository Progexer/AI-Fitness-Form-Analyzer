"""
AI-Powered Fitness Coach — Core Analysis & Computer Vision Service

Connects:
Video Decodng (OpenCV)
       ↓
MediaPipe Pose (33 3D Keypoints)
       ↓
Biomechanical Feature Engineering (Kinematics, Angles, Distances)
       ↓
Exercise Classification (Random Forest / Bi-LSTM)
       ↓
State-Machine Repetition Counter (Inflections, Durations, ROM)
       ↓
Form Fault Classifier (XGBoost + Biomechanical Rules)
       ↓
Multi-Dimensional Scoring Engine (Accuracy, ROM, Tempo, Symmetry)
       ↓
Coaching Feedback & Actionable Corrective Drills
       ↓
Supabase Database Persistence & SSE Live Streaming
"""

import os
import uuid
import time
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, AsyncGenerator
from datetime import datetime, timezone
import cv2
import mediapipe as mp
import numpy as np

from app.services.supabase_client import get_db
from app.core.config import get_settings
from app.core.logging import get_logger

from app.ml.features.feature_pipeline import BiomechanicalFeaturePipeline
from app.ml.random_forest.model import RandomForestExerciseClassifier
from app.ml.xgboost_model.model import XGBoostFormClassifier
from app.ml.rep_counting import create_rep_counter
from app.ml.scoring.engine import BiomechanicalScoringEngine
from app.ml.scoring.feedback import FeedbackGenerator

logger = get_logger(__name__)
settings = get_settings()
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# In-memory progress tracking for live SSE streaming
ACTIVE_PROGRESS: Dict[str, Dict[str, Any]] = {}


class AnalysisService:
    @staticmethod
    def get_analysis_progress(analysis_id: str) -> Optional[Dict[str, Any]]:
        return ACTIVE_PROGRESS.get(analysis_id)

    @staticmethod
    def run_full_analysis(
        video_id: str,
        exercise_override: Optional[str] = None,
        model_type: str = "random_forest",
        user_id: str = "demo_user",
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        analysis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synchronously processes video end-to-end and returns complete analysis.
        If analysis_id is provided (e.g. by the API route for SSE tracking),
        it is reused so progress updates and the stored record share one ID.
        """
        db = get_db()
        vid_res = db.table("videos").eq("id", video_id).execute()
        if not vid_res.data:
            raise ValueError(f"Video {video_id} not found in database.")

        video_record = vid_res.data[0]
        video_rel_path = video_record["file_path"]
        video_full_path = PROJECT_ROOT / video_rel_path

        if not video_full_path.exists():
            raise FileNotFoundError(f"Video file {video_full_path} not found on disk.")

        analysis_id = analysis_id or f"anl_{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()

        # Initialize progress entry
        ACTIVE_PROGRESS[analysis_id] = {
            "analysis_id": analysis_id,
            "status": "processing",
            "progress_percent": 0.0,
            "current_frame": 0,
            "total_frames": video_record.get("total_frames", 100),
            "current_rep": 0,
            "current_phase": "IDLE",
            "current_angle": 0.0,
            "latest_cue": "Starting video analysis...",
        }

        t_start = time.time()
        logger.info(f"Starting analysis {analysis_id} for video {video_id} ({model_type})")

        cap = cv2.VideoCapture(str(video_full_path))
        fps = float(cap.get(cv2.CAP_PROP_FPS)) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100
        ACTIVE_PROGRESS[analysis_id]["total_frames"] = total_frames

        # Load models & pipeline
        rf_classifier = RandomForestExerciseClassifier()
        xgb_classifier = XGBoostFormClassifier()
        pipeline = BiomechanicalFeaturePipeline(fps=fps)

        # Initialize MediaPipe Pose
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        detected_exercise = exercise_override
        rep_counter = None
        form_error_counts: Dict[str, int] = {}
        symmetry_diffs: List[float] = []
        smoothness_scores: List[float] = []
        first_frames_features = []

        frame_idx = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                ts = frame_idx / fps
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb_frame)

                current_cue = "Maintain steady motion"
                current_phase = "IDLE"
                current_angle = 0.0
                current_rep = rep_counter.rep_count if rep_counter else 0

                if results.pose_landmarks:
                    # Convert to (33, 4)
                    lm_arr = np.zeros((33, 4), dtype=np.float32)
                    for i, lm in enumerate(results.pose_landmarks.landmark):
                        lm_arr[i, 0] = lm.x
                        lm_arr[i, 1] = lm.y
                        lm_arr[i, 2] = lm.z
                        lm_arr[i, 3] = lm.visibility

                    # Extract biomechanical features
                    feat_res = pipeline.extract_frame_features(lm_arr, exercise=detected_exercise)
                    angles = feat_res["angles"]
                    distances = feat_res["distances"]
                    rule_errors = feat_res["form_errors"]

                    # Determine exercise if not yet known (predict after accumulating ~15 frames)
                    if not detected_exercise:
                        first_frames_features.append(feat_res["feature_vector"])
                        if len(first_frames_features) >= 15:
                            seq_matrix = np.array(first_frames_features)
                            vote_res = rf_classifier.predict_majority_from_sequence(seq_matrix)
                            detected_exercise = vote_res["exercise"]
                            rep_counter = create_rep_counter(detected_exercise)
                            logger.info(f"Model identified exercise: {detected_exercise} (conf={vote_res['confidence']})")
                    elif rep_counter is None:
                        rep_counter = create_rep_counter(detected_exercise)

                    # Biomechanical form classification via XGBoost + Rules
                    xgb_res = xgb_classifier.predict(feat_res["features_dict"])
                    detected_errors = list(rule_errors)
                    if xgb_res["is_error"] and xgb_res["form_label"] not in detected_errors:
                        detected_errors.append(xgb_res["form_label"])

                    for err in detected_errors:
                        form_error_counts[err] = form_error_counts.get(err, 0) + 1

                    if detected_errors:
                        current_cue = FeedbackGenerator.get_instant_cue(detected_errors[0])

                    # Update Rep Counter
                    if rep_counter:
                        rep_state = rep_counter.update(
                            angles=angles,
                            distances=distances,
                            timestamp=ts,
                            detected_errors=detected_errors
                        )
                        current_rep = rep_state["rep_count"]
                        current_phase = rep_state["phase"]
                        current_angle = rep_state["current_angle"]

                    # Telemetry stats
                    symmetry_diffs.append(angles.get("knee_symmetry_diff", 0.0) + angles.get("elbow_symmetry_diff", 0.0))
                    smoothness_scores.append(feat_res["temporal"].get("smoothness_score", 90.0))

                # Update live progress every 5 frames
                frame_idx += 1
                if frame_idx % 5 == 0 or frame_idx == total_frames:
                    pct = min(100.0, round((frame_idx / total_frames) * 100.0, 1))
                    prog = {
                        "analysis_id": analysis_id,
                        "status": "processing",
                        "progress_percent": pct,
                        "current_frame": frame_idx,
                        "total_frames": total_frames,
                        "current_rep": current_rep,
                        "current_phase": current_phase,
                        "current_angle": current_angle,
                        "latest_cue": current_cue,
                    }
                    ACTIVE_PROGRESS[analysis_id] = prog
                    if progress_callback:
                        progress_callback(prog)

        finally:
            cap.release()
            pose.close()

        # Fallback if exercise never identified
        if not detected_exercise:
            detected_exercise = "squat"
        if rep_counter is None:
            rep_counter = create_rep_counter(detected_exercise)

        # Flush a rep that was still in progress when the video ended
        # (otherwise the final rep of every clip is systematically lost).
        try:
            last_ts = (frame_idx - 1) / fps if fps > 0 else 0.0
            rep_counter.finalize(last_ts)
        except Exception as e:
            logger.warning(f"Rep finalize failed: {e}")

        reps_summary = rep_counter.get_summary()

        # Compute multi-dimensional score
        scoring_results = BiomechanicalScoringEngine.calculate_session_score(
            reps_summary=reps_summary,
            form_error_frequency=form_error_counts,
            total_frames_analyzed=frame_idx,
            symmetry_diffs=symmetry_diffs,
            smoothness_scores=smoothness_scores
        )

        # Generate comprehensive coaching report
        coaching_report = FeedbackGenerator.generate_coaching_report(
            exercise=detected_exercise,
            scoring_results=scoring_results,
            reps_summary=reps_summary
        )

        elapsed_sec = round(time.time() - t_start, 2)

        # Prepare database records
        analysis_record = {
            "id": analysis_id,
            "video_id": video_id,
            "user_id": user_id,
            "exercise": detected_exercise,
            "model_used": model_type,
            "status": "completed",
            "overall_score": scoring_results["overall_score"],
            "grade": scoring_results["grade"],
            "total_reps": reps_summary["total_reps"],
            "metrics_breakdown": scoring_results["metrics_breakdown"],
            "coaching_feedback": coaching_report,
            "processing_time_sec": elapsed_sec,
            "created_at": now_str
        }

        db.table("analyses").insert(analysis_record)

        # Insert rep details
        reps_data_list = []
        for r in reps_summary.get("reps", []):
            rep_id = f"rep_{uuid.uuid4().hex[:10]}"
            rep_row = {
                "id": rep_id,
                "analysis_id": analysis_id,
                "rep_number": r["rep_number"],
                "duration_sec": r["duration_sec"],
                "eccentric_duration_sec": r["eccentric_duration_sec"],
                "concentric_duration_sec": r["concentric_duration_sec"],
                "min_angle": r["min_angle"],
                "max_angle": r["max_angle"],
                "rom": r["rom"],
                "form_errors": r["form_errors"],
                "score": r["score"],
                "created_at": now_str
            }
            db.table("reps").insert(rep_row)
            reps_data_list.append(rep_row)

        analysis_record["reps"] = reps_data_list

        # Mark progress as completed
        ACTIVE_PROGRESS[analysis_id] = {
            "analysis_id": analysis_id,
            "status": "completed",
            "progress_percent": 100.0,
            "current_frame": frame_idx,
            "total_frames": total_frames,
            "current_rep": reps_summary["total_reps"],
            "current_phase": "COMPLETED",
            "current_angle": 0.0,
            "latest_cue": "Analysis successfully completed!",
            "result": analysis_record
        }

        logger.info(f"Completed analysis {analysis_id} in {elapsed_sec}s: {detected_exercise}, "
                    f"{reps_summary['total_reps']} reps, score={scoring_results['overall_score']}")

        return analysis_record

    @staticmethod
    def get_analysis_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        res = db.table("analyses").eq("id", analysis_id).execute()
        if not res.data:
            return None
        analysis = res.data[0]
        # Attach reps
        reps_res = db.table("reps").eq("analysis_id", analysis_id).order("rep_number", desc=False).execute()
        analysis["reps"] = reps_res.data or []
        return analysis

    @staticmethod
    def list_user_analyses(user_id: str = "demo_user") -> List[Dict[str, Any]]:
        db = get_db()
        res = db.table("analyses").eq("user_id", user_id).order("created_at", desc=True).execute()
        analyses = res.data or []
        for a in analyses:
            reps_res = db.table("reps").eq("analysis_id", a["id"]).order("rep_number", desc=False).execute()
            a["reps"] = reps_res.data or []
        return analyses
