from __future__ import annotations

import numpy as np
import pytest

from src.features import compute_interface_features, compute_interchain_block_mean, compute_ipae_8A_with_count


def test_interface_feature_definitions_match_ordered_pairs() -> None:
    coords = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [20.0, 0.0, 0.0],
        ]
    )
    chains = np.array(["A", "B", "B"], dtype=object)
    pae = np.array(
        [
            [0.0, 2.0, 7.0],
            [3.0, 0.0, 4.0],
            [8.0, 5.0, 0.0],
        ]
    )
    iface_mean, n_contacts = compute_ipae_8A_with_count(pae, coords, chains)
    block_mean = compute_interchain_block_mean(pae, chains)
    feats = compute_interface_features(coords, pae, chains)
    assert n_contacts == 2
    assert np.isclose(iface_mean, (2.0 + 3.0) / 2.0)
    assert np.isclose(block_mean, (2.0 + 7.0 + 3.0 + 8.0) / 4.0)
    assert np.isclose(feats["iface_pae_mean"], iface_mean)
    assert np.isclose(feats["interchain_block_mean"], block_mean)


def test_feature_dimension_mismatches_raise_clear_errors() -> None:
    pae = np.zeros((3, 3), dtype=float)
    coords = np.zeros((2, 3), dtype=float)
    chains = np.array(["A", "B", "B"], dtype=object)
    with pytest.raises(ValueError, match="dimension mismatch"):
        compute_ipae_8A_with_count(pae, coords, chains)
    with pytest.raises(ValueError, match="does not match"):
        compute_interchain_block_mean(pae, np.array(["A", "B"], dtype=object))
