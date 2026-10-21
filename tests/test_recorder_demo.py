"""Actual fictional recorder behavioral tests by Jason Stys; JUnit mapping: evidencekit/junit.py.

Functions test_recorder_roundtrip/reset/invalid exercise a small synthetic software component.
No flight hardware, physical reset or telemetry link is involved. Index: docs/CODE_INDEX.md.
"""

import json

import pytest

from evidencekit.delivery.io import canonical, load_json


def test_recorder_roundtrip(tmp_path):
    """Verify deterministic serialization preserves accepted synthetic recorder samples."""
    samples = {"samples": [{"sequence": i, "value": i * 3} for i in range(50)]}
    path = tmp_path / "recorder.json"
    path.write_bytes(canonical(samples))
    assert load_json(path) == samples


def test_recorder_reset(tmp_path):
    """Simulate losing in-memory state and reconstruct it from the persisted JSON checkpoint."""
    path = tmp_path / "checkpoint.json"
    initial = {"last_sequence": 17, "buffer": [2, 4, 8]}
    path.write_bytes(canonical(initial))
    del initial
    restored = load_json(path)
    assert restored == {"last_sequence": 17, "buffer": [2, 4, 8]}
    assert json.loads(canonical(restored)) == restored


def test_recorder_invalid(tmp_path):
    """A truncated persisted sample must produce a diagnostic rather than a plausible partial sample."""
    path = tmp_path / "truncated.json"
    path.write_bytes(b'{"samples":[1,2,')
    with pytest.raises(ValueError):
        load_json(path)
