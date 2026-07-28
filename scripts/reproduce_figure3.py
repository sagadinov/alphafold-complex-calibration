"""Reproduce the permutation importance figure from locked CSV summaries."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from scripts.common import ANALYSIS, PAPER_FIG


def draw(ax, df: pd.DataFrame, title: str) -> None:
    df = df.sort_values("pearson_drop_mean", ascending=True)
    ax.barh(df["display_name"], df["pearson_drop_mean"], xerr=df["pearson_drop_std"], color="#2563EB", alpha=0.85)
    ax.set_xlabel("Pearson drop when shuffled")
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.12)


def main() -> None:
    abag = pd.read_csv(ANALYSIS / "permutation_importance_abag_v2.csv")
    general = pd.read_csv(ANALYSIS / "permutation_importance_general_v2.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    draw(axes[0], abag, "Ab-Ag")
    draw(axes[1], general, "General")
    fig.tight_layout()
    fig.savefig(PAPER_FIG / "F3_permutation_importance.pdf", bbox_inches="tight")
    fig.savefig(PAPER_FIG / "F3_permutation_importance.png", bbox_inches="tight", dpi=300)
    print("Saved F3_permutation_importance.pdf/.png")


if __name__ == "__main__":
    main()

