"""
Dataset Inspection Script
=========================
Inspects Dataset1 (CSV pose/time-series) and Dataset2 (video-based exercise data).
Generates:
  - reports/dataset1_inspection.md
  - reports/dataset2_inspection.md
  - reports/dataset1_schema.json
  - reports/dataset2_schema.json

Usage:
    python scripts/inspect_datasets.py
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import pandas as pd
import cv2

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET1_DIR = PROJECT_ROOT / "Dataset" / "Dataset1"
DATASET2_DIR = PROJECT_ROOT / "Dataset" / "Dataset2"
REPORTS_DIR  = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv", ".flv"}


# ════════════════════════════════════════════════════════════════════════
#  DATASET 1 INSPECTION
# ════════════════════════════════════════════════════════════════════════

def inspect_dataset1():
    """Inspect all CSV files in Dataset1 and generate report + schema."""
    print("=" * 60)
    print("INSPECTING DATASET 1")
    print("=" * 60)

    csv_files = sorted(DATASET1_DIR.glob("*.csv"))
    if not csv_files:
        print("ERROR: No CSV files found in", DATASET1_DIR)
        return

    report_lines = []
    schema = {"dataset_name": "Physical Exercise Recognition | Time Series Dataset",
              "location": str(DATASET1_DIR),
              "inspection_date": datetime.now().isoformat(),
              "files": {}}

    report_lines.append("# Dataset1 Inspection Report")
    report_lines.append(f"\n**Dataset:** Physical Exercise Recognition | Time Series Dataset")
    report_lines.append(f"**Location:** `{DATASET1_DIR}`")
    report_lines.append(f"**Inspection Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    # ── Load all CSVs ──────────────────────────────────────────────────
    dfs = {}
    for csv_path in csv_files:
        name = csv_path.stem
        print(f"  Reading {csv_path.name}...")
        df = pd.read_csv(csv_path)
        dfs[name] = df

    # ── Per-file inspection ────────────────────────────────────────────
    report_lines.append("## File Summary\n")
    report_lines.append("| File | Rows | Columns | Size |")
    report_lines.append("|------|------|---------|------|")
    for csv_path in csv_files:
        name = csv_path.stem
        df = dfs[name]
        size_mb = csv_path.stat().st_size / (1024 * 1024)
        report_lines.append(f"| `{csv_path.name}` | {df.shape[0]:,} | {df.shape[1]} | {size_mb:.1f} MB |")
    report_lines.append("")

    for csv_path in csv_files:
        name = csv_path.stem
        df = dfs[name]
        size_bytes = csv_path.stat().st_size

        report_lines.append(f"---\n## {csv_path.name}\n")
        report_lines.append(f"- **Shape:** {df.shape[0]:,} rows × {df.shape[1]} columns")
        report_lines.append(f"- **File size:** {size_bytes / (1024*1024):.2f} MB")
        report_lines.append(f"- **Missing values:** {df.isnull().sum().sum()}")
        report_lines.append(f"- **Duplicate rows:** {df.duplicated().sum()}")
        report_lines.append("")

        # Columns and types
        report_lines.append("### Columns\n")
        report_lines.append("| Column | Data Type | Non-Null | Unique | Sample Values |")
        report_lines.append("|--------|-----------|----------|--------|---------------|")
        for col in df.columns:
            dtype = str(df[col].dtype)
            non_null = df[col].notna().sum()
            nunique = df[col].nunique()
            samples = df[col].dropna().unique()[:3]
            sample_str = ", ".join(str(s) for s in samples)
            if len(sample_str) > 50:
                sample_str = sample_str[:50] + "..."
            report_lines.append(f"| `{col}` | {dtype} | {non_null:,} | {nunique:,} | {sample_str} |")
        report_lines.append("")

        # Schema entry
        file_schema = {
            "filename": csv_path.name,
            "shape": list(df.shape),
            "size_bytes": size_bytes,
            "columns": {},
            "missing_values": int(df.isnull().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
        }
        for col in df.columns:
            file_schema["columns"][col] = {
                "dtype": str(df[col].dtype),
                "non_null_count": int(df[col].notna().sum()),
                "unique_count": int(df[col].nunique()),
                "sample_values": [str(v) for v in df[col].dropna().unique()[:5]],
            }
        schema["files"][name] = file_schema

    # ── Labels analysis ────────────────────────────────────────────────
    if "labels" in dfs:
        labels_df = dfs["labels"]
        report_lines.append("---\n## Class Distribution\n")
        class_counts = labels_df["class"].value_counts()
        report_lines.append("| Class | Count | Percentage |")
        report_lines.append("|-------|-------|------------|")
        total = len(labels_df)
        for cls, count in class_counts.items():
            pct = count / total * 100
            report_lines.append(f"| `{cls}` | {count} | {pct:.1f}% |")
        report_lines.append(f"\n**Total videos:** {total}")
        report_lines.append("")

        schema["class_distribution"] = {str(k): int(v) for k, v in class_counts.items()}
        schema["total_videos"] = int(total)

    # ── Landmarks analysis ─────────────────────────────────────────────
    if "landmarks" in dfs:
        lm = dfs["landmarks"]
        report_lines.append("---\n## Landmarks Analysis\n")
        lm_cols = [c for c in lm.columns if c not in ["vid_id", "frame_order"]]
        n_landmarks = len(lm_cols) // 3
        report_lines.append(f"- **Landmark feature columns:** {len(lm_cols)}")
        report_lines.append(f"- **Implied landmarks:** {n_landmarks} (×3 for x, y, z)")
        report_lines.append(f"- **Visibility columns:** None (not present)")
        report_lines.append(f"- **Unique video IDs:** {lm['vid_id'].nunique()}")
        report_lines.append("")

        frames_per_vid = lm.groupby("vid_id")["frame_order"].count()
        report_lines.append("### Frames Per Video\n")
        report_lines.append(f"- **Mean:** {frames_per_vid.mean():.1f}")
        report_lines.append(f"- **Std:** {frames_per_vid.std():.1f}")
        report_lines.append(f"- **Min:** {frames_per_vid.min()}")
        report_lines.append(f"- **Max:** {frames_per_vid.max()}")
        report_lines.append(f"- **Median:** {frames_per_vid.median():.1f}")
        report_lines.append("")

        # Extract landmark names
        landmark_names = sorted(set(c.split("_", 1)[1] if c.startswith(("x_", "y_", "z_")) else c
                                    for c in lm_cols))
        report_lines.append("### Landmark Names\n")
        for i, name in enumerate(landmark_names):
            report_lines.append(f"{i+1}. `{name}`")
        report_lines.append("")

        schema["landmarks"] = {
            "feature_count": len(lm_cols),
            "implied_landmarks": n_landmarks,
            "has_visibility": False,
            "unique_videos": int(lm["vid_id"].nunique()),
            "frames_per_video": {
                "mean": round(frames_per_vid.mean(), 1),
                "std": round(frames_per_vid.std(), 1),
                "min": int(frames_per_vid.min()),
                "max": int(frames_per_vid.max()),
            },
            "landmark_names": landmark_names,
        }

    # ── Angles analysis ────────────────────────────────────────────────
    if "angles" in dfs:
        ang = dfs["angles"]
        angle_cols = [c for c in ang.columns if c not in ["vid_id", "frame_order"]]
        report_lines.append("---\n## Angles Analysis\n")
        report_lines.append(f"- **Angle feature columns:** {len(angle_cols)}")
        report_lines.append("- **Angle definitions:**")
        for col in angle_cols:
            stats = ang[col].describe()
            report_lines.append(f"  - `{col}`: mean={stats['mean']:.1f}°, std={stats['std']:.1f}°, "
                                f"range=[{stats['min']:.1f}°, {stats['max']:.1f}°]")
        report_lines.append("")
        schema["angles"] = {
            "columns": angle_cols,
            "count": len(angle_cols),
        }

    # ── Distances analysis ─────────────────────────────────────────────
    if "calculated_3d_distances" in dfs:
        dist = dfs["calculated_3d_distances"]
        dist_cols = [c for c in dist.columns if c not in ["vid_id", "frame_order"]]
        report_lines.append("---\n## 3D Distances Analysis\n")
        report_lines.append(f"- **Distance feature columns:** {len(dist_cols)}")
        report_lines.append("- **Distance pairs:**")
        for col in dist_cols:
            report_lines.append(f"  - `{col}`")
        report_lines.append("")
        schema["distances_3d"] = {"columns": dist_cols, "count": len(dist_cols)}

    if "xyz_distances" in dfs:
        xyz = dfs["xyz_distances"]
        xyz_cols = [c for c in xyz.columns if c not in ["vid_id", "frame_order"]]
        report_lines.append("---\n## XYZ Distances Analysis\n")
        report_lines.append(f"- **XYZ distance feature columns:** {len(xyz_cols)}")
        report_lines.append(f"- **Implied distance pairs:** {len(xyz_cols) // 3} (×3 for x, y, z)")
        report_lines.append("")
        schema["distances_xyz"] = {"columns": xyz_cols[:10], "count": len(xyz_cols),
                                   "implied_pairs": len(xyz_cols) // 3}

    # ── Cross-file relationship ────────────────────────────────────────
    report_lines.append("---\n## Cross-File Relationships\n")
    if "landmarks" in dfs and "angles" in dfs:
        lm_vids = set(dfs["landmarks"]["vid_id"].unique())
        ang_vids = set(dfs["angles"]["vid_id"].unique())
        dist_vids = set(dfs["calculated_3d_distances"]["vid_id"].unique()) if "calculated_3d_distances" in dfs else set()
        xyz_vids = set(dfs["xyz_distances"]["vid_id"].unique()) if "xyz_distances" in dfs else set()
        lbl_vids = set(dfs["labels"]["vid_id"].unique()) if "labels" in dfs else set()

        report_lines.append(f"- All files share `vid_id` and `frame_order` as join keys")
        report_lines.append(f"- landmarks vid_ids: {len(lm_vids)}")
        report_lines.append(f"- angles vid_ids: {len(ang_vids)}")
        report_lines.append(f"- distances vid_ids: {len(dist_vids)}")
        report_lines.append(f"- xyz_distances vid_ids: {len(xyz_vids)}")
        report_lines.append(f"- labels vid_ids: {len(lbl_vids)}")
        report_lines.append(f"- All identical: {lm_vids == ang_vids == dist_vids == xyz_vids == lbl_vids}")

        # Row counts
        report_lines.append(f"- landmarks rows: {len(dfs['landmarks']):,}")
        report_lines.append(f"- angles rows: {len(dfs['angles']):,}")
        if "calculated_3d_distances" in dfs:
            report_lines.append(f"- distances rows: {len(dfs['calculated_3d_distances']):,}")
        if "xyz_distances" in dfs:
            report_lines.append(f"- xyz_distances rows: {len(dfs['xyz_distances']):,}")
        report_lines.append(f"- All row counts identical: "
                            f"{len(dfs['landmarks']) == len(dfs['angles'])}")
    report_lines.append("")

    # ── Target exercise overlap ────────────────────────────────────────
    report_lines.append("---\n## Relevance to Target Exercises\n")
    target = {"squat", "push_up", "bicep_curl", "shoulder_press"}
    if "labels" in dfs:
        available = set(dfs["labels"]["class"].unique())
        overlap = target & available
        missing = target - available
        extra = available - target
        report_lines.append(f"- **Target exercises:** {sorted(target)}")
        report_lines.append(f"- **Available in Dataset1:** {sorted(available)}")
        report_lines.append(f"- **Overlap:** {sorted(overlap)}")
        report_lines.append(f"- **Missing from Dataset1:** {sorted(missing)}")
        report_lines.append(f"- **Extra in Dataset1 (not needed):** {sorted(extra)}")
        report_lines.append("")
        report_lines.append("> **Conclusion:** Dataset1 only provides `push_up` and `squat` data. "
                            "It does NOT contain `bicep_curl` or `shoulder_press`. "
                            "Dataset1 will be used as supplementary data only.")

    # ── Save ───────────────────────────────────────────────────────────
    report_path = REPORTS_DIR / "dataset1_inspection.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"  Saved: {report_path}")

    schema_path = REPORTS_DIR / "dataset1_schema.json"
    schema_path.write_text(json.dumps(schema, indent=2, default=str), encoding="utf-8")
    print(f"  Saved: {schema_path}")


# ════════════════════════════════════════════════════════════════════════
#  DATASET 2 INSPECTION
# ════════════════════════════════════════════════════════════════════════

def get_video_metadata(video_path: str) -> dict:
    """Extract video metadata using OpenCV."""
    meta = {
        "path": video_path,
        "filename": os.path.basename(video_path),
        "extension": os.path.splitext(video_path)[1].lower(),
        "size_bytes": os.path.getsize(video_path),
        "corrupted": False,
    }
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            meta["corrupted"] = True
            return meta
        meta["fps"] = cap.get(cv2.CAP_PROP_FPS)
        meta["width"] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        meta["height"] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        meta["frame_count"] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if meta["fps"] and meta["fps"] > 0:
            meta["duration_seconds"] = round(meta["frame_count"] / meta["fps"], 2)
        else:
            meta["duration_seconds"] = None
        cap.release()
    except Exception as e:
        meta["corrupted"] = True
        meta["error"] = str(e)
    return meta


def file_hash(filepath: str, chunk_size: int = 8192) -> str:
    """Compute MD5 hash of a file for duplicate detection."""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def inspect_dataset2():
    """Inspect all video folders in Dataset2 and generate report + schema."""
    print("\n" + "=" * 60)
    print("INSPECTING DATASET 2")
    print("=" * 60)

    report_lines = []
    schema = {
        "dataset_name": "Real-Time Exercise Recognition Dataset",
        "location": str(DATASET2_DIR),
        "inspection_date": datetime.now().isoformat(),
        "folders": {},
    }

    report_lines.append("# Dataset2 Inspection Report")
    report_lines.append(f"\n**Dataset:** Real-Time Exercise Recognition Dataset")
    report_lines.append(f"**Location:** `{DATASET2_DIR}`")
    report_lines.append(f"**Inspection Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    folders = ["final_kaggle_with_additional_video", "my_test_video_1",
               "similar_dataset", "synthetic_dataset"]

    all_videos_meta = []
    folder_summaries = {}

    for folder_name in folders:
        folder_path = DATASET2_DIR / folder_name
        if not folder_path.exists():
            print(f"  WARNING: {folder_path} does not exist")
            continue

        print(f"\n  Inspecting {folder_name}...")
        report_lines.append(f"---\n## {folder_name}\n")

        folder_data = {"exercises": {}, "total_videos": 0, "total_size_bytes": 0}
        exercise_dirs = []

        # Handle nested synthetic_dataset
        if folder_name == "synthetic_dataset":
            nested = folder_path / "synthetic_dataset"
            if nested.exists():
                folder_path = nested

        for item in sorted(folder_path.iterdir()):
            if item.is_dir():
                exercise_dirs.append(item)

        if not exercise_dirs:
            report_lines.append("*No exercise subdirectories found.*\n")
            continue

        report_lines.append("### Exercise Classes\n")
        report_lines.append("| Exercise | Videos | Extensions | Total Size | Avg Duration | Avg FPS | Resolutions |")
        report_lines.append("|----------|--------|------------|------------|-------------|---------|-------------|")

        for ex_dir in exercise_dirs:
            exercise_name = ex_dir.name
            # Find video files
            video_files = []
            json_files = []
            other_files = []

            for f in sorted(ex_dir.iterdir()):
                if f.is_file():
                    ext = f.suffix.lower()
                    if ext in VIDEO_EXTENSIONS:
                        video_files.append(f)
                    elif ext == ".json":
                        json_files.append(f)
                    else:
                        other_files.append(f)

            if not video_files:
                report_lines.append(f"| `{exercise_name}` | 0 | — | — | — | — | — |")
                continue

            # Get metadata for each video (sample up to 25 for performance)
            metas = []
            sample_videos = video_files[:25] if folder_name != "synthetic_dataset" else video_files[:10]
            for vf in sample_videos:
                print(f"    Inspecting {vf.name}...")
                meta = get_video_metadata(str(vf))
                meta["exercise"] = exercise_name
                meta["folder"] = folder_name
                metas.append(meta)
                all_videos_meta.append(meta)

            extensions = sorted(set(m["extension"] for m in metas))
            total_size = sum(m["size_bytes"] for m in metas)
            corrupted = [m for m in metas if m.get("corrupted")]
            valid_metas = [m for m in metas if not m.get("corrupted") and m.get("duration_seconds")]

            avg_duration = (sum(m["duration_seconds"] for m in valid_metas) / len(valid_metas)
                           if valid_metas else 0)
            avg_fps = (sum(m["fps"] for m in valid_metas) / len(valid_metas)
                       if valid_metas else 0)
            resolutions = sorted(set(f"{m['width']}×{m['height']}" for m in valid_metas))

            report_lines.append(
                f"| `{exercise_name}` | {len(video_files)} | "
                f"{', '.join(extensions)} | {total_size/(1024*1024):.1f} MB | "
                f"{avg_duration:.1f}s | {avg_fps:.1f} | {', '.join(resolutions[:3])} |"
            )

            folder_data["exercises"][exercise_name] = {
                "video_count": len(video_files),
                "json_count": len(json_files),
                "extensions": extensions,
                "total_size_bytes": total_size,
                "corrupted_count": len(corrupted),
                "avg_duration_seconds": round(avg_duration, 2) if valid_metas else None,
                "avg_fps": round(avg_fps, 1) if valid_metas else None,
                "resolutions": resolutions,
                "sample_filenames": [vf.name for vf in video_files[:5]],
            }
            folder_data["total_videos"] += len(video_files)
            folder_data["total_size_bytes"] += total_size

        report_lines.append("")
        report_lines.append(f"**Total videos in folder:** {folder_data['total_videos']}")
        report_lines.append(f"**Total size (sampled):** {folder_data['total_size_bytes']/(1024*1024):.1f} MB")
        report_lines.append("")

        # Folder-specific notes
        if folder_name == "final_kaggle_with_additional_video":
            report_lines.append("> **Note:** Contains `hammer curl` (19 videos) which is NOT a target exercise. "
                                "Must be excluded from training.\n")
        elif folder_name == "my_test_video_1":
            report_lines.append("> **Note:** Contains only 3–4 videos per exercise. "
                                "These are user test videos and should be treated as EXTERNAL TEST DATA only.\n")
        elif folder_name == "similar_dataset":
            report_lines.append("> **Note:** Contains UUID-named files and videos from UCF101 dataset "
                                "(v_PushUps, v_BodyWeightSquats patterns). "
                                "7 shoulder press files overlap with final_kaggle by filename.\n")
        elif folder_name == "synthetic_dataset":
            report_lines.append("> **Note:** Synthetic data with COCO-format JSON annotations (17 keypoints). "
                                "Videos are 224×224 resolution. Must re-process through MediaPipe for "
                                "consistent 33-landmark features. Track synthetic contribution separately.\n")

        schema["folders"][folder_name] = folder_data
        folder_summaries[folder_name] = folder_data

    # ── Duplicate detection across folders ─────────────────────────────
    report_lines.append("---\n## Cross-Folder Analysis\n")

    # Check shoulder press overlap
    report_lines.append("### Filename Overlap Detection\n")
    final_kaggle = DATASET2_DIR / "final_kaggle_with_additional_video"
    similar = DATASET2_DIR / "similar_dataset"
    target_exercises = ["barbell biceps curl", "push-up", "shoulder press", "squat"]

    for ex in target_exercises:
        fk_dir = final_kaggle / ex
        sim_dir = similar / ex
        if fk_dir.exists() and sim_dir.exists():
            fk_files = set(f.name for f in fk_dir.iterdir() if f.is_file())
            sim_files = set(f.name for f in sim_dir.iterdir() if f.is_file())
            overlap = fk_files & sim_files
            if overlap:
                report_lines.append(f"- **{ex}:** {len(overlap)} overlapping filenames: "
                                    f"`{'`, `'.join(sorted(overlap)[:5])}`")
            else:
                report_lines.append(f"- **{ex}:** No filename overlap")
    report_lines.append("")

    # ── Recommended usage manifest ─────────────────────────────────────
    report_lines.append("---\n## Recommended Usage\n")
    report_lines.append("| Folder | Recommended Usage | Synthetic/Real | Notes |")
    report_lines.append("|--------|-------------------|----------------|-------|")
    report_lines.append("| `final_kaggle_with_additional_video` | **Primary Training** | Real | "
                        "Exclude hammer_curl |")
    report_lines.append("| `similar_dataset` | **Supplementary Training/Validation** | Real + UCF101 | "
                        "Deduplicate shoulder press overlap |")
    report_lines.append("| `my_test_video_1` | **External Test Only** | Real | "
                        "User-provided test videos |")
    report_lines.append("| `synthetic_dataset` | **Augmentation (optional)** | Synthetic | "
                        "224×224, needs MediaPipe re-processing |")
    report_lines.append("")

    # ── Save ───────────────────────────────────────────────────────────
    report_path = REPORTS_DIR / "dataset2_inspection.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"\n  Saved: {report_path}")

    schema_path = REPORTS_DIR / "dataset2_schema.json"
    schema_path.write_text(json.dumps(schema, indent=2, default=str), encoding="utf-8")
    print(f"  Saved: {schema_path}")


# ════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Dataset1: {DATASET1_DIR}")
    print(f"Dataset2: {DATASET2_DIR}")
    print()

    inspect_dataset1()
    inspect_dataset2()

    print("\n" + "=" * 60)
    print("INSPECTION COMPLETE")
    print("=" * 60)
    print(f"Reports saved to: {REPORTS_DIR}")
