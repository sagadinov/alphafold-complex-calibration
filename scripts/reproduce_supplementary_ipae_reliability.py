"""Render the supplementary Ab-Ag iPAE reliability figure from frozen decision-use CSVs."""

from __future__ import annotations

from common import ANALYSIS, SUPP_FIG, ensure_dirs
from render_decision_use_v2_figures import load_csvs, render_abag_ipae_supplementary


def main() -> None:
    ensure_dirs()
    data = load_csvs(ANALYSIS / "decision_use")
    render_abag_ipae_supplementary(data["rel_curve"], data["rel_boot"], SUPP_FIG)
    print("Saved S2_abag_ipae_reliability.pdf/.png")


if __name__ == "__main__":
    main()
