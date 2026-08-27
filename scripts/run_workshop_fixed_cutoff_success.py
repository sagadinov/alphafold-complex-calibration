#!/usr/bin/env python3
"""Describe empirical success fractions above fixed frozen score cutoffs on Ab-Ag.

This is a descriptive held-out analysis. Cutoffs are a predefined grid and are
never optimized against Ab-Ag test labels. No model is fitted or refitted here.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import DATA, PDF_METADATA, THRESHOLDS, write_text


ROOT = Path(__file__).resolve().parents[1]
WORKSHOP = ROOT / "analysis" / "workshop"
OUT_DIR = WORKSHOP / "fixed_cutoff_success"
SOURCE = DATA / "abag_predictions_v3.csv"
# The regular descriptive grid plus the published pDockQ2 reference cutoff .23.
GRID = np.unique(np.round(np.r_[np.arange(0.0, 0.951, 0.05), 0.23], 2))
SUMMARY_CUTOFF = 0.80
DESCRIPTIVE_PDOCKQ2_CUTOFF = 0.23

REFIT = {"L": 2.0, "k": 0.01947584, "x0": 40.21941805, "b": -0.65947117, "d0": 10.0}

STYLES = {
    "Raw ipTM": {"color": "#374151", "linestyle": "--", "marker": "s"},
    "Isotonic ipTM": {"color": "#2563EB", "linestyle": "-", "marker": "o"},
    "pDockQ2 (published)": {"color": "#F59E0B", "linestyle": "--", "marker": "^"},
    "pDockQ2 (Ab-Ag refit)": {"color": "#B45309", "linestyle": "-", "marker": "^"},
    "pDockQ2 (General refit)": {"color": "#B45309", "linestyle": "-", "marker": "^"},
}


def verified_refit_scores(frame: pd.DataFrame) -> np.ndarray:
    """Recompute the requested refit score from the specified frozen parameters."""
    xi = (1.0 / (1.0 + (frame["iface_pae_mean"].to_numpy(float) / REFIT["d0"]) ** 2)) * frame["mean_plddt"].to_numpy(float)
    expected = np.clip(
        REFIT["L"] / (1.0 + np.exp(-REFIT["k"] * (xi - REFIT["x0"]))) + REFIT["b"],
        0.0,
        1.0,
    )
    observed = frame["p_pdockq2_refit"].to_numpy(float)
    # CSV serialization of the frozen score column differs only at <1e-7.
    if not np.allclose(expected, observed, rtol=0.0, atol=1e-7):
        raise RuntimeError("Frozen pDockQ2 refit column differs materially from the specified verified parameters.")
    return expected


def score_columns(threshold_name: str, refit_label: str, refit_column: str) -> dict[str, str]:
    return {
        "Raw ipTM": "p_raw_iptm",
        "Isotonic ipTM": f"p_iso_iptm_{threshold_name}",
        "pDockQ2 (published)": "p_pdockq2_published",
        refit_label: refit_column,
    }


def compute_cutoff_table(frame: pd.DataFrame, dataset_label: str, refit_label: str, refit_column: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    total = len(frame)
    for threshold_name, threshold_value in THRESHOLDS:
        labels = (frame["dockq"].to_numpy(float) >= threshold_value).astype(int)
        for method, column in score_columns(threshold_name, refit_label, refit_column).items():
            scores = frame[column].to_numpy(float)
            for cutoff in GRID:
                selected = np.isfinite(scores) & (scores >= cutoff)
                n_selected = int(selected.sum())
                rows.append(
                    {
                        "dataset": dataset_label,
                        "n_total": total,
                        "threshold": threshold_name,
                        "threshold_val": threshold_value,
                        "method": method,
                        "score_column": column,
                        "cutoff": cutoff,
                        "n_selected": n_selected,
                        "fraction_selected": n_selected / total,
                        "observed_success_fraction": float(labels[selected].mean()) if n_selected else np.nan,
                    }
                )
    return pd.DataFrame(rows)


def render(table: pd.DataFrame, pdock_method: str, out_base: str, out_dir: Path) -> None:
    methods = ["Raw ipTM", "Isotonic ipTM", pdock_method]
    plt.rcParams.update({"font.size": 12, "axes.labelsize": 13, "axes.titlesize": 14, "legend.fontsize": 10, "xtick.labelsize": 11, "ytick.labelsize": 11})
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), sharey=True)
    for ax, (threshold_name, threshold_value) in zip(axes, THRESHOLDS):
        panel = table.loc[(table["threshold"] == threshold_name) & (table["method"].isin(methods))]
        for method in methods:
            line = panel.loc[(panel["method"] == method) & panel["observed_success_fraction"].notna()]
            style = STYLES[method]
            ax.plot(
                line["cutoff"],
                line["observed_success_fraction"],
                color=style["color"],
                linestyle=style["linestyle"],
                marker=style["marker"],
                linewidth=2.0,
                markersize=5,
                label=method if threshold_name == "acceptable" else None,
            )
        ax.set_title(f"DockQ >= {threshold_value:.2f}")
        ax.set_xlim(-0.02, 0.97)
        ax.set_ylim(-0.02, 1.02)
        ax.set_xticks(np.arange(0.0, 1.01, 0.2))
        ax.grid(alpha=0.16)
        ax.set_xlabel("Score cutoff c")
    axes[0].set_ylabel("Fraction satisfying DockQ criterion")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.03))
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    fig.savefig(out_dir / f"{out_base}.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    fig.savefig(out_dir / f"{out_base}.png", bbox_inches="tight", dpi=300)
    plt.close(fig)


def format_summary(table: pd.DataFrame, refit_label: str) -> pd.DataFrame:
    methods = ["Raw ipTM", "Isotonic ipTM", "pDockQ2 (published)", refit_label]
    summary = table.loc[(table["cutoff"] == SUMMARY_CUTOFF) & table["method"].isin(methods)].copy()
    descriptive = table.loc[
        (table["cutoff"] == DESCRIPTIVE_PDOCKQ2_CUTOFF)
        & table["method"].isin(["pDockQ2 (published)", refit_label])
    ].copy()
    summary["cutoff_label"] = "hard-coded c=0.80"
    descriptive["cutoff_label"] = "descriptive pDockQ2 c=0.23"
    return pd.concat([summary, descriptive], ignore_index=True)


def markdown_table(frame: pd.DataFrame) -> str:
    """Render the small review table without requiring the optional tabulate package."""
    headers = list(frame.columns)
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for _, row in frame.iterrows():
        values = []
        for column in headers:
            value = row[column]
            if pd.isna(value):
                values.append("NA")
            elif isinstance(value, (float, np.floating)):
                values.append(f"{value:.4f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Describe frozen fixed-cutoff success fractions.")
    parser.add_argument("--dataset", choices=["abag", "general"], default="abag")
    args = parser.parse_args()

    if args.dataset == "abag":
        source, out_dir, expected_rows, dataset_label = SOURCE, OUT_DIR, 62681, "Ab-Ag"
        refit_label, refit_column = "pDockQ2 (Ab-Ag refit)", "p_pdockq2_refit_verified"
    else:
        source, out_dir, expected_rows, dataset_label = DATA / "general_predictions_v3.csv", WORKSHOP / "fixed_cutoff_success_general", 5496, "General OOF"
        refit_label, refit_column = "pDockQ2 (General refit)", "p_pdockq2_refit"

    out_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(source, low_memory=False)
    if len(frame) != expected_rows:
        raise RuntimeError(f"Expected {expected_rows:,} frozen {dataset_label} rows, found {len(frame):,}.")
    if args.dataset == "abag":
        frame[refit_column] = verified_refit_scores(frame)
    table = compute_cutoff_table(frame, dataset_label, refit_label, refit_column)
    summary = format_summary(table, refit_label)
    dataset_suffix = "abag" if args.dataset == "abag" else "general"
    table.to_csv(out_dir / f"fixed_cutoff_success_{dataset_suffix}.csv", index=False)
    summary.to_csv(out_dir / "fixed_cutoff_success_c080_summary.csv", index=False)
    figure_prefix = "F2_fixed_cutoff_success" if args.dataset == "abag" else "F2_general_fixed_cutoff_success"
    render(table, "pDockQ2 (published)", f"{figure_prefix}_published", out_dir)
    render(table, refit_label, f"{figure_prefix}_refit", out_dir)

    display = summary.loc[:, ["threshold", "threshold_val", "cutoff_label", "method", "n_selected", "fraction_selected", "observed_success_fraction"]]
    print("\nHard-coded cutoff summary (no test-label optimization):")
    print(display.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    text = f"# Fixed Cutoff Success-Fraction Analysis ({dataset_label})\n\n"
    text += f"Frozen input: `{source.relative_to(ROOT)}` ({expected_rows:,} rows). No score was fitted or refitted during this analysis.\n\n"
    text += "For each fixed cutoff $c$, the reported value is $P(\\mathrm{DockQ} \\ge t \\mid s \\ge c)$. The cutoff grid is 0.00 to 0.95 in increments of 0.05. Rows with zero selected models are retained in the CSV with an undefined success fraction and omitted from the plotted line.\n\n"
    text += "`c=0.80` is reported for every method without substitution. The separate pDockQ2 `c=0.23` rows are descriptive fixed-cutoff rows, included because .8 may retain relatively few pDockQ2 predictions.\n\n"
    text += "## c=0.80 and descriptive pDockQ2 c=0.23\n\n"
    text += markdown_table(display) + "\n"
    write_text(out_dir / "README.md", text)
    print(f"\nSaved: {out_dir}")
    if args.dataset == "abag":
        print("Verified frozen pDockQ2 refit column against L=2, k=0.01947584, x0=40.21941805, b=-0.65947117, d0=10.")


if __name__ == "__main__":
    main()
