#!/usr/bin/env python3
"""Add a valid finite-DockQ MLP row to the AFDB workshop table.

The 304-row universe is defined before thresholding by finite ``dockq_native``.
The frozen General-trained MLP is evaluated on the 303 of these rows with all
five required inputs. Existing workshop baseline rows are preserved verbatim.
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["iface_pae_mean", "interchain_block_mean", "iptm", "ranking_score", "ptm"]
THRESHOLDS = [("acceptable", 0.23), ("medium", 0.49), ("high", 0.80)]
METHOD_ORDER = ["Raw ipTM", "Raw ranking conf.", "pDockQ2max (published)", "ipSAEmax", "Iso. ipTM", "MLP 5-feat CE"]


class MultiOutputMLP(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(5, 64), torch.nn.ReLU(), torch.nn.Dropout(0.1),
            torch.nn.Linear(64, 32), torch.nn.ReLU(), torch.nn.Dropout(0.1),
            torch.nn.Linear(32, 4),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def ece(y_true: np.ndarray, probabilities: np.ndarray, n_bins: int = 10) -> float:
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    result = 0.0
    for index in range(n_bins):
        if index < n_bins - 1:
            mask = (probabilities >= edges[index]) & (probabilities < edges[index + 1])
        else:
            mask = (probabilities >= edges[index]) & (probabilities <= edges[index + 1])
        if mask.any():
            result += mask.mean() * abs(probabilities[mask].mean() - y_true[mask].mean())
    return float(result)


def metrics(y_true: np.ndarray, probabilities: np.ndarray) -> dict[str, float | int]:
    valid = np.isfinite(probabilities)
    yt = y_true[valid].astype(int)
    yp = np.clip(probabilities[valid].astype(float), 0.0, 1.0)
    prediction = (yp >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(yt, prediction, labels=[0, 1]).ravel()
    precision, recall, cutoffs = precision_recall_curve(yt, yp)
    best = None
    for observed_precision, observed_recall, cutoff in zip(precision[:-1], recall[:-1], cutoffs):
        selected = yp >= cutoff
        if selected.any() and observed_precision >= 0.90:
            if best is None or observed_recall > best["recall"]:
                best = {
                    "selected": int(selected.sum()),
                    "precision": float(observed_precision),
                    "recall": float(observed_recall),
                }
    return {
        "n_valid": int(valid.sum()),
        "n_pos": int(yt.sum()),
        "n_neg": int((1 - yt).sum()),
        "brier": float(brier_score_loss(yt, yp)),
        "ece": ece(yt, yp),
        "auroc": float(roc_auc_score(yt, yp)),
        "auprc": float(average_precision_score(yt, yp)),
        "mcc": float(matthews_corrcoef(yt, prediction)),
        "ppv": float(precision_score(yt, prediction, zero_division=0)),
        "recall": float(recall_score(yt, prediction, zero_division=0)),
        "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
        "matched_90_selected": np.nan if best is None else best["selected"],
        "matched_90_precision": np.nan if best is None else best["precision"],
        "matched_90_recall": np.nan if best is None else best["recall"],
    }


def predict_mlp(df: pd.DataFrame) -> dict[str, np.ndarray]:
    valid = df[FEATURES].notna().all(axis=1).to_numpy()
    model = MultiOutputMLP()
    state = torch.load(ROOT / "models" / "locked_ce_5feat_general.pt", map_location="cpu", weights_only=False)
    model.load_state_dict(state.get("model_state_dict", state.get("state_dict", state)) if isinstance(state, dict) else state)
    model.eval()
    scaler = joblib.load(ROOT / "models" / "scaler_5feat_general.pkl")
    scores = {name: np.full(len(df), np.nan, dtype=float) for name, _ in THRESHOLDS}
    with torch.no_grad():
        features = scaler.transform(df.loc[valid, FEATURES].to_numpy(dtype=float))
        probs = F.softmax(model(torch.tensor(features, dtype=torch.float32)), dim=-1).numpy()
    scores["acceptable"][valid] = probs[:, 1:].sum(axis=1)
    scores["medium"][valid] = probs[:, 2:].sum(axis=1)
    scores["high"][valid] = probs[:, 3]
    return scores


def fmt(value: float, digits: int) -> str:
    text = f"{float(value):.{digits}f}"
    return text[1:] if text.startswith("0") else text


def write_latex(table: pd.DataFrame) -> None:
    lines = [
        r"\begin{table}[t]",
        r"\caption{AFDB structural validation on the 304 positive complexes with finite DockQ. General-trained isotonic calibrators and the frozen General-trained MLP are applied without AFDB fitting. The MLP has all five required features for 303 of 304 complexes; all other rows use 304. ipSAEmax and pDockQ2max are the published AFDB directional-max scores.}",
        r"\label{tab:workshop_afdb_with_mlp}",
        r"\centering",
        r"\resizebox{\columnwidth}{!}{%",
        r"\begin{tabular}{lcccccc}",
        r"\toprule",
        r"Method & AUROC & AUPRC & Brier$\downarrow$ & ECE$\downarrow$ & $n_{90}$ & Recall$_{90}$ \\",
        r"\midrule",
    ]
    for method in METHOD_ORDER:
        row = table[(table["threshold"] == "acceptable") & (table["method"] == method)]
        if row.empty:
            continue
        row = row.iloc[0]
        n90 = "---" if pd.isna(row["matched_90_selected"]) else str(int(row["matched_90_selected"]))
        lines.append(
            f"{method} & {fmt(row['auroc'], 3)} & {fmt(row['auprc'], 3)} & {fmt(row['brier'], 4)} & "
            f"{fmt(row['ece'], 4)} & {n90} & {fmt(row['matched_90_recall'], 3)} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}", r"}%", r"\end{table}", ""]
    (ROOT / "paper" / "tables" / "tab_workshop_afdb_with_mlp.tex").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    features = pd.read_csv(ROOT / "analysis" / "afdb" / "afdb_positive_dockq_features.csv", low_memory=False)
    features["dockq_native"] = pd.to_numeric(features["dockq_native"], errors="coerce")
    finite = features.loc[np.isfinite(features["dockq_native"])].copy()
    if len(finite) != 304:
        raise RuntimeError(f"Expected 304 finite-DockQ rows, got {len(finite)}")
    mlp = predict_mlp(finite)
    baseline = pd.read_csv(ROOT / "analysis" / "workshop" / "workshop_afdb_304_metrics.csv")
    baseline = baseline[baseline["method"].isin(METHOD_ORDER[:-1])].copy()
    rows = [baseline]
    for name, value in THRESHOLDS:
        y_true = (finite["dockq_native"].to_numpy(dtype=float) >= value).astype(int)
        rows.append(pd.DataFrame([{"threshold": name, "threshold_val": value, "method": "MLP 5-feat CE", **metrics(y_true, mlp[name])}]))
    table = pd.concat(rows, ignore_index=True)
    table["method"] = pd.Categorical(table["method"], METHOD_ORDER, ordered=True)
    table = table.sort_values(["threshold_val", "method"], kind="mergesort").reset_index(drop=True)
    out = ROOT / "analysis" / "workshop" / "workshop_afdb_304_with_mlp_metrics.csv"
    table.to_csv(out, index=False)
    write_latex(table)
    print(table[table["method"] == "MLP 5-feat CE"].to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
