"""Reproduce final manuscript Figure 3: minimum-reliability transfer."""

from __future__ import annotations

from common import ANALYSIS, PAPER_FIG, ensure_dirs
from render_decision_use_v2_figures import load_csvs, render_reliability_transfer_main


def main() -> None:
    ensure_dirs()
    data = load_csvs(ANALYSIS / "decision_use")
    render_reliability_transfer_main(data["rel_curve"], data["rel_boot"], PAPER_FIG)
    print("Saved F3_reliability_transfer.pdf/.png")


if __name__ == "__main__":
    main()
