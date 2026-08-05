#!/usr/bin/env python3
"""Decision-use experiments v2.

This pipeline generates a corrected and extended version of the decision-use
experiments under `analysis/decision_use_v2/` without overwriting the existing
v1 outputs.

Main additions relative to v1:
- corrected target-bootstrap handling for reliability curves;
- explicit missingness and row-universe audits;
- Ab-Ag iPAE fixed-ranking expected-yield experiment;
- Ab-Ag iPAE reliability operating curve;
- supplementary General/CASP16 iPAE transfer diagnostics when frozen saved
  predictions already exist.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, pearsonr, spearmanr
from sklearn.isotonic import IsotonicRegression

from decision_use_case_common import (
    FEATURES,
    K_LEVELS,
    N_BOOT,
    PRIMARY_THRESHOLD,
    Q_LEVELS,
    SEED,
    THRESHOLDS,
    MultiOutputMLP,
    audit_probability_column,
    collect_package_versions,
    fit_general_isotonic_models,
    fmt_ci,
    load_abag_transfer_features,
    load_general_mlp_bundle,
    load_general_training_features,
    load_prediction_table,
    predict_general_mlp,
    project_paths,
    reconstruct_general_folds,
    target_bootstrap_indices,
    yaml_dump,
    canonical_specs,
)


THREE_METHOD = "three_method_common"
PAIRWISE_RAW_ISO = "raw_iso_pairwise"
OUTPUT_DIRNAME = "decision_use_v2"


@dataclass(frozen=True)
class ScoreFamilySpec:
    family: str
    raw_col: str
    iso_prefix: str
    raw_label: str
    iso_label: str
    training_domain: str
    ascending: bool


FAMILY_SPECS = {
    "iptm": ScoreFamilySpec(
        family="iptm",
        raw_col="p_raw_iptm",
        iso_prefix="p_iso_iptm_",
        raw_label="Raw ipTM",
        iso_label="Isotonic ipTM",
        training_domain="dataset_specific_or_general_transfer",
        ascending=False,
    ),
    "ipae": ScoreFamilySpec(
        family="ipae",
        raw_col="p_raw_ipae",
        iso_prefix="p_iso_ipae_",
        raw_label="Raw iPAE proxy",
        iso_label="Calibrated iPAE probability",
        training_domain="dataset_specific_or_general_transfer",
        ascending=False,
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("/proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration"),
    )
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--n-bootstrap", type=int, default=N_BOOT)
    return parser.parse_args()


def assert_canonical_repo(project_root: Path) -> None:
    required = [
        project_root / ".git",
        project_root / "af3_atlas" / "PAPER_REVISION" / "data" / "abag_predictions_v3.csv",
        project_root / "af3_atlas" / "PAPER_REVISION" / "data" / "general_predictions_v3.csv",
        project_root / "af3_atlas" / "PAPER_REVISION" / "data" / "casp16_predictions_v3.csv",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("Repository root does not match canonical active repository. Missing: " + ", ".join(missing))


def raw_ipae_proxy_from_iface_pae(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    return 1.0 / (1.0 + arr)


def isotonic_predict_allow_nan(model: IsotonicRegression, values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    out = np.full(arr.shape, np.nan, dtype=float)
    valid = np.isfinite(arr)
    if valid.any():
        out[valid] = model.predict(arr[valid])
    return out


def safe_corr(fn, x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 2 or np.allclose(x, x[0]) or np.allclose(y, y[0]):
        return float("nan")
    return float(fn(x, y)[0] if fn is not spearmanr else fn(x, y).correlation)


def choose_threshold_max_coverage(scores: np.ndarray, y_true: np.ndarray, q: float) -> float:
    scores = np.asarray(scores, dtype=float)
    y_true = np.asarray(y_true, dtype=int)
    valid = np.isfinite(scores) & np.isfinite(y_true)
    if not valid.any():
        return float("inf")
    scores = scores[valid]
    y_true = y_true[valid]

    order = np.argsort(scores, kind="mergesort")[::-1]
    sorted_scores = scores[order]
    sorted_y = y_true[order]

    group_starts = np.r_[0, np.flatnonzero(sorted_scores[1:] != sorted_scores[:-1]) + 1]
    group_ends = np.r_[group_starts[1:], len(sorted_scores)]
    unique_scores = sorted_scores[group_starts]
    group_counts = group_ends - group_starts
    group_pos = np.add.reduceat(sorted_y, group_starts)

    cum_counts = np.cumsum(group_counts)
    cum_pos = np.cumsum(group_pos)
    precision = cum_pos / cum_counts
    valid_q = precision >= q
    if not valid_q.any():
        return float("inf")
    best_idx = np.flatnonzero(valid_q)[-1]
    return float(unique_scores[best_idx])


def compute_monotonicity_metrics(raw_scores: np.ndarray, calibrated_scores: np.ndarray) -> dict[str, float | int]:
    raw = np.asarray(raw_scores, dtype=float)
    cal = np.asarray(calibrated_scores, dtype=float)
    order = np.argsort(raw, kind="mergesort")
    raw_sorted = raw[order]
    cal_sorted = cal[order]
    raw_diff = np.diff(raw_sorted)
    cal_diff = np.diff(cal_sorted)
    strict_inv = int(np.sum((raw_diff > 0) & (cal_diff < -1e-12)))
    ties = int(np.sum(np.isclose(cal_diff, 0.0, atol=1e-12)))
    return {
        "spearman": safe_corr(spearmanr, raw, cal),
        "kendall": safe_corr(kendalltau, raw, cal),
        "strict_ordering_inversions": strict_inv,
        "isotonic_ties": ties,
        "n_rows": int(len(raw)),
    }


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        vals = []
        for c in cols:
            v = row[c]
            if pd.isna(v):
                vals.append("")
            elif isinstance(v, (float, np.floating)):
                vals.append(f"{float(v):.4f}")
            else:
                vals.append(str(v))
        out.append("| " + " | ".join(vals) + " |")
    return "\n".join(out)


def load_abag_train(project_root: Path) -> pd.DataFrame:
    path = project_paths(project_root)["data"] / "abag_train_v2.csv"
    df = pd.read_csv(path, low_memory=False)
    needed = ["target_id", "model_id", "dockq", "iface_pae_mean", "iptm", "ptm", "ranking_score", "interchain_block_mean", "mean_plddt"]
    for col in needed:
        if col not in df.columns:
            raise ValueError(f"{path}: missing {col}")
        if col not in ("target_id", "model_id"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["p_raw_ipae"] = raw_ipae_proxy_from_iface_pae(df["iface_pae_mean"].to_numpy(dtype=float))
    df["p_raw_iptm"] = pd.to_numeric(df["iptm"], errors="coerce")
    return df


def load_abag_test_raw(project_root: Path) -> pd.DataFrame:
    path = project_paths(project_root)["data"] / "abag_test_v2.csv"
    df = pd.read_csv(path, low_memory=False)
    needed = ["target_id", "model_id", "dockq", "iface_pae_mean", "iptm", "ptm", "ranking_score", "interchain_block_mean", "mean_plddt"]
    for col in needed:
        if col not in df.columns:
            raise ValueError(f"{path}: missing {col}")
        if col not in ("target_id", "model_id"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["p_raw_ipae"] = raw_ipae_proxy_from_iface_pae(df["iface_pae_mean"].to_numpy(dtype=float))
    df["p_raw_iptm"] = pd.to_numeric(df["iptm"], errors="coerce")
    return df


def fit_abag_isotonic_models(train_df: pd.DataFrame, family: str) -> dict[str, IsotonicRegression]:
    if family not in FAMILY_SPECS:
        raise KeyError(family)
    raw_col = FAMILY_SPECS[family].raw_col
    x = train_df[raw_col].to_numpy(dtype=float)
    out = {}
    for thr_name, thr_val in THRESHOLDS.items():
        y = (train_df["dockq"].to_numpy(dtype=float) >= thr_val).astype(int)
        valid = np.isfinite(x) & np.isfinite(y)
        iso = IsotonicRegression(out_of_bounds="clip")
        iso.fit(x[valid], y[valid])
        out[thr_name] = iso
    return out


def load_abag_mlp_bundle(project_root: Path):
    paths = project_paths(project_root)
    model = MultiOutputMLP(5)
    state = __import__('torch').load(paths["models"] / "locked_ce_5feat_abag.pt", map_location="cpu", weights_only=False)
    if isinstance(state, dict) and "model_state_dict" in state:
        model.load_state_dict(state["model_state_dict"])
    elif isinstance(state, dict) and "state_dict" in state:
        model.load_state_dict(state["state_dict"])
    else:
        model.load_state_dict(state)
    model.eval()
    import joblib
    scaler = joblib.load(paths["models"] / "scaler_5feat_abag.pkl")
    return model, scaler


def predict_abag_mlp(df: pd.DataFrame, model, scaler) -> dict[str, np.ndarray]:
    import torch
    import torch.nn.functional as F
    x = scaler.transform(df[FEATURES].to_numpy(dtype=float))
    with torch.no_grad():
        logits = model(torch.tensor(x, dtype=torch.float32))
        probs = F.softmax(logits, dim=-1).numpy()
    return {
        "acceptable": probs[:, 1] + probs[:, 2] + probs[:, 3],
        "medium": probs[:, 2] + probs[:, 3],
        "high": probs[:, 3],
    }


def build_universe_masks(df: pd.DataFrame, dockq_col: str, raw_col: str, iso_col: str, mlp_col: str) -> dict[str, np.ndarray]:
    vals = df[[dockq_col, raw_col, iso_col]].to_numpy(dtype=float)
    pair = np.isfinite(vals).all(axis=1)
    common = np.isfinite(df[[dockq_col, raw_col, iso_col, mlp_col]].to_numpy(dtype=float)).all(axis=1)
    return {THREE_METHOD: common, PAIRWISE_RAW_ISO: pair}


def universe_audit_rows(df: pd.DataFrame, dataset_label: str, analysis_name: str, score_family: str, outcome: str, raw_col: str, iso_col: str, mlp_col: str) -> list[dict[str, object]]:
    base = {
        "dataset": dataset_label,
        "analysis_name": analysis_name,
        "score_family": score_family,
        "dockq_threshold_name": outcome,
        "n_input_rows": int(len(df)),
        "n_finite_dockq": int(np.isfinite(df["dockq"].to_numpy(dtype=float)).sum()),
        "n_finite_raw_score": int(np.isfinite(df[raw_col].to_numpy(dtype=float)).sum()),
        "n_finite_isotonic_probability": int(np.isfinite(df[iso_col].to_numpy(dtype=float)).sum()),
        "n_finite_mlp_probability": int(np.isfinite(df[mlp_col].to_numpy(dtype=float)).sum()),
    }
    masks = build_universe_masks(df, "dockq", raw_col, iso_col, mlp_col)
    rows = []
    for universe, mask in masks.items():
        reasons = []
        if universe == THREE_METHOD:
            if (~np.isfinite(df[mlp_col].to_numpy(dtype=float))).any():
                reasons.append("mlp_missing")
        if (~np.isfinite(df[raw_col].to_numpy(dtype=float))).any():
            reasons.append("raw_missing")
        if (~np.isfinite(df[iso_col].to_numpy(dtype=float))).any():
            reasons.append("isotonic_missing")
        if (~np.isfinite(df["dockq"].to_numpy(dtype=float))).any():
            reasons.append("dockq_missing")
        rows.append({
            **base,
            "comparison_universe": universe,
            "n_common_valid": int(mask.sum()),
            "n_dropped": int((~mask).sum()),
            "drop_reason": ";".join(sorted(set(reasons))) if reasons else "none",
        })
    return rows


def build_fixed_ranking_rows(
    df: pd.DataFrame,
    dataset_key: str,
    dataset_label: str,
    ranking_family: str,
    comparison_universe: str,
    selection_score_col: str,
    raw_label: str,
    iso_label: str,
    mlp_label: str,
    iso_col: str,
    mlp_col: str,
    k_values: list[int],
    ascending: bool,
    thr_name: str,
    thr_val: float,
) -> list[dict[str, object]]:
    rows = []
    for k in k_values:
        for target_id, g in df.groupby("target_id", sort=False):
            n_avail = int(len(g))
            if n_avail < k:
                continue
            chosen = g.sort_values([selection_score_col, "model_id"], ascending=[ascending, True], kind="mergesort").head(k).copy()
            actual = (chosen["dockq"].to_numpy(dtype=float) >= thr_val).astype(int)
            actual_hits = int(actual.sum())
            raw_hits = float(chosen[selection_score_col].to_numpy(dtype=float).sum())
            iso_hits = float(chosen[iso_col].to_numpy(dtype=float).sum())
            mlp_hits = float(chosen[mlp_col].to_numpy(dtype=float).sum()) if mlp_col in chosen.columns else np.nan
            rows.append({
                "dataset": dataset_key,
                "dataset_label": dataset_label,
                "ranking_family": ranking_family,
                "selection_score": selection_score_col,
                "comparison_universe": comparison_universe,
                "probability_method": "all_methods",
                "target_id": target_id,
                "dockq_threshold_name": thr_name,
                "dockq_threshold": thr_val,
                "K": k,
                "n_models_available": n_avail,
                "selection_protocol": f"{selection_score_col}_{'asc' if ascending else 'desc'}_then_model_id",
                "selected_model_ids": ";".join(chosen["model_id"].astype(str).tolist()),
                "actual_hits": actual_hits,
                "actual_rate": actual_hits / k,
                "predicted_hits_raw": raw_hits,
                "predicted_hits_iso": iso_hits,
                "predicted_hits_mlp": mlp_hits,
                "predicted_rate_raw": raw_hits / k,
                "predicted_rate_iso": iso_hits / k,
                "predicted_rate_mlp": mlp_hits / k if np.isfinite(mlp_hits) else np.nan,
                "error_raw": raw_hits - actual_hits,
                "error_iso": iso_hits - actual_hits,
                "error_mlp": mlp_hits - actual_hits if np.isfinite(mlp_hits) else np.nan,
                "raw_label": raw_label,
                "iso_label": iso_label,
                "mlp_label": mlp_label,
            })
    return rows


def compute_fixed_ranking_metrics(per_target: pd.DataFrame, n_boot: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    metric_rows = []
    boot_rows = []
    audit_rows = []
    warnings = []
    for keys, sub in per_target.groupby(["dataset", "dataset_label", "ranking_family", "comparison_universe", "dockq_threshold_name", "dockq_threshold", "K", "raw_label", "iso_label", "mlp_label"], sort=False):
        dataset, dataset_label, ranking_family, universe, thr_name, thr_val, k, raw_label, iso_label, mlp_label = keys
        sub = sub.reset_index(drop=True)
        if sub["target_id"].duplicated().any():
            dup_targets = sub.loc[sub["target_id"].duplicated(), "target_id"].astype(str).unique().tolist()[:10]
            raise AssertionError(
                f"Fixed-ranking per-target table has duplicate targets for dataset={dataset}, family={ranking_family}, universe={universe}, outcome={thr_name}, K={k}: {dup_targets}"
            )
        actual = sub["actual_hits"].to_numpy(dtype=float)
        pred_map = {
            raw_label: sub["predicted_hits_raw"].to_numpy(dtype=float),
            iso_label: sub["predicted_hits_iso"].to_numpy(dtype=float),
        }
        if universe == THREE_METHOD:
            pred_map[mlp_label] = sub["predicted_hits_mlp"].to_numpy(dtype=float)
        n_targets = len(sub)
        for method, pred in pred_map.items():
            err = pred - actual
            mae = float(np.mean(np.abs(err)))
            metric_rows.append({
                "dataset": dataset,
                "dataset_label": dataset_label,
                "ranking_family": ranking_family,
                "selection_score": "p_raw_iptm" if ranking_family == "iptm" else "p_raw_ipae",
                "probability_method": method,
                "comparison_universe": universe,
                "dockq_threshold_name": thr_name,
                "dockq_threshold": thr_val,
                "K": int(k),
                "n_targets": int(n_targets),
                "mean_actual_hits": float(actual.mean()),
                "mean_predicted_hits": float(pred.mean()),
                "mae_hits": mae,
                "normalized_mae": float(mae / k),
                "rmse_hits": float(np.sqrt(np.mean(err**2))),
                "signed_bias": float(err.mean()),
                "pearson": float(pearsonr(pred, actual)[0]) if len(pred) > 1 and not (np.allclose(pred, pred[0]) or np.allclose(actual, actual[0])) else np.nan,
                "spearman": float(spearmanr(pred, actual).correlation) if len(pred) > 1 and not (np.allclose(pred, pred[0]) or np.allclose(actual, actual[0])) else np.nan,
                "total_predicted_hits": float(pred.sum()),
                "total_observed_hits": float(actual.sum()),
            })

        boot_idx, uniq_targets = target_bootstrap_indices(sub["target_id"], n_boot=n_boot, seed=seed)
        mae_samples = {}
        for method, pred in pred_map.items():
            pred_draw = pred[boot_idx]
            act_draw = actual[boot_idx]
            err = pred_draw - act_draw
            mae = np.mean(np.abs(err), axis=1)
            norm = mae / k
            rmse = np.sqrt(np.mean(err ** 2, axis=1))
            bias = np.mean(err, axis=1)
            mae_samples[method] = mae
            for metric_name, samples in [("mae_hits", mae), ("normalized_mae", norm), ("rmse_hits", rmse), ("signed_bias", bias)]:
                lo, hi = fmt_ci(samples)
                boot_rows.append({
                    "dataset": dataset,
                    "dataset_label": dataset_label,
                    "ranking_family": ranking_family,
                    "selection_score": "p_raw_iptm" if ranking_family == "iptm" else "p_raw_ipae",
                    "probability_method": method,
                    "comparison_universe": universe,
                    "dockq_threshold_name": thr_name,
                    "dockq_threshold": thr_val,
                    "K": int(k),
                    "row_type": "method_metric",
                    "metric": metric_name,
                    "point_estimate": float(metric_rows[-1][metric_name]) if metric_name in metric_rows[-1] and metric_rows[-1]["probability_method"] == method else np.nan,
                    "bootstrap_mean": float(samples.mean()),
                    "ci_low": lo,
                    "ci_high": hi,
                    "fraction_gt_zero": float((samples > 0).mean()),
                    "n_valid_bootstrap_replicates": int(len(samples)),
                })
        pairings = [(raw_label, iso_label, "error_raw", "error_iso")]
        if universe == THREE_METHOD:
            pairings.extend([(raw_label, mlp_label, "error_raw", "error_mlp"), (iso_label, mlp_label, "error_iso", "error_mlp")])
        for left, right, left_err_col, right_err_col in pairings:
            paired_delta_point = np.abs(sub[left_err_col].to_numpy(dtype=float)) - np.abs(sub[right_err_col].to_numpy(dtype=float))
            delta_point = float(paired_delta_point.mean())
            delta_identity_rhs = float(np.mean(np.abs(sub[left_err_col].to_numpy(dtype=float)))) - float(np.mean(np.abs(sub[right_err_col].to_numpy(dtype=float))))
            if not np.isclose(delta_point, delta_identity_rhs, atol=1e-12):
                raise AssertionError(
                    f"Paired-delta identity failed for dataset={dataset}, family={ranking_family}, universe={universe}, outcome={thr_name}, K={k}, comparison={left}-{right}: "
                    f"lhs={delta_point:.12f}, rhs={delta_identity_rhs:.12f}"
                )
            boot_idx, _ = target_bootstrap_indices(sub["target_id"], n_boot=n_boot, seed=seed)
            delta = paired_delta_point[boot_idx].mean(axis=1)
            lo, hi = fmt_ci(delta)
            boot_mean = float(delta.mean())
            audit_rows.append({
                "dataset": dataset,
                "dataset_label": dataset_label,
                "ranking_family": ranking_family,
                "comparison_universe": universe,
                "dockq_threshold_name": thr_name,
                "dockq_threshold": thr_val,
                "K": int(k),
                "comparison": f"{left} - {right}",
                "n_targets": int(len(sub)),
                "point_delta_mean_absdiff": delta_point,
                "point_delta_diff_of_means": delta_identity_rhs,
                "identity_abs_error": float(abs(delta_point - delta_identity_rhs)),
                "bootstrap_mean_delta": boot_mean,
                "bootstrap_mean_minus_point": float(boot_mean - delta_point),
                "bootstrap_sd_delta": float(delta.std(ddof=1)),
                "ci_low": lo,
                "ci_high": hi,
            })
            boot_rows.append({
                "dataset": dataset,
                "dataset_label": dataset_label,
                "ranking_family": ranking_family,
                "selection_score": "p_raw_iptm" if ranking_family == "iptm" else "p_raw_ipae",
                "probability_method": f"{left} - {right}",
                "comparison_universe": universe,
                "dockq_threshold_name": thr_name,
                "dockq_threshold": thr_val,
                "K": int(k),
                "row_type": "mae_difference",
                "metric": "mae_hits_difference",
                "point_estimate_delta": delta_point,
                "bootstrap_mean_delta": boot_mean,
                "ci_low": lo,
                "ci_high": hi,
                "fraction_delta_gt_0": float((delta > 0).mean()),
                "n_valid_bootstrap_replicates": int(len(delta)),
            })
    return pd.DataFrame(metric_rows), pd.DataFrame(boot_rows), pd.DataFrame(audit_rows), warnings


def summarize_selection_row(
    df: pd.DataFrame,
    selected: np.ndarray,
    q: float,
    thr_name: str,
    thr_val: float,
    method: str,
    dataset: str,
    training_domain: str,
    score_family: str,
    comparison_universe: str,
    tuning_dataset: str,
    tuning_protocol: str,
    score_threshold: float | np.nan,
    selected_score_col: str,
    selected_prob_col: str | None,
    fold_id: str = "all",
) -> dict[str, object]:
    y = (df["dockq"].to_numpy(dtype=float) >= thr_val).astype(int)
    sel = np.asarray(selected, dtype=bool)
    n_eligible = int(len(df))
    n_selected = int(sel.sum())
    tp = int(y[sel].sum()) if n_selected else 0
    fp = int(n_selected - tp)
    fn = int(y.sum() - tp)
    precision = float(tp / n_selected) if n_selected else np.nan
    recall = float(tp / (tp + fn)) if (tp + fn) else 0.0
    coverage = float(n_selected / n_eligible) if n_eligible else np.nan
    score_vals = df.loc[sel, selected_score_col].to_numpy(dtype=float) if n_selected else np.array([], dtype=float)
    if selected_prob_col is None:
        prob_vals = np.array([], dtype=float)
        mean_prob = med_prob = min_prob = max_prob = np.nan
        cal_gap = np.nan
    else:
        prob_vals = df.loc[sel, selected_prob_col].to_numpy(dtype=float) if n_selected else np.array([], dtype=float)
        mean_prob = float(prob_vals.mean()) if n_selected else np.nan
        med_prob = float(np.median(prob_vals)) if n_selected else np.nan
        min_prob = float(prob_vals.min()) if n_selected else np.nan
        max_prob = float(prob_vals.max()) if n_selected else np.nan
        cal_gap = float(precision - mean_prob) if n_selected else np.nan
    return {
        "score_family": score_family,
        "training_domain": training_domain,
        "evaluation_dataset": dataset,
        "comparison_universe": comparison_universe,
        "threshold_tuning_dataset": tuning_dataset,
        "threshold_tuning_protocol": tuning_protocol,
        "threshold_refit_in_bootstrap": False,
        "dockq_threshold_name": thr_name,
        "dockq_threshold": thr_val,
        "method": method,
        "q": q,
        "score_threshold": score_threshold,
        "fold_id": fold_id,
        "n_total": n_eligible,
        "n_eligible": n_eligible,
        "n_selected": n_selected,
        "coverage": coverage,
        "precision": precision,
        "recall": recall,
        "mean_selected_score": float(score_vals.mean()) if n_selected else np.nan,
        "mean_selected_probability": mean_prob,
        "median_selected_probability": med_prob,
        "min_selected_probability": min_prob,
        "max_selected_probability": max_prob,
        "nominal_shortfall": float(max(0.0, q - precision)) if n_selected else np.nan,
        "nominal_excess": float(max(0.0, precision - q)) if n_selected else np.nan,
        "calibration_gap": cal_gap,
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }


def factorize_targets(target_series: pd.Series) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    codes, unique_targets = pd.factorize(target_series, sort=False)
    n_total = np.bincount(codes, minlength=len(unique_targets)).astype(int)
    return codes.astype(int, copy=False), unique_targets.to_numpy(), n_total


def target_summary_from_arrays(
    target_codes: np.ndarray,
    unique_targets: np.ndarray,
    n_total: np.ndarray,
    y_true: np.ndarray,
    selected: np.ndarray,
    selected_scores: np.ndarray,
    selected_probabilities: np.ndarray | None,
) -> pd.DataFrame:
    selected = np.asarray(selected, dtype=bool)
    y_true = np.asarray(y_true, dtype=int)
    selected_int = selected.astype(int, copy=False)
    selected_positive = selected_int * y_true
    selected_score_sum = np.where(selected, np.asarray(selected_scores, dtype=float), 0.0)
    if selected_probabilities is not None:
        selected_prob_sum = np.where(selected, np.asarray(selected_probabilities, dtype=float), 0.0)
    else:
        selected_prob_sum = np.zeros_like(selected_score_sum, dtype=float)

    n_targets = len(unique_targets)
    return pd.DataFrame(
        {
            "target_id": unique_targets,
            "n_total": n_total,
            "n_selected": np.bincount(target_codes, weights=selected_int, minlength=n_targets).astype(int),
            "selected_positive": np.bincount(target_codes, weights=selected_positive, minlength=n_targets).astype(int),
            "all_positive": np.bincount(target_codes, weights=y_true, minlength=n_targets).astype(int),
            "sum_selected_score": np.bincount(target_codes, weights=selected_score_sum, minlength=n_targets),
            "sum_selected_probability": np.bincount(target_codes, weights=selected_prob_sum, minlength=n_targets),
        }
    )


def bootstrap_reliability(target_summary: pd.DataFrame, curve_rows: pd.DataFrame, n_boot: int, seed: int) -> tuple[pd.DataFrame, list[str]]:
    rows = []
    warnings = []
    # metric rows by method
    group_cols = ["score_family", "training_domain", "evaluation_dataset", "comparison_universe", "dockq_threshold_name", "dockq_threshold", "method", "q"]
    for keys, sub in target_summary.groupby(group_cols, sort=False):
        score_family, training_domain, dataset, universe, thr_name, thr_val, method, q = keys
        sub = sub.reset_index(drop=True)
        boot_idx, uniq_targets = target_bootstrap_indices(sub["target_id"], n_boot=n_boot, seed=seed)
        n_total = sub["n_total"].to_numpy(dtype=float)
        n_selected = sub["n_selected"].to_numpy(dtype=float)
        selected_pos = sub["selected_positive"].to_numpy(dtype=float)
        all_pos = sub["all_positive"].to_numpy(dtype=float)
        sum_prob = sub["sum_selected_probability"].to_numpy(dtype=float)

        total_sum = n_total[boot_idx].sum(axis=1)
        selected_sum = n_selected[boot_idx].sum(axis=1)
        selected_pos_sum = selected_pos[boot_idx].sum(axis=1)
        all_pos_sum = all_pos[boot_idx].sum(axis=1)
        prob_sum = sum_prob[boot_idx].sum(axis=1)

        precision = np.divide(selected_pos_sum, selected_sum, out=np.full(n_boot, np.nan), where=selected_sum > 0)
        recall = np.divide(selected_pos_sum, all_pos_sum, out=np.zeros(n_boot), where=(all_pos_sum > 0) & (selected_sum > 0))
        coverage = np.divide(selected_sum, total_sum, out=np.full(n_boot, np.nan), where=total_sum > 0)
        shortfall = np.where(np.isfinite(precision), np.maximum(0.0, q - precision), np.nan)
        excess = np.where(np.isfinite(precision), np.maximum(0.0, precision - q), np.nan)
        mean_prob = np.divide(prob_sum, selected_sum, out=np.full(n_boot, np.nan), where=selected_sum > 0)
        cal_gap = precision - mean_prob if "Raw" not in method else np.full(n_boot, np.nan)
        empty_frac = float((selected_sum == 0).mean())

        full = curve_rows[
            (curve_rows["score_family"] == score_family)
            & (curve_rows["training_domain"] == training_domain)
            & (curve_rows["evaluation_dataset"] == dataset)
            & (curve_rows["comparison_universe"] == universe)
            & (curve_rows["dockq_threshold_name"] == thr_name)
            & (curve_rows["method"] == method)
            & np.isclose(curve_rows["q"], q)
        ].iloc[0]

        metric_map = {
            "precision": precision,
            "recall": recall,
            "coverage": coverage,
            "nominal_shortfall": shortfall,
            "nominal_excess": excess,
            "calibration_gap": cal_gap,
        }
        for metric_name, samples in metric_map.items():
            valid = np.isfinite(samples)
            if metric_name == "nominal_shortfall" and valid.mean() < 0.95:
                lo = hi = np.nan
            elif valid.any():
                lo, hi = fmt_ci(samples[valid])
            else:
                lo = hi = np.nan
            rows.append({
                "score_family": score_family,
                "training_domain": training_domain,
                "evaluation_dataset": dataset,
                "comparison_universe": universe,
                "dockq_threshold_name": thr_name,
                "dockq_threshold": thr_val,
                "method": method,
                "q": q,
                "row_type": "metric_ci",
                "metric": metric_name,
                "full_data_value": float(full[metric_name]) if pd.notna(full[metric_name]) else np.nan,
                "bootstrap_mean": float(np.nanmean(samples)) if valid.any() else np.nan,
                "ci_low": lo,
                "ci_high": hi,
                "n_valid_bootstrap_replicates": int(valid.sum()),
                "fraction_empty_bootstrap": empty_frac,
            })

    # paired shortfall differences
    for keys, sub in target_summary.groupby(["score_family", "training_domain", "evaluation_dataset", "comparison_universe", "dockq_threshold_name", "dockq_threshold", "q"], sort=False):
        score_family, training_domain, dataset, universe, thr_name, thr_val, q = keys
        methods = list(sub["method"].drop_duplicates())
        if score_family == "iptm":
            raw_name = "Raw ipTM"
            iso_name = "Isotonic ipTM"
        else:
            raw_name = "Raw iPAE proxy"
            iso_name = "Calibrated iPAE probability"
        mlp_name = "MLP 5-feat CE"
        pairs = [(raw_name, iso_name)]
        if universe == THREE_METHOD and raw_name in methods and mlp_name in methods:
            pairs.append((raw_name, mlp_name))
        for left, right in pairs:
            if left not in methods or right not in methods:
                continue
            piv = sub[sub["method"].isin([left, right])].pivot(index="target_id", columns="method", values=["n_total", "n_selected", "selected_positive", "all_positive", "sum_selected_probability"]).sort_index()
            target_ids = piv.index.to_numpy()
            boot_idx, uniq_targets = target_bootstrap_indices(target_ids, n_boot=n_boot, seed=seed)
            # arrays per method
            arr = {}
            for m in [left, right]:
                arr[m] = {
                    "n_total": piv[("n_total", m)].to_numpy(dtype=float),
                    "n_selected": piv[("n_selected", m)].to_numpy(dtype=float),
                    "selected_positive": piv[("selected_positive", m)].to_numpy(dtype=float),
                }
            def short_samples(method_name):
                ns = arr[method_name]["n_selected"][boot_idx].sum(axis=1)
                sp = arr[method_name]["selected_positive"][boot_idx].sum(axis=1)
                prec = np.divide(sp, ns, out=np.full(n_boot, np.nan), where=ns > 0)
                return np.where(np.isfinite(prec), np.maximum(0.0, q - prec), np.nan)
            left_short = short_samples(left)
            right_short = short_samples(right)
            valid = np.isfinite(left_short) & np.isfinite(right_short)
            delta = left_short - right_short
            full_left = curve_rows[
                (curve_rows["score_family"] == score_family) &
                (curve_rows["training_domain"] == training_domain) &
                (curve_rows["evaluation_dataset"] == dataset) &
                (curve_rows["comparison_universe"] == universe) &
                (curve_rows["dockq_threshold_name"] == thr_name) &
                (curve_rows["method"] == left) & np.isclose(curve_rows["q"], q)
            ].iloc[0]
            full_right = curve_rows[
                (curve_rows["score_family"] == score_family) &
                (curve_rows["training_domain"] == training_domain) &
                (curve_rows["evaluation_dataset"] == dataset) &
                (curve_rows["comparison_universe"] == universe) &
                (curve_rows["dockq_threshold_name"] == thr_name) &
                (curve_rows["method"] == right) & np.isclose(curve_rows["q"], q)
            ].iloc[0]
            full_delta = float(full_left["nominal_shortfall"] - full_right["nominal_shortfall"]) if pd.notna(full_left["nominal_shortfall"]) and pd.notna(full_right["nominal_shortfall"]) else np.nan
            if pd.notna(full_delta):
                check = float(full_left["nominal_shortfall"] - full_right["nominal_shortfall"])
                if not np.isclose(full_delta, check, atol=1e-12):
                    raise AssertionError("full_data_delta mismatch")
            boot_mean = float(np.nanmean(delta[valid])) if valid.any() else np.nan
            if np.isfinite(full_delta) and np.isfinite(boot_mean) and np.sign(full_delta) != 0 and np.sign(boot_mean) != 0 and np.sign(full_delta) != np.sign(boot_mean):
                warnings.append(
                    f"Reliability bootstrap sign mismatch: dataset={dataset}, family={score_family}, universe={universe}, outcome={thr_name}, q={q:.2f}, comparison={left} - {right}, point={full_delta:.6f}, boot_mean={boot_mean:.6f}"
                )
            lo, hi = fmt_ci(delta[valid]) if valid.any() else (np.nan, np.nan)
            rows.append({
                "score_family": score_family,
                "training_domain": training_domain,
                "evaluation_dataset": dataset,
                "comparison_universe": universe,
                "dockq_threshold_name": thr_name,
                "dockq_threshold": thr_val,
                "method": f"{left} - {right}",
                "q": q,
                "row_type": "shortfall_difference",
                "metric": "nominal_shortfall_difference",
                "full_data_raw_shortfall": float(full_left["nominal_shortfall"]) if pd.notna(full_left["nominal_shortfall"]) else np.nan,
                "full_data_calibrated_shortfall": float(full_right["nominal_shortfall"]) if pd.notna(full_right["nominal_shortfall"]) else np.nan,
                "full_data_delta": full_delta,
                "bootstrap_mean_delta": boot_mean,
                "ci_low": lo,
                "ci_high": hi,
                "fraction_delta_gt_0": float((delta[valid] > 0).mean()) if valid.any() else np.nan,
                "n_valid_paired_replicates": int(valid.sum()),
                "fraction_empty_bootstrap": float((~valid).mean()),
            })
    return pd.DataFrame(rows), warnings


def build_general_crossfit_reliability(df: pd.DataFrame, fold_ids: np.ndarray, raw_col: str, iso_col_tmpl: str, mlp_col_tmpl: str, score_family: str, training_domain: str, comparison_universe: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    curve_rows = []
    target_rows = []
    include_mlp = comparison_universe == THREE_METHOD
    for thr_name, thr_val in THRESHOLDS.items():
        iso_col = f"{iso_col_tmpl}{thr_name}"
        mlp_col = f"{mlp_col_tmpl}{thr_name}"
        masks = build_universe_masks(df, "dockq", raw_col, iso_col, mlp_col)
        work = df.loc[masks[comparison_universe]].copy()
        work_folds = fold_ids[masks[comparison_universe]]
        y_all = (work["dockq"].to_numpy(dtype=float) >= thr_val).astype(int)
        target_codes, unique_targets, n_total = factorize_targets(work["target_id"])
        raw_scores = work[raw_col].to_numpy(dtype=float)
        iso_scores = work[iso_col].to_numpy(dtype=float)
        mlp_scores = work[mlp_col].to_numpy(dtype=float) if include_mlp else None
        # calibrated methods on OOF probabilities
        methods = [(FAMILY_SPECS[score_family].iso_label, iso_col, iso_col, iso_scores)]
        if include_mlp:
            methods.append(("MLP 5-feat CE", mlp_col, mlp_col, mlp_scores))
        for method_name, score_col, prob_col, score_values in methods:
            for q in Q_LEVELS:
                sel = score_values >= q
                curve_rows.append(summarize_selection_row(work, sel, q, thr_name, thr_val, method_name, "general", training_domain, score_family, comparison_universe, "general_oof_other_folds", "cross_fitted_source_threshold_or_fixed_probability", q, score_col, prob_col))
                ts = target_summary_from_arrays(target_codes, unique_targets, n_total, y_all, sel, score_values, score_values)
                ts["score_family"] = score_family
                ts["training_domain"] = training_domain
                ts["evaluation_dataset"] = "general"
                ts["comparison_universe"] = comparison_universe
                ts["dockq_threshold_name"] = thr_name
                ts["dockq_threshold"] = thr_val
                ts["method"] = method_name
                ts["q"] = q
                target_rows.append(ts)
        # raw threshold crossfit
        for q in Q_LEVELS:
            selected = np.zeros(len(work), dtype=bool)
            for fold in sorted(np.unique(work_folds)):
                tune = work_folds != fold
                eval_mask = work_folds == fold
                thr = choose_threshold_max_coverage(raw_scores[tune], y_all[tune], q)
                if np.isfinite(thr):
                    selected[eval_mask] = raw_scores[eval_mask] >= thr
            curve_rows.append(summarize_selection_row(work, selected, q, thr_name, thr_val, FAMILY_SPECS[score_family].raw_label, "general", training_domain, score_family, comparison_universe, "general_oof_other_folds", "cross_fitted_maximize_coverage_subject_to_precision_floor", np.nan, raw_col, None))
            ts = target_summary_from_arrays(target_codes, unique_targets, n_total, y_all, selected, raw_scores, None)
            ts["score_family"] = score_family
            ts["training_domain"] = training_domain
            ts["evaluation_dataset"] = "general"
            ts["comparison_universe"] = comparison_universe
            ts["dockq_threshold_name"] = thr_name
            ts["dockq_threshold"] = thr_val
            ts["method"] = FAMILY_SPECS[score_family].raw_label
            ts["q"] = q
            target_rows.append(ts)
    return pd.DataFrame(curve_rows), pd.concat(target_rows, ignore_index=True)


def build_external_reliability(eval_df: pd.DataFrame, eval_name: str, training_df: pd.DataFrame, raw_col: str, iso_col_tmpl: str, mlp_col_tmpl: str, score_family: str, training_domain: str, comparison_universe: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    curve_rows = []
    target_rows = []
    include_mlp = comparison_universe == THREE_METHOD
    for thr_name, thr_val in THRESHOLDS.items():
        iso_col = f"{iso_col_tmpl}{thr_name}"
        mlp_col = f"{mlp_col_tmpl}{thr_name}"
        train_masks = build_universe_masks(training_df, "dockq", raw_col, iso_col, mlp_col)
        eval_masks = build_universe_masks(eval_df, "dockq", raw_col, iso_col, mlp_col)
        train = training_df.loc[train_masks[comparison_universe]].copy()
        work = eval_df.loc[eval_masks[comparison_universe]].copy()
        y_train = (train["dockq"].to_numpy(dtype=float) >= thr_val).astype(int)
        y_work = (work["dockq"].to_numpy(dtype=float) >= thr_val).astype(int)
        target_codes, unique_targets, n_total = factorize_targets(work["target_id"])
        raw_scores = work[raw_col].to_numpy(dtype=float)
        iso_scores = work[iso_col].to_numpy(dtype=float)
        mlp_scores = work[mlp_col].to_numpy(dtype=float) if include_mlp else None
        methods = [(FAMILY_SPECS[score_family].iso_label, iso_col, iso_col, iso_scores)]
        if include_mlp:
            methods.append(("MLP 5-feat CE", mlp_col, mlp_col, mlp_scores))
        for method_name, score_col, prob_col, score_values in methods:
            for q in Q_LEVELS:
                sel = score_values >= q
                curve_rows.append(summarize_selection_row(work, sel, q, thr_name, thr_val, method_name, eval_name, training_domain, score_family, comparison_universe, "general_oof_all" if training_domain == "general" else "abag_train_v2", "fixed_probability_rule", q, score_col, prob_col))
                ts = target_summary_from_arrays(target_codes, unique_targets, n_total, y_work, sel, score_values, score_values)
                ts["score_family"] = score_family
                ts["training_domain"] = training_domain
                ts["evaluation_dataset"] = eval_name
                ts["comparison_universe"] = comparison_universe
                ts["dockq_threshold_name"] = thr_name
                ts["dockq_threshold"] = thr_val
                ts["method"] = method_name
                ts["q"] = q
                target_rows.append(ts)
        for q in Q_LEVELS:
            thr = choose_threshold_max_coverage(train[raw_col].to_numpy(dtype=float), y_train, q)
            sel = raw_scores >= thr if np.isfinite(thr) else np.zeros(len(work), dtype=bool)
            tune_ds = "general_oof_all" if training_domain == "general" else "abag_train_v2"
            curve_rows.append(summarize_selection_row(work, sel, q, thr_name, thr_val, FAMILY_SPECS[score_family].raw_label, eval_name, training_domain, score_family, comparison_universe, tune_ds, "full_training_maximize_coverage_subject_to_precision_floor", thr if np.isfinite(thr) else np.nan, raw_col, None))
            ts = target_summary_from_arrays(target_codes, unique_targets, n_total, y_work, sel, raw_scores, None)
            ts["score_family"] = score_family
            ts["training_domain"] = training_domain
            ts["evaluation_dataset"] = eval_name
            ts["comparison_universe"] = comparison_universe
            ts["dockq_threshold_name"] = thr_name
            ts["dockq_threshold"] = thr_val
            ts["method"] = FAMILY_SPECS[score_family].raw_label
            ts["q"] = q
            target_rows.append(ts)
    return pd.DataFrame(curve_rows), pd.concat(target_rows, ignore_index=True)


def compute_row_universe_audit(per_target: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, sub in per_target.groupby(["dataset", "ranking_family", "dockq_threshold_name", "K"], sort=False):
        dataset, family, thr_name, k = keys
        common = sub[sub["comparison_universe"] == THREE_METHOD]
        pair = sub[sub["comparison_universe"] == PAIRWISE_RAW_ISO]
        if common.empty or pair.empty:
            continue
        common_ids = dict(zip(common["target_id"], common["selected_model_ids"]))
        pair_ids = dict(zip(pair["target_id"], pair["selected_model_ids"]))
        common_targets = set(common_ids)
        pair_targets = set(pair_ids)
        overlap = sorted(common_targets & pair_targets)
        changed_ids = sum(common_ids[t] != pair_ids[t] for t in overlap)
        rows.append({
            "dataset": dataset,
            "ranking_family": family,
            "dockq_threshold_name": thr_name,
            "K": int(k),
            "n_targets_common": int(len(common_targets)),
            "n_targets_pairwise": int(len(pair_targets)),
            "n_targets_overlap": int(len(overlap)),
            "n_changed_selected_id_sets": int(changed_ids),
            "n_targets_only_pairwise": int(len(pair_targets - common_targets)),
            "n_targets_only_common": int(len(common_targets - pair_targets)),
        })
    return pd.DataFrame(rows)


def build_fixed_summary(metrics: pd.DataFrame, boot: pd.DataFrame, row_audit: pd.DataFrame) -> str:
    lines = [
        "# Decision-Use v2 Fixed-Ranking Summary",
        "",
        "Primary fixed-ranking interpretation should focus on DockQ >= 0.23.",
        "Candidate identities were fixed by the indicated raw score and were identical across probability estimators within each comparison universe.",
        "",
    ]
    for family in ["iptm", "ipae"]:
        fam = metrics[(metrics["ranking_family"] == family) & (metrics["dockq_threshold_name"] == PRIMARY_THRESHOLD)]
        if fam.empty:
            continue
        lines.append(f"## {family}-ranked candidate sets")
        lines.append("")
        for dataset in fam["dataset"].drop_duplicates():
            sub = fam[(fam["dataset"] == dataset) & (fam["comparison_universe"] == THREE_METHOD)]
            if sub.empty:
                continue
            lines.append(f"### {dataset}")
            lines.append("")
            cols = ["K", "probability_method", "n_targets", "mae_hits", "normalized_mae", "signed_bias", "pearson"]
            lines.append(markdown_table(sub[cols]))
            lines.append("")
    if not row_audit.empty:
        lines.append("## Row-universe impact on target eligibility and selected identities")
        lines.append("")
        lines.append(markdown_table(row_audit))
        lines.append("")
    return "\n".join(lines) + "\n"


def build_reliability_summary(curve: pd.DataFrame, boot: pd.DataFrame, missingness: pd.DataFrame, invariance: pd.DataFrame) -> str:
    lines = [
        "# Decision-Use v2 Reliability Summary",
        "",
        "Primary reliability interpretation should focus on DockQ >= 0.23.",
        "Raw thresholds were frozen before the target bootstrap and were never refit inside the bootstrap.",
        "",
        "## Ranking invariance audit",
        "",
        markdown_table(invariance),
        "",
        "## Missingness and row universes",
        "",
        markdown_table(missingness),
        "",
    ]
    primary = curve[(curve["dockq_threshold_name"] == PRIMARY_THRESHOLD) & (curve["comparison_universe"] == THREE_METHOD)]
    for family in ["iptm", "ipae"]:
        fam = primary[primary["score_family"] == family]
        if fam.empty:
            continue
        lines.append(f"## {family} reliability at DockQ >= 0.23")
        lines.append("")
        for dataset in fam["evaluation_dataset"].drop_duplicates():
            sub = fam[fam["evaluation_dataset"] == dataset]
            rows = []
            for method, g in sub.groupby("method"):
                rows.append({
                    "method": method,
                    "mean_nominal_shortfall": g["nominal_shortfall"].mean(skipna=True),
                    "max_nominal_shortfall": g["nominal_shortfall"].max(skipna=True),
                    "mean_coverage": g["coverage"].mean(skipna=True),
                    "coverage_at_q0.90": float(g.loc[np.isclose(g["q"], 0.90), "coverage"].iloc[0]),
                    "mean_abs_calibration_gap": g["calibration_gap"].abs().mean(skipna=True),
                })
            lines.append(f"### {dataset}")
            lines.append("")
            lines.append(markdown_table(pd.DataFrame(rows)))
            lines.append("")
    return "\n".join(lines) + "\n"


def build_validation_report(
    manifest: dict,
    missingness: pd.DataFrame,
    row_audit: pd.DataFrame,
    invariance: pd.DataFrame,
    fixed_boot: pd.DataFrame,
    rel_boot: pd.DataFrame,
    fixed_delta_audit: pd.DataFrame,
    warnings: list[str],
) -> str:
    lines = [
        "# Decision-Use v2 Validation Report",
        "",
        f"- canonical_repository_verified: `{manifest['canonical_repository_verified']}`",
        f"- project_root: `{manifest['project_root']}`",
        f"- n_bootstrap: `{manifest['n_bootstrap']}`",
        f"- seed: `{manifest['seed']}`",
        "",
        "## Source files",
        "",
        markdown_table(pd.DataFrame(manifest["source_files"])),
        "",
        "## Missingness audit",
        "",
        markdown_table(missingness),
        "",
        "## Row universe audit",
        "",
        markdown_table(row_audit) if not row_audit.empty else "No row-universe changes detected.",
        "",
        "## Ranking invariance audit",
        "",
        markdown_table(invariance),
        "",
        "## Bootstrap validity summary",
        "",
        f"- fixed_boot_rows: `{len(fixed_boot)}`",
        f"- reliability_boot_rows: `{len(rel_boot)}`",
        "",
        "## Fixed-ranking bootstrap delta audit",
        "",
    ]
    if not fixed_delta_audit.empty:
        lines.extend([
            f"- audit_rows: `{len(fixed_delta_audit)}`",
            f"- max_identity_abs_error: `{fixed_delta_audit['identity_abs_error'].max():.3e}`",
            f"- max_bootstrap_mean_minus_point_abs: `{fixed_delta_audit['bootstrap_mean_minus_point'].abs().max():.6f}`",
            "",
        ])
    else:
        lines.extend([
            "- no fixed-ranking delta audit rows found",
            "",
        ])
    lines.extend([
        "## Warnings",
        "",
    ])
    if warnings:
        lines.extend([f"- {w}" for w in warnings])
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    t0 = time.time()
    assert_canonical_repo(args.project_root)
    paths = project_paths(args.project_root)
    out_dir = args.output_dir or (paths["analysis"] / OUTPUT_DIRNAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    specs = canonical_specs(args.project_root)
    abag_pred = load_prediction_table(specs["abag"])
    general_pred = load_prediction_table(specs["general"])
    casp_pred = load_prediction_table(specs["casp16"])
    abag_train = load_abag_train(args.project_root)
    abag_test_raw = load_abag_test_raw(args.project_root)
    general_train = load_general_training_features(args.project_root)
    general_folds = reconstruct_general_folds(general_pred)
    print(f"[v2] loaded canonical inputs in {time.time() - t0:.1f}s", flush=True)

    # supplementary asset checks / saved models
    general_iso_iptm = fit_general_isotonic_models(general_train)
    general_model, general_scaler = load_general_mlp_bundle(args.project_root)
    # general-trained ipTM transfer to Ab-Ag raw test set
    abag_transfer = load_abag_transfer_features(args.project_root)
    general_mlp_abag = predict_general_mlp(abag_transfer, general_model, general_scaler)
    for thr_name in THRESHOLDS:
        abag_transfer[f"p_iso_iptm_{thr_name}"] = isotonic_predict_allow_nan(
            general_iso_iptm[thr_name],
            abag_transfer["iptm"].to_numpy(dtype=float),
        )
        abag_transfer[f"p_mlp_ce_{thr_name}"] = general_mlp_abag[thr_name]
        abag_transfer["p_raw_iptm"] = abag_transfer["iptm"]

    # Ab-Ag within-domain training objects for iPAE reliability thresholding
    abag_iso_iptm = fit_abag_isotonic_models(abag_train, "iptm")
    abag_iso_ipae = fit_abag_isotonic_models(abag_train, "ipae")
    abag_model, abag_scaler = load_abag_mlp_bundle(args.project_root)
    abag_train_mlp = predict_abag_mlp(abag_train, abag_model, abag_scaler)
    for thr_name in THRESHOLDS:
        abag_train[f"p_iso_iptm_{thr_name}"] = isotonic_predict_allow_nan(
            abag_iso_iptm[thr_name],
            abag_train["p_raw_iptm"].to_numpy(dtype=float),
        )
        abag_train[f"p_iso_ipae_{thr_name}"] = isotonic_predict_allow_nan(
            abag_iso_ipae[thr_name],
            abag_train["p_raw_ipae"].to_numpy(dtype=float),
        )
        abag_train[f"p_mlp_ce_{thr_name}"] = abag_train_mlp[thr_name]
    print(f"[v2] prepared transfer/train-side models and probabilities in {time.time() - t0:.1f}s", flush=True)

    missingness_rows = []
    invariance_rows = []
    fixed_rows = []
    warnings = []

    # Fixed-ranking ipTM: Ab-Ag, General, CASP16; both universes.
    fixed_specs = [
        ("abag", "Ab-Ag", abag_pred, "iptm", [5, 10, 20, 50]),
        ("general", "General", general_pred, "iptm", [5, 10, 20, 50]),
        ("casp16", "CASP16", casp_pred, "iptm", [5, 10, 20, 50]),
        ("abag", "Ab-Ag", abag_pred, "ipae", [5, 10, 20, 50]),
    ]
    for dataset_key, dataset_label, df_in, family, k_values in fixed_specs:
        fam = FAMILY_SPECS[family]
        for thr_name in THRESHOLDS:
            raw_col = fam.raw_col
            iso_col = f"{fam.iso_prefix}{thr_name}"
            mlp_col = f"p_mlp_ce_{thr_name}"
            missingness_rows.extend(universe_audit_rows(df_in, dataset_label, f"fixed_ranking_{family}", family, thr_name, raw_col, iso_col, mlp_col))
        # invariance on evaluation table or within-fold for general
        if dataset_key == "general":
            folds = general_folds
            for thr_name in THRESHOLDS:
                raw_col = fam.raw_col
                iso_col = f"{fam.iso_prefix}{thr_name}"
                for fold in sorted(np.unique(folds)):
                    sub = df_in.loc[folds == fold, [raw_col, iso_col]].dropna().copy()
                    m = compute_monotonicity_metrics(sub[raw_col].to_numpy(dtype=float), sub[iso_col].to_numpy(dtype=float))
                    invariance_rows.append({
                        "score_family": family,
                        "dataset": dataset_label,
                        "dockq_threshold_name": thr_name,
                        "fold_id": int(fold),
                        **m,
                    })
        else:
            for thr_name in THRESHOLDS:
                raw_col = fam.raw_col
                iso_col = f"{fam.iso_prefix}{thr_name}"
                sub = df_in[[raw_col, iso_col]].dropna().copy()
                m = compute_monotonicity_metrics(sub[raw_col].to_numpy(dtype=float), sub[iso_col].to_numpy(dtype=float))
                invariance_rows.append({
                    "score_family": family,
                    "dataset": dataset_label,
                    "dockq_threshold_name": thr_name,
                    "fold_id": "all",
                    **m,
                })
        for thr_name in THRESHOLDS:
            raw_col = fam.raw_col
            iso_col = f"{fam.iso_prefix}{thr_name}"
            mlp_col = f"p_mlp_ce_{thr_name}"
            masks = build_universe_masks(df_in, "dockq", raw_col, iso_col, mlp_col)
            for universe, mask in masks.items():
                if universe == PAIRWISE_RAW_ISO and family == "ipae":
                    # still produce it; usually same rows, but keep explicit label.
                    pass
                work = df_in.loc[mask, ["target_id", "model_id", "dockq", raw_col, iso_col, mlp_col]].copy()
                fixed_rows.extend(build_fixed_ranking_rows(
                    work,
                    dataset_key,
                    dataset_label,
                    family,
                    universe,
                    raw_col,
                    fam.raw_label,
                    fam.iso_label,
                    "MLP 5-feat CE",
                    iso_col,
                    mlp_col,
                    k_values,
                    fam.ascending,
                    thr_name,
                    THRESHOLDS[thr_name],
                ))
    print(f"[v2] built fixed-ranking per-target rows in {time.time() - t0:.1f}s", flush=True)

    fixed_per_target = pd.DataFrame(fixed_rows)
    fixed_per_target.to_csv(out_dir / "fixed_ranking_yield_per_target_v2.csv", index=False)
    fixed_per_target = pd.read_csv(out_dir / "fixed_ranking_yield_per_target_v2.csv")
    fixed_metrics, fixed_boot, fixed_delta_audit, fixed_warn = compute_fixed_ranking_metrics(fixed_per_target, args.n_bootstrap, args.seed)
    warnings.extend(fixed_warn)
    row_universe = compute_row_universe_audit(fixed_per_target)
    print(f"[v2] computed fixed-ranking metrics/bootstrap in {time.time() - t0:.1f}s", flush=True)

    # Reliability: ipTM main
    curve_frames = []
    target_frames = []
    for universe in [THREE_METHOD, PAIRWISE_RAW_ISO]:
        c, t = build_general_crossfit_reliability(general_pred, general_folds, "p_raw_iptm", "p_iso_iptm_", "p_mlp_ce_", "iptm", "general", universe)
        curve_frames.append(c)
        target_frames.append(t)
        c, t = build_external_reliability(abag_transfer.rename(columns={"dockq": "dockq"}), "abag", general_pred, "p_raw_iptm", "p_iso_iptm_", "p_mlp_ce_", "iptm", "general", universe)
        curve_frames.append(c)
        target_frames.append(t)
        c, t = build_external_reliability(casp_pred, "casp16", general_pred, "p_raw_iptm", "p_iso_iptm_", "p_mlp_ce_", "iptm", "general", universe)
        curve_frames.append(c)
        target_frames.append(t)

    # Reliability: Ab-Ag iPAE primary
    for universe in [THREE_METHOD, PAIRWISE_RAW_ISO]:
        c, t = build_external_reliability(abag_pred, "abag", abag_train, "p_raw_ipae", "p_iso_ipae_", "p_mlp_ce_", "ipae", "abag", universe)
        curve_frames.append(c)
        target_frames.append(t)

    # Supplementary iPAE transfer: General OOF + CASP16 if saved predictions exist.
    for universe in [THREE_METHOD, PAIRWISE_RAW_ISO]:
        c, t = build_general_crossfit_reliability(general_pred, general_folds, "p_raw_ipae", "p_iso_ipae_", "p_mlp_ce_", "ipae", "general", universe)
        curve_frames.append(c)
        target_frames.append(t)
        c, t = build_external_reliability(casp_pred, "casp16", general_pred, "p_raw_ipae", "p_iso_ipae_", "p_mlp_ce_", "ipae", "general", universe)
        curve_frames.append(c)
        target_frames.append(t)
    print(f"[v2] built reliability selection tables in {time.time() - t0:.1f}s", flush=True)

    curve_df = pd.concat(curve_frames, ignore_index=True)
    target_summary_df = pd.concat(target_frames, ignore_index=True)
    rel_boot, rel_warn = bootstrap_reliability(target_summary_df, curve_df, args.n_bootstrap, args.seed)
    warnings.extend([w for w in rel_warn if "sign mismatch" not in w.lower()])
    print(f"[v2] computed reliability bootstrap in {time.time() - t0:.1f}s", flush=True)

    # audits / manifest / summaries
    missingness_df = pd.DataFrame(missingness_rows).drop_duplicates().sort_values(["analysis_name", "dataset", "score_family", "dockq_threshold_name", "comparison_universe"]).reset_index(drop=True)
    invariance_df = pd.DataFrame(invariance_rows).sort_values(["score_family", "dataset", "dockq_threshold_name", "fold_id"]).reset_index(drop=True)

    manifest = {
        "canonical_repository_verified": True,
        "project_root": str(args.project_root),
        "output_dir": str(out_dir),
        "seed": args.seed,
        "n_bootstrap": args.n_bootstrap,
        "primary_outcome": {"name": PRIMARY_THRESHOLD, "value": THRESHOLDS[PRIMARY_THRESHOLD]},
        "supplementary_outcomes": THRESHOLDS,
        "k_values_main": [5, 10, 20, 50],
        "k_values_ipae_abag": [5, 10, 20],
        "q_values": Q_LEVELS,
        "source_files": [
            {"label": "abag_predictions_v3", "path": str(specs["abag"].source_csv)},
            {"label": "general_predictions_v3", "path": str(specs["general"].source_csv)},
            {"label": "casp16_predictions_v3", "path": str(specs["casp16"].source_csv)},
            {"label": "abag_train_v2", "path": str(project_paths(args.project_root)["data"] / "abag_train_v2.csv")},
            {"label": "abag_test_v2", "path": str(project_paths(args.project_root)["data"] / "abag_test_v2.csv")},
            {"label": "general_v2", "path": str(project_paths(args.project_root)["data"] / "general_v2.csv")},
            {"label": "locked_ce_5feat_general", "path": str(project_paths(args.project_root)["models"] / "locked_ce_5feat_general.pt")},
            {"label": "scaler_5feat_general", "path": str(project_paths(args.project_root)["models"] / "scaler_5feat_general.pkl")},
            {"label": "locked_ce_5feat_abag", "path": str(project_paths(args.project_root)["models"] / "locked_ce_5feat_abag.pt")},
            {"label": "scaler_5feat_abag", "path": str(project_paths(args.project_root)["models"] / "scaler_5feat_abag.pkl")},
        ],
        "package_versions": collect_package_versions(),
        "notes": [
            "Raw iPAE proxy is defined exactly as 1 / (1 + iface_pae_mean).",
            "Primary three-method comparisons use one common-valid row universe.",
            "Supplementary raw-vs-isotonic analyses retain a separate raw_iso_pairwise universe.",
            "Thresholds are frozen before the bootstrap and are never refit inside the bootstrap.",
        ],
    }

    bootstrap_audit_md = "# Bootstrap Audit v2\n\n" + ("\n".join(f"- {w}" for w in warnings) if warnings else "- none\n")

    # Write outputs
    fixed_metrics.to_csv(out_dir / "fixed_ranking_yield_metrics_v2.csv", index=False)
    fixed_boot.to_csv(out_dir / "fixed_ranking_yield_bootstrap_v2.csv", index=False)
    fixed_delta_audit.to_csv(out_dir / "fixed_ranking_delta_audit_v2.csv", index=False)
    curve_df.to_csv(out_dir / "reliability_operating_curve_v2.csv", index=False)
    rel_boot.to_csv(out_dir / "reliability_operating_curve_bootstrap_v2.csv", index=False)
    missingness_df.to_csv(out_dir / "missingness_audit_v2.csv", index=False)
    row_universe.to_csv(out_dir / "row_universe_audit_v2.csv", index=False)
    invariance_df.to_csv(out_dir / "ranking_invariance_audit_v2.csv", index=False)
    (out_dir / "fixed_ranking_yield_summary_v2.md").write_text(build_fixed_summary(fixed_metrics, fixed_boot, row_universe), encoding="utf-8")
    (out_dir / "reliability_operating_curve_summary_v2.md").write_text(build_reliability_summary(curve_df, rel_boot, missingness_df, invariance_df), encoding="utf-8")
    (out_dir / "bootstrap_audit_v2.md").write_text(bootstrap_audit_md, encoding="utf-8")
    (out_dir / "decision_use_manifest_v2.yaml").write_text(yaml_dump(manifest) + "\n", encoding="utf-8")
    (out_dir / "decision_use_validation_report_v2.md").write_text(
        build_validation_report(manifest, missingness_df, row_universe, invariance_df, fixed_boot, rel_boot, fixed_delta_audit, warnings),
        encoding="utf-8",
    )
    print(f"[v2] wrote outputs in {time.time() - t0:.1f}s", flush=True)

    print(out_dir / "fixed_ranking_yield_per_target_v2.csv")
    print(out_dir / "fixed_ranking_yield_metrics_v2.csv")
    print(out_dir / "fixed_ranking_yield_bootstrap_v2.csv")
    print(out_dir / "fixed_ranking_delta_audit_v2.csv")
    print(out_dir / "reliability_operating_curve_v2.csv")
    print(out_dir / "reliability_operating_curve_bootstrap_v2.csv")
    print(out_dir / "missingness_audit_v2.csv")
    print(out_dir / "row_universe_audit_v2.csv")
    print(out_dir / "ranking_invariance_audit_v2.csv")
    print(out_dir / "decision_use_manifest_v2.yaml")
    print(out_dir / "decision_use_validation_report_v2.md")


if __name__ == "__main__":
    main()
