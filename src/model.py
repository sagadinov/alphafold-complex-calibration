"""Locked MLP architecture used in the paper release."""

from __future__ import annotations

import torch
import torch.nn as nn


class MultiOutputMLP(nn.Module):
    """4-class cumulative softmax MLP for DockQ quality prediction."""

    def __init__(self, in_dim: int = 5):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 4),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

