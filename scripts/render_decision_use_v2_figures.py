#!/usr/bin/env python3
"""Render decision-use v2 figures strictly from frozen corrected CSV outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PRIMARY_THRESHOLD = "acceptable"
Q_LEVELS = [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95]
K_LEVELS = [5, 10, 20, 50]
THRESHOLDS = {"acceptable": 0.23, "medium": 0.49, "high": 0.80}

FIXED_METHOD_ORDER = ["Raw ipTM", "Isotonic ipTM", "MLP 5-feat CE"]
IPAE_METHOD_ORDER = ["Raw iPAE proxy", "Calibrated iPAE probability", "MLP 5-feat CE"]
METHOD_COLORS = {
    "Raw ipTM": "#6B7280",
    "Isotonic ipTM": "#2563EB",
    "MLP 5-feat CE": "#DC2626",
    "Raw iPAE proxy": "#6B7280",
    "Calibrated iPAE probability": "#2563EB",
}
K_MARKERS = {5: "o", 10: "s", 20: "^", 50: "D"}
DISPLAY_LABELS = {
    "Raw iPAE proxy": "Raw inverse-iPAE proxy",
    "Calibrated iPAE probability": "Calibrated iPAE probability",
    "MLP 5-feat CE": "MLP 5-feat CE",
    "Raw ipTM": "Raw ipTM",
    "Isotonic ipTM": "Isotonic ipTM",
}

FIXED_CAPTION = (
    "Candidate identities were fixed by the indicated raw confidence score and were identical across "
    "probability estimators; only the predicted expected yield differed."
)
GENERAL_K_NOTE = (
    "Only K=5 is shown because no General target contained at least ten eligible models in the locked dataset."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(
            "/proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration/"
            "af3_atlas/PAPER_REVISION/analysis/decision_use_v2"
        ),
    )
    return parser.parse_args()


def load_csvs(base: Path) -> dict[str, pd.DataFrame]:
    files = {
        "fixed_per_target": "fixed_ranking_yield_per_target_v2.csv",
        "fixed_metrics": "fixed_ranking_yield_metrics_v2.csv",
        "fixed_boot": "fixed_ranking_yield_bootstrap_v2.csv",
        "rel_curve": "reliability_operating_curve_v2.csv",
        "rel_boot": "reliability_operating_curve_bootstrap_v2.csv",
    }
    out = {}
    for key, fname in files.items():
        path = base / fname
        if not path.exists():
            raise FileNotFoundError(path)
        out[key] = pd.read_csv(path)
    return out


def write_captions(base: Path) -> None:
    text = "\n".join(
        [
            "# Decision-Use v2 Figure Captions",
            "",
            "## fixed_ranking_yield_figure_v2",
            "",
            (
                "Fixed-ranking expected-yield estimation at DockQ ≥0.23. "
                "Top-left: Ab-Ag, candidates ranked by raw ipTM. "
                "Top-right: Ab-Ag, candidates ranked by iPAE. "
                "Bottom-left: General, candidates ranked by raw ipTM. "
                "Bottom-right: CASP16, candidates ranked by raw ipTM. "
                "Within each panel, candidate identities were identical for the compared estimators; "
                "only the estimated probability of structural success differed. "
                "The y-axis reports MAE in predicted success fraction, defined as the target-level mean of |Ĥ_t/K - H_t/K|. "
                "Points show target-level MAE in predicted success fraction and error bars show 95% target-bootstrap confidence intervals. "
                "General is shown only at K=5, because no General target contained at least ten eligible predictions in the locked dataset."
            ),
            "",
            "## reliability_transfer_figure_v2",
            "",
            (
                "Transfer of minimum-reliability decision rules at DockQ ≥0.23. "
                "Top row: observed precision. Bottom row: coverage. "
                "For calibrated methods, predictions were selected using p-hat ≥ q. "
                "On General, raw ipTM thresholds were evaluated using target-grouped cross-fitting. "
                "For external transfer, one threshold per requested reliability level was fitted using all General OOF predictions and applied unchanged to Ab-Ag and CASP16. "
                "General-trained calibrated probabilities were likewise applied frozen to both external benchmarks. "
                "Points show observed precision and coverage; error bars show 95% target-bootstrap confidence intervals. "
                "The dashed line in the precision panels represents the requested minimum reliability; "
                "values above it indicate conservative selection rather than perfect calibration."
            ),
            "",
            "## reliability_precision_figure_v2",
            "",
            (
                "Observed precision under minimum-reliability decision rules at DockQ ≥0.23. "
                "The dashed line represents the requested minimum reliability, not an ideal calibration line. "
                "Values above the line indicate that the rule satisfies or exceeds the requested minimum reliability."
            ),
            "",
            "## reliability_coverage_figure_v2",
            "",
            (
                "Coverage of minimum-reliability decision rules at DockQ ≥0.23. "
                "Coverage is the fraction of eligible predictions retained by the rules evaluated in the accompanying precision figure. "
                "Precision and coverage should therefore be interpreted jointly."
            ),
            "",
            "## abag_ipae_reliability_figure_v2",
            "",
            (
                "Within-domain reliability and coverage of iPAE-based decision rules on the held-out Ab-Ag test set at DockQ ≥0.23. "
                "Raw inverse-iPAE thresholds were selected using the Ab-Ag training/calibration data and applied frozen to the test set. "
                "Calibrated iPAE and the five-feature MLP selected predictions with p-hat ≥ q. "
                "Left: observed precision relative to the requested minimum reliability. "
                "Right: corresponding coverage. "
                "High-q operating points with very small selected sets are marked explicitly by selected-count annotations on the coverage panel."
            ),
            "",
        ]
    ) + "\n"
    (base / "figure_captions_v2.md").write_text(text, encoding="utf-8")


def render_fixed_ranking_figure(per_target: pd.DataFrame, metrics: pd.DataFrame, boot: pd.DataFrame, out_dir: Path) -> None:
    mt = metrics[
        (metrics["dockq_threshold_name"] == PRIMARY_THRESHOLD)
        & (metrics["comparison_universe"] == "three_method_common")
    ].copy()
    bt = boot[
        (boot["dockq_threshold_name"] == PRIMARY_THRESHOLD)
        & (boot["comparison_universe"] == "three_method_common")
        & (boot["row_type"] == "method_metric")
        & (boot["metric"] == "normalized_mae")
    ].copy()
    panel_specs = [
        ("abag", "iptm", "Ab-Ag: ipTM-ranked"),
        ("abag", "ipae", "Ab-Ag: iPAE-ranked"),
        ("general", "iptm", "General: ipTM-ranked, K=5 only"),
        ("casp16", "iptm", "CASP16: ipTM-ranked"),
    ]
    panel_methods = {
        "iptm": FIXED_METHOD_ORDER,
        "ipae": IPAE_METHOD_ORDER,
    }
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.5), constrained_layout=True)
    offsets = {
        0: 0.0,
        1: 0.0,
        2: 0.0,
        5: -0.35,
        10: 0.0,
        20: 0.35,
        50: 0.0,
    }
    for ax, (dataset, family, title) in zip(axes.ravel(), panel_specs):
        msub = mt[(mt["dataset"] == dataset) & (mt["ranking_family"] == family)].copy()
        bsub = bt[(bt["dataset"] == dataset) & (bt["ranking_family"] == family)].copy()
        if msub.empty:
            ax.axis("off")
            continue
        methods = panel_methods[family]
        for mi, method in enumerate(methods):
            line = msub[msub["probability_method"] == method].sort_values("K")
            if line.empty:
                continue
            ci = bsub[bsub["probability_method"] == method].sort_values("K")
            x = line["K"].to_numpy(dtype=float)
            x_plot = np.array([v + offsets.get(int(v), 0.0) + (mi - 1) * 0.6 for v in x], dtype=float)
            y = line["normalized_mae"].to_numpy(dtype=float)
            if len(ci) == len(line):
                lo = ci["ci_low"].to_numpy(dtype=float)
                hi = ci["ci_high"].to_numpy(dtype=float)
                yerr = np.vstack([y - lo, hi - y])
            else:
                yerr = None
            ax.errorbar(
                x_plot,
                y,
                yerr=yerr,
                fmt=K_MARKERS.get(int(x[0]), "o"),
                color=METHOD_COLORS[method],
                ecolor=METHOD_COLORS[method],
                elinewidth=1.3,
                capsize=3,
                markersize=7,
                linestyle="none",
                label=DISPLAY_LABELS.get(method, method) if (dataset, family) == ("abag", "iptm") else None,
            )
        ax.set_title(title)
        ax.set_xlabel("K")
        ax.set_ylabel("MAE in predicted success fraction")
        ticks = sorted(msub["K"].drop_duplicates().tolist())
        ax.set_xticks(ticks)
        ax.set_ylim(0.0, 0.42)
        ax.grid(axis="y", alpha=0.2)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    uniq = dict(zip(labels, handles))
    fig.legend(uniq.values(), uniq.keys(), loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Fixed-ranking expected-yield estimation at DockQ ≥ 0.23", y=1.02, fontsize=14)
    fig.savefig(out_dir / "fixed_ranking_yield_figure_v2.pdf", bbox_inches="tight")
    fig.savefig(out_dir / "fixed_ranking_yield_figure_v2.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def render_reliability_family(curve: pd.DataFrame, boot: pd.DataFrame, out_dir: Path, score_family: str, stem_prefix: str, datasets: list[str], methods: list[str]) -> None:
    curve = curve[
        (curve["dockq_threshold_name"] == PRIMARY_THRESHOLD)
        & (curve["fold_id"].astype(str) == "all")
        & (curve["comparison_universe"] == "three_method_common")
        & (curve["score_family"] == score_family)
    ].copy()
    boot = boot[
        (boot["dockq_threshold_name"] == PRIMARY_THRESHOLD)
        & (boot["row_type"] == "metric_ci")
        & (boot["comparison_universe"] == "three_method_common")
        & (boot["score_family"] == score_family)
    ].copy()
    titles = {"abag": "Ab-Ag", "general": "General", "casp16": "CASP16"}
    metric_to_file = [
        ("precision", f"{stem_prefix}_precision_figure_v2", "Observed precision", True),
        ("coverage", f"{stem_prefix}_coverage_figure_v2", "Coverage", False),
    ]
    for metric, stem, ylabel, with_identity in metric_to_file:
        fig, axes = plt.subplots(1, len(datasets), figsize=(5.2 * len(datasets), 4.5), constrained_layout=True)
        if len(datasets) == 1:
            axes = [axes]
        for ax, dataset in zip(axes, datasets):
            sub = curve[curve["evaluation_dataset"] == dataset].copy()
            csub = boot[(boot["evaluation_dataset"] == dataset) & (boot["metric"] == metric)].copy()
            if with_identity:
                ax.plot(Q_LEVELS, Q_LEVELS, "k--", linewidth=1, alpha=0.6)
            for method in methods:
                line = sub[sub["method"] == method].sort_values("q")
                if line.empty:
                    continue
                ci = csub[csub["method"] == method].sort_values("q")
                x = line["q"].to_numpy(dtype=float)
                y = line[metric].to_numpy(dtype=float)
                if len(ci) == len(line):
                    lo = ci["ci_low"].to_numpy(dtype=float)
                    hi = ci["ci_high"].to_numpy(dtype=float)
                    yerr = np.vstack([y - lo, hi - y])
                else:
                    yerr = None
                ax.errorbar(
                    x,
                    y,
                    yerr=yerr,
                    color=METHOD_COLORS[method],
                    ecolor=METHOD_COLORS[method],
                    marker="o",
                    linestyle="-",
                    linewidth=1.8,
                    elinewidth=1.2,
                    capsize=2.5,
                    markersize=5,
                    label=DISPLAY_LABELS.get(method, method) if dataset == datasets[0] else None,
                )
            ax.set_title(titles[dataset])
            ax.set_xlabel("Requested reliability q")
            ax.set_xlim(min(Q_LEVELS) - 0.02, max(Q_LEVELS) + 0.02)
            ax.set_ylim(0.0, 1.02)
            if ax is axes[0]:
                ax.set_ylabel(ylabel)
            ax.grid(axis="y", alpha=0.2)
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.05))
        fig.savefig(out_dir / f"{stem}.pdf", bbox_inches="tight")
        fig.savefig(out_dir / f"{stem}.png", dpi=300, bbox_inches="tight")
        plt.close(fig)


def render_reliability_transfer_combined(curve: pd.DataFrame, boot: pd.DataFrame, out_dir: Path) -> None:
    curve = curve[
        (curve["dockq_threshold_name"] == PRIMARY_THRESHOLD)
        & (curve["fold_id"].astype(str) == "all")
        & (curve["comparison_universe"] == "three_method_common")
        & (curve["score_family"] == "iptm")
    ].copy()
    boot = boot[
        (boot["dockq_threshold_name"] == PRIMARY_THRESHOLD)
        & (boot["row_type"] == "metric_ci")
        & (boot["comparison_universe"] == "three_method_common")
        & (boot["score_family"] == "iptm")
    ].copy()
    datasets = ["general", "abag", "casp16"]
    titles = {"abag": "Ab-Ag", "general": "General", "casp16": "CASP16"}
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), constrained_layout=True, sharex=True)
    for col, dataset in enumerate(datasets):
        for row, (metric, ylabel, with_identity) in enumerate(
            [("precision", "Observed precision", True), ("coverage", "Coverage", False)]
        ):
            ax = axes[row, col]
            sub = curve[curve["evaluation_dataset"] == dataset].copy()
            csub = boot[(boot["evaluation_dataset"] == dataset) & (boot["metric"] == metric)].copy()
            if with_identity:
                ax.plot(Q_LEVELS, Q_LEVELS, "k--", linewidth=1, alpha=0.6)
            for method in FIXED_METHOD_ORDER:
                line = sub[sub["method"] == method].sort_values("q")
                if line.empty:
                    continue
                ci = csub[csub["method"] == method].sort_values("q")
                x = line["q"].to_numpy(dtype=float)
                y = line[metric].to_numpy(dtype=float)
                if len(ci) == len(line):
                    lo = ci["ci_low"].to_numpy(dtype=float)
                    hi = ci["ci_high"].to_numpy(dtype=float)
                    yerr = np.vstack([y - lo, hi - y])
                else:
                    yerr = None
                ax.errorbar(
                    x,
                    y,
                    yerr=yerr,
                    color=METHOD_COLORS[method],
                    ecolor=METHOD_COLORS[method],
                    marker="o",
                    linestyle="-",
                    linewidth=1.8,
                    elinewidth=1.2,
                    capsize=2.5,
                    markersize=5,
                    label=DISPLAY_LABELS.get(method, method) if (row, col) == (0, 0) else None,
                )
            if row == 0:
                ax.set_title(titles[dataset])
            if col == 0:
                ax.set_ylabel(ylabel)
            if row == 1:
                ax.set_xlabel("Requested minimum reliability q")
            ax.set_xlim(min(Q_LEVELS) - 0.02, max(Q_LEVELS) + 0.02)
            ax.set_ylim(0.0, 1.02)
            ax.grid(axis="y", alpha=0.2)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("Transfer of minimum-reliability decision rules at DockQ ≥ 0.23", y=1.02, fontsize=14)
    fig.savefig(out_dir / "reliability_transfer_figure_v2.pdf", bbox_inches="tight")
    fig.savefig(out_dir / "reliability_transfer_figure_v2.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def render_abag_ipae_combined(curve: pd.DataFrame, boot: pd.DataFrame, out_dir: Path) -> None:
    curve = curve[
        (curve["dockq_threshold_name"] == PRIMARY_THRESHOLD)
        & (curve["fold_id"].astype(str) == "all")
        & (curve["comparison_universe"] == "three_method_common")
        & (curve["score_family"] == "ipae")
        & (curve["evaluation_dataset"] == "abag")
    ].copy()
    boot = boot[
        (boot["dockq_threshold_name"] == PRIMARY_THRESHOLD)
        & (boot["row_type"] == "metric_ci")
        & (boot["comparison_universe"] == "three_method_common")
        & (boot["score_family"] == "ipae")
        & (boot["evaluation_dataset"] == "abag")
    ].copy()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    small_n_threshold = 100
    for ax, metric, ylabel, with_identity in [
        (axes[0], "precision", "Observed precision", True),
        (axes[1], "coverage", "Coverage", False),
    ]:
        if with_identity:
            ax.plot(Q_LEVELS, Q_LEVELS, "k--", linewidth=1, alpha=0.6)
        for method in IPAE_METHOD_ORDER:
            line = curve[curve["method"] == method].sort_values("q")
            if line.empty:
                continue
            ci = boot[(boot["method"] == method) & (boot["metric"] == metric)].sort_values("q")
            x = line["q"].to_numpy(dtype=float)
            y = line[metric].to_numpy(dtype=float)
            if metric == "precision":
                y = np.where(line["n_selected"].to_numpy(dtype=float) > 0, y, np.nan)
            if len(ci) == len(line):
                lo = ci["ci_low"].to_numpy(dtype=float)
                hi = ci["ci_high"].to_numpy(dtype=float)
                yerr = np.vstack([y - lo, hi - y])
            else:
                yerr = None
            ax.errorbar(
                x,
                y,
                yerr=yerr,
                color=METHOD_COLORS[method],
                ecolor=METHOD_COLORS[method],
                marker="o",
                linestyle="-",
                linewidth=1.8,
                elinewidth=1.2,
                capsize=2.5,
                markersize=5,
                label=DISPLAY_LABELS.get(method, method),
            )
            n_small = line["n_selected"].to_numpy(dtype=float) < small_n_threshold
            if n_small.any():
                ax.scatter(
                    x[n_small],
                    y[n_small],
                    s=44,
                    facecolors="white",
                    edgecolors=METHOD_COLORS[method],
                    linewidths=1.4,
                    zorder=5,
                )
            if metric == "coverage":
                for q_annot in [0.90, 0.95]:
                    row = line[np.isclose(line["q"], q_annot)]
                    if row.empty:
                        continue
                    n_sel = int(row["n_selected"].iloc[0])
                    yv = float(row[metric].iloc[0])
                    xv = float(row["q"].iloc[0])
                    ax.annotate(
                        f"n={n_sel}",
                        (xv, yv),
                        textcoords="offset points",
                        xytext=(0, 8 if q_annot >= 0.95 else -12),
                        ha="center",
                        fontsize=8,
                        color=METHOD_COLORS[method],
                    )
        ax.set_xlabel("Requested reliability q")
        ax.set_ylabel(ylabel)
        ax.set_xlim(min(Q_LEVELS) - 0.02, max(Q_LEVELS) + 0.02)
        ax.set_ylim(0.0, 1.02)
        ax.grid(axis="y", alpha=0.2)
    axes[0].set_title("Ab-Ag iPAE reliability: precision")
    axes[1].set_title("Ab-Ag iPAE reliability: coverage")
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.05))
    fig.savefig(out_dir / "abag_ipae_reliability_figure_v2.pdf", bbox_inches="tight")
    fig.savefig(out_dir / "abag_ipae_reliability_figure_v2.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    base = args.input_dir
    data = load_csvs(base)
    render_fixed_ranking_figure(data["fixed_per_target"], data["fixed_metrics"], data["fixed_boot"], base)
    render_reliability_family(
        data["rel_curve"],
        data["rel_boot"],
        base,
        score_family="iptm",
        stem_prefix="reliability",
        datasets=["general", "abag", "casp16"],
        methods=["Raw ipTM", "Isotonic ipTM", "MLP 5-feat CE"],
    )
    render_reliability_transfer_combined(data["rel_curve"], data["rel_boot"], base)
    render_abag_ipae_combined(data["rel_curve"], data["rel_boot"], base)
    write_captions(base)


if __name__ == "__main__":
    main()
