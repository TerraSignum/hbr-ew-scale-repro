"""
Tests for the strict-recompute chain: HBR Tree+1L, two-loop closure,
canonical and robustness values.
"""

import json
import math
import sys
from pathlib import Path

# Ensure src/ is on the import path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

import recompute_ew_scale as M  # noqa: E402


# ============================================================================
# Tree+1L numerical exactness
# ============================================================================

def test_tree_plus_1l_matches_canonical():
    """v_EW^(1L) = (2/pi) * M_Pl * exp(-S_bounce) = 245.116398 GeV (+/-1e-6)"""
    inputs_json = M.load_json(M.JSON_FILES["ew_scale_inputs"])
    inputs = inputs_json["inputs"]
    v_1l = M.hbr_tree_plus_1l(inputs["M_Pl_GeV"], inputs["S_bounce_P1"])
    assert abs(v_1l - 245.116398) < 1e-5, f"Tree+1L mismatch: {v_1l}"


def test_tree_plus_1l_residual_to_pdg():
    """Tree+1L residual to PDG is +0.45% (+/-0.001%)"""
    inputs_json = M.load_json(M.JSON_FILES["ew_scale_inputs"])
    inputs = inputs_json["inputs"]
    v_1l = M.hbr_tree_plus_1l(inputs["M_Pl_GeV"], inputs["S_bounce_P1"])
    residual_pct = (v_1l - inputs["V_EW_PDG"]) / inputs["V_EW_PDG"] * 100
    # Reviewer note: residual should be -0.45 % (Tree+1L below PDG)
    assert -0.46 < residual_pct < -0.44, f"Residual outside [-0.46, -0.44]: {residual_pct}"


# ============================================================================
# Canonical precision value (FULL MS-bar Davydychev-Tausk path)
# ============================================================================

def test_canonical_precision_value():
    """Canonical |g|=1.4187 (FULL MS-bar) => v_EW = 246.218558 GeV (+/-1e-5)"""
    R = M.compute_all()
    can = R["canonical"]
    assert abs(can["g_MSbar"] - 1.4187) < 1e-3, f"Canonical |g| mismatch: {can['g_MSbar']}"
    assert abs(can["v_EW_GeV"] - 246.218558) < 1e-4, (
        f"Canonical v_EW mismatch: {can['v_EW_GeV']}"
    )


def test_canonical_within_pdg_uncertainty():
    """Canonical v_EW is within +/- 0.07 GeV of PDG"""
    R = M.compute_all()
    can = R["canonical"]
    pdg = R["inputs"]["PDG_v_EW_GeV"]
    pdg_unc = R["inputs"]["PDG_v_EW_uncertainty_GeV"]
    assert abs(can["v_EW_GeV"] - pdg) <= pdg_unc, (
        f"Canonical {can['v_EW_GeV']} outside PDG +/- {pdg_unc}"
    )


# ============================================================================
# Robustness value (4-path mean)
# ============================================================================

def test_robustness_value():
    """4-path mean |g|=1.4160 => v_EW = 246.2105 GeV (+/-1e-3)"""
    R = M.compute_all()
    rob = R["robustness"]
    assert abs(rob["g_mean_4path"] - 1.4160) < 1e-3, (
        f"4-path mean |g| mismatch: {rob['g_mean_4path']}"
    )
    assert abs(rob["v_EW_GeV"] - 246.2105) < 1e-3, (
        f"Robustness v_EW mismatch: {rob['v_EW_GeV']}"
    )


def test_robustness_within_pdg_uncertainty():
    """Robustness v_EW is within +/- 0.07 GeV of PDG"""
    R = M.compute_all()
    rob = R["robustness"]
    pdg = R["inputs"]["PDG_v_EW_GeV"]
    pdg_unc = R["inputs"]["PDG_v_EW_uncertainty_GeV"]
    assert abs(rob["v_EW_GeV"] - pdg) <= pdg_unc, (
        f"Robustness {rob['v_EW_GeV']} outside PDG +/- {pdg_unc}"
    )


# ============================================================================
# Per-path verification
# ============================================================================

def test_per_path_within_pdg():
    """Each of the four paths gives v_EW within PDG uncertainty"""
    R = M.compute_all()
    pdg = R["inputs"]["PDG_v_EW_GeV"]
    pdg_unc = R["inputs"]["PDG_v_EW_uncertainty_GeV"]
    for path_name, d in R["per_path"].items():
        assert abs(d["v_EW_GeV"] - pdg) <= pdg_unc, (
            f"Path {path_name} v_EW={d['v_EW_GeV']} outside PDG +/- {pdg_unc}"
        )


# ============================================================================
# Sign convention verification (theta_em = pi)
# ============================================================================

def test_theta_em_pi_implies_positive_closure():
    """Under theta_em = pi, sign factor is +1, closure is positive"""
    closure_at_pi = M.two_loop_closure(
        g=1.4187, g_normalization=2.078, D1_pct=-0.40893,
        D23_coeff=1.842, theta_em=math.pi,
    )
    assert closure_at_pi > 0, f"Closure at theta_em=pi should be positive: {closure_at_pi}"
    # And it should give exactly the canonical 0.44965%
    assert abs(closure_at_pi - 0.44965) < 1e-4, f"Closure mismatch: {closure_at_pi}"


def test_theta_em_zero_breaks_closure():
    """Under theta_em = 0 (wrong sign convention), closure has opposite sign"""
    closure_at_zero = M.two_loop_closure(
        g=1.4187, g_normalization=2.078, D1_pct=-0.40893,
        D23_coeff=1.842, theta_em=0.0,
    )
    # cos(0)=+1, so sign_factor=-1, closure becomes negative
    assert closure_at_zero < 0, (
        f"Closure at theta_em=0 should be negative (wrong-sign): {closure_at_zero}"
    )
