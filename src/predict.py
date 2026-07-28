"""User-facing prediction helpers for locked calibrated models."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

from .model import MultiOutputMLP


class CalibratedPredictor:
    """Apply a locked calibrated MLP to AF3/AFM summary features."""

    FEATURES = [
        "iface_pae_mean",
        "interchain_block_mean",
        "iptm",
        "ranking_score",
        "ptm",
    ]

    def __init__(self, model: MultiOutputMLP, scaler):
        self.model = model
        self.scaler = scaler
        self.model.eval()

    @classmethod
    def load(cls, model_dir: str | Path, domain: str = "abag") -> "CalibratedPredictor":
        model_dir = Path(model_dir)
        model = MultiOutputMLP(5)
        # These checkpoints are shipped with this repository and use the older
        # pickle-based layout, so explicit weights_only=False keeps loading
        # stable across PyTorch >=2.6.
        state = torch.load(
            model_dir / f"locked_ce_5feat_{domain}.pt",
            map_location="cpu",
            weights_only=False,
        )
        if isinstance(state, dict) and "model_state_dict" in state:
            model.load_state_dict(state["model_state_dict"])
        elif isinstance(state, dict) and "state_dict" in state:
            model.load_state_dict(state["state_dict"])
        else:
            model.load_state_dict(state)
        scaler = joblib.load(model_dir / f"scaler_5feat_{domain}.pkl")
        return cls(model, scaler)

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "ranking_score" not in df.columns:
            df["ranking_score"] = 0.8 * df["iptm"] + 0.2 * df["ptm"]
        X = self.scaler.transform(df[self.FEATURES].to_numpy(dtype=np.float32))
        with torch.no_grad():
            logits = self.model(torch.tensor(X, dtype=torch.float32))
            probs = F.softmax(logits, dim=-1).numpy()
        return pd.DataFrame(
            {
                "p_acceptable": probs[:, 1] + probs[:, 2] + probs[:, 3],
                "p_medium": probs[:, 2] + probs[:, 3],
                "p_high": probs[:, 3],
            },
            index=df.index,
        )

    def predict_with_sample_size(self, df: pd.DataFrame, confidence: float = 0.95) -> pd.DataFrame:
        out = self.predict(df)
        for prob_col, n_col in [
            ("p_acceptable", "n_seeds_acceptable"),
            ("p_medium", "n_seeds_medium"),
            ("p_high", "n_seeds_high"),
        ]:
            p = out[prob_col].to_numpy(dtype=float)
            with np.errstate(divide="ignore", invalid="ignore"):
                n = np.ceil(np.log(1.0 - confidence) / np.log(1.0 - p))
            n[p <= 0.0] = np.inf
            n[p >= 1.0] = 1.0
            out[n_col] = n
        return out
