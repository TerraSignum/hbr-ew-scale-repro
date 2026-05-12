"""
Verify that the figure-generation script produces all four figures
in both PDF and PNG, and that they are non-empty.

These tests do not check the visual content of the figures (that is
the job of the maintainer's eyes); they only verify that the script
runs end-to-end without errors and that the expected files are
written. This guards against silent failures in the figure-generation
pipeline (e.g., a missing import, a misnamed output file, a backend
issue on a fresh CI runner).

The tests skip cleanly if matplotlib is not installed, so the rest
of the test suite remains useful in minimal environments.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src" / "make_figures.py"
FIGDIR = REPO / "paper" / "figures"

EXPECTED_STEMS = [
    "fig1_pipeline",
    "fig2_g_consensus",
    "fig3_v_ew_per_path",
    "fig4_falsification",
]


def _matplotlib_available() -> bool:
    return importlib.util.find_spec("matplotlib") is not None


pytestmark = pytest.mark.skipif(
    not _matplotlib_available(),
    reason="matplotlib not installed; figure tests skipped",
)


def test_make_figures_script_exists():
    assert SRC.exists(), f"Missing figure-generation script: {SRC}"


def test_make_figures_runs_end_to_end(tmp_path):
    """
    Run the figure script in-place and check that all four figures
    exist and are non-empty afterward.

    We do not redirect output to tmp_path because the script writes
    to its conventional location (paper/figures/). The pre-existing
    figures are overwritten in place; if the script crashes, the
    timestamps will be older than the run and we'll detect it via
    a deliberate touch + run + check pattern would be overkill here.
    Instead we just verify that the script returns 0 and produces
    non-empty PDF + PNG for every figure.
    """
    result = subprocess.run(
        [sys.executable, str(SRC)],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    assert result.returncode == 0, (
        f"make_figures.py failed (rc={result.returncode}).\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    for stem in EXPECTED_STEMS:
        for ext in ("pdf", "png"):
            f = FIGDIR / f"{stem}.{ext}"
            assert f.exists(), f"Missing figure: {f}"
            assert f.stat().st_size > 1000, (
                f"Figure {f} is suspiciously small ({f.stat().st_size} bytes); "
                f"figure generation likely produced an empty/corrupt file."
            )


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_each_figure_pdf_has_pdf_header(stem):
    """
    PDF files start with '%PDF-'. This is a cheap sanity check that
    we are writing real PDFs and not, say, an HTML error page.
    """
    f = FIGDIR / f"{stem}.pdf"
    if not f.exists():
        pytest.skip(f"{f} does not exist yet; run make_figures.py first")
    with open(f, "rb") as fh:
        head = fh.read(5)
    assert head == b"%PDF-", f"{f} does not start with PDF header (got {head!r})"


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_each_figure_png_has_png_header(stem):
    """
    PNG files start with the 8-byte signature 89 50 4E 47 0D 0A 1A 0A.
    """
    f = FIGDIR / f"{stem}.png"
    if not f.exists():
        pytest.skip(f"{f} does not exist yet; run make_figures.py first")
    with open(f, "rb") as fh:
        head = fh.read(8)
    expected = b"\x89PNG\r\n\x1a\n"
    assert head == expected, f"{f} does not start with PNG signature (got {head!r})"
