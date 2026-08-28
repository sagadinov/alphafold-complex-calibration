#!/usr/bin/env python3
"""Render fixed-cutoff success curves from the frozen workshop CSVs.

No scores are refit or recalibrated here.  The script only combines the
precomputed Ab-Ag and General OOF cutoff sweeps for visual comparison.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUTS = [
    (
        "Ab-Ag",
        ROOT / "analysis/workshop/fixed_cutoff_success/fixed_cutoff_success_abag.csv",
        "pDockQ2 (Ab-Ag refit)",
    ),
    (
        "General OOF",
        ROOT / "analysis/workshop/fixed_cutoff_success_general/fixed_cutoff_success_general.csv",
        "pDockQ2 (General refit)",
    ),
]
OUT_DIR = ROOT / "paper/figures"
SOURCE_DIR = OUT_DIR / "source_data"
THRESHOLDS = [("acceptable", 0.23), ("medium", 0.49), ("high", 0.80)]

STYLES = {
    "Raw ipTM": {"color": "#374151", "linestyle": "--", "marker": "s", "label": "Raw ipTM"},
    "Isotonic ipTM": {"color": "#2563EB", "linestyle": "-", "marker": "o", "label": "Isotonic ipTM"},
    "pDockQ2 (published)": {
        "color": "#F59E0B", "linestyle": "--", "marker": "^", "label": "pDockQ2 (published)"
    },
    "pDockQ2 (refit)": {"color": "#B45309", "linestyle": "-", "marker": "^", "label": "pDockQ2 (refit)"},
}


def load_data() -> pd.DataFrame:
    frames = []
    for dataset_label, path, refit_name in INPUTS:
        frame = pd.read_csv(path)
        frame = frame[frame["method"] != "method"].copy()  # Defensive against an appended CSV header.
        frame["cutoff"] = pd.to_numeric(frame["cutoff"], errors="coerce")
        frame["observed_success_fraction"] = pd.to_numeric(
            frame["observed_success_fraction"], errors="coerce"
        )
        frame["n_selected"] = pd.to_numeric(frame["n_selected"], errors="coerce")
        frame["dataset_label"] = dataset_label
        frame["method_plot"] = frame["method"].replace({refit_name: "pDockQ2 (refit)"})
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    expected = set(STYLES)
    observed = set(data["method_plot"].dropna())
    missing = expected - observed
    if missing:
        raise ValueError(f"Missing frozen cutoff curves: {sorted(missing)}")
    return data


def main() -> None:
    plt.rcParams.update(
        {
            "font.size": 16,
            "axes.labelsize": 18,
            "axes.titlesize": 19,
            "xtick.labelsize": 15,
            "ytick.labelsize": 15,
            "legend.fontsize": 16,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data()
    data.to_csv(SOURCE_DIR / "F6_workshop_fixed_cutoff_success_comparison.csv", index=False)

    fig, axes = plt.subplots(2, 3, figsize=(16.4, 9.0), sharex=True, sharey=True)
    handles = []
    for row, (dataset_label, _, _) in enumerate(INPUTS):
        for col, (threshold, threshold_value) in enumerate(THRESHOLDS):
            ax = axes[row, col]
            panel = data[(data["dataset_label"] == dataset_label) & (data["threshold"] == threshold)]
            for method, style in STYLES.items():
                curve = panel[(panel["method_plot"] == method) & panel["n_selected"].gt(0)].sort_values("cutoff")
                curve = curve.dropna(subset=["cutoff", "observed_success_fraction"])
                line = ax.plot(
                    curve["cutoff"],
                    curve["observed_success_fraction"],
                    linewidth=2.7,
                    markersize=6.5,
                    markeredgewidth=0,
                    **style,
                )[0]
                if row == 0 and col == 0:
                    handles.append(line)
            ax.set_title(f"DockQ $\\geq$ {threshold_value:.2f}", pad=8)
            ax.set_xlim(-0.02, 0.97)
            ax.set_ylim(-0.02, 1.02)
            ax.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8])
            ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
            ax.grid(True, alpha=0.15, linewidth=0.8)
            if col == 0:
                ax.set_ylabel("Fraction satisfying\nDockQ criterion")
            if row == 1:
                ax.set_xlabel("Score cutoff $c$")

    fig.text(0.016, 0.72, "Ab-Ag", rotation=90, va="center", ha="center", fontsize=19, fontweight="bold")
    fig.text(0.016, 0.285, "General", rotation=90, va="center", ha="center", fontsize=19, fontweight="bold")
    fig.legend(
        handles,
        [line.get_label() for line in handles],
        loc="upper center",
        ncol=4,
        frameon=False,
        bbox_to_anchor=(0.53, 1.01),
        columnspacing=1.4,
        handletextpad=0.5,
    )
    fig.tight_layout(rect=(0.035, 0.0, 1.0, 0.94), h_pad=2.2, w_pad=1.5)

    metadata = {"Creator": "alphafold-complex-calibration"}
    for suffix, kwargs in (("pdf", {"metadata": metadata}), ("png", {"dpi": 300})):
        fig.savefig(OUT_DIR / f"F6_workshop_fixed_cutoff_success_comparison.{suffix}", bbox_inches="tight", **kwargs)
    plt.close(fig)


if __name__ == "__main__":
    main()
