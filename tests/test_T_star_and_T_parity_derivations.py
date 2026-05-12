"""Tests for the upgrade of T* and theta_em from convention to
derivation:
  - T* = gamma^(V) = 1/(N_gen^2 + 1) = 1/10 (Paper6 Theorem 1).
  - theta_em = pi from chirality-pairing on the symmetric Xi-graph
    (Paper4A APS + Paper4D Kogut-Susskind index closure)."""
from __future__ import annotations
import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from verify_T_star_equals_gamma_vacuum import (
    gamma_vacuum_branch, T_STAR_AS_USED, N_GEN,
)
from verify_T_parity_from_chirality_pairing import (
    synthetic_chirality_paired_witness,
)


def test_T_star_equals_gamma_vacuum_exact():
    """T* (HBR scale) coincides exactly with gamma^(V) = 1/10
    from the two-phase coefficient theorem (Paper6 Thm.~1)."""
    assert N_GEN == 3
    assert gamma_vacuum_branch() == Fraction(1, 10)
    assert T_STAR_AS_USED == Fraction(1, 10)
    assert T_STAR_AS_USED == gamma_vacuum_branch()


def test_chirality_pair_residual_at_machine_precision():
    """Hermitian Wilson-Dirac H = gamma_5 D_W has a chirality-
    paired spectrum (+lambda, -lambda) at machine precision."""
    w = synthetic_chirality_paired_witness(n=32, seed=7)
    assert w["chirality_pairing_holds"]
    assert w["max_chirality_pair_residual"] < 1e-10


def test_eta_partial_zero_on_chirality_paired_spectrum():
    """eta_partial = sum_k sgn(lambda_k) = 0 when the spectrum is
    chirality-paired; this is the input that promotes the APS
    decomposition to log Omega(A) = A/4 + o(A) without boundary
    correction (Paper4A)."""
    w = synthetic_chirality_paired_witness(n=64, seed=11)
    assert w["eta_partial_zero"]
    assert abs(w["eta_invariant_sgn_sum"]) < 1e-10
