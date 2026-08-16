"""Shared helpers for curated public reproduction scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MODELS = ROOT / "models"
ANALYSIS = ROOT / "analysis"
PAPER = ROOT / "paper"
PAPER_FIG = PAPER / "figures"
PAPER_TAB = PAPER / "tables"
SUPP = PAPER / "supplementary"
SUPP_FIG = SUPP / "figures"
SUPP_TAB = SUPP / "tables"

THRESHOLDS = [("acceptable", 0.23), ("medium", 0.49), ("high", 0.80)]
THRESHOLD_LABELS = {name: value for name, value in THRESHOLDS}

PDF_METADATA = {
    "Creator": "alphafold-complex-calibration",
    "CreationDate": None,
    "ModDate": None,
}

ABAG_METHOD_ORDER = [
    "Raw ipTM",
    "Raw ranking confidence",
    "Raw pDockQ2 (published)",
    "Raw pDockQ2 (refit)",
    "ABAG-Rank",
    "Isotonic ipTM",
    "Isotonic iPAE",
    "MLP 5-feat CE",
]

GENERAL_METHOD_ORDER = [
    "Raw ipTM",
    "Raw ranking confidence",
    "Raw pDockQ2 (published)",
    "Raw pDockQ2 (refit)",
    "Isotonic ipTM",
    "Isotonic iPAE",
    "MLP 5-feat CE",
]

DISPLAY_NAME_TEX = {
    "Raw ipTM": "Raw ipTM",
    "Raw ranking confidence": "Raw ranking confidence",
    "Raw pDockQ2 (published)": "Raw pDockQ2 (published)",
    "Raw pDockQ2 (refit)": "Raw pDockQ2 (refit)",
    "ABAG-Rank": "ABAG-Rank$^\\dagger$",
    "Isotonic ipTM": "Iso. ipTM",
    "Isotonic iPAE": "Iso. iPAE",
    "MLP 5-feat CE": "MLP 5-feat CE",
}


def ensure_dirs() -> None:
    PAPER_FIG.mkdir(parents=True, exist_ok=True)
    PAPER_TAB.mkdir(parents=True, exist_ok=True)
    SUPP_FIG.mkdir(parents=True, exist_ok=True)
    SUPP_TAB.mkdir(parents=True, exist_ok=True)


def load_predictions(dataset: str) -> pd.DataFrame:
    return pd.read_csv(DATA / f"{dataset}_predictions_v3.csv", low_memory=False)


def load_report() -> dict:
    return json.loads((DATA / "report_data_v3.json").read_text(encoding="utf-8"))


def metric_is_min(metric: str) -> bool:
    return metric in {"brier", "ece"}


def format_metric(value: float | int | None, decimals: int = 4, drop_zero: bool = False) -> str:
    if value is None or pd.isna(value):
        return "---"
    text = f"{float(value):.{decimals}f}"
    if drop_zero and text.startswith("0"):
        text = text[1:]
    return text


def method_rows_from_report(report: dict, dataset: str, threshold_name: str, method_order: Iterable[str]) -> list[dict]:
    result = []
    threshold_block = report["results"][dataset][threshold_name]
    for method in method_order:
        if method in threshold_block:
            row = {"method": method, **threshold_block[method]}
            result.append(row)
    return result


def bold_best(rows: list[dict], metric: str) -> set[str]:
    scored = [(row["method"], row.get(metric)) for row in rows if row.get(metric) is not None and not pd.isna(row.get(metric))]
    if not scored:
        return set()
    values = [float(v) for _, v in scored]
    best = min(values) if metric_is_min(metric) else max(values)
    return {method for method, value in scored if abs(float(value) - best) < 1e-12}


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
