"""Reproduce the Ab-Ag reliability diagram from locked predictions."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from scripts.common import PAPER_FIG, THRESHOLDS, base_axes_style, load_predictions

PDF_METADATA = {
    "Creator": "alphafold-complex-calibration",
    "CreationDate": None,
    "ModDate": None,
}

METHODS = {
    "Raw ipTM": ("p_raw_iptm", "#9CA3AF", "--"),
    "Iso. ipTM": {
        "acceptable": ("p_iso_iptm_acceptable", "#2563EB", "-"),
        "medium": ("p_iso_iptm_medium", "#2563EB", "-"),
        "high": ("p_iso_iptm_high", "#2563EB", "-"),
    },
    "Iso. iPAE": {
        "acceptable": ("p_iso_ipae_acceptable", "#60A5FA", "-"),
        "medium": ("p_iso_ipae_medium", "#60A5FA", "-"),
        "high": ("p_iso_ipae_high", "#60A5FA", "-"),
    },
    "MLP 5-feat CE": {
        "acceptable": ("p_mlp_ce_acceptable", "#DC2626", "-"),
        "medium": ("p_mlp_ce_medium", "#DC2626", "-"),
        "high": ("p_mlp_ce_high", "#DC2626", "-"),
    },
}


def reliability_curve(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10):
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    x, y = [], []
    for i in range(n_bins):
        if i < n_bins - 1:
            mask = (y_prob >= edges[i]) & (y_prob < edges[i + 1])
        else:
            mask = (y_prob >= edges[i]) & (y_prob <= edges[i + 1])
        if mask.sum() == 0:
            continue
        x.append(float(y_prob[mask].mean()))
        y.append(float(y_true[mask].mean()))
    return np.asarray(x), np.asarray(y)


def main() -> None:
    df = load_predictions("abag")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, (thr_name, thr_val) in zip(axes, THRESHOLDS):
        y_true = (df["dockq"].to_numpy(dtype=float) >= thr_val).astype(int)
        for method, spec in METHODS.items():
            if isinstance(spec, dict):
                col, color, ls = spec[thr_name]
            else:
                col, color, ls = spec
            x, y = reliability_curve(y_true, df[col].to_numpy(dtype=float))
            ax.plot(x, y, color=color, linestyle=ls, linewidth=2, marker="o", markersize=4, label=method)
        ax.plot([0, 1], [0, 1], "k--", alpha=0.3, linewidth=0.8)
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(-0.02, 1.02)
        ax.set_xlabel("Predicted probability")
        ax.set_ylabel("Observed frequency")
        base_axes_style(ax, f"DockQ >= {thr_val:.2f}")
        ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(PAPER_FIG / "F1_reliability_abag.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    fig.savefig(PAPER_FIG / "F1_reliability_abag.png", bbox_inches="tight", dpi=300)
    print("Saved F1_reliability_abag.pdf/.png")


if __name__ == "__main__":
    main()
