"""Metrics and selection utilities used throughout the paper release."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)


def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.clip(np.asarray(y_prob, dtype=float), 0.0, 1.0)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        if i < n_bins - 1:
            mask = (y_prob >= edges[i]) & (y_prob < edges[i + 1])
        else:
            mask = (y_prob >= edges[i]) & (y_prob <= edges[i + 1])
        if mask.sum() == 0:
            continue
        ece += (mask.sum() / len(y_prob)) * abs(float(y_prob[mask].mean()) - float(y_true[mask].mean()))
    return float(ece)


def compute_all_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> dict[str, float | int]:
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.clip(np.asarray(y_prob, dtype=float), 0.0, 1.0)
    y_pred = (y_prob >= threshold).astype(int)
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    fp = int(((y_pred == 1) & (y_true == 0)).sum())
    tn = int(((y_pred == 0) & (y_true == 0)).sum())
    fn = int(((y_pred == 0) & (y_true == 1)).sum())
    return {
        "brier": float(brier_score_loss(y_true, y_prob)),
        "ece": compute_ece(y_true, y_prob),
        "auroc": float(roc_auc_score(y_true, y_prob)),
        "auprc": float(average_precision_score(y_true, y_prob)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "ppv": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def matched_precision_selection(
    y_true: np.ndarray,
    y_score: np.ndarray,
    target_precision: float = 0.90,
) -> dict[str, float | int] | None:
    y_true = np.asarray(y_true, dtype=int)
    y_score = np.asarray(y_score, dtype=float)
    thresholds = np.sort(np.unique(y_score))
    best = None
    for thr in thresholds:
        sel = y_score >= thr
        n_sel = int(sel.sum())
        if n_sel == 0:
            continue
        precision = float(y_true[sel].mean())
        if precision >= target_precision:
            recall = float(y_true[sel].sum() / y_true.sum()) if y_true.sum() else 0.0
            mcc = float(matthews_corrcoef(y_true, sel.astype(int)))
            candidate = {
                "threshold": float(thr),
                "n_selected": n_sel,
                "precision": precision,
                "recall": recall,
                "mcc": mcc,
            }
            if best is None or candidate["recall"] > best["recall"]:
                best = candidate
    return best

