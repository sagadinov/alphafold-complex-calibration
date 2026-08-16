"""Reproduce final manuscript Figure 2: fixed-ranking expected-yield estimation."""

from __future__ import annotations

from common import ANALYSIS, PAPER_FIG, ensure_dirs
from render_decision_use_v2_figures import load_csvs, render_fixed_ranking_main


def main() -> None:
    ensure_dirs()
    data = load_csvs(ANALYSIS / "decision_use")
    render_fixed_ranking_main(data["fixed_metrics"], data["fixed_boot"], PAPER_FIG)
    print("Saved F2_fixed_ranking_yield.pdf/.png")


if __name__ == "__main__":
    main()
