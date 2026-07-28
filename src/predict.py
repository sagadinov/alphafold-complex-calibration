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

    @classmethod
    def _prepare_features(cls, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        for col in ["iface_pae_mean", "interchain_block_mean", "iptm", "ptm"]:
            if col not in out.columns:
                raise ValueError(
                    f"missing required input columns: expected {['iface_pae_mean', 'interchain_block_mean', 'iptm', 'ptm']}"
                )
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

    def predict_with_sample_size(self, df: pd.DataFrame, confidence: float = 0.95) -> pd.DataFrame:
        """Return probabilities and an independence-based seed-count estimate.

        The estimate assumes repeated independent trials with a constant
        per-trial success probability equal to the calibrated probability.
        Real AlphaFold samples are not guaranteed to satisfy this assumption,
        so the output should be interpreted as a heuristic planning estimate,
        not as a guaranteed number of seeds.
        """
        if not np.isfinite(confidence) or not (0.0 < confidence < 1.0):
            raise ValueError("confidence must be finite and strictly between 0 and 1")
        out = self.predict(df)
        for prob_col, n_col in [
            ("p_acceptable", "n_seeds_acceptable"),
            ("p_medium", "n_seeds_medium"),
            ("p_high", "n_seeds_high"),
        ]:
            p = out[prob_col].to_numpy(dtype=float)
            n = np.full_like(p, np.nan, dtype=float)
            mask = np.isfinite(p)
            safe = p[mask]
            zero = safe <= 0.0
            one = safe >= 1.0
            mid = (~zero) & (~one)
            n_masked = np.empty_like(safe, dtype=float)
            n_masked[zero] = np.inf
            n_masked[one] = 1.0
            with np.errstate(divide="ignore", invalid="ignore"):
                n_masked[mid] = np.ceil(np.log1p(-confidence) / np.log1p(-safe[mid]))
            n[mask] = n_masked
            out[n_col] = n
        return out
