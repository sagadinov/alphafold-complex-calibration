#!/usr/bin/env python3
"""Target-grouped Ab-Ag recalibration learning curves for ipTM and true ipSAE."""

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss
from sklearn.model_selection import StratifiedShuffleSplit

from common import ANALYSIS, DATA, PDF_METADATA, THRESHOLDS, write_text


ABAG_INPUT = DATA / "abag_predictions_v3.csv"
GENERAL_INPUT = DATA / "general_predictions_v3.csv"
# This full-matrix score is supplied at execution time because the source AF3
# outputs and their per-model ipSAE table cannot be redistributed in this repo.
IPSAE_INPUT = Path(os.environ["ABAG_IPSAE_INPUT"]) if "ABAG_IPSAE_INPUT" in os.environ else None
OUTPUT = ANALYSIS / "workshop" / "workshop_abag_recalibration_source.csv"
REPEATS = ANALYSIS / "workshop" / "workshop_abag_recalibration_repeats.csv"
MODEL_OUTPUT = ANALYSIS / "workshop" / "workshop_abag_recalibration_model_random_source.csv"
MODEL_REPEATS = ANALYSIS / "workshop" / "workshop_abag_recalibration_model_random_repeats.csv"
SUMMARY = ANALYSIS / "workshop" / "workshop_abag_recalibration_summary.md"
FIGURE_DIR = ANALYSIS / "workshop" / "figure_candidates"
TRAIN_PERCENTS = (1, 5, 10, 20, 30, 50)
N_REPEATS = 100
SEED = 42

STYLES = {
    "Raw ipTM": {"color": "#374151", "linestyle": "--"},
    "Isotonic ipTM (General)": {"color": "#FA8072", "linestyle": "--"},
    "Isotonic ipTM (Ab-Ag)": {"color": "#2563EB", "linestyle": "-", "marker": "o"},
    "Raw ipSAEmax": {"color": "#6EE7B7", "linestyle": "--"},
    "Isotonic ipSAEmax (Ab-Ag)": {"color": "#059669", "linestyle": "-", "marker": "o"},
}


def ece(y_true: np.ndarray, probability: np.ndarray, n_bins: int = 10) -> float:
    probability = np.clip(np.asarray(probability, dtype=float), 0.0, 1.0)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    result = 0.0
    for index in range(n_bins):
        upper_inclusive = index == n_bins - 1
        mask = (probability >= edges[index]) & ((probability <= edges[index + 1]) if upper_inclusive else (probability < edges[index + 1]))
        if mask.any():
            result += float(mask.mean()) * abs(float(probability[mask].mean()) - float(y_true[mask].mean()))
    return float(result)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    required = ["target_id", "model_id", "dockq", "iptm"]
    abag = pd.read_csv(ABAG_INPUT, usecols=required)
    general = pd.read_csv(GENERAL_INPUT, usecols=["dockq", "iptm"])
    for frame, name, expected, numeric_cols in [
        (abag, "Ab-Ag", 62681, ["dockq", "iptm"]),
        (general, "General", 5496, ["dockq", "iptm"]),
    ]:
        for column in numeric_cols:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame.dropna(subset=numeric_cols, inplace=True)
        if len(frame) != expected:
            raise RuntimeError(f"Expected {expected:,} finite {name} rows, found {len(frame):,}")
    if IPSAE_INPUT is None or not IPSAE_INPUT.exists():
        raise FileNotFoundError(
            "True ipSAE source is required. Set ABAG_IPSAE_INPUT to the per-model ipSAE CSV."
        )
    ipsae = pd.read_csv(IPSAE_INPUT, usecols=["target_id", "model_id", "ipsae_model_max"])
    ipsae["ipsae_model_max"] = pd.to_numeric(ipsae["ipsae_model_max"], errors="coerce")
    abag = abag.merge(ipsae, on=["target_id", "model_id"], how="left", validate="one_to_one")
    if abag["ipsae_model_max"].isna().any():
        raise RuntimeError(f"Missing true ipSAEmax for {abag['ipsae_model_max'].isna().sum():,} locked Ab-Ag rows")
    if abag["target_id"].nunique() != 1257:
        raise RuntimeError("Expected 1,257 Ab-Ag targets")
    return abag, general


def compute() -> pd.DataFrame:
    abag, general = load_data()
    target_codes, target_ids = pd.factorize(abag["target_id"], sort=True)
    n_targets = len(target_ids)
    train_sizes = {percent: max(2, round(percent / 100.0 * n_targets)) for percent in TRAIN_PERCENTS}
    iptm = abag["iptm"].to_numpy(float)
    ipsae = abag["ipsae_model_max"].to_numpy(float)
    dockq = abag["dockq"].to_numpy(float)
    general_iptm = general["iptm"].to_numpy(float)
    general_dockq = general["dockq"].to_numpy(float)
    target_mean_dockq = abag.groupby("target_id", sort=True)["dockq"].mean().reindex(target_ids).to_numpy(float)
    rows: list[dict[str, object]] = []
    repeat_rows: list[dict[str, object]] = []

    for threshold_index, (threshold_name, threshold_value) in enumerate(THRESHOLDS):
        y = (dockq >= threshold_value).astype(int)
        y_general = (general_dockq >= threshold_value).astype(int)
        target_stratum = (target_mean_dockq >= threshold_value).astype(int)
        general_iso_iptm = IsotonicRegression(out_of_bounds="clip").fit(general_iptm, y_general)

        fixed = {
            "Raw ipTM": iptm,
            "Isotonic ipTM (General)": general_iso_iptm.predict(iptm),
            "Raw ipSAEmax": ipsae,
        }
        for method, probability in fixed.items():
            metrics = {"brier": brier_score_loss(y, probability), "ece": ece(y, probability)}
            for percent, train_size in train_sizes.items():
                for metric, value in metrics.items():
                    rows.append(
                        {
                            "threshold": threshold_name,
                            "threshold_val": threshold_value,
                            "train_percent": percent,
                            "train_targets": train_size,
                            "n_repeats": 1,
                            "method": method,
                            "metric": metric,
                            "mean": float(value),
                            "std": 0.0,
                            "holdout_targets": n_targets,
                            "protocol": "fixed full Ab-Ag evaluation; no Ab-Ag labels used for fitting",
                        }
                    )

        for percent, train_size in train_sizes.items():
            splitter = StratifiedShuffleSplit(
                n_splits=N_REPEATS,
                train_size=train_size,
                random_state=SEED + 1000 * threshold_index + train_size,
            )
            values = {
                "Isotonic ipTM (Ab-Ag)": {"brier": [], "ece": []},
                "Isotonic ipSAEmax (Ab-Ag)": {"brier": [], "ece": []},
            }
            holdout_target_counts: list[int] = []
            for repeat, (train_target_idx, holdout_target_idx) in enumerate(splitter.split(np.zeros(n_targets), target_stratum)):
                train_mask = np.isin(target_codes, train_target_idx)
                holdout_mask = np.isin(target_codes, holdout_target_idx)
                if np.any(train_mask & holdout_mask):
                    raise RuntimeError("Target-grouped train and holdout rows overlap")
                holdout_target_counts.append(len(holdout_target_idx))
                local_iptm = IsotonicRegression(out_of_bounds="clip").fit(iptm[train_mask], y[train_mask])
                local_ipsae = IsotonicRegression(out_of_bounds="clip").fit(ipsae[train_mask], y[train_mask])
                predictions = {
                    "Isotonic ipTM (Ab-Ag)": local_iptm.predict(iptm[holdout_mask]),
                    "Isotonic ipSAEmax (Ab-Ag)": local_ipsae.predict(ipsae[holdout_mask]),
                }
                for method, probability in predictions.items():
                    for metric, value in {
                        "brier": brier_score_loss(y[holdout_mask], probability),
                        "ece": ece(y[holdout_mask], probability),
                    }.items():
                        values[method][metric].append(float(value))
                        repeat_rows.append(
                            {
                                "threshold": threshold_name,
                                "threshold_val": threshold_value,
                                "train_percent": percent,
                                "train_targets": train_size,
                                "repeat": repeat,
                                "method": method,
                                "metric": metric,
                                "value": float(value),
                                "holdout_targets": len(holdout_target_idx),
                                "holdout_models": int(holdout_mask.sum()),
                                "protocol": "paired target-grouped StratifiedShuffleSplit",
                            }
                        )
            for method, metric_values in values.items():
                for metric, observations in metric_values.items():
                    rows.append(
                        {
                            "threshold": threshold_name,
                            "threshold_val": threshold_value,
                            "train_percent": percent,
                            "train_targets": train_size,
                            "n_repeats": N_REPEATS,
                            "method": method,
                            "metric": metric,
                            "mean": float(np.mean(observations)),
                            "std": float(np.std(observations, ddof=1)),
                            "holdout_targets": int(np.mean(holdout_target_counts)),
                            "protocol": "paired target-grouped StratifiedShuffleSplit",
                        }
                    )

    result = pd.DataFrame(rows)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)
    pd.DataFrame(repeat_rows).to_csv(REPEATS, index=False)
    summary = [
        "# Ab-Ag Recalibration Learning Curve",
        "",
        "- Evaluation: target-held-out Ab-Ag test models (62,681 rows, 1,257 targets).",
        "- Local calibrators: paired target-grouped stratified splits, 100 repeats per setting.",
        "- Target-grouped training fractions: 1%, 5%, 10%, 20%, 30%, and 50% of targets (13, 63, 126, 251, 377, and 628 targets).",
        "- Raw scores and General-frozen mappings are each evaluated once on the complete Ab-Ag test universe.",
        "- True ipSAEmax is merged one-to-one from the completed IPSAE Ab-Ag test computation; it is not the inverse-iPAE proxy.",
        "- A separate model-random control is reported in workshop_abag_recalibration_model_random_*.csv; it permits target overlap and is not a complex-held-out estimate.",
    ]
    write_text(SUMMARY, "\n".join(summary) + "\n")
    return result


def compute_model_random() -> pd.DataFrame:
    """Sample individual models, allowing target overlap with the held-out rows."""
    abag, general = load_data()
    train_sizes = {percent: max(2, round(percent / 100.0 * len(abag))) for percent in TRAIN_PERCENTS}
    iptm = abag["iptm"].to_numpy(float)
    ipsae = abag["ipsae_model_max"].to_numpy(float)
    dockq = abag["dockq"].to_numpy(float)
    general_iptm = general["iptm"].to_numpy(float)
    general_dockq = general["dockq"].to_numpy(float)
    rows: list[dict[str, object]] = []
    repeat_rows: list[dict[str, object]] = []

    for threshold_index, (threshold_name, threshold_value) in enumerate(THRESHOLDS):
        y = (dockq >= threshold_value).astype(int)
        y_general = (general_dockq >= threshold_value).astype(int)
        general_iso_iptm = IsotonicRegression(out_of_bounds="clip").fit(general_iptm, y_general)
        fixed = {
            "Raw ipTM": iptm,
            "Isotonic ipTM (General)": general_iso_iptm.predict(iptm),
            "Raw ipSAEmax": ipsae,
        }
        for method, probability in fixed.items():
            metrics = {"brier": brier_score_loss(y, probability), "ece": ece(y, probability)}
            for percent, train_size in train_sizes.items():
                for metric, value in metrics.items():
                    rows.append({
                        "threshold": threshold_name, "threshold_val": threshold_value,
                        "train_percent": percent, "train_models": train_size, "n_repeats": 1,
                        "method": method, "metric": metric, "mean": float(value), "std": 0.0,
                        "holdout_models": len(abag), "protocol": "fixed full Ab-Ag evaluation; no Ab-Ag labels used for fitting",
                    })

        for percent, train_size in train_sizes.items():
            splitter = StratifiedShuffleSplit(
                n_splits=N_REPEATS, train_size=train_size,
                random_state=SEED + 10_000 + 1000 * threshold_index + train_size,
            )
            values = {
                "Isotonic ipTM (Ab-Ag)": {"brier": [], "ece": []},
                "Isotonic ipSAEmax (Ab-Ag)": {"brier": [], "ece": []},
            }
            for repeat, (train_idx, holdout_idx) in enumerate(splitter.split(np.zeros(len(abag)), y)):
                local_iptm = IsotonicRegression(out_of_bounds="clip").fit(iptm[train_idx], y[train_idx])
                local_ipsae = IsotonicRegression(out_of_bounds="clip").fit(ipsae[train_idx], y[train_idx])
                predictions = {
                    "Isotonic ipTM (Ab-Ag)": local_iptm.predict(iptm[holdout_idx]),
                    "Isotonic ipSAEmax (Ab-Ag)": local_ipsae.predict(ipsae[holdout_idx]),
                }
                for method, probability in predictions.items():
                    for metric, value in {"brier": brier_score_loss(y[holdout_idx], probability), "ece": ece(y[holdout_idx], probability)}.items():
                        values[method][metric].append(float(value))
                        repeat_rows.append({
                            "threshold": threshold_name, "threshold_val": threshold_value,
                            "train_percent": percent, "train_models": train_size, "repeat": repeat,
                            "method": method, "metric": metric, "value": float(value),
                            "holdout_models": len(holdout_idx),
                            "protocol": "paired model-random StratifiedShuffleSplit; targets may overlap",
                        })
            for method, metric_values in values.items():
                for metric, observations in metric_values.items():
                    rows.append({
                        "threshold": threshold_name, "threshold_val": threshold_value,
                        "train_percent": percent, "train_models": train_size, "n_repeats": N_REPEATS,
                        "method": method, "metric": metric, "mean": float(np.mean(observations)),
                        "std": float(np.std(observations, ddof=1)), "holdout_models": len(abag) - train_size,
                        "protocol": "paired model-random StratifiedShuffleSplit; targets may overlap",
                    })

    result = pd.DataFrame(rows)
    result.to_csv(MODEL_OUTPUT, index=False)
    pd.DataFrame(repeat_rows).to_csv(MODEL_REPEATS, index=False)
    return result


def render(source: pd.DataFrame, output_name: str, x_label: str) -> None:
    plt.rcParams.update({"font.size": 17, "axes.labelsize": 18, "axes.titlesize": 19, "legend.fontsize": 17, "xtick.labelsize": 16, "ytick.labelsize": 16})
    fig, axes = plt.subplots(2, 3, figsize=(14.8, 8.4), sharex=True)
    fixed = ["Raw ipTM", "Isotonic ipTM (General)", "Raw ipSAEmax"]
    local = ["Isotonic ipTM (Ab-Ag)", "Isotonic ipSAEmax (Ab-Ag)"]
    for column, (threshold_name, threshold_value) in enumerate(THRESHOLDS):
        for row, metric in enumerate(["brier", "ece"]):
            axis = axes[row, column]
            panel = source.loc[(source["threshold"] == threshold_name) & (source["metric"] == metric)]
            for method in fixed:
                line = panel.loc[panel["method"] == method].sort_values("train_percent")
                if not line.empty:
                    axis.axhline(line["mean"].iloc[0], color=STYLES[method]["color"], linestyle="--", linewidth=2.5, alpha=0.65, label=method if (row, column) == (0, 0) else None)
            for method in local:
                line = panel.loc[panel["method"] == method].sort_values("train_percent")
                if not line.empty:
                    style = STYLES[method]
                    axis.errorbar(line["train_percent"], line["mean"], yerr=line["std"], color=style["color"], linestyle="-", marker="o", linewidth=2.8, markersize=6.5, elinewidth=1.5, capsize=3.5, label=method if (row, column) == (0, 0) else None)
            axis.set_title(f"DockQ >= {threshold_value:.2f}")
            axis.set_xlim(0, 31)
            axis.set_xticks(TRAIN_PERCENTS)
            axis.grid(axis="y", alpha=0.16)
            if column == 0:
                axis.set_ylabel("Brier score" if metric == "brier" else "ECE (10 bins)")
            if row == 1:
                axis.set_xlabel(x_label)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.04))
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    output = FIGURE_DIR / output_name
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight", metadata=PDF_METADATA)
    fig.savefig(output.with_suffix(".png"), bbox_inches="tight", dpi=300)
    print(f"Wrote {output.with_suffix('.pdf')}")
    print(f"Wrote {output.with_suffix('.png')}")


if __name__ == "__main__":
    target_grouped = compute()
    render(target_grouped, "F3_workshop_abag_recalibration_candidate", "[%] of unique complexes used")
    model_random = compute_model_random()
    render(model_random, "F3_workshop_abag_recalibration_model_random_candidate", "[%] samples used")
