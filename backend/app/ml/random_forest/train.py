"""
AI-Powered Fitness Coach — Random Forest Exercise Classifier Training

Trains a Random Forest classifier to identify exercise class from biomechanical
and kinematic pose features.
"""

import os
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models" / "random_forest"
REPORT_DIR = PROJECT_ROOT / "reports" / "model_evaluation"

FEATURE_COLS_EXCLUDE = {"video_id", "exercise", "split", "timestamp", "form_label"}


def train_random_forest():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    train_path = PROCESSED_DIR / "train_features.csv"
    val_path = PROCESSED_DIR / "val_features.csv"

    if not train_path.exists():
        print(f"Error: {train_path} not found. Run compile_features.py first.")
        return

    print("=" * 70)
    print("Training Random Forest Exercise Classifier...")
    print("=" * 70)

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path) if val_path.exists() else None

    feature_cols = [c for c in train_df.columns if c not in FEATURE_COLS_EXCLUDE]
    print(f"Number of feature dimensions: {len(feature_cols)}")
    print(f"Training samples: {len(train_df)}")

    X_train = train_df[feature_cols].values
    y_train_raw = train_df["exercise"].values

    le = LabelEncoder()
    y_train = le.fit_transform(y_train_raw)

    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=20,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    clf.fit(X_train, y_train)
    print("Training completed.")

    # Validation evaluation
    val_metrics = {}
    if val_df is not None and len(val_df) > 0:
        X_val = val_df[feature_cols].values
        y_val_raw = val_df["exercise"].values
        y_val = le.transform(y_val_raw)

        y_pred = clf.predict(X_val)
        acc = accuracy_score(y_val, y_pred)
        f1_macro = f1_score(y_val, y_pred, average="macro")
        f1_weighted = f1_score(y_val, y_pred, average="weighted")
        cls_rep = classification_report(y_val, y_pred, target_names=le.classes_, output_dict=True)
        cm = confusion_matrix(y_val, y_pred).tolist()

        print(f"\nValidation Accuracy: {acc:.4f}")
        print(f"Validation Macro F1: {f1_macro:.4f}")
        print("\nPer-class Classification Report:")
        for cls_name in le.classes_:
            p = cls_rep[cls_name]["precision"]
            r = cls_rep[cls_name]["recall"]
            f = cls_rep[cls_name]["f1-score"]
            print(f"  - {cls_name:16s}: Prec={p:.3f}, Rec={r:.3f}, F1={f:.3f}")

        val_metrics = {
            "model_type": "RandomForestClassifier",
            "accuracy": float(round(acc, 4)),
            "macro_f1": float(round(f1_macro, 4)),
            "weighted_f1": float(round(f1_weighted, 4)),
            "classes": list(le.classes_),
            "confusion_matrix": cm,
            "classification_report": cls_rep,
            "feature_importances": {
                feat: float(round(imp, 5))
                for feat, imp in sorted(zip(feature_cols, clf.feature_importances_), key=lambda x: x[1], reverse=True)[:20]
            }
        }

    # Save models
    model_file = MODEL_DIR / "rf_exercise_classifier.joblib"
    encoder_file = MODEL_DIR / "label_encoder.joblib"
    cols_file = MODEL_DIR / "feature_columns.json"

    joblib.dump(clf, model_file)
    joblib.dump(le, encoder_file)
    with open(cols_file, "w") as f:
        json.dump(feature_cols, f)

    if val_metrics:
        with open(REPORT_DIR / "random_forest_metrics.json", "w") as f:
            json.dump(val_metrics, f, indent=2)

    print(f"\nModel artifacts successfully saved to: {MODEL_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    train_random_forest()
