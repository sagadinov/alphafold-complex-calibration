"""Merge split Ab-Ag training CSV shards into one local file."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "data" / "abag_train_v2_parts"
OUT = ROOT / "data" / "abag_train_v2.csv"


def main() -> None:
    manifest = pd.read_csv(PARTS / "manifest.csv")
    frames = [pd.read_csv(PARTS / filename, low_memory=False) for filename in manifest["filename"]]
    merged = pd.concat(frames, ignore_index=True)
    merged.to_csv(OUT, index=False)
    print(f"merged rows={len(merged)} targets={merged['target_id'].nunique()} -> {OUT}")


if __name__ == "__main__":
    main()
