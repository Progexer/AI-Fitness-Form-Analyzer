"""
AI-Powered Fitness Coach — Dataset2 Preprocessing & Manifest Generator

Responsibilities:
1. Scan Dataset2 folders (final_kaggle_with_additional_video, similar_dataset, my_test_video_1).
2. Filter for 4 target exercises: squat, push-up, bicep_curl, shoulder_press.
3. Exclude 'hammer_curl' and any unsupported classes.
4. Deduplicate overlapping shoulder press files (by filename hash / normalized name).
5. Quarantine 'my_test_video_1' strictly as external holdout test set (NEVER leaked to train/val).
6. Perform video-level stratified train (70%) / val (15%) / test (15%) split.
7. Generate comprehensive metadata manifest CSV with video duration, FPS, frame count, resolution.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

# Target exercises mapping (standardized names)
TARGET_EXERCISES = {
    "squat": "squat",
    "squats": "squat",
    "push-up": "push_up",
    "pushup": "push_up",
    "push_up": "push_up",
    "push_ups": "push_up",
    "bicep_curl": "bicep_curl",
    "bicep curl": "bicep_curl",
    "bicep_curls": "bicep_curl",
    "biceps curl": "bicep_curl",
    "barbell biceps curl": "bicep_curl",
    "barbell_biceps_curl": "bicep_curl",
    "shoulder_press": "shoulder_press",
    "shoulder press": "shoulder_press",
}

EXCLUDED_CLASSES = {"hammer_curl", "hammer curl", "hammer_curls"}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "Dataset" / "Dataset2"
MANIFEST_DIR = PROJECT_ROOT / "data" / "manifests"


def compute_file_hash(filepath: Path, chunk_size: int = 65536) -> str:
    """Calculate SHA256 of first 64KB + file size for fast duplicate detection."""
    hasher = hashlib.sha256()
    hasher.update(str(filepath.stat().st_size).encode())
    with open(filepath, "rb") as f:
        hasher.update(f.read(chunk_size))
    return hasher.hexdigest()


def get_video_metadata(video_path: Path) -> Dict[str, Any]:
    """Extract FPS, frame count, width, height, duration via OpenCV."""
    meta = {
        "width": 0,
        "height": 0,
        "fps": 0.0,
        "total_frames": 0,
        "duration_sec": 0.0,
        "is_valid": False,
        "codec": "",
    }
    if cv2 is None:
        return meta

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return meta

    try:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc_int >> 8 * i) & 0xFF) for i in range(4)])

        if fps <= 0:
            fps = 30.0  # Fallback default
        duration_sec = total_frames / fps if total_frames > 0 else 0.0

        meta.update({
            "width": width,
            "height": height,
            "fps": round(fps, 2),
            "total_frames": total_frames,
            "duration_sec": round(duration_sec, 2),
            "is_valid": total_frames > 0 and width > 0 and height > 0,
            "codec": codec.strip(),
        })
    except Exception as e:
        meta["error"] = str(e)
    finally:
        cap.release()

    return meta


def normalize_class_name(raw_name: str) -> Optional[str]:
    """Normalize raw exercise directory/tag to target canonical name."""
    clean = raw_name.strip().lower().replace(" ", "_").replace("-", "_")
    if clean in EXCLUDED_CLASSES:
        return None
    for key, val in TARGET_EXERCISES.items():
        if key.replace(" ", "_").replace("-", "_") == clean:
            return val
    return None


def scan_dataset2() -> List[Dict[str, Any]]:
    """Scan all Dataset2 subdirectories, filter, deduplicate, and assemble records."""
    records = []
    seen_hashes = {}
    seen_basenames = {}

    folders_to_scan = [
        ("final_kaggle_with_additional_video", "primary_training"),
        ("similar_dataset", "supplementary"),
        ("my_test_video_1", "external_test"),
    ]

    for folder_name, source_role in folders_to_scan:
        folder_path = DATA_DIR / folder_name
        if not folder_path.exists():
            print(f"Warning: {folder_path} does not exist.")
            continue

        print(f"Scanning folder: {folder_name} (Role: {source_role})...")
        for root, dirs, files in os.walk(folder_path):
            rel_root = Path(root).relative_to(folder_path)
            parts = rel_root.parts

            if not parts:
                continue

            # Class is typically first subdirectory
            raw_class = parts[0]
            canonical_class = normalize_class_name(raw_class)

            if not canonical_class:
                # Excluded (e.g. hammer_curl) or unrecognized
                continue

            for file in files:
                if not file.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".webm")):
                    continue

                full_path = Path(root) / file
                rel_path = full_path.relative_to(PROJECT_ROOT)
                file_size = full_path.stat().st_size

                # Compute hash for exact duplicate detection
                try:
                    fhash = compute_file_hash(full_path)
                except Exception:
                    fhash = f"{file_size}_{file}"

                # Check duplicate across datasets
                is_duplicate = False
                dup_reason = ""

                # Special deduplication rule: 7 shoulder_press files overlap between similar_dataset and final_kaggle
                if file.lower() in seen_basenames and source_role == "supplementary":
                    is_duplicate = True
                    dup_reason = f"Duplicate filename with {seen_basenames[file.lower()]}"
                elif fhash in seen_hashes:
                    is_duplicate = True
                    dup_reason = f"Identical file content with {seen_hashes[fhash]}"
                else:
                    seen_hashes[fhash] = str(rel_path)
                    seen_basenames[file.lower()] = str(rel_path)

                # Extract video metadata
                meta = get_video_metadata(full_path)

                records.append({
                    "video_id": f"vid_{len(records)+1:04d}",
                    "filename": file,
                    "rel_path": str(rel_path).replace("\\", "/"),
                    "source_folder": folder_name,
                    "source_role": source_role,
                    "exercise": canonical_class,
                    "file_size_bytes": file_size,
                    "file_hash": fhash,
                    "is_duplicate": is_duplicate,
                    "dup_reason": dup_reason,
                    "width": meta["width"],
                    "height": meta["height"],
                    "fps": meta["fps"],
                    "total_frames": meta["total_frames"],
                    "duration_sec": meta["duration_sec"],
                    "is_valid": meta["is_valid"],
                })

    return records


def perform_splits(df: pd.DataFrame, random_state: int = 42) -> pd.DataFrame:
    """
    Perform stratified train/val/test splits strictly at VIDEO level.
    Rules:
    - 'my_test_video_1' -> strictly 'external_test' (never in train/val)
    - Excluded / duplicates / invalid -> 'excluded'
    - Remaining valid videos -> 70% train, 15% val, 15% test stratified by exercise.
    """
    np.random.seed(random_state)
    df["split"] = "unassigned"

    # 1. Mark duplicates and invalid files
    df.loc[df["is_duplicate"] | (~df["is_valid"]), "split"] = "excluded"

    # 2. Mark external test videos
    df.loc[(df["source_role"] == "external_test") & (df["split"] != "excluded"), "split"] = "external_test"

    # 3. Eligible training pool: primary_training & supplementary valid non-duplicates
    trainable_mask = (df["source_role"].isin(["primary_training", "supplementary"])) & (df["split"] == "unassigned")
    trainable_indices = df[trainable_mask].index

    # Stratified split per exercise
    for exercise in TARGET_EXERCISES.values():
        ex_mask = trainable_mask & (df["exercise"] == exercise)
        ex_indices = df[ex_mask].index.tolist()

        if not ex_indices:
            continue

        np.random.shuffle(ex_indices)
        n = len(ex_indices)
        n_train = int(round(n * 0.70))
        n_val = int(round(n * 0.15))
        if n_train + n_val >= n:
            n_val = max(1, n - n_train - 1)
        n_test = n - n_train - n_val

        train_idx = ex_indices[:n_train]
        val_idx = ex_indices[n_train:n_train + n_val]
        test_idx = ex_indices[n_train + n_val:]

        df.loc[train_idx, "split"] = "train"
        df.loc[val_idx, "split"] = "val"
        df.loc[test_idx, "split"] = "test"

    return df


def main():
    print("=" * 70)
    print("Dataset2 Preprocessing & Video Manifest Pipeline")
    print("=" * 70)

    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    records = scan_dataset2()
    df = pd.DataFrame(records)

    print(f"Total videos scanned: {len(df)}")
    print(f"Exercises found: {df['exercise'].value_counts().to_dict()}")
    print(f"Duplicates detected: {df['is_duplicate'].sum()}")

    df = perform_splits(df)

    split_counts = df["split"].value_counts().to_dict()
    print("\nDataset Split Summary:")
    for split_name, count in split_counts.items():
        print(f"  - {split_name}: {count}")

    # Exercise x Split cross-tab
    crosstab = pd.crosstab(df[df["split"].isin(["train", "val", "test", "external_test"])]["exercise"], df["split"])
    print("\nExercise distribution across splits:")
    print(crosstab)

    # Save master manifest
    master_path = MANIFEST_DIR / "dataset2_manifest.csv"
    df.to_csv(master_path, index=False)
    print(f"\nSaved master manifest to: {master_path}")

    # Save split manifests
    for split_val in ["train", "val", "test", "external_test"]:
        sub_df = df[df["split"] == split_val]
        sub_path = MANIFEST_DIR / f"{split_val}_manifest.csv"
        sub_df.to_csv(sub_path, index=False)
        print(f"Saved {split_val} manifest ({len(sub_df)} videos) to: {sub_path}")

    # Save summary stats JSON
    summary = {
        "total_scanned": len(df),
        "total_usable": int((df["split"].isin(["train", "val", "test", "external_test"])).sum()),
        "duplicates_removed": int(df["is_duplicate"].sum()),
        "invalid_videos": int((~df["is_valid"]).sum()),
        "splits": {k: int(v) for k, v in split_counts.items()},
        "exercises": {k: int(v) for k, v in df["exercise"].value_counts().items()},
        "avg_duration_sec": float(round(df[df['is_valid']]['duration_sec'].mean(), 2)),
        "avg_fps": float(round(df[df['is_valid']]['fps'].mean(), 2)),
    }
    with open(MANIFEST_DIR / "manifest_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\nDataset2 manifest generation completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()
