"""Helpers for the split Ab-Ag training CSV shipped with the public release."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

EXPECTED_ROWS = 269_105
EXPECTED_TARGETS = 7_045
MANIFEST_COLUMNS = [
    "part",
    "filename",
    "n_rows",
    "n_targets",
    "target_first",
    "target_last",
    "file_size_bytes",
    "sha256",
]


@dataclass(frozen=True)
class ShardSummary:
    part: int
    filename: str
    n_rows: int
    n_targets: int
    target_first: str
    target_last: str
    file_size_bytes: int
    sha256: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_parts_dir() -> Path:
    return repo_root() / "data" / "abag_train_v2_parts"


def default_output_path() -> Path:
    return repo_root() / "data" / "abag_train_v2.csv"


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def summarize_shard(path: Path, part: int) -> ShardSummary:
    df = pd.read_csv(path, low_memory=False)
    targets = df["target_id"].astype(str)
    unique_targets = targets.drop_duplicates()
    return ShardSummary(
        part=part,
        filename=path.name,
        n_rows=int(len(df)),
        n_targets=int(unique_targets.nunique()),
        target_first=str(unique_targets.iloc[0]) if len(unique_targets) else "",
        target_last=str(unique_targets.iloc[-1]) if len(unique_targets) else "",
        file_size_bytes=path.stat().st_size,
        sha256=sha256_file(path),
    )


def write_manifest(parts_dir: Path | None = None) -> Path:
    parts_dir = Path(parts_dir) if parts_dir else default_parts_dir()
    shard_paths = sorted(parts_dir.glob("abag_train_v2_part*.csv"))
    rows = []
    for idx, shard_path in enumerate(shard_paths, start=1):
        rows.append(summarize_shard(shard_path, idx).__dict__)
    manifest_path = parts_dir / "manifest.csv"
    pd.DataFrame(rows, columns=MANIFEST_COLUMNS).to_csv(
        manifest_path,
        index=False,
        quoting=csv.QUOTE_MINIMAL,
    )
    return manifest_path


def load_manifest(parts_dir: Path | None = None) -> pd.DataFrame:
    parts_dir = Path(parts_dir) if parts_dir else default_parts_dir()
    manifest_path = parts_dir / "manifest.csv"
    manifest = pd.read_csv(manifest_path, low_memory=False)
    missing = [col for col in MANIFEST_COLUMNS if col not in manifest.columns]
    if missing:
        raise ValueError(f"manifest missing required columns: {missing}")
    manifest = manifest[MANIFEST_COLUMNS].copy()
    manifest["part"] = manifest["part"].astype(int)
    manifest["n_rows"] = manifest["n_rows"].astype(int)
    manifest["n_targets"] = manifest["n_targets"].astype(int)
    manifest["file_size_bytes"] = manifest["file_size_bytes"].astype(int)
    manifest = manifest.sort_values("part").reset_index(drop=True)
    if manifest["part"].tolist() != list(range(1, len(manifest) + 1)):
        raise ValueError("manifest parts must be a contiguous 1..N sequence")
    return manifest


def validate_manifest(parts_dir: Path | None = None) -> dict[str, int]:
    parts_dir = Path(parts_dir) if parts_dir else default_parts_dir()
    manifest = load_manifest(parts_dir)
    seen_targets: set[str] = set()
    total_rows = 0
    total_targets = 0
    columns_ref: list[str] | None = None
    for row in manifest.itertuples(index=False):
        shard_path = parts_dir / row.filename
        if not shard_path.exists():
            raise FileNotFoundError(f"missing shard: {shard_path}")
        size_bytes = shard_path.stat().st_size
        if size_bytes != row.file_size_bytes:
            raise ValueError(
                f"file size mismatch for {row.filename}: manifest={row.file_size_bytes} actual={size_bytes}"
            )
        digest = sha256_file(shard_path)
        if digest != row.sha256:
            raise ValueError(f"sha256 mismatch for {row.filename}: manifest={row.sha256} actual={digest}")
        df = pd.read_csv(shard_path, low_memory=False)
        if columns_ref is None:
            columns_ref = list(df.columns)
        elif list(df.columns) != columns_ref:
            raise ValueError(f"column mismatch in {row.filename}")
        unique_targets = df["target_id"].astype(str).drop_duplicates()
        overlap = seen_targets.intersection(set(unique_targets))
        if overlap:
            raise ValueError(f"targets split across shards; first overlap: {sorted(overlap)[:5]}")
        seen_targets.update(unique_targets)
        if len(df) != row.n_rows:
            raise ValueError(f"row count mismatch for {row.filename}: manifest={row.n_rows} actual={len(df)}")
        if unique_targets.nunique() != row.n_targets:
            raise ValueError(
                f"target count mismatch for {row.filename}: manifest={row.n_targets} actual={unique_targets.nunique()}"
            )
        total_rows += len(df)
        total_targets += unique_targets.nunique()
    if total_rows != EXPECTED_ROWS:
        raise ValueError(f"unexpected total row count: {total_rows} != {EXPECTED_ROWS}")
    if total_targets != EXPECTED_TARGETS:
        raise ValueError(f"unexpected total target count: {total_targets} != {EXPECTED_TARGETS}")
    return {
        "n_parts": int(len(manifest)),
        "n_rows": int(total_rows),
        "n_targets": int(total_targets),
    }


def merge_parts(
    output_path: Path | None = None,
    parts_dir: Path | None = None,
    *,
    force: bool = False,
) -> dict[str, int | str]:
    parts_dir = Path(parts_dir) if parts_dir else default_parts_dir()
    output_path = Path(output_path) if output_path else default_output_path()
    validate_manifest(parts_dir)
    if output_path.exists() and not force:
        raise FileExistsError(f"output already exists: {output_path} (pass --force to overwrite)")
    manifest = load_manifest(parts_dir)
    frames = [pd.read_csv(parts_dir / row.filename, low_memory=False) for row in manifest.itertuples(index=False)]
    merged = pd.concat(frames, ignore_index=True)
    rows = int(len(merged))
    targets = int(merged["target_id"].astype(str).nunique())
    if rows != EXPECTED_ROWS or targets != EXPECTED_TARGETS:
        raise ValueError(
            f"merged file failed validation: rows={rows}/{EXPECTED_ROWS}, targets={targets}/{EXPECTED_TARGETS}"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)
    return {
        "output": str(output_path),
        "n_parts": int(len(manifest)),
        "n_rows": rows,
        "n_targets": targets,
    }
