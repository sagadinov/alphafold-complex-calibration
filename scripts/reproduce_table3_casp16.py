"""Reproduce the CASP16 bootstrap table from locked bootstrap summary CSV."""

from __future__ import annotations

import pandas as pd

from scripts.common import DATA, PAPER_TAB, THRESHOLDS, ensure_dirs, markdown_table


def main() -> None:
    ensure_dirs()
    df = pd.read_csv(DATA / "casp16_bootstrap_summary.csv")
    df.to_csv(PAPER_TAB / "tab_casp16_bootstrap_reproduced.csv", index=False)
    md = ["# tab_casp16_bootstrap_reproduced", ""]
    for thr_name, thr_val in THRESHOLDS:
        sub = df[df["threshold_name"] == thr_name].copy()
        keep = [
            "method",
            "brier_mean",
            "ece_mean",
            "auroc_mean",
            "mcc_mean",
            "ppv_mean",
            "brier_std",
            "mcc_std",
        ]
        md.append(f"## DockQ >= {thr_val:.2f}")
        md.append("")
        md.append(markdown_table(sub[keep], keep))
        md.append("")
    (PAPER_TAB / "tab_casp16_bootstrap_reproduced.md").write_text("\n".join(md), encoding="utf-8")
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Reproduced CASP16 bootstrap summary from locked bootstrap results.}",
        "\\label{tab:casp16_reproduced}",
        "\\begin{tabular}{lccccc}",
        "\\toprule",
        "Method & Brier & ECE & AUROC & MCC & PPV \\\\",
        "\\midrule",
    ]
    for thr_name, thr_val in THRESHOLDS:
        lines.append(f"\\multicolumn{{6}}{{l}}{{\\textit{{DockQ $\\geq$ {thr_val:.2f}}}}} \\\\")
        sub = df[df["threshold_name"] == thr_name]
        for _, row in sub.iterrows():
            lines.append(
                f"{row['method']} & {row['brier_mean']:.4f} $\\pm$ {row['brier_std']:.4f} & "
                f"{row['ece_mean']:.4f} $\\pm$ {row['ece_std']:.4f} & "
                f"{row['auroc_mean']:.4f} $\\pm$ {row['auroc_std']:.4f} & "
                f"{row['mcc_mean']:.4f} $\\pm$ {row['mcc_std']:.4f} & "
                f"{row['ppv_mean']:.4f} $\\pm$ {row['ppv_std']:.4f} \\\\"
            )
        if thr_name != THRESHOLDS[-1][0]:
            lines.append("\\midrule")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    (PAPER_TAB / "tab_casp16_bootstrap_reproduced.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()

