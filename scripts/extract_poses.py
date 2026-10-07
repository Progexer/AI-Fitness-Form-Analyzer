"""
AI-Powered Fitness Coach — MediaPipe Pose Extraction Pipeline

Extracts 33 MediaPipe 3D body pose landmarks from all dataset videos according to
the generated split manifests. Saves per-video sequence data to data/interim/poses/.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
import cv2
import mediapipe as mp

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_DIR = PROJECT_ROOT / "data" / "manifests"
OUTPUT_DIR = PROJECT_ROOT / "data" / "interim" / "poses"


def process_single_video(
    video_path: Path,
    pose_detector: Any,
    target_fps: Optional[float] = None,
    min_detection_confidence: float = 0.5,
) -> Optional[Dict[str, Any]]:
    """
    Process a single video through MediaPipe Pose.
    Returns dictionary with metadata and (T, 33, 4) landmark array.
    """
    if not video_path.exists():
        return None

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None

    native_fps = float(cap.get(cv2.CAP_PROP_FPS))
    if native_fps <= 0:
        native_fps = 30.0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Frame sampling stride if target_fps is specified and lower than native
    stride = 1
    if target_fps and target_fps < native_fps:
        stride = max(1, int(round(native_fps / target_fps)))

    frame_indices = []
    timestamps = []
    landmarks_seq = []
    valid_mask = []

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % stride == 0:
            ts = frame_idx / native_fps
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose_detector.process(rgb_frame)

            frame_lm = np.zeros((33, 4), dtype=np.float32)
            is_valid = False

            if results.pose_landmarks:
                is_valid = True
                for i, lm in enumerate(results.pose_landmarks.landmark):
                    frame_lm[i, 0] = lm.x
                    frame_lm[i, 1] = lm.y
                    frame_lm[i, 2] = lm.z
                    frame_lm[i, 3] = lm.visibility

            frame_indices.append(frame_idx)
            timestamps.append(ts)
            landmarks_seq.append(frame_lm)
            valid_mask.append(is_valid)

        frame_idx += 1

    cap.release()

    if not landmarks_seq:
        return None

    landmarks_arr = np.array(landmarks_seq, dtype=np.float32)  # (T, 33, 4)
    valid_arr = np.array(valid_mask, dtype=bool)

    detection_rate = float(np.mean(valid_arr)) if len(valid_arr) > 0 else 0.0

    return {
        "landmarks": landmarks_arr,
        "valid_mask": valid_arr,
        "frame_indices": np.array(frame_indices, dtype=np.int32),
        "timestamps": np.array(timestamps, dtype=np.float32),
        "metadata": {
            "native_fps": native_fps,
            "processed_fps": native_fps / stride,
            "total_frames_sampled": len(landmarks_seq),
            "native_total_frames": total_frames,
            "width": width,
            "height": height,
            "detection_rate": round(detection_rate, 4),
        }
    }


def extract_all_poses(split_names: Optional[List[str]] = None, max_videos: Optional[int] = None):
    """
    Iterate over manifests and extract poses for each video.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if split_names is None:
        split_names = ["train", "val", "test", "external_test"]

    print("=" * 70)
    print("MediaPipe Pose Extraction Pipeline")
    print(f"Target splits: {split_names}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 70)

    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,  # 1 = balanced accuracy/speed
        smooth_landmarks=True,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    summary_records = []
    total_processed = 0

    try:
        for split in split_names:
            manifest_file = MANIFEST_DIR / f"{split}_manifest.csv"
            if not manifest_file.exists():
                print(f"Warning: manifest file {manifest_file} not found. Skipping.")
                continue

            df = pd.read_csv(manifest_file)
            print(f"\nProcessing split '{split}' ({len(df)} videos)...")

            for idx, row in df.iterrows():
                if max_videos and total_processed >= max_videos:
                    print(f"Reached max_videos limit ({max_videos}).")
                    break

                vid_id = row["video_id"]
                rel_path = row["rel_path"]
                exercise = row["exercise"]
                video_full_path = PROJECT_ROOT / rel_path

                out_file = OUTPUT_DIR / f"{vid_id}_{exercise}_{split}.npz"
                if out_file.exists():
                    print(f"  [{total_processed+1}] {vid_id} ({exercise}) already processed -> Skipping.")
                    total_processed += 1
                    continue

                t0 = time.time()
                result = process_single_video(video_full_path, pose, target_fps=20.0)
                elapsed = time.time() - t0

                if result is None:
                    print(f"  [{total_processed+1}] Error reading {vid_id} ({rel_path})")
                    continue

                # Save compressed npz
                np.savez_compressed(
                    out_file,
                    landmarks=result["landmarks"],
                    valid_mask=result["valid_mask"],
                    frame_indices=result["frame_indices"],
                    timestamps=result["timestamps"],
                    metadata=json.dumps(result["metadata"]),
                    exercise=exercise,
                    split=split,
                    video_id=vid_id,
                )

                meta = result["metadata"]
                det_rate = meta["detection_rate"]
                frames_cnt = meta["total_frames_sampled"]

                print(f"  [{total_processed+1}] {vid_id} ({exercise}, {split}) -> {frames_cnt} frames, "
                      f"det_rate={det_rate:.1%}, time={elapsed:.1f}s")

                summary_records.append({
                    "video_id": vid_id,
                    "exercise": exercise,
                    "split": split,
                    "npz_file": out_file.name,
                    "frames_sampled": frames_cnt,
                    "detection_rate": det_rate,
                    "processing_time_sec": round(elapsed, 2),
                })
                total_processed += 1

    finally:
        pose.close()

    # Save summary report
    if summary_records:
        sum_df = pd.DataFrame(summary_records)
        sum_csv = OUTPUT_DIR / "pose_extraction_summary.csv"
        sum_df.to_csv(sum_csv, index=False)
        print(f"\nPose extraction completed. Summary saved to: {sum_csv}")
        print(f"Average detection rate: {sum_df['detection_rate'].mean():.1%}")
        print(f"Total videos processed in this session: {len(sum_df)}")
    print("=" * 70)


if __name__ == "__main__":
    # If run directly with argument, e.g. python extract_poses.py
    extract_all_poses()
