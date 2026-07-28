from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.abag_train_parts import EXPECTED_ROWS, EXPECTED_TARGETS, merge_parts, validate_manifest


ROOT = Path(__file__).resolve().parents[1]


def test_manifest_validation_passes() -> None:
    summary = validate_manifest(ROOT / "data" / "abag_train_v2_parts")
    assert summary["n_rows"] == EXPECTED_ROWS
    assert summary["n_targets"] == EXPECTED_TARGETS


def test_merge_reconstructs_expected_counts_and_preserves_target_partition(tmp_path: Path) -> None:
    out = tmp_path / "abag_train_v2.csv"
    summary = merge_parts(output_path=out, parts_dir=ROOT / "data" / "abag_train_v2_parts")
    assert summary["n_rows"] == EXPECTED_ROWS
    assert summary["n_targets"] == EXPECTED_TARGETS
    merged = pd.read_csv(out, low_memory=False)
    assert len(merged) == EXPECTED_ROWS
    assert merged["target_id"].astype(str).nunique() == EXPECTED_TARGETS

    seen: set[str] = set()
    parts_dir = ROOT / "data" / "abag_train_v2_parts"
    for part in sorted(parts_dir.glob("abag_train_v2_part*.csv")):
        targets = set(pd.read_csv(part, usecols=["target_id"], low_memory=False)["target_id"].astype(str))
        assert not (seen & targets)
        seen.update(targets)
