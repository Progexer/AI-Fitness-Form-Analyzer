"""
AI-Powered Fitness Coach — Bi-LSTM Temporal Sequence Classifier Architecture
"""

from typing import Dict, List, Any, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F


class BiLSTMExerciseClassifier(nn.Module):
    """
    Bidirectional LSTM with self-attention / temporal pooling for exercise recognition.
    Input shape: (batch_size, seq_len, input_size) where input_size=99 (33 landmarks * 3 coords).
    """

    def __init__(
        self,
        input_size: int = 99,
        hidden_size: int = 64,
        num_layers: int = 2,
        num_classes: int = 4,
        dropout: float = 0.3
    ):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_classes = num_classes

        # Bidirectional LSTM
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0
        )

        lstm_out_dim = hidden_size * 2  # Bidirectional

        # Attention layer for temporal weighting
        self.attention = nn.Sequential(
            nn.Linear(lstm_out_dim, 32),
            nn.Tanh(),
            nn.Linear(32, 1)
        )

        # Classification Head
        self.classifier = nn.Sequential(
            nn.Linear(lstm_out_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, D)
        lstm_out, _ = self.lstm(x)  # (B, T, hidden*2)

        # Compute attention weights over time
        attn_scores = self.attention(lstm_out)  # (B, T, 1)
        attn_weights = F.softmax(attn_scores, dim=1)  # (B, T, 1)

        # Context vector via weighted average
        context = torch.sum(lstm_out * attn_weights, dim=1)  # (B, hidden*2)

        # Class logits
        logits = self.classifier(context)  # (B, num_classes)
        return logits
