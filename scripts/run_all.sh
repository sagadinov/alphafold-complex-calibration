#!/bin/bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python}"

echo "=== Reproducing all paper results ==="
echo "=== alphafold-complex-calibration ==="

for script in \
    scripts/reproduce_table1_abag.py \
    scripts/reproduce_table2_general.py \
    scripts/reproduce_table3_casp16.py \
    scripts/reproduce_table4_afdb.py \
    scripts/reproduce_figure1.py \
    scripts/reproduce_figure2.py \
    scripts/reproduce_figure3.py; do
    echo "--- Running $(basename "$script") ---"
    "$PYTHON_BIN" "$script"
    echo
done

echo "=== All reproductions complete ==="
echo "Figures saved to paper/figures/"
echo "Tables saved to paper/tables/"
