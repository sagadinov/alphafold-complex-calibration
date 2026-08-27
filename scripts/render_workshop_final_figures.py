#!/usr/bin/env python3
"""Render the redesigned workshop figures from frozen repository-local artifacts."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import ANALYSIS, DATA, PAPER_FIG, PDF_METADATA, THRESHOLDS, write_text
from compute_workshop_afdb_recalibration import OUTPUT as AFDB_SOURCE_CSV
from compute_workshop_afdb_recalibration import compute_source_data

WORKSHOP = ANALYSIS / "workshop"
DECISION = ANALYSIS / "decision_use"
SOURCE_DIR = PAPER_FIG / "source_data"
README = PAPER_FIG / "WORKSHOP_FIGURES_README.md"
SUMMARY = WORKSHOP / "figure_results_summary.md"

plt.rcParams.update(
    {
        "font.size": 12,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "legend.fontsize": 10,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
    }
)

RELIABILITY_METHODS = {
    "Raw ipTM": {"column_prefix": "p_raw_iptm", "color": "#374151", "linestyle": "--", "marker": "s"},
    "Isotonic ipTM": {"column_prefix": "p_iso_iptm", "color": "#2563EB", "linestyle": "-", "marker": "o"},
}

F2_STYLES = {
    "Observed": {"color": "#111827", "marker": "o", "linestyle": "-", "linewidth": 2.8},
    "Raw ipTM": {"color": "#374151", "marker": "s", "linestyle": "--", "linewidth": 2.0},
    "Isotonic ipTM": {"color": "#2563EB", "marker": "o", "linestyle": "-", "linewidth": 2.3},
    "pDockQ2 (published)": {"color": "#F59E0B", "marker": "^", "linestyle": ":", "linewidth": 2.0},
    "pDockQ2 (Ab-Ag refit)": {"color": "#B45309", "marker": "^", "linestyle": ":", "linewidth": 2.0},
}

F3_STYLES = {
    "Raw ipTM": {"color": "#374151", "linestyle": "--", "marker": "s"},
    "Isotonic ipTM (General frozen)": {"color": "#60A5FA", "linestyle": ":", "marker": "P"},
    "Isotonic ipTM (local AFDB)": {"color": "#2563EB", "linestyle": "-", "marker": "o"},
    "Raw ipSAEmax": {"color": "#10B981", "linestyle": "--", "marker": "D"},
    "Isotonic ipSAEmax (local AFDB)": {"color": "#059669", "linestyle": "-", "marker": "o"},
}

ABAG_ROWS = 62681
GENERAL_ROWS = 5496
AFDB_ROWS = 304
SOURCE_ROOT = Path(__file__).resolve().parents[1]


def load_predictions(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / f"{name}_predictions_v3.csv", low_memory=False)


def reliability_points(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> pd.DataFrame:
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    rows: list[dict[str, float | int]] = []
    for index in range(n_bins):
        if index < n_bins - 1:
            mask = (y_prob >= edges[index]) & (y_prob < edges[index + 1])
        else:
            mask = (y_prob >= edges[index]) & (y_prob <= edges[index + 1])
        count = int(mask.sum())
        if count == 0:
            continue
        rows.append(
            {
                "bin_index": index,
                "count": count,
                "mean_predicted": float(y_prob[mask].mean()),
                "observed_fraction": float(y_true[mask].mean()),
            }
        )
    return pd.DataFrame(rows)


def threshold_suffix(threshold_name: str) -> str:
    return threshold_name


def build_figure1_source() -> pd.DataFrame:
    abag = load_predictions("abag")
    general = load_predictions("general")
    if len(abag) != ABAG_ROWS:
        raise RuntimeError(f"Expected {ABAG_ROWS} Ab-Ag rows, found {len(abag)}")
    if len(general) != GENERAL_ROWS:
        raise RuntimeError(f"Expected {GENERAL_ROWS} General rows, found {len(general)}")

    metrics_lookup = {
        "abag": pd.read_csv(WORKSHOP / "workshop_abag_table.csv"),
        "general": pd.read_csv(WORKSHOP / "workshop_general_table.csv"),
    }
    name_map = {"Raw ipTM": "Raw ipTM", "Isotonic ipTM": "Iso. ipTM"}
    data_frames = {"abag": ("Ab-Ag", abag), "general": ("General", general)}
    rows: list[dict[str, object]] = []

    for dataset_key, (dataset_label, df) in data_frames.items():
        for threshold_name, threshold_value in THRESHOLDS:
            y_true = (df["dockq"].to_numpy(dtype=float) >= threshold_value).astype(int)
            metric_rows = metrics_lookup[dataset_key]
            for method_name, spec in RELIABILITY_METHODS.items():
                if method_name == "Raw ipTM":
                    column = spec["column_prefix"]
                else:
                    column = f"{spec['column_prefix']}_{threshold_suffix(threshold_name)}"
                points = reliability_points(y_true, df[column].to_numpy(dtype=float))
                metric_row = metric_rows.loc[
                    (metric_rows["threshold"] == threshold_name)
                    & (metric_rows["method"] == name_map[method_name])
                ]
                if metric_row.empty:
                    raise RuntimeError(f"Missing workshop metric row for {dataset_key}/{threshold_name}/{method_name}")
                metric_row = metric_row.iloc[0]
                for _, point in points.iterrows():
                    rows.append(
                        {
                            "dataset": dataset_key,
                            "dataset_label": dataset_label,
                            "threshold": threshold_name,
                            "threshold_val": threshold_value,
                            "method": method_name,
                            "source_file": str((DATA / f"{dataset_key}_predictions_v3.csv").relative_to(SOURCE_ROOT)),
                            "brier": float(metric_row["brier"]),
                            "ece": float(metric_row["ece"]),
                            "auroc": float(metric_row["auroc"]),
                            "bin_index": int(point["bin_index"]),
                            "count": int(point["count"]),
                            "mean_predicted": float(point["mean_predicted"]),
                            "observed_fraction": float(point["observed_fraction"]),
                        }
                    )
    source = pd.DataFrame(rows)
    if source.empty:
        raise RuntimeError("Figure 1 source data is empty")
    return source


def render_figure1_panels(source: pd.DataFrame, dataset_order: list[str], out_base: str, figsize: tuple[float, float]) -> None:
    fig, axes = plt.subplots(len(dataset_order), 3, figsize=figsize, sharex=True, sharey=True)
    if len(dataset_order) == 1:
        axes = np.asarray([axes])
    for row_index, dataset_key in enumerate(dataset_order):
        for col_index, (threshold_name, threshold_value) in enumerate(THRESHOLDS):
            ax = axes[row_index, col_index]
            panel = source.loc[
                (source["dataset"] == dataset_key) & (source["threshold"] == threshold_name)
            ].copy()
            for method_name, spec in RELIABILITY_METHODS.items():
                line = panel.loc[panel["method"] == method_name].sort_values("mean_predicted")
                ax.plot(
                    line["mean_predicted"],
                    line["observed_fraction"],
                    color=spec["color"],
                    linestyle=spec["linestyle"],
                    marker=spec["marker"],
                    linewidth=2.7 if method_name == "Isotonic ipTM" else 2.2,
                    markersize=6,
                    label=method_name if (row_index, col_index) == (0, 0) else None,
                )
            ax.plot([0, 1], [0, 1], "k--", linewidth=1.0, alpha=0.35)
            dataset_label = panel["dataset_label"].iloc[0]
            title = f"{dataset_label}: DockQ >= {threshold_value:.2f}" if len(dataset_order) == 1 else f"DockQ >= {threshold_value:.2f}"
            ax.set_title(title)
            ax.set_xlim(-0.02, 1.02)
            ax.set_ylim(-0.02, 1.02)
            ax.grid(alpha=0.14)
            if col_index == 0:
                ax.set_ylabel("Observed fraction")
            if row_index == len(dataset_order) - 1:
                ax.set_xlabel("Score / predicted probability")
            if len(dataset_order) > 1:
                ax.text(
                    0.03,
                    0.92,
                    panel["dataset_label"].iloc[0],
                    transform=ax.transAxes,
                    fontsize=11,
                    color="#4B5563",
                    fontweight="bold",
                )
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(PAPER_FIG / f"{out_base}.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    fig.savefig(PAPER_FIG / f"{out_base}.png", bbox_inches="tight", dpi=300)
    plt.close(fig)


def build_f2_source(variant: str) -> pd.DataFrame:
    if variant not in {"published", "refit"}:
        raise ValueError(f"Unknown Figure 2 variant: {variant}")
    workshop = pd.read_csv(WORKSHOP / "workshop_yield_simplified.csv")
    workshop = workshop.loc[(workshop["dataset"] == "abag") & (workshop["aggregation"] == "macro_fixed_K")].copy()
    workshop["K_numeric"] = pd.to_numeric(workshop["K"], errors="coerce")
    if variant == "published":
        pdock_source = workshop.copy()
        pdock_pred_col = "pdockq2"
        pdock_mae_col = "mae_pdockq2"
        pdock_label = "pDockQ2 (published)"
        source_path = ANALYSIS / "workshop" / "workshop_yield_simplified.csv"
    else:
        pdock_source = pd.read_csv(ANALYSIS / "workshop_yield_with_refit.csv")
        pdock_source = pdock_source.loc[(pdock_source["dataset"] == "abag") & (pdock_source["aggregation"] == "macro_fixed_K")].copy()
        pdock_source["K_numeric"] = pd.to_numeric(pdock_source["K"], errors="coerce")
        pdock_pred_col = "pdockq2_refit"
        pdock_mae_col = "mae_pdockq2_refit"
        pdock_label = "pDockQ2 (Ab-Ag refit)"
        source_path = ANALYSIS / "workshop_yield_with_refit.csv"

    selection = pd.read_csv(DECISION / "fixed_ranking_yield_per_target.csv")
    selection = selection.loc[
        (selection["dataset"] == "abag")
        & (selection["ranking_family"] == "iptm")
        & (selection["comparison_universe"] == "three_method_common")
        & (selection["selection_score"] == "p_raw_iptm")
        & (selection["probability_method"] == "all_methods")
    ]
    if selection.empty:
        raise RuntimeError("Missing fixed-ranking per-target selection audit rows for Figure 2")
    if selection["selected_model_ids"].isna().any():
        raise RuntimeError("Figure 2 selection audit contains missing candidate identities")

    metrics = pd.read_csv(DECISION / "fixed_ranking_yield_metrics.csv")
    metrics = metrics.loc[
        (metrics["dataset"] == "abag")
        & (metrics["ranking_family"] == "iptm")
        & (metrics["comparison_universe"] == "three_method_common")
        & (metrics["probability_method"].isin(["Raw ipTM", "Isotonic ipTM"]))
    ].copy()
    metrics["K_numeric"] = pd.to_numeric(metrics["K"], errors="coerce")

    rows: list[dict[str, object]] = []
    for threshold_name, threshold_value in THRESHOLDS:
        top_row = workshop.loc[(workshop["threshold"] == threshold_name) & (workshop["K_numeric"] == 20)]
        if top_row.empty:
            raise RuntimeError(f"Missing K=20 workshop row for {threshold_name}")
        top_row = top_row.iloc[0]
        pdock_top_row = pdock_source.loc[(pdock_source["threshold"] == threshold_name) & (pdock_source["K_numeric"] == 20)]
        if pdock_top_row.empty:
            raise RuntimeError(f"Missing K=20 {pdock_label} row for {threshold_name}")
        pdock_top_row = pdock_top_row.iloc[0]
        for method_name, value in {
            "Observed": top_row.get("observed"),
            "Raw ipTM": top_row.get("raw_iptm"),
            "Isotonic ipTM": top_row.get("iso_iptm"),
            pdock_label: pdock_top_row.get(pdock_pred_col),
        }.items():
            if pd.isna(value):
                continue
            rows.append(
                {
                    "panel": "K20_models_passing",
                    "variant": variant,
                    "threshold": threshold_name,
                    "threshold_val": threshold_value,
                    "method": method_name,
                    "K": 20,
                    "value": float(value) * 20.0,
                    "value_fraction": float(value),
                    "source_file": str(source_path.relative_to(SOURCE_ROOT)),
                }
            )

        for method_name, metric_col, source_df, file_path in [
            ("Raw ipTM", "normalized_mae", metrics.loc[(metrics["dockq_threshold_name"] == threshold_name) & (metrics["probability_method"] == "Raw ipTM")], DECISION / "fixed_ranking_yield_metrics.csv"),
            ("Isotonic ipTM", "normalized_mae", metrics.loc[(metrics["dockq_threshold_name"] == threshold_name) & (metrics["probability_method"] == "Isotonic ipTM")], DECISION / "fixed_ranking_yield_metrics.csv"),
        ]:
            for _, row in source_df.iterrows():
                rows.append(
                    {
                        "panel": "mae_across_K",
                        "variant": variant,
                        "threshold": threshold_name,
                        "threshold_val": threshold_value,
                        "method": method_name,
                        "K": int(row["K_numeric"]),
                        "value": float(row[metric_col]),
                        "value_fraction": np.nan,
                        "source_file": str(file_path.relative_to(SOURCE_ROOT)),
                    }
                )

        source_slice = pdock_source.loc[pdock_source["threshold"] == threshold_name]
        for _, row in source_slice.iterrows():
            if pd.isna(row[pdock_mae_col]):
                continue
            rows.append(
                {
                    "panel": "mae_across_K",
                    "variant": variant,
                    "threshold": threshold_name,
                    "threshold_val": threshold_value,
                    "method": pdock_label,
                    "K": int(row["K_numeric"]),
                    "value": float(row[pdock_mae_col]),
                    "value_fraction": np.nan,
                    "source_file": str(source_path.relative_to(SOURCE_ROOT)),
                }
            )
    return pd.DataFrame(rows)


def render_figure2(source: pd.DataFrame, variant: str) -> None:
    pdock_label = "pDockQ2 (published)" if variant == "published" else "pDockQ2 (Ab-Ag refit)"
    fig, axes = plt.subplots(2, 3, figsize=(13.8, 7.8))
    for col_index, (threshold_name, threshold_value) in enumerate(THRESHOLDS):
        top_ax = axes[0, col_index]
        top = source.loc[
            (source["panel"] == "K20_models_passing") & (source["threshold"] == threshold_name)
        ].copy()
        method_order = ["Observed", "Raw ipTM", "Isotonic ipTM", pdock_label]
        x = np.arange(len(method_order))
        values = [float(top.loc[top["method"] == method, "value"].iloc[0]) for method in method_order]
        bars = top_ax.bar(
            x,
            values,
            color=[F2_STYLES[method]["color"] for method in method_order],
            edgecolor="none",
        )
        for bar, alpha in zip(bars, [1.0, 0.92, 0.96, 0.9]):
            bar.set_alpha(alpha)
        for bar, value in zip(bars, values):
            top_ax.text(bar.get_x() + bar.get_width() / 2.0, value + 0.35, f"{value:.1f}", ha="center", va="bottom", fontsize=10)
        top_ax.set_xticks(x)
        top_ax.set_xticklabels(["Observed", "Raw ipTM", "Iso. ipTM", "pDockQ2"], rotation=18)
        top_ax.set_ylim(0.0, 20.8)
        top_ax.set_title(f"DockQ >= {threshold_value:.2f}")
        top_ax.set_ylabel("Models passing threshold\nout of 20")
        top_ax.grid(axis="y", alpha=0.16)

        bottom_ax = axes[1, col_index]
        bottom = source.loc[
            (source["panel"] == "mae_across_K") & (source["threshold"] == threshold_name)
        ].copy()
        for method_name in ["Raw ipTM", "Isotonic ipTM", pdock_label]:
            line = bottom.loc[bottom["method"] == method_name].sort_values("K")
            if line.empty:
                continue
            style = F2_STYLES[method_name]
            bottom_ax.plot(
                line["K"],
                line["value"],
                color=style["color"],
                linestyle=style["linestyle"],
                marker=style["marker"],
                linewidth=style["linewidth"],
                markersize=6,
                label=method_name if col_index == 0 else None,
            )
        bottom_ax.set_xlabel("K")
        bottom_ax.set_ylabel("Mean per-target absolute error\nin predicted success fraction")
        bottom_ax.grid(axis="y", alpha=0.16)
        bottom_ax.set_xticks(sorted(bottom["K"].unique()))
    handles, labels = axes[1, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.01))
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out_base = f"F2_workshop_fixedset_{variant}"
    fig.savefig(PAPER_FIG / f"{out_base}.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    fig.savefig(PAPER_FIG / f"{out_base}.png", bbox_inches="tight", dpi=300)
    plt.close(fig)


def render_figure3(source: pd.DataFrame, out_dir: Path = PAPER_FIG, out_base: str = "F3_workshop_afdb_recalibration") -> None:
    fig, axes = plt.subplots(2, 3, figsize=(14.2, 8.0), sharex=True)
    local_methods = ["Isotonic ipTM (local AFDB)", "Isotonic ipSAEmax (local AFDB)"]
    # Nearest supported n=5-grid values to 1%, 5%, 10%, 20%, and 30% of 304.
    display_train_sizes = {5, 15, 30, 60, 90}
    for col_index, (threshold_name, threshold_value) in enumerate(THRESHOLDS):
        for row_index, metric in enumerate(["brier", "ece"]):
            ax = axes[row_index, col_index]
            panel = source.loc[(source["threshold"] == threshold_name) & (source["metric"] == metric)].copy()
            # Baselines are evaluated once on all 304 complexes and therefore
            # appear as flat reference lines without split-wise error bars.
            for method_name in ["Raw ipTM", "Isotonic ipTM (General frozen)", "Raw ipSAEmax"]:
                line = panel.loc[(panel["method"] == method_name) & (panel["available"])].sort_values("train_size")
                if line.empty:
                    continue
                style = F3_STYLES[method_name]
                ax.axhline(
                    float(line["mean"].iloc[0]),
                    color=style["color"],
                    # All reference baselines use the same unobtrusive dash.
                    linestyle="--",
                    linewidth=2.8,
                    alpha=0.65,
                    label=method_name if (row_index, col_index) == (0, 0) else None,
                )
            for method_name in local_methods:
                line = panel.loc[
                    (panel["method"] == method_name)
                    & (panel["available"])
                    & (panel["train_size"].isin(display_train_sizes))
                ].sort_values("train_size")
                if line.empty:
                    continue
                style = F3_STYLES[method_name]
                # The source CSV retains SD and all repeat-level values, but
                # the main Figure 3 intentionally shows local means only.
                ax.plot(
                    line["train_size"].to_numpy(float) / 304.0 * 100.0,
                    line["mean"],
                    color=style["color"],
                    linestyle="-",
                    linewidth=2.8,
                    label=method_name if (row_index, col_index) == (0, 0) else None,
                )
            ax.set_title(f"DockQ >= {threshold_value:.2f}", fontsize=17)
            ax.set_xticks([1, 5, 10, 20, 30])
            ax.set_xlim(0.5, 33.5)
            ax.grid(axis="y", alpha=0.16)
            ax.tick_params(axis="both", labelsize=13)
            if col_index == 0:
                ax.set_ylabel("Brier score" if metric == "brier" else "ECE (10 bins)", fontsize=16)
            if row_index == 1:
                ax.set_xlabel("AFDB dataset used for calibration (%)", fontsize=15)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.035), fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{out_base}.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    fig.savefig(out_dir / f"{out_base}.png", bbox_inches="tight", dpi=300)
    plt.close(fig)


def write_source_csvs(fig1: pd.DataFrame, f2_pub: pd.DataFrame, f2_refit: pd.DataFrame, f3: pd.DataFrame) -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    fig1.to_csv(SOURCE_DIR / "F1_workshop_within_domain_reliability.csv", index=False)
    f2_pub.to_csv(SOURCE_DIR / "F2_workshop_fixedset_published.csv", index=False)
    f2_refit.to_csv(SOURCE_DIR / "F2_workshop_fixedset_refit.csv", index=False)
    f3.to_csv(SOURCE_DIR / "F3_workshop_afdb_recalibration.csv", index=False)


def write_readme() -> None:
    text = """# Workshop Figure Reproduction

## Commands

Run from the repository root:

```bash
/proj/berzelius-2021-29/users/x_sasag/projects/af3_atlas/.venv_threshold_analysis311/bin/python scripts/render_workshop_final_figures.py
```

This script will recompute the AFDB local-recalibration source table and then render:

- `paper/figures/F1_workshop_within_domain_reliability_2x3.pdf`
- `paper/figures/F1_workshop_within_domain_reliability_abag.pdf`
- `paper/figures/F2_workshop_fixedset_published.pdf`
- `paper/figures/F2_workshop_fixedset_refit.pdf`
- `paper/figures/F3_workshop_afdb_recalibration.pdf`

PNG previews are written alongside each PDF.

## Canonical inputs

- Figure 1: `data/abag_predictions_v3.csv`, `data/general_predictions_v3.csv`, `analysis/workshop/workshop_abag_table.csv`, `analysis/workshop/workshop_general_table.csv`
- Figure 2 published variant: `analysis/workshop/workshop_yield_simplified.csv`, `analysis/decision_use/fixed_ranking_yield_metrics.csv`, `analysis/decision_use/fixed_ranking_yield_per_target.csv`
- Figure 2 refit variant: `analysis/workshop_yield_with_refit.csv`, `analysis/decision_use/fixed_ranking_yield_metrics.csv`, `analysis/decision_use/fixed_ranking_yield_per_target.csv`
- Figure 3: `analysis/afdb/afdb_positive_dockq_features.csv`, `data/general_v2.csv`

## Source-data CSVs

Machine-readable source-data tables are written to `paper/figures/source_data/`.

## Assertions enforced by the scripts

- Ab-Ag within-domain evaluation universe is exactly 62,681 rows.
- General within-domain evaluation universe is exactly 5,496 rows.
- AFDB structural recalibration universe is exactly 304 finite-DockQ complexes.
- Figure 2 uses the fixed-candidate audit from `analysis/decision_use/fixed_ranking_yield_per_target.csv`.
- AFDB local recalibration uses disjoint calibration/evaluation splits, paired between ipTM and ipSAEmax.
"""
    write_text(README, text)


def write_summary(fig1: pd.DataFrame, f2_pub: pd.DataFrame, f2_refit: pd.DataFrame, f3: pd.DataFrame) -> None:
    lines = ["# Workshop Figure Results Summary", ""]
    for dataset_key, dataset_label in [("abag", "Ab-Ag"), ("general", "General")]:
        for threshold_name, threshold_value in THRESHOLDS:
            subset = fig1.loc[
                (fig1["dataset"] == dataset_key) & (fig1["threshold"] == threshold_name)
            ]
            raw = subset.loc[subset["method"] == "Raw ipTM"].iloc[0]
            iso = subset.loc[subset["method"] == "Isotonic ipTM"].iloc[0]
            lines.append(
                f"- Figure 1, {dataset_label}, DockQ >= {threshold_value:.2f}: ECE {raw['ece']:.4f} -> {iso['ece']:.4f}, "
                f"Brier {raw['brier']:.4f} -> {iso['brier']:.4f}."
            )
    lines.append("")
    for threshold_name, threshold_value in THRESHOLDS:
        top_pub = f2_pub.loc[
            (f2_pub["panel"] == "K20_models_passing") & (f2_pub["threshold"] == threshold_name)
        ]
        observed = float(top_pub.loc[top_pub["method"] == "Observed", "value"].iloc[0])
        raw = float(top_pub.loc[top_pub["method"] == "Raw ipTM", "value"].iloc[0])
        iso = float(top_pub.loc[top_pub["method"] == "Isotonic ipTM", "value"].iloc[0])
        pdock = float(top_pub.loc[top_pub["method"] == "pDockQ2 (published)", "value"].iloc[0])
        lines.append(
            f"- Figure 2 published, DockQ >= {threshold_value:.2f}, K=20: observed {observed:.2f}/20, "
            f"Raw ipTM {raw:.2f}/20, Isotonic ipTM {iso:.2f}/20, pDockQ2 published {pdock:.2f}/20."
        )
    lines.append("")
    unavailable = f3.loc[(~f3["available"]) & (f3["train_size"] == 1)]
    if not unavailable.empty:
        lines.append("- Figure 3: `train_size = 1` is unavailable under the paired disjoint stratified protocol; the curves therefore begin at 5 examples.")
    for threshold_name, threshold_value in THRESHOLDS:
        subset = f3.loc[(f3["threshold"] == threshold_name) & (f3["metric"] == "brier") & (f3["available"])].copy()
        local_iptm = subset.loc[subset["method"] == "Isotonic ipTM (local AFDB)"].sort_values("train_size")
        local_ipsae = subset.loc[subset["method"] == "Isotonic ipSAEmax (local AFDB)"].sort_values("train_size")
        frozen = subset.loc[subset["method"] == "Isotonic ipTM (General frozen)"].sort_values("train_size")
        if not local_iptm.empty and not local_ipsae.empty and not frozen.empty:
            lines.append(
                f"- Figure 3, DockQ >= {threshold_value:.2f}: local isotonic ipTM Brier reaches {local_iptm['mean'].min():.4f}; "
                f"local isotonic ipSAEmax reaches {local_ipsae['mean'].min():.4f}; "
                f"frozen General isotonic ipTM averages {frozen['mean'].mean():.4f} across the matched holdout splits."
            )
    write_text(SUMMARY, "\n".join(lines).rstrip() + "\n")


def main() -> None:
    fig1_source = build_figure1_source()
    f2_pub_source = build_f2_source("published")
    f2_refit_source = build_f2_source("refit")
    f3_source = pd.read_csv(AFDB_SOURCE_CSV) if AFDB_SOURCE_CSV.exists() else compute_source_data()

    write_source_csvs(fig1_source, f2_pub_source, f2_refit_source, f3_source)
    write_readme()
    render_figure1_panels(fig1_source, ["abag", "general"], "F1_workshop_within_domain_reliability_2x3", (14.0, 8.0))
    render_figure1_panels(fig1_source, ["abag"], "F1_workshop_within_domain_reliability_abag", (14.0, 4.4))
    render_figure2(f2_pub_source, "published")
    render_figure2(f2_refit_source, "refit")
    render_figure3(f3_source)
    write_summary(fig1_source, f2_pub_source, f2_refit_source, f3_source)
    print("Saved workshop figures, source-data CSVs, README, and results summary.")


if __name__ == "__main__":
    main()
