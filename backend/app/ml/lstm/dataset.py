"""
AI-Powered Fitness Coach — PyTorch LSTM Sequence Dataset

Extracts fixed-length sliding temporal windows (e.g., 30 frames) from video pose sequences.
"""

from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import Dataset


class ExerciseSequenceDataset(Dataset):
    """
    Creates temporal sequence windows (T, D) from pose/feature files.
    """

    def __init__(
        self,
        npz_files: List[Path],
        window_size: int = 30,
        stride: int = 10,
        class_to_idx: Optional[Dict[str, int]] = None
    ):
        self.window_size = window_size
        self.stride = stride
        self.samples: List[np.ndarray] = []
        self.labels: List[int] = []

        # Standard class mapping
        if class_to_idx is None:
            self.class_to_idx = {
                "bicep_curl": 0,
                "push_up": 1,
                "shoulder_press": 2,
                "squat": 3
            }
        else:
            self.class_to_idx = class_to_idx

        self._build_dataset(npz_files)

    def _build_dataset(self, npz_files: List[Path]):
        for file_path in npz_files:
            try:
                data = np.load(file_path, allow_pickle=True)
                landmarks = data["landmarks"]  # (T, 33, 4)
                exercise = str(data["exercise"])

                if exercise not in self.class_to_idx:
                    continue

                label = self.class_to_idx[exercise]
                t_len = landmarks.shape[0]

                # Flatten landmarks x,y,z: (T, 99)
                flat_coords = landmarks[:, :, :3].reshape(t_len, -1)

                if t_len < self.window_size:
                    # Pad short sequences
                    pad_len = self.window_size - t_len
                    pad = np.repeat(flat_coords[-1:], pad_len, axis=0)
                    window = np.vstack([flat_coords, pad])
                    self.samples.append(window.astype(np.float32))
                    self.labels.append(label)
                else:
                    for start in range(0, t_len - self.window_size + 1, self.stride):
                        window = flat_coords[start : start + self.window_size]
                        self.samples.append(window.astype(np.float32))
                        self.labels.append(label)

            except Exception as e:
                pass

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        x = torch.from_numpy(self.samples[idx])  # (window_size, 99)
        y = torch.tensor(self.labels[idx], dtype=torch.long)
        return x, y
