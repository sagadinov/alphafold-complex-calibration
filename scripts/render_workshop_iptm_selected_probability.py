#!/usr/bin/env python3
"""Compare probability estimates on candidate sets fixed by raw ipTM cutoffs."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "paper/figures"
SOURCE_OUT = OUT / "source_data"
THRESHOLDS = [("acceptable", 0.23), ("medium", 0.49), ("high", 0.80)]
CUTOFFS = np.round(np.arange(0.0, 0.951, 0.05), 2)

DATASETS = [
    ("Ab-Ag", DATA / "abag_predictions_v3.csv", "p_pdockq2_refit", "pDockQ2 (Ab-Ag refit)"),
    ("General", DATA / "general_predictions_v3.csv", "p_pdockq2_refit", "pDockQ2 (General refit)"),
]

STYLES = {
    "Observed": {"color": "#111827", "linestyle": "-", "marker": "o", "label": "Observed"},
    "Isotonic ipTM": {"color": "#2563EB", "linestyle": "-", "marker": "o", "label": "Isotonic ipTM"},
    "pDockQ2 (published)": {"color": "#F59E0B", "linestyle": "--", "marker": "^", "label": "pDockQ2 (published)"},
    "pDockQ2 (refit)": {"color": "#B45309", "linestyle": "-", "marker": "^", "label": "pDockQ2 (refit)"},
}


def compute_dataset(dataset: str, path: Path, refit_column: str, refit_label: str) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False)
    if dataset == "Ab-Ag":
        # Recreate the verified frozen Ab-Ag refit score; this is a deterministic
        # alias used because the CSV itself stores only p_pdockq2_refit.
        xi = (1.0 / (1.0 + (frame["iface_pae_mean"].to_numpy(float) / 10.0) ** 2)) * frame["mean_plddt"].to_numpy(float)
        frame["p_pdockq2_refit"] = np.clip(
            2.0 / (1.0 + np.exp(-0.01947584 * (xi - 40.21941805))) - 0.65947117,
            0.0,
            1.0,
        )
    rows = []
    for threshold_name, threshold_value in THRESHOLDS:
        label = (frame["dockq"].to_numpy(float) >= threshold_value).astype(float)
        probabilities = {
            "Isotonic ipTM": frame[f"p_iso_iptm_{threshold_name}"].to_numpy(float),
            "pDockQ2 (published)": frame["p_pdockq2_published"].to_numpy(float),
            "pDockQ2 (refit)": frame[refit_column].to_numpy(float),
        }
        iptm = frame["iptm"].to_numpy(float)
        for cutoff in CUTOFFS:
            selected = np.isfinite(iptm) & (iptm >= cutoff)
            row = {
                "dataset": dataset,
                "n_total": len(frame),
                "threshold": threshold_name,
                "threshold_val": threshold_value,
                "iptm_cutoff": cutoff,
                "n_selected": int(selected.sum()),
                "fraction_selected": float(selected.mean()),
                "observed_success_fraction": float(label[selected].mean()) if selected.any() else np.nan,
                "refit_source_label": refit_label,
            }
            for method, values in probabilities.items():
                valid = selected & np.isfinite(values)
                row[f"predicted_{method}"] = float(values[valid].mean()) if valid.any() else np.nan
                row[f"n_valid_{method}"] = int(valid.sum())
            rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    plt.rcParams.update({
        "font.size": 16, "axes.labelsize": 18, "axes.titlesize": 19,
        "xtick.labelsize": 15, "ytick.labelsize": 15, "legend.fontsize": 16,
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })
    OUT.mkdir(parents=True, exist_ok=True)
    SOURCE_OUT.mkdir(parents=True, exist_ok=True)
    table = pd.concat([compute_dataset(*spec) for spec in DATASETS], ignore_index=True)
    table.to_csv(SOURCE_OUT / "F7_workshop_iptm_selected_probability.csv", index=False)

    fig, axes = plt.subplots(2, 3, figsize=(16.4, 9.0), sharex=True, sharey=True)
    handles = []
    for row, (dataset, _, _, _) in enumerate(DATASETS):
        for col, (threshold_name, threshold_value) in enumerate(THRESHOLDS):
            ax = axes[row, col]
            panel = table[(table["dataset"] == dataset) & (table["threshold"] == threshold_name)]
            series = {
                "Observed": panel["observed_success_fraction"],
                "Isotonic ipTM": panel["predicted_Isotonic ipTM"],
                "pDockQ2 (published)": panel["predicted_pDockQ2 (published)"],
                "pDockQ2 (refit)": panel["predicted_pDockQ2 (refit)"],
            }
            for method, values in series.items():
                valid = values.notna() & panel["n_selected"].gt(0)
                style = STYLES[method]
                line = ax.plot(
                    panel.loc[valid, "iptm_cutoff"], values[valid], linewidth=2.7,
                    markersize=6.5, markeredgewidth=0, **style,
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
                ax.set_ylabel("Observed / predicted\nsuccess fraction")
            if row == 1:
                ax.set_xlabel("Raw ipTM selection cutoff $c$")

    fig.text(0.016, 0.72, "Ab-Ag", rotation=90, va="center", ha="center", fontsize=19, fontweight="bold")
    fig.text(0.016, 0.285, "General", rotation=90, va="center", ha="center", fontsize=19, fontweight="bold")
    fig.legend(handles, [handle.get_label() for handle in handles], loc="upper center", ncol=4,
               frameon=False, bbox_to_anchor=(0.53, 1.01), columnspacing=1.4, handletextpad=0.5)
    fig.tight_layout(rect=(0.035, 0.0, 1.0, 0.94), h_pad=2.2, w_pad=1.5)
    metadata = {"Creator": "alphafold-complex-calibration"}
    fig.savefig(OUT / "F7_workshop_iptm_selected_probability.pdf", bbox_inches="tight", metadata=metadata)
    fig.savefig(OUT / "F7_workshop_iptm_selected_probability.png", bbox_inches="tight", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
