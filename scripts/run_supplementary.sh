#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python}"

echo "=== Reproducing supplementary artifacts ==="
for script in \
    scripts/reproduce_decision_use.py \
    scripts/reproduce_supplementary_permutation_importance.py \
    scripts/reproduce_supplementary_afdb.py \
    scripts/reproduce_supplementary_ipae_reliability.py; do
    echo "--- Running $(basename "$script") ---"
    "$PYTHON_BIN" "$script"
    echo
 done

echo "=== Supplementary reproductions complete ==="
