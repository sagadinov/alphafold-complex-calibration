#!/usr/bin/env python3
"""Measure how many AFDB examples isotonic calibration needs.

This is an exploratory, within-AFDB learning curve on the 304 complexes with
finite native DockQ.  For each event and training-set size, a stratified set
is sampled, an isotonic calibrator is fit only on that set, and Brier/ECE are
evaluated on its held-out complement.  Repeats overlap, so their standard
deviations describe split sensitivity rather than independent test sets.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss
from sklearn.model_selection import StratifiedShuffleSplit

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "analysis" / "afdb" / "afdb_positive_dockq_features.csv"
OUTPUT = ROOT / "analysis" / "afdb" / "afdb_dockq304_calibration_learning_curve.csv"
FIGURE_PDF = ROOT / "paper" / "supplementary" / "figures" / "afdb_calibration_learning_curve.pdf"
FIGURE_PNG = ROOT / "paper" / "supplementary" / "figures" / "afdb_calibration_learning_curve.png"

THRESHOLDS = [("acceptable", 0.23), ("medium", 0.49), ("high", 0.80)]
SCORES = {"ipTM": "iptm", "ipSAEmax": "ipsae_max"}
TRAIN_SIZES = [5, 10, 20, 50, 100]
TRAIN_PERCENTAGES = [1, 5, 10, 20, 50]
N_REPEATS = 100
SEED = 42


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


def summarise(values: list[float]) -> tuple[float, float]:
    return float(np.mean(values)), float(np.std(values, ddof=1))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AFDB isotonic-calibration learning curves")
    parser.add_argument(
        "--percentages", action="store_true",
        help="Use 1, 5, 10, 20, and 50 percent of AFDB instead of fixed counts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = pd.read_csv(INPUT, low_memory=False)
    df["dockq_native"] = pd.to_numeric(df["dockq_native"], errors="coerce")
    df = df.loc[np.isfinite(df["dockq_native"])].copy()
    if len(df) != 304:
        raise RuntimeError(f"Expected 304 finite-DockQ entries, found {len(df)}")
    for column in SCORES.values():
        df[column] = pd.to_numeric(df[column], errors="coerce")
        if not np.isfinite(df[column]).all():
            raise RuntimeError(f"{column} is missing on finite-DockQ entries")

    if args.percentages:
        train_schedule = [(percentage, max(2, round(len(df) * percentage / 100))) for percentage in TRAIN_PERCENTAGES]
        output = ROOT / "analysis" / "afdb" / "afdb_dockq304_calibration_learning_curve_percent.csv"
        figure_pdf = ROOT / "paper" / "supplementary" / "figures" / "afdb_calibration_learning_curve_percent.pdf"
        figure_png = ROOT / "paper" / "supplementary" / "figures" / "afdb_calibration_learning_curve_percent.png"
        x_label = "AFDB calibration set (%)"
    else:
        train_schedule = [(size, size) for size in TRAIN_SIZES]
        output, figure_pdf, figure_png = OUTPUT, FIGURE_PDF, FIGURE_PNG
        x_label = "AFDB calibration examples"

    rows: list[dict[str, object]] = []
    for threshold_index, (threshold_name, threshold_value) in enumerate(THRESHOLDS):
        y = (df["dockq_native"].to_numpy() >= threshold_value).astype(int)
        for score_index, (score_name, column) in enumerate(SCORES.items()):
            score = df[column].to_numpy(dtype=float)
            raw_brier = float(brier_score_loss(y, np.clip(score, 0.0, 1.0)))
            raw_ece = compute_ece(y, score)
            for schedule_value, train_size in train_schedule:
                splitter = StratifiedShuffleSplit(
                    n_splits=N_REPEATS,
                    train_size=train_size,
                    random_state=SEED + 1000 * threshold_index + 100 * score_index + train_size,
                )
                briers: list[float] = []
                eces: list[float] = []
                positive_counts: list[int] = []
                for train_idx, holdout_idx in splitter.split(score, y):
                    calibrator = IsotonicRegression(out_of_bounds="clip")
                    calibrator.fit(score[train_idx], y[train_idx])
                    probability = calibrator.predict(score[holdout_idx])
                    briers.append(float(brier_score_loss(y[holdout_idx], probability)))
                    eces.append(compute_ece(y[holdout_idx], probability))
                    positive_counts.append(int(y[train_idx].sum()))
                brier_mean, brier_std = summarise(briers)
                ece_mean, ece_std = summarise(eces)
                rows.append({
                    "threshold": threshold_name,
                    "threshold_val": threshold_value,
                    "score": score_name,
                    "schedule_value": schedule_value,
                    "schedule_unit": "percent" if args.percentages else "examples",
                    "train_size": train_size,
                    "n_repeats": N_REPEATS,
                    "n_total": len(y),
                    "n_pos_total": int(y.sum()),
                    "n_neg_total": int((1 - y).sum()),
                    "train_pos_mean": float(np.mean(positive_counts)),
                    "train_pos_min": int(np.min(positive_counts)),
                    "train_pos_max": int(np.max(positive_counts)),
                    "holdout_size": len(y) - train_size,
                    "brier_mean": brier_mean,
                    "brier_std": brier_std,
                    "ece_mean": ece_mean,
                    "ece_std": ece_std,
                    "raw_brier_full": raw_brier,
                    "raw_ece_full": raw_ece,
                })

    result = pd.DataFrame(rows)
    result.to_csv(output, index=False)
    render_figure(result, figure_pdf, figure_png, x_label)
    print(result.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print(f"Wrote {output}")
    print(f"Wrote {figure_pdf}")
    print(f"Wrote {figure_png}")


def render_figure(result: pd.DataFrame, figure_pdf: Path, figure_png: Path, x_label: str) -> None:
    plt.rcParams.update({"font.size": 10, "axes.labelsize": 10, "axes.titlesize": 11, "legend.fontsize": 9})
    fig, axes = plt.subplots(2, 3, figsize=(11.5, 6.3), sharex=True)
    colors = {"ipTM": "#2563EB", "ipSAEmax": "#059669"}
    for column, (threshold_name, threshold_value) in enumerate(THRESHOLDS):
        subset = result.loc[result["threshold"] == threshold_name]
        for row, (metric, label) in enumerate((("brier", "Brier score"), ("ece", "ECE (10 bins)"))):
            ax = axes[row, column]
            for score_name, color in colors.items():
                values = subset.loc[subset["score"] == score_name].sort_values("train_size")
                ax.errorbar(
                    values["schedule_value"], values[f"{metric}_mean"],
                    yerr=values[f"{metric}_std"], color=color, marker="o", linewidth=2,
                    capsize=3, label=f"Isotonic {score_name}",
                )
                raw_value = float(values[f"raw_{metric}_full"].iloc[0])
                ax.axhline(raw_value, color=color, linestyle="--", linewidth=1.2, alpha=0.75,
                           label=f"Raw {score_name}")
            ax.set_title(f"DockQ >= {threshold_value}")
            if result["schedule_unit"].iloc[0] == "examples":
                ax.set_xscale("log", base=2)
            schedule_values = sorted(result["schedule_value"].unique())
            ax.set_xticks(schedule_values)
            ax.set_xticklabels([str(value) for value in schedule_values])
            ax.grid(axis="y", alpha=0.2)
            if column == 0:
                ax.set_ylabel(label)
            if row == 1:
                ax.set_xlabel(x_label)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    fig.legend(unique.values(), unique.keys(), loc="upper center", ncol=4, frameon=False,
               bbox_to_anchor=(0.5, 1.01))
    fig.text(0.5, 0.0,
             "Mean +/- SD across 100 stratified calibration/holdout splits of the same 304 finite-DockQ AFDB complexes.",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    figure_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_pdf, bbox_inches="tight")
    fig.savefig(figure_png, dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    main()
