"""
Falsification tests — deliberately broken inputs must break the closure.

A reproducibility package that "always passes" is suspicious. These tests
verify that wrong-sign theta_em, |g|-range above threshold, and shifted
S_bounce all correctly fail the closure constraints.
"""

import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

import recompute_ew_scale as M  # noqa: E402


# ============================================================================
# Theta_em wrong sign
# ============================================================================

def test_theta_em_zero_flips_sign():
    """theta_em=0 (wrong sign) must produce a negative closure."""
    cls = M.two_loop_closure(
        g=1.4187, g_normalization=2.078,
        D1_pct=-0.40893, D23_coeff=1.842,
        theta_em=0.0,
    )
    assert cls < 0, f"theta_em=0 should give negative closure, got {cls}"


def test_theta_em_zero_breaks_v_ew():
    """theta_em=0 must move v_EW outside PDG band [246.15, 246.29]."""
    inputs_json = M.load_json(M.JSON_FILES["ew_scale_inputs"])
    inputs = inputs_json["inputs"]
    v_1l = M.hbr_tree_plus_1l(inputs["M_Pl_GeV"], inputs["S_bounce_P1"])
    cls = M.two_loop_closure(
        g=1.4187, g_normalization=2.078,
        D1_pct=-0.40893, D23_coeff=1.842,
        theta_em=0.0,
    )
    v_wrong = M.v_ew_final(v_1l, cls)
    pdg = inputs["V_EW_PDG"]
    pdg_unc = inputs["V_EW_PDG_uncertainty"]
    # v_EW with wrong-sign closure should be far below PDG
    assert v_wrong < pdg - pdg_unc, (
        f"theta_em=0 v_EW={v_wrong} should be below PDG-band [{pdg-pdg_unc}, {pdg+pdg_unc}]"
    )


# ============================================================================
# |g| out of consensus band
# ============================================================================

def test_g_below_band_breaks_closure():
    """|g|=1.1 (below band [1.32, 1.52]) must produce v_EW outside PDG band."""
    inputs_json = M.load_json(M.JSON_FILES["ew_scale_inputs"])
    inputs = inputs_json["inputs"]
    v_1l = M.hbr_tree_plus_1l(inputs["M_Pl_GeV"], inputs["S_bounce_P1"])
    cls = M.two_loop_closure(
        g=1.1, g_normalization=2.078,
        D1_pct=-0.40893, D23_coeff=1.842,
        theta_em=math.pi,
    )
    v_wrong = M.v_ew_final(v_1l, cls)
    pdg = inputs["V_EW_PDG"]
    pdg_unc = inputs["V_EW_PDG_uncertainty"]
    # Closure too small with low |g|: v_EW remains near 245 GeV, well below PDG
    assert abs(v_wrong - pdg) > pdg_unc, (
        f"|g|=1.1 v_EW={v_wrong} should be outside PDG +/- {pdg_unc}"
    )


def test_g_above_band_breaks_closure():
    """|g|=2.0 (above band) must produce v_EW well above PDG."""
    inputs_json = M.load_json(M.JSON_FILES["ew_scale_inputs"])
    inputs = inputs_json["inputs"]
    v_1l = M.hbr_tree_plus_1l(inputs["M_Pl_GeV"], inputs["S_bounce_P1"])
    cls = M.two_loop_closure(
        g=2.0, g_normalization=2.078,
        D1_pct=-0.40893, D23_coeff=1.842,
        theta_em=math.pi,
    )
    v_wrong = M.v_ew_final(v_1l, cls)
    pdg = inputs["V_EW_PDG"]
    pdg_unc = inputs["V_EW_PDG_uncertainty"]
    assert abs(v_wrong - pdg) > pdg_unc, (
        f"|g|=2.0 v_EW={v_wrong} should be outside PDG +/- {pdg_unc}"
    )


# ============================================================================
# S_bounce shifted
# ============================================================================

def test_s_bounce_shifted_breaks_tree():
    """If S_bounce is shifted by +1, the Tree+1L value drops by factor e (~270%)."""
    inputs_json = M.load_json(M.JSON_FILES["ew_scale_inputs"])
    inputs = inputs_json["inputs"]
    v_normal = M.hbr_tree_plus_1l(inputs["M_Pl_GeV"], inputs["S_bounce_P1"])
    v_shifted = M.hbr_tree_plus_1l(inputs["M_Pl_GeV"], inputs["S_bounce_P1"] + 1.0)
    ratio = v_shifted / v_normal
    # exp(-1) = 0.368
    assert 0.36 < ratio < 0.38, f"S_bounce+1 ratio outside [0.36, 0.38]: {ratio}"


def test_s_bounce_shifted_breaks_v_ew():
    """S_bounce shifted by +0.01 must move v_EW outside PDG band."""
    inputs_json = M.load_json(M.JSON_FILES["ew_scale_inputs"])
    inputs = inputs_json["inputs"]
    v_1l_shifted = M.hbr_tree_plus_1l(
        inputs["M_Pl_GeV"], inputs["S_bounce_P1"] + 0.01
    )
    cls = M.two_loop_closure(
        g=1.4187, g_normalization=2.078,
        D1_pct=-0.40893, D23_coeff=1.842,
        theta_em=math.pi,
    )
    v_wrong = M.v_ew_final(v_1l_shifted, cls)
    pdg = inputs["V_EW_PDG"]
    pdg_unc = inputs["V_EW_PDG_uncertainty"]
    # exp(-0.01) ~ 0.99005, so v_EW drops by ~1% (~2.4 GeV) - well outside +/-0.07
    assert abs(v_wrong - pdg) > pdg_unc, (
        f"S_bounce+0.01 v_EW={v_wrong} should be outside PDG +/- {pdg_unc}"
    )


# ============================================================================
# F1: four-path synthesis spread test
# ============================================================================

def test_F1_four_path_synthesis():
    """F1: max-min spread across the four |g|-paths must lie below 0.15.

    This is the synthesis-of-paths falsification trigger: the closure
    must not depend on a single renormalization-scheme choice. The
    empirical four-path spread is documented as ~0.012, so the test
    serves as a regression guard against silent drift in any one path.
    """
    g_per_path = M.load_g_per_path()
    g_paths = list(g_per_path.values())
    spread = max(g_paths) - min(g_paths)
    assert spread <= 0.15, (
        f"F1 falsification triggered: |g|-spread {spread:.4f} exceeds "
        f"0.15 across paths {g_paths}"
    )
    # Empirical spread is ~0.012 — guard against drift.
    assert spread <= 0.05, (
        f"Drift warning: |g|-spread {spread:.4f} above empirical 0.05; "
        f"investigate before reporting closure."
    )


def test_F1_four_path_synthesis_breaks_when_one_path_walks():
    """If one path's |g| is artificially shifted by 0.20, F1 triggers."""
    g_paths = [1.4190, 1.4070, 1.4187, 1.4190]
    g_paths[1] = g_paths[1] + 0.20  # walk one path
    spread = max(g_paths) - min(g_paths)
    assert spread > 0.15, (
        f"F1 must trigger when one path walks by 0.20; "
        f"got spread {spread:.4f}"
    )


# ============================================================================
# Sanity: correct inputs DO pass
# ============================================================================

def test_correct_inputs_pass():
    """With correct theta_em=pi, |g|=1.4187, S_bounce=37.995, must give canonical."""
    inputs_json = M.load_json(M.JSON_FILES["ew_scale_inputs"])
    inputs = inputs_json["inputs"]
    v_1l = M.hbr_tree_plus_1l(inputs["M_Pl_GeV"], inputs["S_bounce_P1"])
    cls = M.two_loop_closure(
        g=1.4187, g_normalization=2.078,
        D1_pct=-0.40893, D23_coeff=1.842,
        theta_em=math.pi,
    )
    v_canonical = M.v_ew_final(v_1l, cls)
    pdg = inputs["V_EW_PDG"]
    pdg_unc = inputs["V_EW_PDG_uncertainty"]
    assert abs(v_canonical - pdg) <= pdg_unc, (
        f"Canonical v_EW={v_canonical} should be within PDG +/- {pdg_unc}"
    )
    # And specifically: 246.218558 +/- 1e-4
    assert abs(v_canonical - 246.218558) < 1e-4, (
        f"Canonical v_EW={v_canonical} mismatch with 246.218558"
    )
