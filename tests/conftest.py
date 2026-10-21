"""Isolated unsigned release fixtures and deterministic properties by Jason Stys.

Functions policy/release construct inert ZIP bytes, never execute them. Index: docs/CODE_INDEX.md.
"""

import hashlib
import zipfile
from pathlib import Path

import pytest
from hypothesis import settings

from evidencekit.delivery.io import canonical
from evidencekit.delivery.verify import REPOSITORY, TrustPolicy

settings.register_profile("ci", max_examples=100, derandomize=True, deadline=None)
settings.load_profile("ci")


@pytest.fixture
def policy() -> TrustPolicy:
    """An explicitly fictional signer identity for unit tests, not real provenance."""
    return TrustPolicy(REPOSITORY, "a" * 40, "1.0.0")


@pytest.fixture
def release(tmp_path: Path, policy: TrustPolicy) -> Path:
    """Create the exact four-file delivery shape with inert payload members and declared checksums."""
    folder = tmp_path / "release"
    folder.mkdir()
    payload = folder / f"release-probe-{policy.version}.pyz"
    with zipfile.ZipFile(payload, "w") as archive:
        for name in (
            "__main__.py",
            "delivery/__init__.py",
            "delivery/io.py",
            "delivery/probe.py",
            "LICENSE",
            "BUILD.json",
        ):
            archive.writestr(name, b"fixture")
    (folder / "sbom.cdx.json").write_bytes(b"{}")
    (folder / "validation.json").write_bytes(b"{}")
    assets = [
        {
            "name": name,
            "size": (folder / name).stat().st_size,
            "sha256": hashlib.sha256((folder / name).read_bytes()).hexdigest(),
        }
        for name in sorted(policy.names)
    ]
    (folder / "release.json").write_bytes(
        canonical(
            {
                "schema": 1,
                "version": policy.version,
                "source": {
                    "repository": policy.repository,
                    "commit": policy.commit,
                    "ref": f"refs/tags/v{policy.version}",
                },
                "assets": assets,
            }
        )
    )
    return folder
