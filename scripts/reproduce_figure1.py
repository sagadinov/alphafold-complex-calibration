"""Reproduce the final manuscript Figure 1: Ab-Ag reliability diagrams."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import PAPER_FIG, PDF_METADATA, THRESHOLDS, load_predictions

METHODS = {
    "Raw ipTM": ("p_raw_iptm", "#9CA3AF", "--"),
    "Isotonic ipTM": {
        "acceptable": ("p_iso_iptm_acceptable", "#2563EB", "-"),
        "medium": ("p_iso_iptm_medium", "#2563EB", "-"),
        "high": ("p_iso_iptm_high", "#2563EB", "-"),
    },
    "MLP 5-feat CE": {
        "acceptable": ("p_mlp_ce_acceptable", "#DC2626", "-"),
        "medium": ("p_mlp_ce_medium", "#DC2626", "-"),
        "high": ("p_mlp_ce_high", "#DC2626", "-"),
    },
}


def reliability_curve(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> tuple[np.ndarray, np.ndarray]:
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    mean_pred, mean_obs = [], []
    for i in range(n_bins):
        if i < n_bins - 1:
            mask = (y_prob >= edges[i]) & (y_prob < edges[i + 1])
        else:
            mask = (y_prob >= edges[i]) & (y_prob <= edges[i + 1])
        if mask.sum() == 0:
            continue
        mean_pred.append(float(y_prob[mask].mean()))
        mean_obs.append(float(y_true[mask].mean()))
    return np.asarray(mean_pred), np.asarray(mean_obs)


def main() -> None:
    df = load_predictions("abag")
    fig, axes = plt.subplots(1, 3, figsize=(14.6, 4.5))
    for ax, (thr_name, thr_val) in zip(axes, THRESHOLDS):
        y_true = (df["dockq"].to_numpy(dtype=float) >= thr_val).astype(int)
        for method, spec in METHODS.items():
            if isinstance(spec, dict):
                col, color, linestyle = spec[thr_name]
            else:
                col, color, linestyle = spec
            x, y = reliability_curve(y_true, df[col].to_numpy(dtype=float))
            ax.plot(x, y, color=color, linestyle=linestyle, linewidth=2.0, marker="o", markersize=4, label=method)
        ax.plot([0, 1], [0, 1], "k--", alpha=0.35, linewidth=0.8)
        ax.set_title(f"DockQ >= {thr_val:.2f}")
        ax.set_xlabel("Predicted probability")
        ax.set_ylabel("Observed frequency")
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(-0.02, 1.02)
        ax.grid(alpha=0.12)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.subplots_adjust(bottom=0.2, wspace=0.22)
    fig.savefig(PAPER_FIG / "F1_reliability_abag.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    fig.savefig(PAPER_FIG / "F1_reliability_abag.png", bbox_inches="tight", dpi=300)
    print("Saved F1_reliability_abag.pdf/.png")


if __name__ == "__main__":
    main()
