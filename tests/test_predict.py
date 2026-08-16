from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.predict import CalibratedPredictor


ROOT = Path(__file__).resolve().parents[1]


def sample_df() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "abag_test_v2.csv", nrows=8, low_memory=False)


def test_model_loading_abag_and_general() -> None:
    CalibratedPredictor.load(ROOT / "models", domain="abag")
    CalibratedPredictor.load(ROOT / "models", domain="general")


def test_prediction_output_properties() -> None:
    predictor = CalibratedPredictor.load(ROOT / "models", domain="abag")
    df = sample_df()
    out = predictor.predict(df)
    assert list(out.columns) == ["p_acceptable", "p_medium", "p_high"]
    assert out.index.equals(df.index)
    assert np.isfinite(out.to_numpy()).all()
    assert ((out.to_numpy() >= 0.0) & (out.to_numpy() <= 1.0)).all()
    assert (out["p_acceptable"] >= out["p_medium"]).all()
    assert (out["p_medium"] >= out["p_high"]).all()


def test_ranking_score_computed_when_missing() -> None:
    predictor = CalibratedPredictor.load(ROOT / "models", domain="abag")
    df = sample_df()
    expected = df.copy()
    expected["ranking_score"] = 0.8 * expected["iptm"] + 0.2 * expected["ptm"]
    with_rank = predictor.predict(expected)
    without_rank = predictor.predict(df.drop(columns=["ranking_score"]))
    pd.testing.assert_frame_equal(with_rank, without_rank)


def test_invalid_domain_raises_clear_error() -> None:
    with pytest.raises(ValueError, match="invalid domain"):
        CalibratedPredictor.load(ROOT / "models", domain="not-a-domain")


def test_missing_required_columns_raise_clear_error() -> None:
    predictor = CalibratedPredictor.load(ROOT / "models", domain="abag")
    df = sample_df().drop(columns=["iptm"])
    with pytest.raises(ValueError, match="missing required input columns"):
        predictor.predict(df)


def test_nans_are_handled_explicitly() -> None:
    predictor = CalibratedPredictor.load(ROOT / "models", domain="abag")
    df = sample_df()
    df.loc[df.index[0], "iface_pae_mean"] = np.nan
    with pytest.raises(ValueError, match="non-finite values in required features"):
        predictor.predict(df)
