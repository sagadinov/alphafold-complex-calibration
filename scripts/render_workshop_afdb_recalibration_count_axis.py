#!/usr/bin/env python3
"""Render the approved AFDB recalibration Figure 3 with a count x-axis."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "analysis/workshop/figure_candidates/F3_workshop_afdb_recalibration_candidate_source.csv"
OUT = ROOT / "analysis/workshop/figure_candidates"
THRESHOLDS = [("acceptable", 0.23), ("medium", 0.49), ("high", 0.80)]
DISPLAY_SIZES = [5, 15, 30, 60, 90]
FIXED = ["Raw ipTM", "Isotonic ipTM (General frozen)", "Raw ipSAEmax"]
LOCAL = ["Isotonic ipTM (local AFDB)", "Isotonic ipSAEmax (local AFDB)"]
STYLE = {
    "Raw ipTM": {"color": "#6B7280", "marker": "s"},
    "Isotonic ipTM (General frozen)": {"color": "#FA8072", "marker": "P"},
    "Raw ipSAEmax": {"color": "#10B981", "marker": "D"},
    "Isotonic ipTM (local AFDB)": {"color": "#2563EB", "marker": "o"},
    "Isotonic ipSAEmax (local AFDB)": {"color": "#059669", "marker": "o"},
}
LABEL = {
    "Raw ipTM": "Raw ipTM",
    "Isotonic ipTM (General frozen)": "Isotonic ipTM (General)",
    "Raw ipSAEmax": "Raw ipSAEmax",
    "Isotonic ipTM (local AFDB)": "Isotonic ipTM (AFDB)",
    "Isotonic ipSAEmax (local AFDB)": "Isotonic ipSAEmax (AFDB)",
}


def main() -> None:
    source = pd.read_csv(SOURCE)
    source = source.loc[source["train_size"].isin(DISPLAY_SIZES)].copy()
    plt.rcParams.update({"font.size": 13, "axes.labelsize": 14, "axes.titlesize": 15,
                         "legend.fontsize": 12, "xtick.labelsize": 12, "ytick.labelsize": 12})
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharex=True)
    for col, (threshold, threshold_value) in enumerate(THRESHOLDS):
        for row, metric in enumerate(["brier", "ece"]):
            ax = axes[row, col]
            panel = source.loc[(source["threshold"] == threshold) & (source["metric"] == metric) & source["available"]]
            for method in FIXED:
                values = panel.loc[panel["method"] == method].sort_values("train_size")
                ax.axhline(values["mean"].iloc[0], color=STYLE[method]["color"], linestyle="--", linewidth=2.3,
                           alpha=0.65, label=LABEL[method] if (row, col) == (0, 0) else None)
            for method in LOCAL:
                values = panel.loc[panel["method"] == method].sort_values("train_size")
                ax.errorbar(values["train_size"], values["mean"], yerr=values["std"], color=STYLE[method]["color"],
                            marker=STYLE[method]["marker"], linestyle="-", linewidth=2.4, markersize=5.5,
                            elinewidth=1.5, capsize=3, label=LABEL[method] if (row, col) == (0, 0) else None)
            ax.set_title(f"DockQ >= {threshold_value:.2f}")
            ax.set_xlim(0, 95)
            ax.set_xticks(DISPLAY_SIZES)
            ax.grid(axis="y", alpha=0.16)
            if col == 0:
                ax.set_ylabel("Brier score" if metric == "brier" else "ECE (10 bins)")
            if row == 1:
                ax.set_xlabel("Number of samples")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.03))
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    OUT.mkdir(parents=True, exist_ok=True)
    source.to_csv(OUT / "F3_workshop_afdb_recalibration_sample_counts_source.csv", index=False)
    fig.savefig(OUT / "F3_workshop_afdb_recalibration_sample_counts.pdf", bbox_inches="tight")
    fig.savefig(OUT / "F3_workshop_afdb_recalibration_sample_counts.png", bbox_inches="tight", dpi=300)
    print("Wrote AFDB Figure 3 candidate with calibration sample counts.")


if __name__ == "__main__":
    main()
