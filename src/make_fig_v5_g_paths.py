"""Generate paper/figures/fig_v5_g_paths.pdf: 3+1 consensus
on the renormalised carrier-defect coupling |g|.

Forest-plot / horizontal-dotplot rendering: each independent path
gets one row labelled on the left, the consensus band is a vertical
shaded region, and the healing-factor commentary lives in a labelled
inset to keep the data region uncluttered.

Reads the bundled v5_g_consensus.json (provenance 2026-04-25,
'four-path converged' status). The three regularization-distinct
paths -- spectral-cutoff, full MS-bar Davydychev--Tausk, and
heat-kernel/zeta on S^4 -- plus the closed-form algebraic
self-consistency check converge inside |g| = 1.4187 +/- 0.10. The
healing factor |g|_MS / |g|_tree = 0.8546 matches
sqrt(0.524 / 0.718) = 0.8543 demanded by the cosmological-transport
over-amplification on the excited regime.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
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

    # Row layout (top -> bottom): tree value on top (visually
    # "before renormalisation"), then the four convergent paths.
    rows = [
        {
            "label": "tree value\n(pre-renormalisation)",
            "value": g_tree,
            "band": None,
            "kind": "tree",
        },
        {
            "label": r"$\sigma$-cutoff scheme" "\n(regularisation-distinct)",
            "value": (paths["v5_5_sigma_cutoff"]["value_band"][0]
                       + paths["v5_5_sigma_cutoff"]["value_band"][1]) / 2,
            "band": paths["v5_5_sigma_cutoff"]["value_band"],
            "kind": "path",
        },
        {
            "label": (r"$\overline{\mathrm{MS}}$"
                       " Davydychev--Tausk\n(canonical reporting)"),
            "value": paths["v5_6_msbar_full"]["value"],
            "band": None,
            "kind": "path",
        },
        {
            "label": (r"heat-kernel $\zeta$ on $S^4$"
                       "\n(geometric strengthening)"),
            "value": paths["v5_7_heat_kernel_zeta_S4"]["value"],
            "band": None,
            "kind": "path",
        },
        {
            "label": ("closed-form setting-sun\n"
                       "(algebraic self-consistency)"),
            "value": paths["v5_4_closed_form"]["value"],
            "band": None,
            "kind": "check",
        },
    ]

    n_rows = len(rows)
    fig, (ax, ax_anno) = plt.subplots(
        nrows=2, figsize=(8.4, 4.6), dpi=160,
        gridspec_kw={"height_ratios": [n_rows + 1, 1.2],
                     "hspace": 0.05},
    )

    # ── Top panel: forest plot ──
    # Consensus band
    ax.axvspan(
        g_band[0], g_band[1], alpha=0.20, color="#2ca02c",
        label=fr"consensus band [{g_band[0]:.3f}, {g_band[1]:.3f}]",
    )
    # Consensus central value (renormalised target)
    ax.axvline(g_central, color="#2ca02c", lw=1.4, linestyle="--",
               label=fr"$|g|_{{\overline{{\rm MS}}}}={g_central:.4f}$")
    # Tree-value reference line
    ax.axvline(g_tree, color="#888", lw=1.0, linestyle=":",
               label=fr"$|g|_{{\rm tree}}={g_tree:.2f}$")

    # Plot each row at a fixed y
    y_pos = list(range(n_rows - 1, -1, -1))  # top -> bottom
    color_kind = {
        "tree": "#444444",
        "path": "#1f77b4",
        "check": "#9467bd",
    }
    marker_kind = {"tree": "o", "path": "s", "check": "D"}
    for r, y in zip(rows, y_pos):
        col = color_kind[r["kind"]]
        m = marker_kind[r["kind"]]
        if r["band"] is not None:
            lo, hi = r["band"]
            ax.errorbar(
                r["value"], y, xerr=[[r["value"] - lo], [hi - r["value"]]],
                fmt=m, ms=9, color=col, ecolor=col, capsize=5,
                elinewidth=1.4, zorder=3,
            )
        else:
            ax.scatter(r["value"], y, marker=m, s=85, color=col,
                       edgecolors="black", linewidths=0.6, zorder=3)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([r["label"] for r in rows], fontsize=9)
    ax.set_xlim(1.10, 1.80)
    ax.set_ylim(-0.6, n_rows - 0.4)
    ax.set_xlabel(r"renormalised carrier-defect coupling $|g|$",
                  fontsize=11)
    ax.set_title(r"$3{+}1$ consensus on the renormalised"
                  r" carrier-defect coupling $|g|$",
                  fontsize=11.5, pad=8)
    ax.grid(axis="x", alpha=0.3)
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.92)

    # ── Bottom panel: healing-factor commentary ──
    ax_anno.axis("off")
    plain_text = (
        f"Healing factor: |g|_MS / |g|_tree = {heal:.4f} "
        f"≈ sqrt(0.524 / 0.718) = 0.8543\n"
        "The same factor is independently demanded by the "
        "cosmological-transport over-amplification on the second\n"
        "canonical regime; the three regularisation-distinct paths "
        "and the algebraic check agree inside a 5% band."
    )
    ax_anno.text(0.5, 0.55, plain_text,
                 ha="center", va="center",
                 fontsize=9.0,
                 bbox={"boxstyle": "round,pad=0.55",
                       "facecolor": "#fff9e6",
                       "edgecolor": "#bba960"})

    fig.subplots_adjust(left=0.21, right=0.97, top=0.92, bottom=0.05)
    fig.savefig(OUT, format="pdf", bbox_inches="tight")
    fig.savefig(OUT_PNG, format="png", bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
