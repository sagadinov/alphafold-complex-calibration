#!/usr/bin/env python3
"""Shared utilities for the final decision-use experiments.

This module intentionally centralizes:
- canonical data loading and provenance;
- deterministic General fold reconstruction;
- locked General MLP loading for transfer evaluation;
- target-level bootstrap helpers;
- probability audits and validation.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import math
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import joblib
import matplotlib
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from scipy.stats import pearsonr, spearmanr
from sklearn.isotonic import IsotonicRegression
from sklearn.model_selection import GroupKFold

matplotlib.use("Agg")


THRESHOLDS = {
    "acceptable": 0.23,
    "medium": 0.49,
    "high": 0.80,
}
PRIMARY_THRESHOLD = "acceptable"
Q_LEVELS = [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95]
K_LEVELS = [5, 10, 20, 50]
SEED = 42
N_BOOT = 2000
FEATURES = ["iface_pae_mean", "interchain_block_mean", "iptm", "ranking_score", "ptm"]


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    source_csv: Path
    dockq_col: str
    target_col: str
    model_col: str
    raw_score_col: str
    iso_col_map: dict[str, str]
    mlp_col_map: dict[str, str]
    training_regime: str
    fold_protocol: str


class MultiOutputMLP(torch.nn.Module):
    def __init__(self, in_dim: int = 5):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(in_dim, 64),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.1),
            torch.nn.Linear(64, 32),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.1),
            torch.nn.Linear(32, 4),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def project_paths(project_root: Path) -> dict[str, Path]:
    paper = project_root / "af3_atlas" / "PAPER_REVISION"
    return {
        "root": project_root,
        "paper": paper,
        "analysis": paper / "analysis",
        "data": paper / "data",
        "casp16": paper / "casp16",
        "models": project_root / "models",
    }


def canonical_specs(project_root: Path) -> dict[str, DatasetSpec]:
    paths = project_paths(project_root)
    return {
        "abag": DatasetSpec(
            name="Ab-Ag",
            source_csv=paths["data"] / "abag_predictions_v3.csv",
            dockq_col="dockq",
            target_col="target_id",
            model_col="model_id",
            raw_score_col="p_raw_iptm",
            iso_col_map={k: f"p_iso_iptm_{k}" for k in THRESHOLDS},
            mlp_col_map={k: f"p_mlp_ce_{k}" for k in THRESHOLDS},
            training_regime="Ab-Ag train -> Ab-Ag test",
            fold_protocol="held-out test",
        ),
        "general": DatasetSpec(
            name="General",
            source_csv=paths["data"] / "general_predictions_v3.csv",
            dockq_col="dockq",
            target_col="target_id",
            model_col="model_id",
            raw_score_col="p_raw_iptm",
            iso_col_map={k: f"p_iso_iptm_{k}" for k in THRESHOLDS},
            mlp_col_map={k: f"p_mlp_ce_{k}" for k in THRESHOLDS},
            training_regime="General grouped 5-fold OOF",
            fold_protocol="deterministic GroupKFold(5) reconstruction by target_id",
        ),
        "casp16": DatasetSpec(
            name="CASP16",
            source_csv=paths["data"] / "casp16_predictions_v3.csv",
            dockq_col="dockq",
            target_col="target_id",
            model_col="model_id",
            raw_score_col="p_raw_iptm",
            iso_col_map={k: f"p_iso_iptm_{k}" for k in THRESHOLDS},
            mlp_col_map={k: f"p_mlp_ce_{k}" for k in THRESHOLDS},
            training_regime="General full training -> frozen external",
            fold_protocol="external frozen evaluation",
        ),
    }


def collect_package_versions() -> dict[str, str]:
    pkgs = ["numpy", "pandas", "scipy", "sklearn", "matplotlib", "torch", "joblib"]
    out = {
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
    }
    for pkg in pkgs:
        try:
            out[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            out[pkg] = "missing"
    return out


def load_prediction_table(spec: DatasetSpec) -> pd.DataFrame:
    df = pd.read_csv(spec.source_csv, low_memory=False)
    needed = [
        spec.target_col,
        spec.model_col,
        spec.dockq_col,
        spec.raw_score_col,
        *spec.iso_col_map.values(),
        *spec.mlp_col_map.values(),
    ]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"{spec.source_csv}: missing required columns {missing}")
    for col in needed:
        if col not in (spec.target_col, spec.model_col):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    dup_mask = df.duplicated([spec.target_col, spec.model_col], keep=False)
    if dup_mask.any():
        raise ValueError(
            f"{spec.source_csv}: duplicated target/model identifiers:\n"
            f"{df.loc[dup_mask, [spec.target_col, spec.model_col]].head(10).to_string(index=False)}"
        )
    return df


def load_abag_transfer_features(project_root: Path) -> pd.DataFrame:
    path = project_paths(project_root)["data"] / "abag_test_v2.csv"
    df = pd.read_csv(path, low_memory=False)
    cols = ["target_id", "model_id", "dockq", *FEATURES]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{path}: missing required transfer columns {missing}")
    for col in cols:
        if col not in ("target_id", "model_id"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    dup_mask = df.duplicated(["target_id", "model_id"], keep=False)
    if dup_mask.any():
        raise ValueError(
            f"{path}: duplicated target/model identifiers:\n"
            f"{df.loc[dup_mask, ['target_id', 'model_id']].head(10).to_string(index=False)}"
        )
    return df[cols].copy()


def load_general_training_features(project_root: Path) -> pd.DataFrame:
    path = project_paths(project_root)["data"] / "general_v2.csv"
    df = pd.read_csv(path, low_memory=False)
    cols = ["target_id", "model_id", "dockq", *FEATURES]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{path}: missing required General feature columns {missing}")
    for col in cols:
        if col not in ("target_id", "model_id"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[cols].copy()


def reconstruct_general_folds(general_pred_df: pd.DataFrame) -> np.ndarray:
    """Reconstruct the canonical 5-fold target-grouped split used in build_final_v2_release.py.

    The build script created General OOF predictions by iterating over the canonical row order of
    `general_v2.csv` / `general_predictions_v3.csv` with `GroupKFold(n_splits=5)` and `groups=target_id`.
    There is no row-level shuffle, so this fold structure is deterministic and exactly reproducible
    from the canonical prediction table itself.
    """

    groups = general_pred_df["target_id"].to_numpy()
    X_dummy = np.arange(len(general_pred_df)).reshape(-1, 1)
    gkf = GroupKFold(n_splits=5)
    fold_ids = np.full(len(general_pred_df), -1, dtype=int)
    for fold_idx, (_, test_idx) in enumerate(gkf.split(X_dummy, groups=groups), start=1):
        fold_ids[test_idx] = fold_idx
    if (fold_ids < 0).any():
        raise RuntimeError("Failed to assign all General rows to a deterministic fold.")
    per_target = pd.DataFrame({"target_id": groups, "fold_id": fold_ids}).groupby("target_id")["fold_id"].nunique()
    if int(per_target.max()) != 1:
        raise RuntimeError("Reconstructed General folds split at least one target across folds.")
    return fold_ids


def load_general_mlp_bundle(project_root: Path) -> tuple[MultiOutputMLP, object]:
    paths = project_paths(project_root)
    model = MultiOutputMLP(5)
    state = torch.load(paths["models"] / "locked_ce_5feat_general.pt", map_location="cpu", weights_only=False)
    if isinstance(state, dict) and "model_state_dict" in state:
        model.load_state_dict(state["model_state_dict"])
    elif isinstance(state, dict) and "state_dict" in state:
        model.load_state_dict(state["state_dict"])
    else:
        model.load_state_dict(state)
    model.eval()
    scaler = joblib.load(paths["models"] / "scaler_5feat_general.pkl")
    return model, scaler


def predict_general_mlp(df: pd.DataFrame, model: MultiOutputMLP, scaler) -> dict[str, np.ndarray]:
    X = scaler.transform(df[FEATURES].to_numpy(dtype=float))
    with torch.no_grad():
        logits = model(torch.tensor(X, dtype=torch.float32))
        probs = F.softmax(logits, dim=-1).numpy()
    return {
        "acceptable": probs[:, 1] + probs[:, 2] + probs[:, 3],
        "medium": probs[:, 2] + probs[:, 3],
        "high": probs[:, 3],
    }


def fit_general_isotonic_models(general_train_df: pd.DataFrame) -> dict[str, IsotonicRegression]:
    out: dict[str, IsotonicRegression] = {}
    x = general_train_df["iptm"].to_numpy(dtype=float)
    for thr_name, thr_val in THRESHOLDS.items():
        y = (general_train_df["dockq"].to_numpy(dtype=float) >= thr_val).astype(int)
        iso = IsotonicRegression(out_of_bounds="clip")
        iso.fit(x, y)
        out[thr_name] = iso
    return out


def audit_probability_column(values: np.ndarray, source_label: str, col_label: str) -> dict[str, object]:
    arr = np.asarray(values, dtype=float)
    finite_mask = np.isfinite(arr)
    below = int((arr[finite_mask] < 0.0).sum())
    above = int((arr[finite_mask] > 1.0).sum())
    n_nan = int((~finite_mask).sum())
    clipped = below + above
    return {
        "source": source_label,
        "column": col_label,
        "n_rows": int(len(arr)),
        "n_finite": int(finite_mask.sum()),
        "n_nan": n_nan,
        "n_below_zero": below,
        "n_above_one": above,
        "n_would_clip": clipped,
    }


def require_probability_ok(values: np.ndarray, source_label: str, col_label: str) -> dict[str, object]:
    audit = audit_probability_column(values, source_label, col_label)
    if audit["n_nan"] or audit["n_would_clip"]:
        raise ValueError(
            f"Probability audit failed for {source_label}/{col_label}: "
            f"{audit['n_nan']} NaN, {audit['n_would_clip']} out-of-range values."
        )
    return audit


def raw_probability_ok(values: np.ndarray, source_label: str, col_label: str) -> dict[str, object]:
    audit = audit_probability_column(values, source_label, col_label)
    if audit["n_nan"]:
        raise ValueError(f"Raw probability audit failed for {source_label}/{col_label}: {audit['n_nan']} NaN values.")
    if audit["n_would_clip"]:
        raise ValueError(
            f"Raw probability audit failed for {source_label}/{col_label}: "
            f"{audit['n_would_clip']} out-of-range values."
        )
    return audit


def monotonicity_audit(raw_scores: np.ndarray, iso_scores: np.ndarray) -> dict[str, object]:
    raw = np.asarray(raw_scores, dtype=float)
    iso = np.asarray(iso_scores, dtype=float)
    spearman = float(spearmanr(raw, iso).correlation)
    order = np.argsort(raw, kind="mergesort")
    raw_sorted = raw[order]
    iso_sorted = iso[order]
    violations = int(np.sum(np.diff(iso_sorted) < -1e-12))
    return {
        "spearman_raw_vs_iso": spearman,
        "adjacent_ordering_violations": violations,
        "n_rows": int(len(raw)),
    }


def target_bootstrap_indices(target_ids: Iterable[str], n_boot: int = N_BOOT, seed: int = SEED) -> tuple[np.ndarray, list[str]]:
    uniq = list(pd.Index(target_ids).drop_duplicates())
    rng = np.random.default_rng(seed)
    boot = rng.integers(0, len(uniq), size=(n_boot, len(uniq)), endpoint=False)
    return boot, uniq


def flatten_target_draw(per_target: pd.DataFrame, target_col: str, sampled_targets: list[str]) -> pd.DataFrame:
    parts = [per_target.loc[per_target[target_col] == t] for t in sampled_targets]
    return pd.concat(parts, ignore_index=True)


def safe_pearson(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 2 or np.allclose(x, x[0]) or np.allclose(y, y[0]):
        return float("nan")
    return float(pearsonr(x, y)[0])


def safe_spearman(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 2 or np.allclose(x, x[0]) or np.allclose(y, y[0]):
        return float("nan")
    return float(spearmanr(x, y).correlation)


def fmt_ci(samples: np.ndarray) -> tuple[float, float]:
    arr = np.asarray(samples, dtype=float)
    return float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975))


def yaml_dump(obj, indent: int = 0) -> str:
    space = "  " * indent
    if isinstance(obj, dict):
        lines = []
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{space}{k}:")
                lines.append(yaml_dump(v, indent + 1))
            else:
                lines.append(f"{space}{k}: {yaml_scalar(v)}")
        return "\n".join(lines)
    if isinstance(obj, list):
        lines = []
        for item in obj:
            if isinstance(item, (dict, list)):
                lines.append(f"{space}-")
                lines.append(yaml_dump(item, indent + 1))
            else:
                lines.append(f"{space}- {yaml_scalar(item)}")
        return "\n".join(lines)
    return f"{space}{yaml_scalar(obj)}"


def yaml_scalar(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "null"
    if isinstance(v, float):
        if math.isnan(v):
            return "nan"
        if math.isinf(v):
            return "inf" if v > 0 else "-inf"
        return repr(float(v))
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    text = str(v)
    if any(ch in text for ch in [":", "#", "{", "}", "[", "]", ","]) or text.strip() != text or "\n" in text:
        return json_quote(text)
    return text


def json_quote(text: str) -> str:
    import json

    return json.dumps(text)

