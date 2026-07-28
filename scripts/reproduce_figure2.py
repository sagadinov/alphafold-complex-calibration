"""Reproduce the matched-precision stacked bar figure."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

from scripts.common import ANALYSIS, PAPER_FIG

TP_COLOR = "#059669"
FP_COLOR = "#F97316"
FAILED_GENERAL = {"Raw iPAE (1/(1+iPAE))", "Iso. iPAE"}
DISPLAY = {
    "MLP 5-feat CE": "MLP 5-feat CE",
    "Iso. iPAE": "Iso. iPAE",
    "Raw iPAE (1/(1+iPAE))": "Raw iPAE proxy",
    "pDockQ2 (published)": "pDockQ2 published",
    "Iso. ipTM": "Iso. ipTM",
    "Raw ipTM": "Raw ipTM",
    "Raw ranking conf.": "Raw ranking conf.",
}
FAMILY = {
    "MLP 5-feat CE": "#DC2626",
    "Iso. iPAE": "#2563EB",
    "Raw iPAE (1/(1+iPAE))": "#60A5FA",
    "pDockQ2 (published)": "#93C5FD",
    "Iso. ipTM": "#6B7280",
    "Raw ipTM": "#9CA3AF",
    "Raw ranking conf.": "#D1D5DB",
}


def load_data() -> pd.DataFrame:
    abag = pd.read_csv(ANALYSIS / "matched_precision_comparison.csv")
    abag = abag[abag["threshold"].eq("acceptable")].copy()
    abag = abag[abag["method"].isin(DISPLAY)].copy()
    abag["dataset"] = "Ab-Ag"
    general = pd.read_csv(ANALYSIS / "matched_precision_general.csv")
    general = general[general["threshold"].eq("acceptable")].copy()
    general = general[general["method"].isin(DISPLAY)].copy()
    general["dataset"] = "General"
    out = pd.concat([abag, general], ignore_index=True)
    out["display_method"] = out["method"].map(DISPLAY)
    out["hatched_max_precision"] = out["dataset"].eq("General") & out["method"].isin(FAILED_GENERAL)
    return out


def draw_panel(ax, df: pd.DataFrame, title: str, total_positives: int) -> None:
    df = df.sort_values("n_selected", ascending=False).reset_index(drop=True)
    for idx, row in df.iterrows():
        method = row["method"]
        tp = int(row["tp"])
        fp = int(row["fp"])
        failed = bool(row["hatched_max_precision"])
        if failed:
            ax.barh(idx, tp, color="white", edgecolor=TP_COLOR, hatch="///", linewidth=1.3)
            ax.barh(idx, fp, left=tp, color="white", edgecolor=FP_COLOR, hatch="///", linewidth=1.3)
            label = f"{int(row['n_selected']):,}  max precision: {row['precision']*100:.1f}%"
        else:
            ax.barh(idx, tp, color=TP_COLOR, edgecolor="black", linewidth=0.25)
            ax.barh(idx, fp, left=tp, color=FP_COLOR, edgecolor="black", linewidth=0.25)
            ax.barh(idx, max(df["n_selected"].max() * 0.006, 12), left=0, color=FAMILY[method], edgecolor="none", alpha=0.95)
            label = f"{int(row['n_selected']):,}"
        ax.text(row["n_selected"] + max(df["n_selected"].max() * 0.015, 20), idx, label, va="center", ha="left", fontsize=7.5)
    ax.axvline(total_positives, color="black", linestyle="--", linewidth=1.1, alpha=0.65)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df["display_method"], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, max(df["n_selected"].max(), total_positives) * 1.10)
    ax.set_xlabel("Selected models at ~90% precision (stacked TP + FP)", fontsize=10)
    ax.set_title(title, fontsize=12)
    ax.grid(axis="x", alpha=0.12)


def main() -> None:
    data = load_data()
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4))
    draw_panel(axes[0], data[data["dataset"].eq("Ab-Ag")], "Ab-Ag (62,681 models)", 22231)
    draw_panel(axes[1], data[data["dataset"].eq("General")], "General multimer (5,496 models, OOF)", 3219)
    handles = [
        Patch(facecolor=TP_COLOR, edgecolor="black", label="True positives"),
        Patch(facecolor=FP_COLOR, edgecolor="black", label="False positives"),
        Patch(facecolor="white", edgecolor="black", hatch="///", label="Cannot reach 90% precision"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.012), fontsize=9)
    fig.text(0.5, 0.095, "Dashed lines mark total positives: Ab-Ag = 22,231; General = 3,219.", ha="center", va="center", fontsize=9)
    fig.suptitle("Matched-precision retrieval at DockQ >= 0.23", fontsize=13, y=1.02)
    fig.tight_layout(rect=[0, 0.14, 1, 1])
    fig.savefig(PAPER_FIG / "F2_matched_precision_bars.pdf", bbox_inches="tight")
    fig.savefig(PAPER_FIG / "F2_matched_precision_bars.png", bbox_inches="tight", dpi=300)
    print("Saved F2_matched_precision_bars.pdf/.png")


if __name__ == "__main__":
    main()

