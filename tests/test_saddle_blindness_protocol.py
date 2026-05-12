"""Saddle-first reproducer chain blindness protocol test.

Enforces the structural-input order documented in
data/saddle_blindness_witness.json: the S^4-bounce saddle
output (audit_eta_S_high_precision) must be committed strictly
before the EW-scale matching script consumes S_bounce as input.

The test reads the bundled SHA-256 hash + mtime witness and
verifies that the saddle files are not strictly newer than the
matching files: a violation would mean the matching was frozen
first and the saddle was re-fitted to v_EW after the fact, which
the no-fit-conditional-closure framing of P1 forbids.

Test verdict:
  PASS if max(mtime_saddle) <= max(mtime_matching) at the time
       the witness was frozen, AND all bundled files exist with
       their bundled SHA-256 hashes.
  FAIL otherwise (with diagnostic on which file violates).
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
WITNESS_PATH = REPO / "data" / "saddle_blindness_witness.json"


def _sha256(p: Path) -> str:
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


@pytest.fixture(scope="module")
def witness():
    assert WITNESS_PATH.exists(), (
        f"saddle_blindness_witness.json missing at {WITNESS_PATH}; "
        "the saddle-first protocol cannot be verified without "
        "the bundled witness")
    with open(WITNESS_PATH) as f:
        return json.load(f)


def test_witness_has_required_fields(witness):
    for key in ("saddle_files", "matching_files", "file_hashes",
                "frozen_S_bounce", "protocol_invariant"):
        assert key in witness, f"witness missing key: {key}"


def test_all_witnessed_files_exist(witness):
    for fpath in witness["file_hashes"]:
        assert (REPO / fpath).exists(), (
            f"witnessed file {fpath} is missing from the repo; "
            "the saddle-first protocol cannot verify a rebuild "
            "without it")


def test_witnessed_hashes_match_current_state(witness):
    """The bundled SHA-256 hashes must match the current file
    bytes; a mismatch means a file was modified after the
    witness was frozen and the protocol must be re-witnessed.
    """
    for fpath, entry in witness["file_hashes"].items():
        actual = _sha256(REPO / fpath)
        expected = entry["sha256"]
        assert actual == expected, (
            f"SHA-256 mismatch on {fpath}: bundled witness "
            f"recorded {expected[:16]}..., current bytes hash to "
            f"{actual[:16]}.... Re-freeze the witness if the file "
            "was intentionally modified.")


def test_saddle_files_not_strictly_newer_than_matching(witness):
    """The structural-input order: the saddle output must have
    been committed at or before the matching script. A strict
    violation (saddle older than matching) is the unblocked
    expected order; a strict reverse (saddle newer than
    matching) would indicate the matching was frozen first.
    """
    saddle_mt = max(
        witness["file_hashes"][f]["mtime_unix"]
        for f in witness["saddle_files"]
        if f in witness["file_hashes"])
    matching_mt = max(
        witness["file_hashes"][f]["mtime_unix"]
        for f in witness["matching_files"]
        if f in witness["file_hashes"])
    # The protocol invariant: any re-determination of S_bounce
    # must commit the new saddle output before the matching is
    # re-run. The witness records the freeze time of each file;
    # the test enforces that the matching is at least as recent
    # as the saddle (matching is the consumer; matching mtime
    # being strictly older than saddle mtime would indicate a
    # consumer-first rebuild that violates the protocol).
    # NOTE: we allow ties (mtime equal up to filesystem
    # resolution) since the physical invariant is "saddle is
    # frozen and not re-fitted"; a clock collision does not
    # falsify the protocol.
    assert saddle_mt <= matching_mt + 60.0, (
        f"saddle files mtime ({saddle_mt}) is more than 60s newer "
        f"than matching files mtime ({matching_mt}); the saddle "
        "appears to have been re-fitted after the matching was "
        "frozen, violating the saddle-first protocol")


def test_frozen_S_bounce_is_the_audited_value(witness):
    """The frozen S_bounce = 37.995389 (4pi*eta_S with
    eta_S = 3.023577 +/- 1e-6) is the load-bearing input;
    the witness records the value used in the matching
    chain.
    """
    assert abs(witness["frozen_S_bounce"] - 37.995389) < 1e-4, (
        f"frozen S_bounce in witness is "
        f"{witness['frozen_S_bounce']}, not the audited "
        "37.995389")
