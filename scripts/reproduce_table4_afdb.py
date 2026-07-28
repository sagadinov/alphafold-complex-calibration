"""Summarize the locked AFDB comparison artifacts."""

from __future__ import annotations

import pandas as pd

from scripts.common import ANALYSIS, PAPER_TAB, ensure_dirs, markdown_table


def main() -> None:
    ensure_dirs()
    comp = pd.read_csv(ANALYSIS / "afdb" / "full691_comparison.csv")
    mp = pd.read_csv(ANALYSIS / "afdb" / "full691_matched_precision.csv")
    comp.to_csv(PAPER_TAB / "tab_afdb_full691_comparison.csv", index=False)
    mp.to_csv(PAPER_TAB / "tab_afdb_full691_matched_precision.csv", index=False)
    md = ["# AFDB locked comparison", "", "## Binary label comparison", ""]
    md.append(markdown_table(comp, list(comp.columns)))
    md += ["", "## Matched-precision comparison", ""]
    md.append(markdown_table(mp, list(mp.columns)))
    md.append("")
    (PAPER_TAB / "tab_afdb_reproduced.md").write_text("\n".join(md), encoding="utf-8")
    print(comp.to_string(index=False))
    print()
    print(mp.to_string(index=False))


if __name__ == "__main__":
    main()

