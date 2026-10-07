# Dataset2 Inspection Report

**Dataset:** Real-Time Exercise Recognition Dataset
**Location:** `D:\AIML_Project\Dataset\Dataset2`
**Inspection Date:** 2026-09-12 01:35:22

---
## final_kaggle_with_additional_video

### Exercise Classes

| Exercise | Videos | Extensions | Total Size | Avg Duration | Avg FPS | Resolutions |
|----------|--------|------------|------------|-------------|---------|-------------|
| `barbell biceps curl` | 25 | .mp4 | 21.7 MB | 3.7s | 29.3 | 1280×720, 1920×1080 |
| `hammer curl` | 19 | .mov, .mp4 | 364.7 MB | 9.8s | 30.0 | 1080×1920, 1080×608, 1280×720 |
| `push-up` | 25 | .mp4 | 14.1 MB | 4.6s | 30.0 | 1920×1080 |
| `shoulder press` | 25 | .mov, .mp4 | 318.7 MB | 11.6s | 28.3 | 1280×720, 1920×1080, 640×360 |
| `squat` | 25 | .mov, .mp4 | 430.7 MB | 11.9s | 26.9 | 1280×720, 1920×1080, 596×336 |

**Total videos in folder:** 119
**Total size (sampled):** 1150.0 MB

> **Note:** Contains `hammer curl` (19 videos) which is NOT a target exercise. Must be excluded from training.

---
## my_test_video_1

### Exercise Classes

| Exercise | Videos | Extensions | Total Size | Avg Duration | Avg FPS | Resolutions |
|----------|--------|------------|------------|-------------|---------|-------------|
| `barbell biceps curl` | 4 | .mp4 | 59.1 MB | 13.2s | 30.0 | 1280×720 |
| `push-up` | 3 | .mp4 | 40.9 MB | 12.8s | 30.0 | 1280×720 |
| `shoulder press` | 4 | .mp4 | 64.7 MB | 14.4s | 30.0 | 1280×720 |
| `squat` | 4 | .mp4 | 66.4 MB | 14.8s | 30.0 | 1280×720 |

**Total videos in folder:** 15
**Total size (sampled):** 231.1 MB

> **Note:** Contains only 3–4 videos per exercise. These are user test videos and should be treated as EXTERNAL TEST DATA only.

---
## similar_dataset

### Exercise Classes

| Exercise | Videos | Extensions | Total Size | Avg Duration | Avg FPS | Resolutions |
|----------|--------|------------|------------|-------------|---------|-------------|
| `barbell biceps curl` | 18 | .mov, .mp4 | 198.2 MB | 10.1s | 27.9 | 1080×1920, 1280×720, 1440×1080 |
| `push-up` | 18 | .avi, .mp4 | 29.4 MB | 7.3s | 34.1 | 1280×720, 1920×1080, 320×240 |
| `shoulder press` | 18 | .mov, .mp4 | 155.0 MB | 10.2s | 28.1 | 1080×1918, 1080×1920, 1280×720 |
| `squat` | 18 | .avi, .mp4 | 13.2 MB | 6.8s | 26.3 | 1280×720, 1920×1080, 320×240 |

**Total videos in folder:** 72
**Total size (sampled):** 395.8 MB

> **Note:** Contains UUID-named files and videos from UCF101 dataset (v_PushUps, v_BodyWeightSquats patterns). 7 shoulder press files overlap with final_kaggle by filename.

---
## synthetic_dataset

### Exercise Classes

| Exercise | Videos | Extensions | Total Size | Avg Duration | Avg FPS | Resolutions |
|----------|--------|------------|------------|-------------|---------|-------------|
| `barbell biceps curl` | 100 | .mp4 | 2.3 MB | 13.7s | 24.0 | 224×224 |
| `push-up` | 100 | .mp4 | 2.3 MB | 13.3s | 24.0 | 224×224 |
| `shoulder press` | 100 | .mp4 | 2.5 MB | 15.0s | 24.0 | 224×224 |
| `squat` | 100 | .mp4 | 3.7 MB | 19.1s | 24.0 | 224×224 |

**Total videos in folder:** 400
**Total size (sampled):** 10.8 MB

> **Note:** Synthetic data with COCO-format JSON annotations (17 keypoints). Videos are 224×224 resolution. Must re-process through MediaPipe for consistent 33-landmark features. Track synthetic contribution separately.

---
## Cross-Folder Analysis

### Filename Overlap Detection

- **barbell biceps curl:** No filename overlap
- **push-up:** No filename overlap
- **shoulder press:** 7 overlapping filenames: `shoulder press_12.mp4`, `shoulder press_3.MOV`, `shoulder press_4.MOV`, `shoulder press_6.mp4`, `shoulder press_7.mp4`
- **squat:** No filename overlap

---
## Recommended Usage

| Folder | Recommended Usage | Synthetic/Real | Notes |
|--------|-------------------|----------------|-------|
| `final_kaggle_with_additional_video` | **Primary Training** | Real | Exclude hammer_curl |
| `similar_dataset` | **Supplementary Training/Validation** | Real + UCF101 | Deduplicate shoulder press overlap |
| `my_test_video_1` | **External Test Only** | Real | User-provided test videos |
| `synthetic_dataset` | **Augmentation (optional)** | Synthetic | 224×224, needs MediaPipe re-processing |
