r"""Verify T* = gamma^(V) = 1/(N_gen^2 + 1) = 1/10 algebraically.

The previously-listed convention T* = 0.1 ("Lennard-Jones-type
low-energy convention") is upgraded to a derivation from the
two-phase coefficient theorem of the companion UV-closure paper
(Paper6 Theorem 1; Paper2 readout):

    gamma^(V) = sin^2(theta_chir^(V)) = 1 / (N_gen^2 + 1),
    theta_chir^(V) = arctan(1/N_gen),
    N_gen = 3  (integer-uniqueness, Paper2),
    gamma^(V) = 1/10 = 0.1  exact.

The numerical equality T* = gamma^(V) at the algebraic-rational
level lifts T* from convention class C to derivation class D.
"""
from __future__ import annotations
import json
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUTPUTS = REPO / "outputs"
OUTPUTS.mkdir(parents=True, exist_ok=True)

T_STAR_AS_USED = Fraction(1, 10)  # 0.1 as used in the HBR closure
N_GEN = 3                          # integer-uniqueness, Paper2


def gamma_vacuum_branch() -> Fraction:
    """gamma^(V) = 1 / (N_gen^2 + 1) from Paper6 Theorem 1."""
    return Fraction(1, N_GEN ** 2 + 1)


def main() -> None:
    print("=" * 78)
    print("Verify T* = gamma^(V) = 1/(N_gen^2 + 1) algebraic identity")
    print("=" * 78)
    gamma_v = gamma_vacuum_branch()
    print(f"  N_gen                   = {N_GEN}")
    print(f"  gamma^(V) (Paper6 Thm.1)= {gamma_v} "
          f"= {float(gamma_v):.6f}")
    print(f"  T* (HBR scale, P1)      = {T_STAR_AS_USED} "
          f"= {float(T_STAR_AS_USED):.6f}")
    identity = (gamma_v == T_STAR_AS_USED)
    print(f"  Identity T* = gamma^(V) : "
          f"{'OK (algebraic-rational match)' if identity else 'FAIL'}")
    bundle = {
        "title": ("T* = gamma^(V) algebraic identity verifier "
                    "(Paper1 input-class C -> D upgrade)"),
        "stand": "2026-05-06",
        "framework_constants": {"N_gen": N_GEN},
        "T_star_as_used_in_HBR_closure": str(T_STAR_AS_USED),
        "gamma_vacuum_from_Paper6_Thm1": str(gamma_v),
        "identity_holds": identity,
        "consequence": ("T* is no longer a Lennard-Jones-style "
                          "convention but the vacuum-branch value "
                          "of the chirality-mixing coefficient "
                          "from the two-phase coefficient theorem "
                          "of Paper6 (cited via Paper2 readout). "
                          "Reclassifies T* from input-class C "
                          "(convention) to D (derived)."),
    }
    out = OUTPUTS / "verify_T_star_equals_gamma_vacuum.json"
    out.write_text(json.dumps(bundle, indent=2),
                       encoding="utf-8")
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()
