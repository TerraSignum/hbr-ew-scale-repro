"""Generate paper/figures/fig_v5_g_paths.pdf: 3+1 consensus
on the renormalised carrier-defect coupling |g|.

Reads the bundled v5_g_consensus.json (provenance 2026-04-25,
'four-path converged' status). Plots the tree value g_tree=1.66,
each of the three regularization-distinct paths
(spectral-cutoff, MS-bar Davydychev--Tausk, heat-kernel/zeta on
S^4) plus the algebraic self-consistency cross-check
(closed-form setting-sun), and the consensus band
|g| = 1.4187 +- 0.10. The healing factor
|g|_MS/|g|_tree = 0.8546 matches sqrt(0.524/0.718) = 0.8543 on
the cosmological-transport side to three significant digits.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless CI / no-DISPLAY
matplotlib.rcParams["pdf.fonttype"] = 42  # embed TrueType (vector, arXiv-friendly)
matplotlib.rcParams["ps.fonttype"] = 42

import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "v5_g_consensus.json"
OUT = REPO / "paper" / "figures" / "fig_v5_g_paths.pdf"
OUT_PNG = OUT.with_suffix(".png")


def main():
    with open(DATA, encoding="utf-8") as f:
        d = json.load(f)
    g_tree = d["consensus_tree_value"]
    g_band = d["consensus_band"]
    g_central = d["consensus_value_msbar_central"]
    heal = d["msbar_heal_factor"]
    paths = d["paths"]

    point_paths = [
        ("closed-form setting-sun (algebraic self-consistency)",
         paths["v5_4_closed_form"]["value"], None),
        ("spectral-cutoff (regularization-distinct)",
         (paths["v5_5_sigma_cutoff"]["value_band"][0]
          + paths["v5_5_sigma_cutoff"]["value_band"][1]) / 2,
         paths["v5_5_sigma_cutoff"]["value_band"]),
        ("MS-bar Davydychev--Tausk (canonical reporting)",
         paths["v5_6_msbar_full"]["value"], None),
        ("heat-kernel zeta on $S^4$ (geometric strengthening)",
         paths["v5_7_heat_kernel_zeta_S4"]["value"], None),
    ]

    fig, ax = plt.subplots(figsize=(7.6, 4.0), dpi=160)

    ax.axvspan(g_band[0], g_band[1], alpha=0.20, color="C2",
               label=f"consensus band [{g_band[0]:.2f}, {g_band[1]:.2f}]")
    ax.axvline(g_central, color="C2", lw=1.6, linestyle="--",
               label=f"$|g|_\\mathrm{{MS}}={g_central:.4f}$")
    ax.scatter([g_tree], [len(point_paths)], marker="o",
               s=110, facecolors="white", edgecolors="black", lw=1.8,
               zorder=4, label=f"tree value $|g|_\\mathrm{{tree}}={g_tree:.2f}$")

    y_pos = list(range(len(point_paths) - 1, -1, -1))
    for (lbl, val, band), y in zip(point_paths, y_pos):
        if band is not None:
            ax.errorbar(val, y,
                         xerr=[[val - band[0]], [band[1] - val]],
                         fmt="o", ms=8, color="C0", capsize=5)
        else:
            ax.scatter(val, y, marker="s", s=80, color="C0", zorder=3)
        ax.text(val, y + 0.18, lbl, ha="center", va="bottom",
                 fontsize=9.0)

    # Healing factor annotation
    ax.annotate(
        f"healing factor "
        f"$|g|_\\mathrm{{MS}}/|g|_\\mathrm{{tree}}={heal:.4f}$\n"
        r"$=\sqrt{0.524/0.718}=0.8543$"
        " demanded by\ncosmological-transport amplification\n"
        "(second-canonical-regime ratio)",
        xy=(g_central, 1.5), xytext=(1.18, 0.0),
        fontsize=8.5,
        arrowprops=dict(arrowstyle="->", color="gray"),
    )

    ax.set_xlim(1.10, 1.80)
    ax.set_ylim(-0.6, len(point_paths) + 0.6)
    ax.set_xlabel(r"renormalised carrier-defect coupling $|g|$",
                   fontsize=11)
    ax.set_yticks(y_pos + [len(point_paths)])
    ax.set_yticklabels([
        "closed-form\n(self-consistency)",
        r"$\sigma$-cutoff",
        r"MS-bar (canonical)",
        r"heat-kernel/zeta $S^4$",
        "tree value (pre-renorm)",
    ])
    ax.set_title("$3{+}1$ consensus on the renormalised "
                  "carrier-defect coupling $|g|$\n"
                  "(three regularization-distinct paths "
                  "+ one algebraic self-consistency check)",
                  fontsize=10)
    ax.legend(loc="lower right", fontsize=8.5, framealpha=0.95)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT, format="pdf", bbox_inches="tight")
    fig.savefig(OUT_PNG, format="png", bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
