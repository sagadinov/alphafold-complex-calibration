from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SCRIPTS = [
    ("scripts/reproduce_table1_abag.py", ROOT / "paper" / "tables" / "tab_abag_main_reproduced.csv"),
    ("scripts/reproduce_table2_general.py", ROOT / "paper" / "tables" / "tab_general_main_reproduced.csv"),
    ("scripts/reproduce_table3_casp16.py", ROOT / "paper" / "tables" / "tab_casp16_bootstrap_reproduced.csv"),
    ("scripts/reproduce_table4_afdb.py", ROOT / "paper" / "tables" / "tab_afdb_full691_comparison.csv"),
    ("scripts/reproduce_figure1.py", ROOT / "paper" / "figures" / "F1_reliability_abag.pdf"),
    ("scripts/reproduce_figure2.py", ROOT / "paper" / "figures" / "F2_matched_precision_bars.pdf"),
    ("scripts/reproduce_figure3.py", ROOT / "paper" / "figures" / "F3_permutation_importance.pdf"),
]


def test_manifest_script_passes() -> None:
    subprocess.run(["bash", "scripts/verify_manifest.sh"], cwd=ROOT, check=True)


def test_run_all_script_passes() -> None:
    env = os.environ.copy()
    env["PYTHON"] = sys.executable
    env["PYTHONPATH"] = str(ROOT)
    subprocess.run(["bash", "scripts/run_all.sh"], cwd=ROOT, check=True, env=env)


def test_prediction_smoke_via_subprocess() -> None:
    code = (
        "import pandas as pd; "
        "from src.predict import CalibratedPredictor; "
        "df = pd.read_csv('data/abag_test_v2.csv', nrows=2); "
        "pred = CalibratedPredictor.load('models', domain='abag'); "
        "out = pred.predict(df); "
        "assert list(out.columns) == ['p_acceptable','p_medium','p_high']"
    )
    subprocess.run([sys.executable, "-c", code], cwd=ROOT, check=True)


def test_individual_reproduction_scripts_create_expected_outputs() -> None:
    for script, output in SCRIPTS:
        subprocess.run([sys.executable, script], cwd=ROOT, check=True)
        assert output.exists()
        assert output.stat().st_size > 0
