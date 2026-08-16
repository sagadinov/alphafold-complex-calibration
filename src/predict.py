"""User-facing prediction helpers for the locked calibrated release models."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

from .model import MultiOutputMLP


class CalibratedPredictor:
    """Apply a locked calibrated MLP to precomputed complex-level summary features."""

    FEATURES = [
        "iface_pae_mean",
        "interchain_block_mean",
        "iptm",
        "ranking_score",
        "ptm",
    ]
    VALID_DOMAINS = {"abag", "general"}

    def __init__(self, model: MultiOutputMLP, scaler):
        self.model = model
        self.scaler = scaler
        self.model.eval()

    @classmethod
    def load(cls, model_dir: str | Path, domain: str = "abag") -> "CalibratedPredictor":
        if domain not in cls.VALID_DOMAINS:
            raise ValueError(f"invalid domain '{domain}'; expected one of {sorted(cls.VALID_DOMAINS)}")
        model_dir = Path(model_dir)
        model = MultiOutputMLP(5)
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

    @classmethod
    def _prepare_features(cls, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        required = ["iface_pae_mean", "interchain_block_mean", "iptm", "ptm"]
        missing = [col for col in required if col not in out.columns]
        if missing:
            raise ValueError(f"missing required input columns: expected {required}")
        if "ranking_score" not in out.columns:
            out["ranking_score"] = 0.8 * pd.to_numeric(out["iptm"], errors="coerce") + 0.2 * pd.to_numeric(
                out["ptm"], errors="coerce"
            )
        feature_frame = out[cls.FEATURES].apply(pd.to_numeric, errors="coerce")
        bad = feature_frame.isna().sum()
        bad = bad[bad > 0]
        if not bad.empty:
            details = ", ".join(f"{col}={int(count)}" for col, count in bad.items())
            raise ValueError(f"non-finite values in required features: {details}")
        out.loc[:, cls.FEATURES] = feature_frame
        return out

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._prepare_features(df)
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
