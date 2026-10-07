"""
AI-Powered Fitness Coach — PyTorch LSTM Classifier Training Pipeline
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.lstm.dataset import ExerciseSequenceDataset
from app.ml.lstm.model import BiLSTMExerciseClassifier

POSES_DIR = PROJECT_ROOT / "data" / "interim" / "poses"
MODEL_DIR = PROJECT_ROOT / "models" / "lstm"
REPORT_DIR = PROJECT_ROOT / "reports" / "model_evaluation"


def train_lstm(epochs: int = 25, batch_size: int = 32, lr: float = 1e-3):
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device for LSTM training: {device}")

    # Gather split files
    train_files = list(POSES_DIR.glob("*_train.npz"))
    val_files = list(POSES_DIR.glob("*_val.npz"))

    if not train_files:
        print("No training npz files found. Poses are still being extracted or path is empty.")
        return

    print(f"Loading datasets: {len(train_files)} train videos, {len(val_files)} val videos...")

    class_to_idx = {
        "bicep_curl": 0,
        "push_up": 1,
        "shoulder_press": 2,
        "squat": 3
    }
    idx_to_class = {v: k for k, v in class_to_idx.items()}

    train_ds = ExerciseSequenceDataset(train_files, window_size=30, stride=10, class_to_idx=class_to_idx)
    val_ds = ExerciseSequenceDataset(val_files, window_size=30, stride=15, class_to_idx=class_to_idx) if val_files else None

    print(f"Created {len(train_ds)} train sequence windows.")
    if val_ds:
        print(f"Created {len(val_ds)} validation sequence windows.")

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, drop_last=len(train_ds) > batch_size)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False) if val_ds and len(val_ds) > 0 else None

    model = BiLSTMExerciseClassifier(
        input_size=99,
        hidden_size=64,
        num_layers=2,
        num_classes=4,
        dropout=0.3
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=3)

    best_val_f1 = 0.0
    history = []

    print("\nStarting LSTM Training...")
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        correct = 0
        total = 0

        for x_b, y_b in train_loader:
            x_b, y_b = x_b.to(device), y_b.to(device)
            optimizer.zero_grad()
            logits = model(x_b)
            loss = criterion(logits, y_b)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            train_loss += loss.item() * len(y_b)
            preds = torch.argmax(logits, dim=1)
            correct += (preds == y_b).sum().item()
            total += len(y_b)

        epoch_train_loss = train_loss / max(1, total)
        epoch_train_acc = correct / max(1, total)

        # Validation
        val_acc, val_f1, val_loss = 0.0, 0.0, 0.0
        if val_loader:
            model.eval()
            val_preds, val_targets = [], []
            with torch.no_grad():
                for x_v, y_v in val_loader:
                    x_v, y_v = x_v.to(device), y_v.to(device)
                    v_logits = model(x_v)
                    v_loss = criterion(v_logits, y_v)
                    val_loss += v_loss.item() * len(y_v)
                    val_preds.extend(torch.argmax(v_logits, dim=1).cpu().numpy())
                    val_targets.extend(y_v.cpu().numpy())

            val_loss = val_loss / len(val_targets)
            val_acc = accuracy_score(val_targets, val_preds)
            val_f1 = f1_score(val_targets, val_preds, average="macro", zero_division=0)
            scheduler.step(val_f1)

            if val_f1 > best_val_f1:
                best_val_f1 = val_f1
                # Save best checkpoint
                torch.save(model.state_dict(), MODEL_DIR / "bilstm_best.pth")

        print(f"Epoch {epoch:02d}/{epochs} | Train Loss: {epoch_train_loss:.4f} Acc: {epoch_train_acc:.3f} | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc:.3f} F1: {val_f1:.3f}")

        history.append({
            "epoch": epoch,
            "train_loss": round(epoch_train_loss, 4),
            "train_acc": round(epoch_train_acc, 4),
            "val_loss": round(val_loss, 4),
            "val_acc": round(val_acc, 4),
            "val_f1": round(val_f1, 4),
        })

    # Save final model and config
    torch.save(model.state_dict(), MODEL_DIR / "bilstm_final.pth")
    cfg = {
        "input_size": 99,
        "hidden_size": 64,
        "num_layers": 2,
        "num_classes": 4,
        "class_to_idx": class_to_idx,
        "idx_to_class": idx_to_class,
        "best_val_f1": round(best_val_f1, 4),
        "history": history
    }
    with open(MODEL_DIR / "lstm_config.json", "w") as f:
        json.dump(cfg, f, indent=2)

    with open(REPORT_DIR / "lstm_metrics.json", "w") as f:
        json.dump({"model": "BiLSTM", "best_val_f1": best_val_f1, "history": history}, f, indent=2)

    print(f"\nLSTM training finished. Checkpoints saved to: {MODEL_DIR}")


if __name__ == "__main__":
    train_lstm()
