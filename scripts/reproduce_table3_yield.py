"""Reproduce final manuscript Table 3: Ab-Ag fixed-ranking expected-yield estimation."""

from __future__ import annotations

import pandas as pd

from common import ANALYSIS, PAPER_TAB, ensure_dirs, write_text

PRIMARY_THRESHOLD = "acceptable"
UNIVERSE = "three_method_common"
def _slug(method: str) -> str:
    return method.lower().replace(" ", "_").replace(".", "").replace("-", "_").replace("(", "").replace(")", "")


RANKING_FAMILIES = [
    ("iptm", "ipTM-ranked", ["Raw ipTM", "Isotonic ipTM", "MLP 5-feat CE"]),
    ("ipae", "iPAE-ranked", ["Raw iPAE proxy", "Calibrated iPAE probability", "MLP 5-feat CE"]),
]


def build_table() -> pd.DataFrame:
    metrics = pd.read_csv(ANALYSIS / "decision_use" / "fixed_ranking_yield_metrics.csv")
    rows = []
    for family, label, methods in RANKING_FAMILIES:
        sub = metrics[
            (metrics["dataset"] == "abag")
            & (metrics["ranking_family"] == family)
            & (metrics["dockq_threshold_name"] == PRIMARY_THRESHOLD)
            & (metrics["comparison_universe"] == UNIVERSE)
            & (metrics["probability_method"].isin(methods))
        ].copy()
        for k in sorted(sub["K"].unique()):
            block = sub[sub["K"] == k].copy()
            row = {
                "ranking_family": family,
                "ranking_label": label,
                "K": int(k),
                "n_targets": int(block["n_targets"].iloc[0]),
            }
            for method in methods:
                value = float(block.loc[block["probability_method"] == method, "normalized_mae"].iloc[0])
                key = _slug(method)
                row[key] = value
            rows.append(row)
    return pd.DataFrame(rows)


def build_markdown(df: pd.DataFrame) -> str:
    lines = ["# Table 3: Ab-Ag fixed-ranking expected-yield estimation", ""]
    for family, label, methods in RANKING_FAMILIES:
        sub = df[df["ranking_family"] == family].copy()
        cols = ["K", "n_targets"] + [_slug(m) for m in methods]
        lines += [f"## {label}", ""]
        headers = ["K", "Targets"] + methods
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for _, row in sub.iterrows():
            vals = [str(int(row["K"])), str(int(row["n_targets"]))] + [f"{row[c]:.4f}" for c in cols[2:]]
            lines.append("| " + " | ".join(vals) + " |")
        lines.append("")
    return "\n".join(lines)


def build_latex(df: pd.DataFrame) -> str:
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Ab-Ag fixed-ranking expected-yield estimation at DockQ $\\geq 0.23$. Values are target-level mean absolute error in predicted success fraction; lower is better.}",
        "\\label{tab:fixed_ranking_yield}",
        "\\begin{tabular}{lcccc}",
        "\\toprule",
        "K & Targets & Raw & Calibrated & MLP \\",
        "\\midrule",
        "\\multicolumn{5}{l}{\\textit{ipTM-ranked}} \\",
    ]
    iptm = df[df["ranking_family"] == "iptm"].copy()
    for _, row in iptm.iterrows():
        lines.append(
            f"{int(row['K'])} & {int(row['n_targets'])} & {row['raw_iptm']:.4f} & {row['isotonic_iptm']:.4f} & {row['mlp_5_feat_ce']:.4f} \\")
    lines += [
        "\\midrule",
        "\\multicolumn{5}{l}{\\textit{iPAE-ranked}} \\",
    ]
    ipae = df[df["ranking_family"] == "ipae"].copy()
    for _, row in ipae.iterrows():
        lines.append(
            f"{int(row['K'])} & {int(row['n_targets'])} & {row['raw_ipae_proxy']:.4f} & {row['calibrated_ipae_probability']:.4f} & {row['mlp_5_feat_ce']:.4f} \\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()
    df = build_table()
    df.to_csv(PAPER_TAB / "tab3_fixed_ranking_yield.csv", index=False)
    write_text(PAPER_TAB / "tab3_fixed_ranking_yield.md", build_markdown(df))
    write_text(PAPER_TAB / "tab3_fixed_ranking_yield.tex", build_latex(df))
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
