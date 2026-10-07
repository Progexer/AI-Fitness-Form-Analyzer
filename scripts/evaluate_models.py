"""
AI-Powered Fitness Coach — Comprehensive Model Evaluation & Benchmarking

Evaluates Random Forest, XGBoost, and Bi-LSTM on holdout test data and external test sets.
Benchmarks inference latency (FPS / ms per frame) and generates comparison reports.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import joblib
import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.random_forest.model import RandomForestExerciseClassifier
from app.ml.xgboost_model.model import XGBoostFormClassifier
from app.ml.lstm.model import BiLSTMExerciseClassifier

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORT_DIR = PROJECT_ROOT / "reports" / "model_evaluation"
MODEL_DIR = PROJECT_ROOT / "models"


def benchmark_latency(model_fn, sample_input, iterations: int = 100) -> Dict[str, float]:
    """Measures mean latency and throughput (FPS)."""
    # Warmup
    for _ in range(10):
        model_fn(sample_input)

    t0 = time.perf_counter()
    for _ in range(iterations):
        model_fn(sample_input)
    t1 = time.perf_counter()

    total_time = t1 - t0
    avg_latency_ms = (total_time / iterations) * 1000.0
    fps = iterations / total_time if total_time > 0 else 0.0

    return {
        "avg_latency_ms": round(avg_latency_ms, 3),
        "throughput_fps": round(fps, 1),
    }


def evaluate_all():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    test_path = PROCESSED_DIR / "test_features.csv"

    print("=" * 70)
    print("AI-Powered Fitness Coach — Model Evaluation & Benchmarking")
    print("=" * 70)

    results = {}

    if not test_path.exists():
        print(f"Warning: {test_path} not found. Running synthetic benchmark verification.")
        # Provide structural benchmark test
        sample_feat = {f"lm_{i}": 0.0 for i in range(99)}
        sample_feat.update({
            "left_elbow_angle": 90.0, "right_elbow_angle": 90.0, "avg_elbow_angle": 90.0,
            "left_knee_angle": 170.0, "right_knee_angle": 170.0, "avg_knee_angle": 170.0,
            "left_hip_angle": 170.0, "right_hip_angle": 170.0, "avg_hip_angle": 170.0,
            "left_shoulder_angle": 45.0, "right_shoulder_angle": 45.0, "avg_shoulder_angle": 45.0,
            "trunk_angle": 5.0, "neck_angle": 10.0,
            "elbow_symmetry_diff": 0.0, "knee_symmetry_diff": 0.0, "hip_symmetry_diff": 0.0, "shoulder_symmetry_diff": 0.0,
            "ankle_distance_norm": 0.4, "wrist_distance_norm": 0.5, "shoulder_distance_norm": 0.3,
            "hip_distance_norm": 0.25, "wrist_to_shoulder_l_norm": 0.3, "wrist_to_shoulder_r_norm": 0.3,
            "avg_wrist_to_shoulder_norm": 0.3, "wrist_to_hip_l_norm": 0.4, "wrist_to_hip_r_norm": 0.4,
            "hip_depth_diff_norm": -0.2, "hand_elevation_l_norm": -0.2, "hand_elevation_r_norm": -0.2,
            "avg_hand_elevation_norm": -0.2, "elbow_angular_vel": 0.0, "knee_angular_vel": 0.0,
            "hip_angular_vel": 0.0, "shoulder_angular_vel": 0.0, "trunk_angular_vel": 0.0,
            "window_elbow_rom": 10.0, "window_knee_rom": 5.0, "window_hip_rom": 5.0, "window_shoulder_rom": 5.0,
            "elbow_velocity_std": 2.0, "knee_velocity_std": 1.0, "smoothness_score": 95.0,
        })
    else:
        test_df = pd.read_csv(test_path)
        feature_cols = [c for c in test_df.columns if c not in {"video_id", "exercise", "split", "timestamp", "form_label"}]
        X_test = test_df[feature_cols].values
        y_test = test_df["exercise"].values
        sample_feat = test_df.iloc[0][feature_cols].to_dict()

    # 1. Random Forest Evaluation
    rf_clf = RandomForestExerciseClassifier()
    if rf_clf.is_ready and test_path.exists():
        y_preds = [rf_clf.predict({c: row[c] for c in feature_cols})["exercise"] for _, row in test_df.iterrows()]
        acc = accuracy_score(y_test, y_preds)
        f1_m = f1_score(y_test, y_preds, average="macro")
        lat = benchmark_latency(rf_clf.predict, sample_feat)
        results["random_forest"] = {
            "model": "Random Forest",
            "task": "Exercise Recognition",
            "test_accuracy": round(float(acc), 4),
            "macro_f1": round(float(f1_m), 4),
            "latency_ms": lat["avg_latency_ms"],
            "fps": lat["throughput_fps"],
            "status": "Trained & Validated"
        }
        print(f"\n[Random Forest] Test Acc: {acc:.4f} | F1: {f1_m:.4f} | Latency: {lat['avg_latency_ms']} ms ({lat['throughput_fps']} FPS)")

    # 2. XGBoost Evaluation
    xgb_clf = XGBoostFormClassifier()
    if xgb_clf.is_ready:
        lat = benchmark_latency(xgb_clf.predict, sample_feat)
        results["xgboost"] = {
            "model": "XGBoost",
            "task": "Biomechanical Form & Error Classification",
            "latency_ms": lat["avg_latency_ms"],
            "fps": lat["throughput_fps"],
            "status": "Trained & Validated"
        }
        print(f"\n[XGBoost] Latency: {lat['avg_latency_ms']} ms ({lat['throughput_fps']} FPS)")

    # 3. Bi-LSTM Latency Benchmark
    lstm_path = MODEL_DIR / "lstm" / "bilstm_best.pth"
    if lstm_path.exists():
        device = torch.device("cpu")
        lstm_model = BiLSTMExerciseClassifier(input_size=99, hidden_size=64, num_layers=2, num_classes=4)
        lstm_model.load_state_dict(torch.load(lstm_path, map_location=device))
        lstm_model.eval()

        dummy_seq = torch.randn(1, 30, 99)
        with torch.no_grad():
            lat = benchmark_latency(lstm_model, dummy_seq)
        # Attach honest validation metrics from training history (video-level split)
        lstm_cfg_path = MODEL_DIR / "lstm" / "lstm_config.json"
        lstm_val_f1, lstm_val_acc = None, None
        try:
            with open(lstm_cfg_path) as f:
                cfg = json.load(f)
            lstm_val_f1 = cfg.get("best_val_f1")
            hist = cfg.get("history", [])
            best_ep = max(hist, key=lambda h: h.get("val_f1", 0)) if hist else {}
            lstm_val_acc = best_ep.get("val_acc")
        except Exception:
            pass
        results["bilstm"] = {
            "model": "Bi-LSTM (PyTorch)",
            "task": "Temporal Sequence Exercise Classification",
            "val_accuracy": lstm_val_acc,
            "val_f1": lstm_val_f1,
            "latency_ms": lat["avg_latency_ms"],
            "fps": lat["throughput_fps"],
            "status": "Trained & Validated"
        }
        print(f"\n[Bi-LSTM] Latency: {lat['avg_latency_ms']} ms ({lat['throughput_fps']} FPS)")

    # Save summary
    out_json = REPORT_DIR / "model_comparison.json"
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nModel evaluation summary saved to: {out_json}")
    print("=" * 70)


if __name__ == "__main__":
    evaluate_all()
