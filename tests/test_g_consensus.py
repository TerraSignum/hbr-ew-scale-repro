"""
Tests for the |g|-consensus across the four paths.

These tests verify that the four independent calculation paths converge
within the falsification threshold and that the canonical FULL-MS-bar
value is loaded correctly.
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

import recompute_ew_scale as M  # noqa: E402


def test_four_paths_loaded():
    """All four paths must be present in the consensus."""
    consensus = M.four_path_consensus()
    paths = consensus["paths"]
    assert len(paths) == 4, f"Expected 4 paths, got {len(paths)}: {list(paths.keys())}"


def test_g_range_below_falsification_threshold():
    """|g|-range must be <= 0.15 (falsification threshold)."""
    consensus = M.four_path_consensus()
    assert consensus["g_range"] <= 0.15, (
        f"|g|-range {consensus['g_range']} exceeds threshold 0.15"
    )
    assert consensus["passes_falsification"], "Falsification check failed"


def test_all_g_values_in_band():
    """All four |g| values must be within [1.32, 1.52] (consensus band)."""
    consensus = M.four_path_consensus()
    for path_name, g in consensus["paths"].items():
        assert 1.32 <= g <= 1.52, (
            f"|g| out of band for {path_name}: {g} not in [1.32, 1.52]"
        )


def test_msbar_path_canonical_value():
    """The full MS-bar two-loop path should give |g| = 1.4187."""
    consensus = M.four_path_consensus()
    paths = consensus["paths"]
    msbar_g = paths.get("msbar_full_two_loop")
    assert msbar_g is not None, f"msbar_full_two_loop path missing: {list(paths.keys())}"
    assert abs(msbar_g - 1.4187) < 1e-3, f"Full MS-bar |g| mismatch: {msbar_g}"


def test_g_mean_close_to_canonical():
    """4-path mean should be near (but not equal to) canonical 1.4187."""
    consensus = M.four_path_consensus()
    g_mean = consensus["g_mean"]
    # Mean of 1.4190, 1.4070, 1.4187, 1.4190 = 1.4160
    assert abs(g_mean - 1.4160) < 1e-3, f"Mean mismatch: {g_mean}"
    # Sanity: mean is below canonical because the sigma-cutoff path is lowest
    assert g_mean < 1.4187, "Mean should be below canonical (sigma-cutoff path is lower)"


def test_max_dev_from_mean_acceptable():
    """Maximum deviation from mean should be small (< 0.02)."""
    consensus = M.four_path_consensus()
    assert consensus["g_max_dev_from_mean"] < 0.02, (
        f"Max dev too large: {consensus['g_max_dev_from_mean']}"
    )
