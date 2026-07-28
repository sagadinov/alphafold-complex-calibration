"""Feature computation utilities for raw structure and PAE arrays."""

from __future__ import annotations

import numpy as np
from scipy.spatial.distance import cdist

IPAE_CUTOFF = 8.0


def virtual_cb(n: np.ndarray, ca: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Construct a virtual Cbeta coordinate for glycine from the backbone frame."""

    v1 = c - ca
    v1 = v1 / np.linalg.norm(v1)
    v2 = n - ca
    v2 = v2 - np.dot(v2, v1) * v1
    v2 = v2 / np.linalg.norm(v2)
    v3 = np.cross(v1, v2)
    return ca + (-0.5416 * v1 + -0.7700 * v2 + -1.2065 * v3)


def compute_interface_features(
    structure_cb: np.ndarray,
    pae_matrix: np.ndarray,
    chain_ids: list[str] | np.ndarray,
) -> dict[str, float]:
    """Compute iPAE-style summary features from coordinates and a PAE matrix."""

    chain_arr = np.asarray(chain_ids)
    cross_chain = chain_arr[:, None] != chain_arr[None, :]
    if cross_chain.sum() == 0:
        return {
            "iface_pae_mean": float("nan"),
            "interchain_block_mean": float("nan"),
            "n_contacts": 0,
        }

    interchain_block_mean = float(np.asarray(pae_matrix)[cross_chain].mean())
    dist_matrix = cdist(structure_cb, structure_cb)
    interface_mask = cross_chain & (dist_matrix < IPAE_CUTOFF)
    n_contacts = int(interface_mask.sum())
    iface_pae_mean = float(np.asarray(pae_matrix)[interface_mask].mean()) if n_contacts else float("nan")
    return {
        "iface_pae_mean": iface_pae_mean,
        "interchain_block_mean": interchain_block_mean,
        "n_contacts": n_contacts,
    }

