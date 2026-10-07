"""
AI-Powered Fitness Coach — XGBoost Form & Error Classifier Training

Trains an XGBoost model on biomechanical features to detect movement faults
(e.g., knee_valgus, shallow_depth, elbow_flare, sagging_hips, etc.).
"""

import os
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models" / "xgboost"
REPORT_DIR = PROJECT_ROOT / "reports" / "model_evaluation"

FEATURE_COLS_EXCLUDE = {"video_id", "exercise", "split", "timestamp", "form_label"}


def train_xgboost_form_classifier():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    train_path = PROCESSED_DIR / "train_features.csv"
    val_path = PROCESSED_DIR / "val_features.csv"

    if not train_path.exists():
        print(f"Error: {train_path} not found. Run compile_features.py first.")
        return

    print("=" * 70)
    print("Training XGBoost Form Fault Classifier...")
    print("=" * 70)

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path) if val_path.exists() else None

    # Filter samples that have a valid form label
    train_df = train_df[train_df["form_label"].notna() & (train_df["form_label"] != "unknown")]

    feature_cols = [c for c in train_df.columns if c not in FEATURE_COLS_EXCLUDE]
    print(f"Number of biomechanical features: {len(feature_cols)}")
    print(f"Form-labeled training samples: {len(train_df)}")

    X_train = train_df[feature_cols].values
    y_train_raw = train_df["form_label"].values

    le = LabelEncoder()
    y_train = le.fit_transform(y_train_raw)

    xgb = XGBClassifier(
        n_estimators=120,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1
    )

    xgb.fit(X_train, y_train)
    print("XGBoost training completed.")

    val_metrics = {}
    if val_df is not None and len(val_df) > 0:
        val_df = val_df[val_df["form_label"].notna() & (val_df["form_label"] != "unknown")]
        # Keep only classes seen in train
        val_df = val_df[val_df["form_label"].isin(le.classes_)]

        if len(val_df) > 0:
            X_val = val_df[feature_cols].values
            y_val_raw = val_df["form_label"].values
            y_val = le.transform(y_val_raw)

            y_pred = xgb.predict(X_val)
            acc = accuracy_score(y_val, y_pred)
            f1_macro = f1_score(y_val, y_pred, average="macro", zero_division=0)
            all_labels = list(range(len(le.classes_)))
            cls_rep = classification_report(y_val, y_pred, labels=all_labels, target_names=list(le.classes_), output_dict=True, zero_division=0)
            cm = confusion_matrix(y_val, y_pred, labels=all_labels).tolist()

            print(f"\nValidation Accuracy: {acc:.4f}")
            print(f"Validation Macro F1: {f1_macro:.4f}")

            val_metrics = {
                "model_type": "XGBClassifier",
                "accuracy": float(round(acc, 4)),
                "macro_f1": float(round(f1_macro, 4)),
                "classes": list(le.classes_),
                "confusion_matrix": cm,
                "classification_report": cls_rep,
            }

    # Save models
    model_file = MODEL_DIR / "xgb_form_classifier.joblib"
    encoder_file = MODEL_DIR / "form_label_encoder.joblib"
    cols_file = MODEL_DIR / "form_feature_columns.json"

    joblib.dump(xgb, model_file)
    joblib.dump(le, encoder_file)
    with open(cols_file, "w") as f:
        json.dump(feature_cols, f)

    if val_metrics:
        with open(REPORT_DIR / "xgboost_metrics.json", "w") as f:
            json.dump(val_metrics, f, indent=2)

    print(f"\nXGBoost artifacts successfully saved to: {MODEL_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    train_xgboost_form_classifier()
