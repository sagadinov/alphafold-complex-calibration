#!/usr/bin/env python3
"""Render the Ab-Ag count-grid recalibration curve without General reference."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper/figures/source_data/F4_workshop_abag_recalibration_model_random_counts_train_to_test.csv"
OUT = ROOT / "analysis/workshop/figure_candidates"
THRESHOLDS = [("acceptable", 0.23), ("medium", 0.49), ("high", 0.80)]
STYLES = {
    "Raw ipTM": {"color": "#374151", "linestyle": "--", "marker": None},
    "Isotonic ipTM (Ab-Ag train)": {"color": "#2563EB", "linestyle": "-", "marker": "o"},
}
LABELS = {"Raw ipTM": "Raw ipTM", "Isotonic ipTM (Ab-Ag train)": "Isotonic ipTM (Ab-Ag)"}


def main() -> None:
    source = pd.read_csv(SOURCE)
    source = source.loc[source["method"].isin(STYLES)].copy()
    expected = {"Raw ipTM", "Isotonic ipTM (Ab-Ag train)"}
    if set(source["method"]) != expected:
        raise RuntimeError("Unexpected source methods after excluding General isotonic reference.")

    plt.rcParams.update({"font.size": 13, "axes.labelsize": 14, "axes.titlesize": 15,
                         "legend.fontsize": 12, "xtick.labelsize": 12, "ytick.labelsize": 12})
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharex=True)
    for col, (threshold, value) in enumerate(THRESHOLDS):
        for row, metric in enumerate(["brier", "ece"]):
            ax = axes[row, col]
            panel = source.loc[(source["threshold"] == threshold) & (source["metric"] == metric)]
            for method, style in STYLES.items():
                line = panel.loc[panel["method"] == method].sort_values("x_value")
                if method == "Isotonic ipTM (Ab-Ag train)":
                    ax.errorbar(line["x_value"], line["mean"], yerr=line["std"], color=style["color"],
                                linestyle=style["linestyle"], marker=style["marker"], linewidth=2.5,
                                markersize=5.5, capsize=3, label=LABELS[method])
                else:
                    ax.plot(line["x_value"], line["mean"], color=style["color"], linestyle=style["linestyle"],
                            linewidth=2.5, label=LABELS[method])
            ax.set_xscale("log")
            ax.set_xlim(40, 12000)
            ax.set_xticks([50, 100, 200, 500, 1000, 10000])
            ax.set_xticklabels(["50", "100", "200", "500", "1,000", "10,000"])
            ax.set_title(f"DockQ >= {value:.2f}")
            ax.grid(alpha=0.15)
            if col == 0:
                ax.set_ylabel("Brier score" if metric == "brier" else "ECE (10 bins)")
            if row == 1:
                ax.set_xlabel("Number of Ab-Ag training samples")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.01))
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    OUT.mkdir(parents=True, exist_ok=True)
    source.to_csv(OUT / "F3_workshop_abag_recalibration_log_samples_no_general_source.csv", index=False)
    fig.savefig(OUT / "F3_workshop_abag_recalibration_log_samples_no_general.pdf", bbox_inches="tight")
    fig.savefig(OUT / "F3_workshop_abag_recalibration_log_samples_no_general.png", bbox_inches="tight", dpi=300)
    print("Wrote Ab-Ag count-grid candidate without General isotonic reference.")


if __name__ == "__main__":
    main()
