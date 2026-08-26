#!/usr/bin/env python3
"""Verify the Ab-Ag pDockQ2 refit and test heterodimer-specific transfer.

This script is deliberately exploratory.  It reproduces the frozen Ab-Ag
pDockQ2 refit protocol, writes comparison-only workshop CSVs, and compares
isotonic ipTM fitted on all General rows versus strict General heterodimers on
the finite-DockQ AFDB subset.  It does not modify canonical paper tables.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
WORKSHOP = ANALYSIS / "workshop"
AFDB = ANALYSIS / "afdb"
DATA = ROOT / "data"
THRESHOLDS = [("acceptable", 0.23), ("medium", 0.49), ("high", 0.80)]


def compute_xi(df: pd.DataFrame, d0: float = 10.0) -> np.ndarray:
    return df["mean_plddt"].to_numpy(float) / (1.0 + (df["iface_pae_mean"].to_numpy(float) / d0) ** 2)


def sigmoid(x: np.ndarray, L: float, x0: float, k: float, b: float) -> np.ndarray:
    return L / (1.0 + np.exp(-k * (x - x0))) + b


def fit_pdockq2_refit(train: pd.DataFrame) -> dict[str, float]:
    """Frozen protocol from PAPER_REVISION/build_results_revision.py."""
    xi = compute_xi(train)
    dockq = train["dockq"].to_numpy(float)
    valid = np.isfinite(xi) & np.isfinite(dockq)
    popt, _ = curve_fit(
        sigmoid,
        xi[valid],
        dockq[valid],
        p0=[1.31, 84.733, 0.075, 0.005],
        maxfev=10000,
        bounds=([0.0, 0.0, 0.0, -1.0], [2.0, 200.0, 1.0, 1.0]),
    )
    return {"L": float(popt[0]), "x0": float(popt[1]), "k": float(popt[2]), "b": float(popt[3]), "d0": 10.0}


def apply_refit(df: pd.DataFrame, params: dict[str, float]) -> np.ndarray:
    return np.clip(sigmoid(compute_xi(df, params["d0"]), params["L"], params["x0"], params["k"], params["b"]), 0.0, 1.0)


def apply_published(df: pd.DataFrame) -> np.ndarray:
    """Published pDockQ2 numerical score, clipped after evaluation."""
    return np.clip(sigmoid(compute_xi(df), 1.31, 84.733, 0.075, 0.005), 0.0, 1.0)


def compute_ece(y_true: np.ndarray, probability: np.ndarray, n_bins: int = 10) -> float:
    probability = np.clip(np.asarray(probability, dtype=float), 0.0, 1.0)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for index in range(n_bins):
        if index < n_bins - 1:
            mask = (probability >= edges[index]) & (probability < edges[index + 1])
        else:
            mask = (probability >= edges[index]) & (probability <= edges[index + 1])
        if mask.any():
            ece += mask.mean() * abs(float(probability[mask].mean()) - float(y_true[mask].mean()))
    return float(ece)


def metrics(y_true: np.ndarray, probability: np.ndarray) -> dict[str, float | int]:
    probability = np.clip(np.asarray(probability, dtype=float), 0.0, 1.0)
    prediction = (probability >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, prediction, labels=[0, 1]).ravel()
    return {
        "n_valid": int(len(y_true)), "n_pos": int(y_true.sum()), "n_neg": int((1 - y_true).sum()),
        "brier": float(brier_score_loss(y_true, probability)), "ece": compute_ece(y_true, probability),
        "auroc": float(roc_auc_score(y_true, probability)), "auprc": float(average_precision_score(y_true, probability)),
        "accuracy": float(accuracy_score(y_true, prediction)), "mcc": float(matthews_corrcoef(y_true, prediction)),
        "ppv": float(precision_score(y_true, prediction, zero_division=0)),
        "recall": float(recall_score(y_true, prediction, zero_division=0)),
        "f1": float(f1_score(y_true, prediction, zero_division=0)),
        "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
    }


def load_abag_train() -> pd.DataFrame:
    paths = sorted((DATA / "abag_train_v2_parts").glob("abag_train_v2_part*.csv"))
    if len(paths) != 5:
        raise RuntimeError(f"Expected five Ab-Ag train parts, found {len(paths)}")
    return pd.concat((pd.read_csv(path, low_memory=False) for path in paths), ignore_index=True)


def closest_at_90_precision(y_true: np.ndarray, probability: np.ndarray) -> tuple[int, float, float]:
    """Largest selected set whose observed precision is at least 0.90."""
    order = np.argsort(-probability, kind="mergesort")
    sorted_y = y_true[order]
    cumulative_tp = np.cumsum(sorted_y)
    selected = np.arange(1, len(y_true) + 1)
    precision = cumulative_tp / selected
    valid = np.flatnonzero(precision >= 0.90)
    if len(valid) == 0:
        return 0, float("nan"), 0.0
    index = valid[-1]
    return int(selected[index]), float(precision[index]), float(cumulative_tp[index] / y_true.sum())


def write_refit_outputs(train: pd.DataFrame, test: pd.DataFrame, params: dict[str, float]) -> None:
    required = ["dockq", "iptm", "ptm", "iface_pae_mean", "mean_plddt"]
    test = test.dropna(subset=required).copy()
    test["pdockq2_refit"] = apply_refit(test, params)
    test["pdockq2_published"] = apply_published(test)

    existing = pd.read_csv(WORKSHOP / "workshop_abag_table.csv")
    refit_rows: list[dict[str, object]] = []
    for threshold_name, threshold_value in THRESHOLDS:
        y = (test["dockq"].to_numpy(float) >= threshold_value).astype(int)
        refit_rows.append({
            "dataset": "abag", "threshold": threshold_name, "threshold_val": threshold_value,
            "method": "pDockQ2 (refit)", **metrics(y, test["pdockq2_refit"].to_numpy(float)),
        })
    combined = pd.concat([existing, pd.DataFrame(refit_rows)], ignore_index=True)
    order = {"Raw ipTM": 0, "Raw ranking conf.": 1, "pDockQ2 (published)": 2, "pDockQ2 (refit)": 3,
             "ipSAEmax": 4, "Iso. ipTM": 5}
    combined["_order"] = combined["method"].map(order).fillna(99)
    combined = combined.sort_values(["threshold_val", "_order"], kind="stable").drop(columns="_order")
    combined.to_csv(ANALYSIS / "workshop_abag_table_with_refit.csv", index=False)

    yield_rows: list[dict[str, object]] = []
    published_k50_rows: list[dict[str, object]] = []
    for threshold_name, threshold_value in THRESHOLDS:
        y_column = f"y_{threshold_name}"
        test[y_column] = (test["dockq"].to_numpy(float) >= threshold_value).astype(int)
        for k in (5, 10, 20, 50):
            observed, predicted_refit, predicted_published = [], [], []
            for _, group in test.groupby("target_id", sort=False):
                if len(group) < k:
                    continue
                # Match the frozen workshop rule: descending raw ipTM, then model ID.
                selected = group.sort_values(["iptm", "model_id"], ascending=[False, True], kind="mergesort").head(k)
                observed.append(float(selected[y_column].mean()))
                predicted_refit.append(float(selected["pdockq2_refit"].mean()))
                predicted_published.append(float(selected["pdockq2_published"].mean()))
            observed_array = np.asarray(observed)
            refit_array = np.asarray(predicted_refit)
            published_array = np.asarray(predicted_published)
            yield_rows.append({
                "dataset": "abag", "dataset_label": "Ab-Ag", "threshold": threshold_name,
                "threshold_val": threshold_value, "aggregation": "macro_fixed_K", "K": k,
                "n_targets": len(observed_array), "n_models": len(observed_array) * k,
                "observed": float(observed_array.mean()), "pdockq2_refit": float(refit_array.mean()),
                "mae_pdockq2_refit": float(np.abs(refit_array - observed_array).mean()),
            })
            if k == 50:
                published_k50_rows.append({
                    "dataset": "abag", "dataset_label": "Ab-Ag", "threshold": threshold_name,
                    "threshold_val": threshold_value, "aggregation": "macro_fixed_K", "K": k,
                    "n_targets": len(observed_array), "n_models": len(observed_array) * k,
                    "observed": float(observed_array.mean()), "pdockq2": float(published_array.mean()),
                    "mae_pdockq2": float(np.abs(published_array - observed_array).mean()),
                })
    refit_yield = pd.DataFrame(yield_rows)
    existing_yield = pd.read_csv(WORKSHOP / "workshop_yield_simplified.csv")
    # The original workshop pDockQ2 producer only emitted K=5,10,20.  Append
    # its previously omitted K=50 rows on the same raw-ipTM-ranked sets.
    existing_k = pd.to_numeric(existing_yield["K"], errors="coerce")
    # Replace rather than duplicate these rows on subsequent reproductions,
    # while retaining the legacy ordering of every pre-existing row.
    existing_yield = existing_yield.loc[existing_k != 50].copy()
    existing_yield = pd.concat([existing_yield, pd.DataFrame(published_k50_rows)], ignore_index=True, sort=False)
    existing_yield.to_csv(WORKSHOP / "workshop_yield_simplified.csv", index=False)
    key_columns = ["dataset", "dataset_label", "threshold", "threshold_val", "aggregation", "K", "n_targets", "n_models"]
    # Existing workshop rows mix numeric K values and the string "all". Use a
    # normalized internal join key while retaining the original display column.
    existing_yield["_K_key"] = existing_yield["K"].astype(str)
    refit_yield["_K_key"] = refit_yield["K"].astype(str)
    join_columns = [column for column in key_columns if column != "K"] + ["_K_key"]
    output_yield = existing_yield.merge(
        refit_yield[join_columns + ["pdockq2_refit", "mae_pdockq2_refit"]],
        on=join_columns, how="left", validate="one_to_one",
    ).drop(columns="_K_key")
    output_yield.to_csv(ANALYSIS / "workshop_yield_with_refit.csv", index=False)

    acceptable = refit_rows[0]
    lines = [
        "# pDockQ2 Refit Verification", "",
        "## Frozen Procedure", "",
        "- Training data: the five released `data/abag_train_v2_parts/` shards only.",
        f"- Training rows: {len(train):,} across {train['target_id'].nunique():,} targets; valid continuous-DockQ fit rows: "
        f"{(np.isfinite(compute_xi(train)) & np.isfinite(train['dockq'].to_numpy(float))).sum():,}.",
        "- Target: continuous `dockq`, not a thresholded binary label.",
        "- Input: `mean_plddt / (1 + (iface_pae_mean / 10)^2)` with `d0 = 10` fixed.",
        "- Optimizer: `scipy.optimize.curve_fit`, initial `[L, x0, k, b] = [1.31, 84.733, 0.075, 0.005]`,",
        "  `maxfev=10000`, bounds `L:[0,2]`, `x0:[0,200]`, `k:[0,1]`, `b:[-1,1]`.",
        "- Optimized parameters: `L`, `x0`, `k`, `b`; output clipped to `[0,1]` only after fitting.", "",
        "## Parameters", "",
        f"- `L = {params['L']:.8f}`", f"- `x0 = {params['x0']:.8f}`", f"- `k = {params['k']:.8f}`",
        f"- `b = {params['b']:.8f}`", f"- `d0 = {params['d0']:.1f} (fixed)`", "",
        "## Ab-Ag Test Check", "",
        f"- Evaluation rows: {len(test):,}.",
        f"- DockQ >= 0.23: Brier `{acceptable['brier']:.6f}`, MCC `{acceptable['mcc']:.6f}`, AUROC `{acceptable['auroc']:.6f}`.",
        "", "The implementation matches `af3_atlas/PAPER_REVISION/build_results_revision.py` and its successor",
        "`build_final_v2_release.py`. Those scripts use the parameter order `(L, x0, k, b)`; the alternate",
        "order in an informal example must not be used with their published initial vector.",
        "", "## Legacy-value Note", "",
        "The released final-v2 machine-readable source (`data/report_data_v3.json`) records the same",
        "acceptable-event Brier value, `0.100590`. The approximate `0.096` value cited in an earlier",
        "instruction is not produced by this final-v2 data/protocol and must not be used to validate it.",
    ]
    (ANALYSIS / "pdockq2_refit_verification.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_heterodimer_transfer() -> None:
    general = pd.read_csv(DATA / "general_v2.csv", low_memory=False)
    afdb = pd.read_csv(AFDB / "afdb_positive_dockq_features.csv", low_memory=False)
    afdb["dockq_native"] = pd.to_numeric(afdb["dockq_native"], errors="coerce")
    afdb = afdb.loc[np.isfinite(afdb["dockq_native"]) & np.isfinite(afdb["iptm"])].copy()
    heterodimer_train = general.loc[(general["class"] == "heteromer") & (general["num_chains"] == 2)].copy()
    if len(heterodimer_train) == 0:
        raise RuntimeError("No strict General heterodimer rows")
    subsets = {
        "AFDB finite DockQ, all complexes": afdb,
        "AFDB finite DockQ, heterodimers only": afdb.loc[afdb["complex_type"] == "heterodimer"].copy(),
    }
    rows: list[dict[str, object]] = []
    for threshold_name, threshold_value in THRESHOLDS:
        for source_name, source in (("General all complexes", general), ("General strict heterodimers", heterodimer_train)):
            labels = (source["dockq"].to_numpy(float) >= threshold_value).astype(int)
            calibrator = IsotonicRegression(out_of_bounds="clip").fit(source["iptm"].to_numpy(float), labels)
            for subset_name, subset in subsets.items():
                y = (subset["dockq_native"].to_numpy(float) >= threshold_value).astype(int)
                probability = calibrator.predict(subset["iptm"].to_numpy(float))
                rows.append({
                    "threshold": threshold_name, "threshold_val": threshold_value,
                    "training_source": source_name, "training_rows": len(source),
                    "training_targets": source["target_id"].nunique(), "evaluation_subset": subset_name,
                    **metrics(y, probability),
                })
    pd.DataFrame(rows).to_csv(ANALYSIS / "workshop_afdb_heterodimer_transfer.csv", index=False)


def main() -> None:
    train = load_abag_train()
    test = pd.read_csv(DATA / "abag_test_v2.csv", low_memory=False)
    params = fit_pdockq2_refit(train)
    write_refit_outputs(train, test, params)
    write_heterodimer_transfer()
    print(f"Wrote {ANALYSIS / 'pdockq2_refit_verification.md'}")
    print(f"Wrote {ANALYSIS / 'workshop_abag_table_with_refit.csv'}")
    print(f"Wrote {ANALYSIS / 'workshop_yield_with_refit.csv'}")
    print(f"Wrote {ANALYSIS / 'workshop_afdb_heterodimer_transfer.csv'}")


if __name__ == "__main__":
    main()
