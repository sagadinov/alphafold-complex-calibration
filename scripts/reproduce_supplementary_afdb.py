"""Export AFDB supporting artifacts into the supplementary release tree."""

from __future__ import annotations

import shutil

import pandas as pd

from scripts.common import ANALYSIS, SUPP_FIG, SUPP_TAB, ensure_dirs, write_text


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        vals = [str(row[c]) for c in cols]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    ensure_dirs()
    base = ANALYSIS / "afdb"
    tables = {
        "afdb_full691_comparison.csv": pd.read_csv(base / "full691_comparison.csv"),
        "afdb_full691_matched_precision.csv": pd.read_csv(base / "full691_matched_precision.csv"),
        "afdb_positive_dockq_full_comparison.csv": pd.read_csv(base / "afdb_positive_dockq_full_comparison.csv"),
        "afdb_positive_dockq_matched_precision.csv": pd.read_csv(base / "afdb_positive_dockq_matched_precision.csv"),
        "afdb_positive_dockq_steinegger_transfer.csv": pd.read_csv(base / "afdb_positive_dockq_steinegger_transfer.csv"),
    }
    for name, df in tables.items():
        df.to_csv(SUPP_TAB / name, index=False)
    for fig_name in ["afdb_positive_dockq_pr_acceptable.pdf", "afdb_positive_dockq_pr_acceptable.png", "full691_pr_curve.pdf"]:
        src = base / fig_name
        if src.exists():
            shutil.copy2(src, SUPP_FIG / fig_name)
    md = ["# AFDB supplementary artifacts", ""]
    for name, df in tables.items():
        md += [f"## {name}", "", markdown_table(df), ""]
    write_text(SUPP_TAB / "afdb_summary.md", "\n".join(md))
    print("Saved AFDB supplementary tables and figures")


if __name__ == "__main__":
    main()
