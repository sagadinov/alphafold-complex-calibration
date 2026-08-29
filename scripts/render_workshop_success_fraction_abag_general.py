#!/usr/bin/env python3
"""Render fixed-set success fractions with an Ab-Ag-only pDockQ2 refit.

The Ab-Ag pDockQ2 refit was trained for the Ab-Ag domain and is deliberately
not shown in the General panels. Candidate sets are fixed by raw ipTM; these
curves only compare the resulting success-fraction estimates.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
OUT = ANALYSIS / "workshop" / "figure_candidates"
SOURCE = OUT / "F2_workshop_success_fraction_abag_general_source.csv"
THRESHOLDS = [("acceptable", 0.23), ("medium", 0.49), ("high", 0.80)]
K_VALUES = [5, 10, 20, 50]

STYLES = {
    "Observed": {"color": "#111827", "marker": "o", "linestyle": "-", "linewidth": 2.8},
    "Raw ipTM": {"color": "#374151", "marker": "s", "linestyle": "--", "linewidth": 2.0},
    "Isotonic ipTM": {"color": "#2563EB", "marker": "o", "linestyle": "-", "linewidth": 2.3},
    "pDockQ2 (published)": {"color": "#F59E0B", "marker": "^", "linestyle": "--", "linewidth": 2.0},
    "pDockQ2 (Ab-Ag refit)": {"color": "#B45309", "marker": "^", "linestyle": "-", "linewidth": 2.0},
}
ABAG_METHODS = list(STYLES)
GENERAL_METHODS = ABAG_METHODS[:-1]


def rows_from_yield_table(table: pd.DataFrame, dataset: str, methods: dict[str, str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    table = table.copy()
    # The mixed numeric/"all" source column is read as strings by pandas.
    table["K_numeric"] = pd.to_numeric(table["K"], errors="coerce")
    subset = table.loc[
        (table["dataset"] == dataset)
        & (table["aggregation"] == "macro_fixed_K")
        & (table["K_numeric"].isin(K_VALUES))
    ]
    for _, record in subset.iterrows():
        for method, column in methods.items():
            rows.append(
                {
                    "dataset": dataset,
                    "dataset_label": "Ab-Ag" if dataset == "abag" else "General",
                    "threshold": record["threshold"],
                    "threshold_val": float(record["threshold_val"]),
                    "method": method,
                    "K": int(record["K_numeric"]),
                    "value_fraction": float(record[column]),
                    "n_targets": int(record["n_targets"]),
                    "n_models": int(record["n_models"]),
                }
            )
    return rows


def build_source() -> pd.DataFrame:
    abag = pd.read_csv(ANALYSIS / "workshop_yield_with_refit.csv")
    general = pd.read_csv(ANALYSIS / "workshop" / "workshop_yield_simplified.csv")
    abag_methods = {
        "Observed": "observed",
        "Raw ipTM": "raw_iptm",
        "Isotonic ipTM": "iso_iptm",
        "pDockQ2 (published)": "pdockq2",
        "pDockQ2 (Ab-Ag refit)": "pdockq2_refit",
    }
    general_methods = {
        "Observed": "observed",
        "Raw ipTM": "raw_iptm",
        "Isotonic ipTM": "iso_iptm",
        "pDockQ2 (published)": "pdockq2",
    }
    return pd.DataFrame(
        rows_from_yield_table(abag, "abag", abag_methods)
        + rows_from_yield_table(general, "general", general_methods)
    )


def render(source: pd.DataFrame) -> None:
    plt.rcParams.update({"font.size": 13, "axes.labelsize": 15, "axes.titlesize": 16,
                         "legend.fontsize": 13, "xtick.labelsize": 13, "ytick.labelsize": 13})
    fig, axes = plt.subplots(2, 3, figsize=(14.8, 8.4), sharey=True)
    for row_index, dataset in enumerate(["abag", "general"]):
        methods = ABAG_METHODS if dataset == "abag" else GENERAL_METHODS
        for col_index, (threshold, threshold_value) in enumerate(THRESHOLDS):
            ax = axes[row_index, col_index]
            panel = source.loc[(source["dataset"] == dataset) & (source["threshold"] == threshold)]
            if dataset == "abag":
                for method in methods:
                    line = panel.loc[panel["method"] == method].sort_values("K")
                    style = STYLES[method]
                    ax.plot(line["K"], line["value_fraction"], label=method if (row_index, col_index) == (0, 0) else None,
                            color=style["color"], marker=style["marker"], linestyle=style["linestyle"],
                            linewidth=style["linewidth"], markersize=6.5)
                ax.set_xticks(K_VALUES)
                ax.set_xlabel("K (candidates per target)")
            else:
                values = [float(panel.loc[panel["method"] == method, "value_fraction"].iloc[0]) for method in methods]
                x = np.arange(len(methods))
                ax.bar(x, values, color=[STYLES[method]["color"] for method in methods], edgecolor="none")
                ax.set_xticks(x, ["Observed", "Raw ipTM", "Iso. ipTM", "pDockQ2"], rotation=14)
            ax.set_title(f"DockQ >= {threshold_value:.2f}")
            ax.set_ylim(0, 0.58)
            ax.grid(axis="y", alpha=0.16)
            if col_index == 0:
                ax.set_ylabel("Fraction of success")
    fig.text(0.012, 0.72, "Ab-Ag", rotation=90, va="center", ha="center", fontsize=17,
             color="#4B5563", fontweight="bold")
    fig.text(0.012, 0.28, "General", rotation=90, va="center", ha="center", fontsize=17,
             color="#4B5563", fontweight="bold")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=5, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout(rect=(0.03, 0, 1, 0.95))
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "F2_workshop_success_fraction_abag_general_candidate.pdf", bbox_inches="tight")
    fig.savefig(OUT / "F2_workshop_success_fraction_abag_general_candidate.png", bbox_inches="tight", dpi=300)
    plt.close(fig)


def main() -> None:
    source = build_source()
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    source.to_csv(SOURCE, index=False)
    render(source)
    print(f"Wrote {SOURCE}")


if __name__ == "__main__":
    main()
