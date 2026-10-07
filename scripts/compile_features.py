"""
AI-Powered Fitness Coach — Feature Compilation Pipeline

Reads extracted pose sequences (.npz) from data/interim/poses/,
runs the BiomechanicalFeaturePipeline on each frame,
and compiles master tabular datasets (train/val/test/external_test)
into data/processed/.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.features.feature_pipeline import BiomechanicalFeaturePipeline

POSES_DIR = PROJECT_ROOT / "data" / "interim" / "poses"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def compile_features_from_poses(max_per_video_frames: int = 150):
    """
    Load all available .npz files, extract features, and save per-split CSVs.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    pipeline = BiomechanicalFeaturePipeline()

    npz_files = list(POSES_DIR.glob("*.npz"))
    print("=" * 70)
    print(f"Compiling Features from {len(npz_files)} pose files...")
    print("=" * 70)

    split_dfs = {
        "train": [],
        "val": [],
        "test": [],
        "external_test": []
    }

    video_level_records = []

    for i, npz_path in enumerate(npz_files):
        try:
            data = np.load(npz_path, allow_pickle=True)
            landmarks = data["landmarks"]      # (T, 33, 4)
            valid_mask = data["valid_mask"]    # (T,)
            timestamps = data["timestamps"]    # (T,)
            exercise = str(data["exercise"])
            split = str(data["split"])
            vid_id = str(data["video_id"])

            if split not in split_dfs:
                continue

            t_len = landmarks.shape[0]
            if t_len == 0:
                continue

            pipeline.reset()
            frame_records = []

            # Sample frames to avoid massive files (e.g. at most max_per_video_frames evenly spaced)
            if t_len > max_per_video_frames:
                indices = np.linspace(0, t_len - 1, max_per_video_frames, dtype=int)
            else:
                indices = np.arange(t_len)

            for t in indices:
                if not valid_mask[t]:
                    continue

                res = pipeline.extract_frame_features(landmarks[t], exercise=exercise)
                feat_row = dict(res["features_dict"])
                feat_row["video_id"] = vid_id
                feat_row["exercise"] = exercise
                feat_row["split"] = split
                feat_row["timestamp"] = float(timestamps[t])
                feat_row["form_label"] = res["form_label"]
                frame_records.append(feat_row)

            if frame_records:
                split_dfs[split].extend(frame_records)
                video_level_records.append({
                    "video_id": vid_id,
                    "exercise": exercise,
                    "split": split,
                    "total_frames": t_len,
                    "sampled_frames": len(frame_records)
                })

            if (i + 1) % 10 == 0 or (i + 1) == len(npz_files):
                print(f"  Processed {i + 1}/{len(npz_files)} video pose files...")

        except Exception as e:
            print(f"  Error loading {npz_path.name}: {e}")

    # Export consolidated CSVs and Parquet files
    for split_name, rows in split_dfs.items():
        if rows:
            df = pd.DataFrame(rows)
            csv_path = PROCESSED_DIR / f"{split_name}_features.csv"
            df.to_csv(csv_path, index=False)
            print(f"Saved {split_name} features ({len(df)} frames) to: {csv_path}")
            # Try saving parquet as well for high-speed loading
            try:
                parquet_path = PROCESSED_DIR / f"{split_name}_features.parquet"
                df.to_parquet(parquet_path, index=False)
            except Exception:
                pass

    if video_level_records:
        summary_df = pd.DataFrame(video_level_records)
        summary_df.to_csv(PROCESSED_DIR / "compiled_videos_summary.csv", index=False)

    print("\nFeature compilation finished.")
    print("=" * 70)


if __name__ == "__main__":
    compile_features_from_poses()
