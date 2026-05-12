# hbr-ew-scale-repro

**HBR electroweak-scale reproduction with defect-field two-loop correction
on the FL-S^4 bounce background.**

[![CI: reproduce-ew-scale](https://github.com/TerraSignum/hbr-ew-scale-repro/actions/workflows/reproduce.yml/badge.svg)](https://github.com/TerraSignum/hbr-ew-scale-repro/actions/workflows/reproduce.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This repository reproduces the electroweak vacuum expectation value `v_EW`
from a Hierarchy-Bridge-Relation (HBR) calculation with a defect-field
two-loop correction.

## Result in one line

```
v_EW (canonical, FULL MS-bar) = 246.2186 GeV
v_EW (robustness, 4-path mean)= 246.2103 GeV
PDG (2024)                    = 246.22 +/- 0.07 GeV
Both within PDG uncertainty.
```

## Scope

This package does **not** claim a complete theory of nature. It presents
a sharply defined, reproducible electroweak-scale calculation:

1. The HBR tree+1L formula sets the EW anchor:
   `v_EW^(1L) = (2/pi) * M_Pl * exp(-S_bounce) = 245.1164 GeV`
   (residual `+0.45%` to PDG).

2. A defect-field two-loop correction on the FL-S^4 bounce background closes
   the residual:
   `closure_pct = D_1 + (g/g_norm)^2 * D_23 * (-cos(theta_em))`
   with `theta_em = pi` (consequence of the T-parity source axiom that
   identifies the defect field with the bounce negative mode).

3. Four independent calculations of the coupling `|g|` give a consensus
   `|g| = 1.42 +/- 0.10` (MS-bar). The four paths agree within `0.012`,
   well below the falsification threshold `0.15`.

4. The Mode-B strict-recompute script reproduces both values from inputs
   without any hardcoded canonical override.

## What this is **not**

- Not a complete Standard-Model derivation
- Not a complete Quantum-Gravity theory
- Not a claim outside the closure domain
- The result is conditional on the T-parity source axiom, the MS-bar
  scheme for the two-loop contribution, and the HBR scale convention `T* = 0.1`

## Installation (Windows PowerShell)

```powershell
git clone https://github.com/TerraSignum/hbr-ew-scale-repro.git
cd hbr-ew-scale-repro

py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Installation (POSIX)

```bash
git clone https://github.com/TerraSignum/hbr-ew-scale-repro.git
cd hbr-ew-scale-repro

python3.11 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Reproduce the result

```powershell
python .\src\recompute_ew_scale.py
pytest
```

## Expected output (key lines)

```text
v_EW^(1L) = (2/pi) * M_Pl * exp(-S_bounce) = 245.116398 GeV
v_EW canonical (FULL MS-bar)  = 246.218558 GeV
v_EW robustness (4-path mean) = 246.210333 GeV
Within PDG uncertainty (+/-0.07 GeV)?  Canonical: True   Robustness: True
|g|-Range = 0.0120 (threshold 0.15) -- PASS
```

The complete expected output is in [`outputs/expected_output.txt`](outputs/expected_output.txt).

## Repository structure

```
hbr-ew-scale-repro/
├── README.md
├── LICENSE
├── CITATION.cff
├── requirements.txt
├── pyproject.toml
├── data/
│   ├── ew_scale_inputs.json
│   ├── g_consensus.json
│   ├── g_path_closed_form.json
│   ├── g_path_sigma_cutoff.json
│   ├── g_path_msbar.json
│   └── g_path_s4_heat_kernel.json
├── src/
│   └── recompute_ew_scale.py
├── tests/
│   ├── test_recompute_ew_scale.py
│   ├── test_g_consensus.py
│   ├── test_falsification.py
│   └── test_figures.py
├── outputs/
│   ├── expected_output.txt
│   └── recompute_result.json
├── paper/
│   ├── manuscript.tex
│   ├── manuscript.pdf
│   └── figures/
│       ├── fig1_pipeline.{pdf,png}
│       ├── fig2_g_consensus.{pdf,png}
│       ├── fig3_v_ew_per_path.{pdf,png}
│       └── fig4_falsification.{pdf,png}
└── .github/workflows/
    └── reproduce.yml
```

## Inputs and conventions

| Quantity | Value | Role |
|---|---:|---|
| `M_Pl` | 1.2209e+19 GeV | external scale input (PDG) |
| `S_bounce` | 37.995389 | HBR / Coleman bounce action |
| `T*` | 0.1 | HBR scale convention (NOT MS-bar) |
| `theta_em` | pi | T-parity source-axiom consequence |
| `D_1` | -0.40893% | pure-phi figure-8 diagram |
| `D_23` | 1.842 | mixed diagrams (D_2 + D_3) |
| `g_norm` | 2.078 | normalization |
| PDG `v_EW` | 246.22 +/- 0.07 GeV | benchmark |

**Two distinct conventions:**
- **MS-bar**: renormalization of the two-loop contribution
- **T* = 0.1**: HBR scale convention (Lennard-Jones, Landau-Lifshitz QM section 132)

These are **not the same thing** and must not be conflated.

## Falsification

The closure fails if any of the following occur:

1. `|g|`-range across four paths > 0.15
2. `theta_em` differs from pi (the T-parity source-axiom test, F2 in the paper)
3. `S_bounce` shifted such that recompute leaves `[246.15, 246.29]` GeV

The `tests/test_falsification.py` test deliberately constructs broken
configurations and checks that the script correctly identifies them as
out-of-bounds.

## Method names and source files

The four independent calculations of the two-loop coupling `|g|`
correspond to the following per-method JSON files:

| Method (paper) | Source file |
|---|---|
| Closed-form setting-sun | `data/g_path_closed_form.json` |
| Sigma-cutoff scheme | `data/g_path_sigma_cutoff.json` |
| Full MS-bar Davydychev--Tausk | `data/g_path_msbar.json` |
| Four-sphere heat-kernel / zeta | `data/g_path_s4_heat_kernel.json` |

Each JSON includes a `block` field with an internal archival identifier;
this is preserved purely for cross-reference to the originating
calculation and is not part of the physics content.

## Citation

If you use this code or data, please cite:

```bibtex
@misc{bucciarelli2026hbrew,
  author    = {Bucciarelli, Sandro},
  title     = {HBR electroweak-scale reproduction package},
  year      = {2026},
  version   = {0.1.0},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.XXXXXXX}
}
```

See [CITATION.cff](CITATION.cff) for machine-readable metadata.

## Data integrity

SHA-256 hashes of all data files are in [`data/SHA256SUMS`](data/SHA256SUMS).
The published results correspond to data release `v0.1.0`.

## License

MIT License. See [LICENSE](LICENSE).
