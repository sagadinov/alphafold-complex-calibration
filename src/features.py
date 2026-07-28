"""Feature computation helpers for pre-extracted coordinate and PAE arrays.

These routines implement the release v2 feature definitions used for the public
models:

- `iface_pae_mean`: mean PAE over ordered cross-chain residue pairs whose
  predicted C-beta distance is below 8 A
- `interchain_block_mean`: mean PAE over all ordered cross-chain residue pairs

The helpers operate on arrays that have already been aligned to the PAE matrix.
They do not parse complete AlphaFold output directories.
"""

from __future__ import annotations

import numpy as np
IPAE_CUTOFF = 8.0


def virtual_cb(n: np.ndarray, ca: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Construct the glycine virtual C-beta used in the locked v2 pipeline."""

    b = ca - n
    cvec = c - ca
    a = np.cross(b, cvec)
    return ca + (-0.58273431 * b + 0.56802827 * cvec + 0.54067466 * a)


def compute_interchain_block_mean(pae_matrix: np.ndarray, chain_ids: list[str] | np.ndarray) -> float:
    """Return the mean PAE over all ordered cross-chain residue pairs."""

    pae = np.asarray(pae_matrix, dtype=float)
    chains = np.asarray(chain_ids)
    if pae.ndim != 2 or pae.shape[0] != pae.shape[1]:
        raise ValueError(f"expected a square PAE matrix, got shape {pae.shape}")
    if len(chains) != pae.shape[0]:
        raise ValueError(f"chain_ids length {len(chains)} does not match PAE size {pae.shape[0]}")
    cross_chain = chains[:, None] != chains[None, :]
    vals = pae[cross_chain]
    return float(np.mean(vals)) if vals.size else float("nan")


def compute_ipae_8A_with_count(
    pae_matrix: np.ndarray,
    cb_coords: np.ndarray,
    chain_ids: list[str] | np.ndarray,
    cutoff_A: float = IPAE_CUTOFF,
) -> tuple[float, int]:
    """Return release-v2 iPAE and the number of ordered interface pairs.

    Ordered residue pairs are counted the same way as in the frozen manuscript
    pipeline: if residues i and j are cross-chain contacts, both (i, j) and
    (j, i) contribute.
    """

    pae = np.asarray(pae_matrix, dtype=float)
    coords = np.asarray(cb_coords, dtype=float)
    chains = np.asarray(chain_ids)
    if pae.ndim != 2 or pae.shape[0] != pae.shape[1]:
        raise ValueError(f"expected a square PAE matrix, got shape {pae.shape}")
    if coords.ndim != 2 or coords.shape[1] != 3:
        raise ValueError(f"expected coordinates with shape (N, 3), got {coords.shape}")
    if len(coords) != pae.shape[0] or len(chains) != pae.shape[0]:
        raise ValueError(
            f"dimension mismatch: coords={len(coords)} chains={len(chains)} pae={pae.shape[0]}"
        )
    dist = np.sqrt(np.sum((coords[:, None, :] - coords[None, :, :]) ** 2, axis=2))
    cross_chain = chains[:, None] != chains[None, :]
    iface_mask = cross_chain & (dist < cutoff_A)
    iface_vals = pae[iface_mask]
    return (float(np.mean(iface_vals)) if iface_vals.size else float("nan"), int(iface_mask.sum()))


def compute_interface_features(
    structure_cb: np.ndarray,
    pae_matrix: np.ndarray,
    chain_ids: list[str] | np.ndarray,
) -> dict[str, float]:
    """Compute release-v2 interface features from aligned arrays."""

    interchain_block_mean = compute_interchain_block_mean(pae_matrix, chain_ids)
    iface_pae_mean, n_contacts = compute_ipae_8A_with_count(
        pae_matrix,
        structure_cb,
        chain_ids,
        cutoff_A=IPAE_CUTOFF,
    )
    return {
        "iface_pae_mean": iface_pae_mean,
        "interchain_block_mean": interchain_block_mean,
        "n_contacts": n_contacts,
    }
