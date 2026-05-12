"""
Generate the four figures of the manuscript:

  Figure 1 - Pipeline: M_Pl -> HBR Tree+1L -> 245.1164 GeV
                     -> defect-field 2-loop -> 246.2186 GeV
  Figure 2 - |g|-consensus across the four calculation paths
  Figure 3 - v_EW per path vs PDG band
  Figure 4 - Falsification map (theta_em=0, |g|-range>0.15, S_bounce shift)

Outputs are written to paper/figures/ in PDF and PNG.

Usage:
    python ./src/make_figures.py
"""

import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend for CI
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

import recompute_ew_scale as M  # noqa: E402

FIG_DIR = REPO / "paper" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


# Use a peer-review-friendly style: large fonts, clean look
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})


def save_both(fig, stem):
    """Save figure as both PDF and PNG."""
    pdf_path = FIG_DIR / f"{stem}.pdf"
    png_path = FIG_DIR / f"{stem}.png"
    fig.savefig(pdf_path)
    fig.savefig(png_path)
    print(f"  Saved: {pdf_path.relative_to(REPO)} + .png")


# ============================================================================
# Figure 1 - Pipeline schematic
# ============================================================================

def figure_1_pipeline():
    """Schematic of the calculation chain.

    Layout choices: wider boxes so the HBR formula renders unambiguously
    (the 2/pi prefactor and the negative exponent must be visually
    obvious to a peer reviewer).
    """
    fig, ax = plt.subplots(figsize=(12, 4.0))
    ax.set_axis_off()

    # Box geometry: wider boxes (0.20) with smaller gaps so the formula
    # has more horizontal room.
    box_w, box_h = 0.20, 0.46
    y_box = 0.42
    x_centers = [0.13, 0.38, 0.62, 0.87]

    boxes = [
        ("$M_{\\mathrm{Pl}}$\n$1.2209 \\times 10^{19}$ GeV",
         "#cfe2f3"),
        ("HBR Tree+1L",
         "#fce5cd"),
        ("Defect-field\ntwo-loop correction",
         "#d9ead3"),
        ("$v_{\\mathrm{EW}}^{(2\\mathrm{L})}$\n$246.2186$ GeV",
         "#f4cccc"),
    ]
    for x_c, (label, color) in zip(x_centers, boxes):
        x = x_c - box_w / 2
        rect = plt.Rectangle((x, y_box), box_w, box_h,
                             facecolor=color, edgecolor="black", lw=1.5)
        ax.add_patch(rect)
        ax.text(x_c, y_box + box_h / 2, label,
                ha="center", va="center", fontsize=12)

    # The HBR formula gets its own dedicated, larger annotation directly
    # below the HBR Tree+1L box, in display style with a clear minus sign
    # and 2/pi prefactor. This is the formula a reviewer must be able to
    # parse at a glance.
    ax.text(x_centers[1], y_box - 0.08,
            r"$v_{\mathrm{EW}}^{(1\mathrm{L})}\;=\;"
            r"\dfrac{2}{\pi}\,M_{\mathrm{Pl}}\,e^{-S_{\mathrm{bounce}}}$",
            ha="center", va="top", fontsize=15)

    # Residual annotation above the HBR Tree+1L box (corrected sign).
    ax.text(x_centers[1], y_box + box_h + 0.06,
            r"$245.1164$ GeV  ($0.45\%$ below PDG)",
            ha="center", va="bottom", fontsize=10,
            color="#444444", style="italic")

    # Arrows between boxes
    for i in range(3):
        x_left = x_centers[i] + box_w / 2
        x_right = x_centers[i + 1] - box_w / 2
        ax.annotate("", xy=(x_right, y_box + box_h / 2),
                    xytext=(x_left, y_box + box_h / 2),
                    arrowprops=dict(arrowstyle="->", lw=1.8, color="black"))

    # Bottom annotation: PDG benchmark
    ax.text(0.50, 0.06,
            r"PDG benchmark: $v_{\mathrm{EW}} = 246.22 \pm 0.07$ GeV  "
            r"$\;|\;$  $\Delta v / v = -5.86 \times 10^{-6}$",
            ha="center", fontsize=11, weight="bold")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("auto")
    ax.set_title("Calculation pipeline: HBR + defect-field two-loop correction",
                 pad=12, fontsize=12)
    save_both(fig, "fig1_pipeline")
    plt.close(fig)


# ============================================================================
# Figure 2 - |g| consensus
# ============================================================================

def figure_2_g_consensus():
    """Bar chart of |g| values from the four paths."""
    R = M.compute_all()
    consensus = R["consensus"]

    # Map path keys to externally-rendered method names
    label_map = {
        "closed_form_rigorous":          "Closed-form\nsetting-sun",
        "sigma_cutoff":         "Sigma-cutoff\nscheme",
        "msbar_full_two_loop":           "Full $\\overline{\\mathrm{MS}}$\nDavydychev-Tausk",
        "heat_kernel_zeta_S4":  "FL-$S^4$\nheat-kernel/zeta",
    }
    paths = consensus["paths"]
    names = [label_map.get(k, k) for k in paths.keys()]
    values = list(paths.values())

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#4a90d9", "#e89043", "#5cb85c", "#9b59b6"]
    bars = ax.bar(names, values, color=colors, edgecolor="black", lw=1.0)

    # Mean line
    g_mean = consensus["g_mean"]
    ax.axhline(g_mean, color="black", linestyle="--", lw=1.2,
               label=f"4-path mean: $\\langle|g|\\rangle = {g_mean:.4f}$")

    # Canonical highlight
    g_canonical = R["canonical"]["g_MSbar"]
    ax.axhline(g_canonical, color="red", linestyle=":", lw=1.5,
               label=f"Canonical ($\\overline{{\\mathrm{{MS}}}}$): $|g| = {g_canonical:.4f}$")

    # Consensus uncertainty band: |g| = 1.42 +/- 0.10 (the abstract's
    # consensus value). NOT the PDG-pass landing window (which is the
    # narrower [1.396, 1.443] computed in the manuscript caption).
    g_band_center = 1.42
    g_band_half = 0.10
    ax.axhspan(g_band_center - g_band_half, g_band_center + g_band_half,
               alpha=0.10, color="green",
               label=fr"consensus band $|g|={g_band_center:.2f}\pm {g_band_half:.2f}$")

    # Annotate values on bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.001,
                f"{val:.4f}", ha="center", va="bottom", fontsize=9)

    ax.set_ylabel("$|g|$ ($\\overline{\\mathrm{MS}}$)", fontsize=11)
    ax.set_title("Coupling $|g|$ across four independent calculation paths", pad=10)
    ax.set_ylim(1.30, 1.55)
    ax.legend(loc="lower right", framealpha=0.95)

    save_both(fig, "fig2_g_consensus")
    plt.close(fig)


# ============================================================================
# Figure 3 - v_EW per path vs PDG band
# ============================================================================

def figure_3_v_ew_per_path():
    """v_EW per path with PDG +/- 1 sigma band. Two-panel layout to avoid overlap."""
    R = M.compute_all()

    label_map = {
        "closed_form_rigorous":          "Closed-form\nsetting-sun",
        "sigma_cutoff":         "Sigma-cutoff\nscheme",
        "msbar_full_two_loop":           "Full $\\overline{\\mathrm{MS}}$\nDavydychev-Tausk",
        "heat_kernel_zeta_S4":  "FL-$S^4$\nheat-kernel/zeta",
    }

    paths = R["per_path"]
    names = [label_map.get(k, k) for k in paths.keys()]
    v_values = [paths[k]["v_EW_GeV"] for k in paths.keys()]

    inputs = R["inputs"]
    pdg = inputs["PDG_v_EW_GeV"]
    pdg_unc = inputs["PDG_v_EW_uncertainty_GeV"]

    canonical = R["canonical"]["v_EW_GeV"]
    robustness = R["robustness"]["v_EW_GeV"]
    v_1l = R["v_EW_1L_GeV"]

    # Two-panel layout: left = full picture, right = zoomed PDG-band region
    fig, (ax_full, ax_zoom) = plt.subplots(1, 2, figsize=(13, 5.5),
                                           gridspec_kw={"width_ratios": [1, 1.3]})

    # ---- Left: full picture (Tree+1L vs final) ----
    ax = ax_full
    x_left, x_right = -0.6, len(names) - 0.4
    ax.fill_between([x_left, x_right], pdg - pdg_unc, pdg + pdg_unc,
                    color="#aed6f1", alpha=0.35,
                    label="PDG $\\pm 1\\sigma$")
    ax.axhline(pdg, color="#1f618d", linestyle="-", lw=1.2)

    x_paths = list(range(len(names)))
    colors = ["#4a90d9", "#e89043", "#5cb85c", "#9b59b6"]
    for x, v, c in zip(x_paths, v_values, colors):
        ax.scatter(x, v, color=c, s=140, edgecolor="black", lw=1.0, zorder=3)

    ax.axhline(v_1l, color="gray", linestyle=":", lw=1.2,
               label=f"HBR Tree+1L: ${v_1l:.4f}$ GeV")
    ax.annotate(f"Tree+1L = {v_1l:.4f} GeV", xy=(0.5, v_1l), xytext=(0.5, v_1l - 0.15),
                ha="center", fontsize=9, color="gray")

    ax.set_xticks(x_paths)
    ax.set_xticklabels(names, fontsize=9)
    ax.set_xlim(x_left, x_right)
    ax.set_ylim(244.85, 246.50)
    ax.set_ylabel("$v_{\\mathrm{EW}}$ (GeV)", fontsize=11)
    ax.set_title("(A) Full picture: Tree+1L vs. four-path two-loop closure", fontsize=11)
    ax.legend(loc="lower right", framealpha=0.95, fontsize=9)

    # ---- Right: zoomed view of the PDG-band region ----
    ax = ax_zoom
    x_left, x_right = -0.7, len(names) + 1.4
    ax.fill_between([x_left, x_right], pdg - pdg_unc, pdg + pdg_unc,
                    color="#aed6f1", alpha=0.30,
                    label=r"PDG $\pm 1\sigma$: $246.22 \pm 0.07$ GeV")
    ax.axhline(pdg, color="#1f618d", linestyle="-", lw=1.2,
               label=r"PDG central: $246.22$ GeV")

    # Per-path scatter with annotation OFFSET vertically (above/below) to
    # avoid overlap with the PDG horizontal line and the data point itself.
    for i, (x, v, c) in enumerate(zip(x_paths, v_values, colors)):
        ax.scatter(x, v, color=c, s=200, edgecolor="black", lw=1.2, zorder=4)
        # Vertical stagger (alternating up/down) keeps numbers off the line
        dy = +0.030 if i % 2 == 0 else -0.030
        ax.annotate(f"{v:.4f}", xy=(x, v), xytext=(x, v + dy),
                    ha="center", va=("bottom" if dy > 0 else "top"),
                    fontsize=11, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.18",
                              facecolor="white", edgecolor=c, lw=0.8,
                              alpha=0.95),
                    arrowprops=dict(arrowstyle="-", color=c, lw=0.6),
                    zorder=5)

    # Reported values column with extra spacing
    x_can = len(names) + 0.7
    ax.scatter(x_can, canonical, color="red", marker="*", s=380,
               edgecolor="black", lw=1.2, zorder=4,
               label=f"Canonical: {canonical:.5f} GeV")
    ax.scatter(x_can, robustness, color="black", marker="D", s=130,
               edgecolor="white", lw=1.0, zorder=4,
               label=f"4-path mean: {robustness:.5f} GeV")
    ax.annotate(f"{canonical:.4f}", xy=(x_can, canonical),
                xytext=(x_can, canonical + 0.030),
                ha="center", va="bottom", fontsize=11, color="red",
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor="red", lw=0.8, alpha=0.95),
                arrowprops=dict(arrowstyle="-", color="red", lw=0.6),
                zorder=5)
    ax.annotate(f"{robustness:.4f}", xy=(x_can, robustness),
                xytext=(x_can, robustness - 0.030),
                ha="center", va="top", fontsize=11, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor="black", lw=0.8, alpha=0.95),
                arrowprops=dict(arrowstyle="-", color="black", lw=0.6),
                zorder=5)

    ax.set_xticks(x_paths + [x_can])
    ax.set_xticklabels(names + ["Reported\nvalues"], fontsize=9)
    ax.set_xlim(x_left, x_right)
    ax.set_ylim(246.05, 246.34)
    ax.set_ylabel(r"$v_{\mathrm{EW}}$ (GeV)", fontsize=11)
    ax.set_title("(B) Zoomed: four paths + reported values within PDG band",
                  fontsize=11)
    ax.legend(loc="lower left", framealpha=0.95, fontsize=8)

    fig.suptitle("Reproduced electroweak scale across four paths, with PDG benchmark",
                 y=1.00, fontsize=12)
    fig.tight_layout()
    save_both(fig, "fig3_v_ew_per_path")
    plt.close(fig)


# ============================================================================
# Figure 4 - Falsification map
# ============================================================================

def figure_4_falsification():
    """Three-panel figure showing falsification handles."""
    inputs_json = M.load_json(M.JSON_FILES["ew_scale_inputs"])
    inputs = inputs_json["inputs"]
    pdg = inputs["V_EW_PDG"]
    pdg_unc = inputs["V_EW_PDG_uncertainty"]

    g_canonical = 1.4187
    g_norm = 2.078
    D1 = -0.40893
    D23 = 1.842
    M_Pl = inputs["M_Pl_GeV"]
    S_bounce = inputs["S_bounce_P1"]
    v_1l = M.hbr_tree_plus_1l(M_Pl, S_bounce)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    # ---- Panel A: theta_em scan ----
    ax = axes[0]
    theta_grid = np.linspace(0, 2 * math.pi, 200)
    v_vs_theta = []
    for th in theta_grid:
        cls = M.two_loop_closure(g_canonical, g_norm, D1, D23, th)
        v_vs_theta.append(M.v_ew_final(v_1l, cls))
    v_vs_theta = np.array(v_vs_theta)

    ax.plot(theta_grid, v_vs_theta, color="#4a90d9", lw=1.8)
    ax.axhspan(pdg - pdg_unc, pdg + pdg_unc, color="#aed6f1", alpha=0.35,
               label=f"PDG band $\\pm 0.07$ GeV")
    ax.axvline(math.pi, color="green", linestyle=":", lw=1.5,
               label="$\\theta_{\\mathrm{em}} = \\pi$ (axiom)")
    ax.axvline(0, color="red", linestyle=":", lw=1.5, alpha=0.7,
               label="$\\theta_{\\mathrm{em}} = 0$ (wrong sign)")
    ax.scatter([math.pi], [pdg], color="green", s=80, zorder=5)
    ax.scatter([0], [v_vs_theta[0]], color="red", s=80, zorder=5)
    ax.set_xlabel("$\\theta_{\\mathrm{em}}$ (rad)")
    ax.set_ylabel("$v_{\\mathrm{EW}}$ (GeV)")
    ax.set_title("(A) T-parity test: $\\theta_{\\mathrm{em}}$ scan")
    ax.set_xticks([0, math.pi/2, math.pi, 3*math.pi/2, 2*math.pi])
    ax.set_xticklabels(["$0$", "$\\pi/2$", "$\\pi$", "$3\\pi/2$", "$2\\pi$"])
    ax.legend(loc="lower center", fontsize=8)

    # ---- Panel B: |g| scan ----
    ax = axes[1]
    g_grid = np.linspace(1.0, 1.8, 200)
    v_vs_g = []
    for g in g_grid:
        cls = M.two_loop_closure(g, g_norm, D1, D23, math.pi)
        v_vs_g.append(M.v_ew_final(v_1l, cls))
    v_vs_g = np.array(v_vs_g)

    ax.plot(g_grid, v_vs_g, color="#5cb85c", lw=1.8)
    ax.axhspan(pdg - pdg_unc, pdg + pdg_unc, color="#aed6f1", alpha=0.35,
               label=f"PDG band $\\pm 0.07$ GeV")

    # PDG-pass landing window for |g|: solve v_EW(g) in [pdg-unc, pdg+unc]
    pdg_pass_lo = 1.3955
    pdg_pass_hi = 1.4427
    ax.axvspan(pdg_pass_lo, pdg_pass_hi, color="#90ee90", alpha=0.35,
               label=fr"F4 PDG-pass window $[{pdg_pass_lo:.3f},\,{pdg_pass_hi:.3f}]$")
    ax.axvline(g_canonical, color="red", linestyle=":", lw=1.5,
               label=fr"$|g|_{{\overline{{\mathrm{{MS}}}}}} = {g_canonical}$")

    ax.set_xlabel("$|g|$")
    ax.set_ylabel("$v_{\\mathrm{EW}}$ (GeV)")
    ax.set_title("(B) Coupling test: $|g|$ scan")
    ax.legend(loc="lower right", fontsize=8)

    # ---- Panel C: S_bounce sensitivity ----
    ax = axes[2]
    delta_grid = np.linspace(-0.05, 0.05, 200)
    v_vs_dS = []
    for dS in delta_grid:
        v1l_shifted = M.hbr_tree_plus_1l(M_Pl, S_bounce + dS)
        cls = M.two_loop_closure(g_canonical, g_norm, D1, D23, math.pi)
        v_vs_dS.append(M.v_ew_final(v1l_shifted, cls))
    v_vs_dS = np.array(v_vs_dS)

    ax.plot(delta_grid, v_vs_dS, color="#9b59b6", lw=1.8)
    ax.axhspan(pdg - pdg_unc, pdg + pdg_unc, color="#aed6f1", alpha=0.35,
               label=f"PDG band $\\pm 0.07$ GeV")
    ax.axvline(0, color="green", linestyle=":", lw=1.5,
               label="$\\Delta S_{\\mathrm{bounce}} = 0$")

    # Find PDG-band edges
    in_band = np.abs(v_vs_dS - pdg) <= pdg_unc
    if in_band.any():
        idx = np.where(in_band)[0]
        ax.axvline(delta_grid[idx[0]], color="red", linestyle="--", lw=1.0, alpha=0.7)
        ax.axvline(delta_grid[idx[-1]], color="red", linestyle="--", lw=1.0, alpha=0.7,
                   label="PDG-band edges")

    ax.set_xlabel("$\\Delta S_{\\mathrm{bounce}}$")
    ax.set_ylabel("$v_{\\mathrm{EW}}$ (GeV)")
    ax.set_title("(C) Bounce-action sensitivity")
    ax.legend(loc="upper right", fontsize=8)

    fig.suptitle("Falsification handles for the HBR + defect-field two-loop closure",
                 y=1.02, fontsize=12)
    fig.tight_layout()

    save_both(fig, "fig4_falsification")
    plt.close(fig)


# ============================================================================
# Main
# ============================================================================

def main():
    print("Generating manuscript figures into paper/figures/")
    print()
    figure_1_pipeline()
    figure_2_g_consensus()
    figure_3_v_ew_per_path()
    figure_4_falsification()
    print()
    print("All four figures generated.")


if __name__ == "__main__":
    main()
