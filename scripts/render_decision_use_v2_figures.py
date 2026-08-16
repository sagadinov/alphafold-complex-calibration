#!/usr/bin/env python3
"""Render final decision-use figures from frozen repository-local CSV outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import PDF_METADATA

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis" / "decision_use"

PRIMARY_THRESHOLD = "acceptable"
Q_LEVELS = [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95]
FIXED_METHOD_ORDER = ["Raw ipTM", "Isotonic ipTM", "MLP 5-feat CE"]
IPAE_METHOD_ORDER = ["Raw iPAE proxy", "Calibrated iPAE probability", "MLP 5-feat CE"]
METHOD_COLORS = {
    "Raw ipTM": "#6B7280",
    "Isotonic ipTM": "#2563EB",
    "MLP 5-feat CE": "#DC2626",
    "Raw iPAE proxy": "#6B7280",
    "Calibrated iPAE probability": "#2563EB",
}
DISPLAY_LABELS = {
    "Raw ipTM": "Raw ipTM",
    "Isotonic ipTM": "Isotonic ipTM",
    "MLP 5-feat CE": "MLP 5-feat CE",
    "Raw iPAE proxy": "Raw inverse-iPAE proxy",
    "Calibrated iPAE probability": "Calibrated iPAE probability",
}
FIXED_CAPTION = (
    "Candidate identities were fixed by the indicated raw confidence score and were identical across "
    "probability estimators; only the predicted expected yield differed."
)
GENERAL_K_NOTE = (
    "Only K=5 is shown because no General target contained at least ten eligible models in the locked dataset."
)


def load_csvs(base: Path | None = None) -> dict[str, pd.DataFrame]:
    base = base or ANALYSIS
    files = {
        "fixed_metrics": "fixed_ranking_yield_metrics.csv",
        "fixed_boot": "fixed_ranking_yield_bootstrap.csv",
        "rel_curve": "reliability_operating_curve.csv",
        "rel_boot": "reliability_operating_curve_bootstrap.csv",
    }
    return {key: pd.read_csv(base / name) for key, name in files.items()}


def write_captions(base: Path) -> None:
    text = "\n".join(
        [
            "# Decision-Use Figure Captions",
            "",
            "## F2_fixed_ranking_yield",
            "",
            (
                "Fixed-ranking expected-yield estimation at DockQ >= 0.23. "
                + FIXED_CAPTION
                + " Panels show Ab-Ag ipTM-ranked, Ab-Ag iPAE-ranked, General ipTM-ranked, and CASP16 ipTM-ranked. "
                "The y-axis is MAE in predicted success fraction, defined as the mean absolute difference between predicted and observed success fractions across targets. "
                + GENERAL_K_NOTE
            ),
            "",
            "## F3_reliability_transfer",
            "",
            (
                "Transfer of minimum-reliability decision rules at DockQ >= 0.23. Top row: observed precision. Bottom row: coverage. "
                "On General, raw ipTM thresholds were evaluated using target-grouped cross-fitting. For external transfer, one threshold per requested reliability level was fitted using all General OOF predictions and applied unchanged to Ab-Ag and CASP16. "
                "General-trained calibrated probabilities were likewise applied frozen to both external benchmarks."
            ),
            "",
            "## S2_abag_ipae_reliability",
            "",
            (
                "Within-domain Ab-Ag reliability and coverage of iPAE-based decision rules at DockQ >= 0.23. "
                "Raw inverse-iPAE proxy, calibrated iPAE probability, and the five-feature MLP are compared. "
                "Precision is omitted at q values where no predictions are selected."
            ),
            "",
        ]
    ) + "\n"
    (base / "figure_captions.md").write_text(text, encoding="utf-8")


def _errorbars(ci_sub: pd.DataFrame, line_sub: pd.DataFrame, metric_col: str) -> np.ndarray | None:
    ci_sub = ci_sub.sort_values("q")
    line_sub = line_sub.sort_values("q")
    if len(ci_sub) != len(line_sub):
        return None
    lo = ci_sub["ci_low"].to_numpy(dtype=float)
    hi = ci_sub["ci_high"].to_numpy(dtype=float)
    y = line_sub[metric_col].to_numpy(dtype=float)
    return np.vstack([y - lo, hi - y])


def render_fixed_ranking_main(metrics: pd.DataFrame, boot: pd.DataFrame, out_dir: Path) -> None:
    mt = metrics[
        (metrics["dockq_threshold_name"] == PRIMARY_THRESHOLD)
        & (metrics["comparison_universe"] == "three_method_common")
        & (metrics["dataset"].isin(["abag", "general", "casp16"]))
    ].copy()
    bt = boot[
        (boot["dockq_threshold_name"] == PRIMARY_THRESHOLD)
        & (boot["comparison_universe"] == "three_method_common")
        & (boot["row_type"] == "method_metric")
        & (boot["metric"] == "normalized_mae")
        & (boot["dataset"].isin(["abag", "general", "casp16"]))
    ].copy()

    panel_specs = [
        ("abag", "iptm", "Ab-Ag: ipTM-ranked"),
        ("abag", "ipae", "Ab-Ag: iPAE-ranked"),
        ("general", "iptm", "General: ipTM-ranked, K=5 only"),
        ("casp16", "iptm", "CASP16: ipTM-ranked"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.2), sharey=True)
    for ax, (dataset, family, title) in zip(axes.ravel(), panel_specs):
        msub = mt[(mt["dataset"] == dataset) & (mt["ranking_family"] == family)].copy()
        bsub = bt[(bt["dataset"] == dataset) & (bt["ranking_family"] == family)].copy()
        methods = FIXED_METHOD_ORDER if family == "iptm" else IPAE_METHOD_ORDER
        if msub.empty:
            ax.axis("off")
            continue
        k_values = sorted(msub["K"].unique())
        x_base = np.arange(len(k_values), dtype=float)
        offsets = np.linspace(-0.22, 0.22, len(methods))
        for mi, method in enumerate(methods):
            line = msub[msub["probability_method"] == method].sort_values("K")
            if line.empty:
                continue
            k_to_idx = {k: idx for idx, k in enumerate(k_values)}
            x = np.array([k_to_idx[int(k)] for k in line["K"]], dtype=float) + offsets[mi]
            y = line["normalized_mae"].to_numpy(dtype=float)
            ci = bsub[bsub["probability_method"] == method].sort_values("K")
            yerr = None
            if len(ci) == len(line):
                lo = ci["ci_low"].to_numpy(dtype=float)
                hi = ci["ci_high"].to_numpy(dtype=float)
                yerr = np.vstack([y - lo, hi - y])
            ax.errorbar(
                x,
                y,
                yerr=yerr,
                marker="o",
                linestyle="-",
                linewidth=1.7,
                markersize=5,
                capsize=2.5,
                color=METHOD_COLORS[method],
                label=DISPLAY_LABELS[method] if (dataset, family) == ("abag", "iptm") else None,
            )
        ax.set_title(title)
        ax.set_xticks(x_base)
        ax.set_xticklabels([str(int(k)) for k in k_values])
        ax.set_xlabel("K")
        ax.set_ylim(0.0, 0.42)
        ax.grid(axis="y", alpha=0.2)
    axes[0, 0].set_ylabel("MAE in predicted success fraction")
    axes[1, 0].set_ylabel("MAE in predicted success fraction")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.subplots_adjust(bottom=0.14, wspace=0.18, hspace=0.28)
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / "F2_fixed_ranking_yield.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    fig.savefig(out_dir / "F2_fixed_ranking_yield.png", bbox_inches="tight", dpi=300)
    plt.close(fig)


def render_reliability_transfer_main(curve: pd.DataFrame, boot: pd.DataFrame, out_dir: Path) -> None:
    curve = curve[
        (curve["dockq_threshold_name"] == PRIMARY_THRESHOLD)
        & (curve["fold_id"].astype(str) == "all")
        & (curve["comparison_universe"] == "three_method_common")
        & (curve["score_family"] == "iptm")
        & (curve["method"].isin(FIXED_METHOD_ORDER))
    ].copy()
    boot = boot[
        (boot["dockq_threshold_name"] == PRIMARY_THRESHOLD)
        & (boot["row_type"] == "metric_ci")
        & (boot["comparison_universe"] == "three_method_common")
        & (boot["score_family"] == "iptm")
        & (boot["method"].isin(FIXED_METHOD_ORDER))
    ].copy()
    datasets = [("general", "General"), ("abag", "Ab-Ag"), ("casp16", "CASP16")]
    fig, axes = plt.subplots(2, 3, figsize=(14.6, 8.2), sharex=True)
    for col, (dataset, title) in enumerate(datasets):
        for row, metric in enumerate(["precision", "coverage"]):
            ax = axes[row, col]
            sub = curve[curve["evaluation_dataset"] == dataset].copy()
            csub = boot[(boot["evaluation_dataset"] == dataset) & (boot["metric"] == metric)].copy()
            if metric == "precision":
                ax.plot(Q_LEVELS, Q_LEVELS, "k--", linewidth=1.0, alpha=0.45)
            for method in FIXED_METHOD_ORDER:
                line = sub[sub["method"] == method].sort_values("q")
                if line.empty:
                    continue
                ci = csub[csub["method"] == method].sort_values("q")
                x = line["q"].to_numpy(dtype=float)
                y = line[metric].to_numpy(dtype=float)
                yerr = _errorbars(ci, line, metric)
                ax.errorbar(
                    x,
                    y,
                    yerr=yerr,
                    color=METHOD_COLORS[method],
                    marker="o",
                    linestyle="-",
                    linewidth=1.8,
                    markersize=4.5,
                    capsize=2.2,
                    label=DISPLAY_LABELS[method] if (row, col) == (0, 0) else None,
                )
            if row == 0:
                ax.set_title(title)
            if col == 0:
                ax.set_ylabel("Observed precision" if metric == "precision" else "Coverage")
            if row == 1:
                ax.set_xlabel("Requested minimum reliability q")
            ax.set_xlim(0.48, 0.97)
            ax.set_ylim(0.0, 1.02)
            ax.grid(axis="y", alpha=0.2)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.08))
    fig.subplots_adjust(bottom=0.18, wspace=0.2, hspace=0.22)
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / "F3_reliability_transfer.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    fig.savefig(out_dir / "F3_reliability_transfer.png", bbox_inches="tight", dpi=300)
    plt.close(fig)


def render_abag_ipae_supplementary(curve: pd.DataFrame, boot: pd.DataFrame, out_dir: Path) -> None:
    curve = curve[
        (curve["dockq_threshold_name"] == PRIMARY_THRESHOLD)
        & (curve["fold_id"].astype(str) == "all")
        & (curve["comparison_universe"] == "three_method_common")
        & (curve["score_family"] == "ipae")
        & (curve["evaluation_dataset"] == "abag")
        & (curve["method"].isin(IPAE_METHOD_ORDER))
    ].copy()
    boot = boot[
        (boot["dockq_threshold_name"] == PRIMARY_THRESHOLD)
        & (boot["row_type"] == "metric_ci")
        & (boot["comparison_universe"] == "three_method_common")
        & (boot["score_family"] == "ipae")
        & (boot["evaluation_dataset"] == "abag")
        & (boot["method"].isin(IPAE_METHOD_ORDER))
    ].copy()
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6), sharex=True)
    for ax, metric in zip(axes, ["precision", "coverage"]):
        if metric == "precision":
            ax.plot(Q_LEVELS, Q_LEVELS, "k--", linewidth=1.0, alpha=0.45)
        for method in IPAE_METHOD_ORDER:
            line = curve[curve["method"] == method].sort_values("q").copy()
            if line.empty:
                continue
            ci = boot[(boot["method"] == method) & (boot["metric"] == metric)].sort_values("q")
            if metric == "precision":
                line.loc[line["n_selected"].fillna(0) <= 0, metric] = np.nan
            x = line["q"].to_numpy(dtype=float)
            y = line[metric].to_numpy(dtype=float)
            yerr = None
            if len(ci) == len(line):
                lo = ci["ci_low"].to_numpy(dtype=float)
                hi = ci["ci_high"].to_numpy(dtype=float)
                yerr = np.vstack([np.nan_to_num(y - lo, nan=0.0), np.nan_to_num(hi - y, nan=0.0)])
            ax.errorbar(
                x,
                y,
                yerr=yerr,
                color=METHOD_COLORS[method],
                marker="o",
                linestyle="-",
                linewidth=1.8,
                markersize=4.5,
                capsize=2.2,
                label=DISPLAY_LABELS[method],
            )
            if metric == "coverage":
                for q in (0.90, 0.95):
                    match = line[np.isclose(line["q"], q)]
                    if not match.empty:
                        n_sel = int(match["n_selected"].iloc[0])
                        cov = float(match["coverage"].iloc[0])
                        label = "no selections" if n_sel == 0 else f"n={n_sel}"
                        ax.annotate(label, (q, cov), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8)
        ax.set_xlim(0.48, 0.97)
        ax.set_ylim(0.0, 1.02)
        ax.grid(axis="y", alpha=0.2)
        ax.set_xlabel("Requested minimum reliability q")
        ax.set_ylabel("Observed precision" if metric == "precision" else "Coverage")
        ax.set_title("Ab-Ag iPAE reliability" if metric == "precision" else "Ab-Ag iPAE coverage")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.08))
    fig.subplots_adjust(bottom=0.22, wspace=0.22)
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / "S2_abag_ipae_reliability.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    fig.savefig(out_dir / "S2_abag_ipae_reliability.png", bbox_inches="tight", dpi=300)
    plt.close(fig)
