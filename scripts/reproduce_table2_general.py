"""Reproduce final manuscript Table 2: General multimer calibration and classification metrics."""

from __future__ import annotations

import pandas as pd

from common import (
    DISPLAY_NAME_TEX,
    GENERAL_METHOD_ORDER,
    PAPER_TAB,
    THRESHOLDS,
    bold_best,
    ensure_dirs,
    format_metric,
    load_report,
    method_rows_from_report,
    write_text,
)

MAIN_METRICS = ["brier", "ece", "auroc", "mcc", "ppv"]

CAPTION = (
    "General multimer calibration and classification results (5{,}496 models, 1{,}922 targets). "
    "All fitted methods use grouped 5-fold AFM-benchmark evaluation. pDockQ2 (published) uses "
    "original parameters from \\citet{zhu2023evaluation}; pDockQ2 (refit) uses parameters "
    "optimized on AFM-benchmark training data. Best per column in \\textbf{bold}."
)


def build_dataframe(report: dict) -> pd.DataFrame:
    rows = []
    for thr_name, thr_val in THRESHOLDS:
        for row in method_rows_from_report(report, "general", thr_name, GENERAL_METHOD_ORDER):
            rows.append({"threshold": thr_name, "threshold_val": thr_val, **row})
    return pd.DataFrame(rows)


def build_markdown(df: pd.DataFrame) -> str:
    lines = ["# Table 2: General multimer main metrics", ""]
    for thr_name, thr_val in THRESHOLDS:
        sub = df[df["threshold"] == thr_name].copy()
        n_pos = int(sub["n_pos"].dropna().iloc[0])
        n_neg = int(sub["n_neg"].dropna().iloc[0])
        lines += [f"## DockQ >= {thr_val:.2f} (n+={n_pos:,}, n-={n_neg:,})", ""]
        cols = ["Method", "Brier", "ECE", "AUROC", "MCC", "PPV"]
        lines.append("| " + " | ".join(cols) + " |")
        lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
        for _, row in sub.iterrows():
            vals = [
                row["method"],
                format_metric(row["brier"], 4),
                format_metric(row["ece"], 4),
                format_metric(row["auroc"], 3),
                format_metric(row["mcc"], 3),
                format_metric(row["ppv"], 3),
            ]
            lines.append("| " + " | ".join(vals) + " |")
        lines.append("")
    return "\n".join(lines)


def build_latex(df: pd.DataFrame) -> str:
    lines = [
        "\\begin{table}[t]",
        f"\\caption{{{CAPTION}}}",
        "\\label{tab:general_main}",
        "\\centering",
        "\\resizebox{\\columnwidth}{!}{%",
        "\\begin{tabular}{lccccc}",
        "\\toprule",
        "Method & Brier$\\downarrow$ & ECE$\\downarrow$ & AUROC$\\uparrow$ & MCC$\\uparrow$ & PPV$\\uparrow$ \\",
        "\\midrule",
    ]
    for idx, (thr_name, thr_val) in enumerate(THRESHOLDS):
        sub = df[df["threshold"] == thr_name].copy()
        n_pos = int(sub["n_pos"].dropna().iloc[0])
        n_neg = int(sub["n_neg"].dropna().iloc[0])
        lines.append(
            f"\\multicolumn{{6}}{{l}}{{\\textit{{DockQ $\\ge$ {thr_val:.2f} --- $n_+$\\!=\\!{n_pos:,}, $n_-$\\!=\\!{n_neg:,}}}}} \\")
        best = {metric: bold_best(sub.to_dict('records'), metric) for metric in MAIN_METRICS}
        for _, row in sub.iterrows():
            cells = [DISPLAY_NAME_TEX[row["method"]]]
            for metric in MAIN_METRICS:
                decimals = 4 if metric in {"brier", "ece"} else 3
                text = format_metric(row[metric], decimals, drop_zero=True)
                if row["method"] in best[metric] and text != "---":
                    text = f"\\textbf{{{text}}}"
                cells.append(text)
            lines.append(" & ".join(cells) + " \\")
        if idx != len(THRESHOLDS) - 1:
            lines.append("\\midrule")
    lines += ["\\bottomrule", "\\end{tabular}", "}%", "\\end{table}"]
    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()
    report = load_report()
    df = build_dataframe(report)
    df.to_csv(PAPER_TAB / "tab2_general_main.csv", index=False)
    write_text(PAPER_TAB / "tab2_general_main.md", build_markdown(df))
    write_text(PAPER_TAB / "tab2_general_main.tex", build_latex(df))
    print(df[["threshold", "method", "brier", "ece", "auroc", "mcc", "ppv"]].to_string(index=False))


if __name__ == "__main__":
    main()
