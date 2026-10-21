"""Bounded JSON, files, archives and trust-policy rejection tests. Created by Jason Stys."""
# Reused/adapted authored adversarial tests; exact lines: docs/CODE_INDEX.md.

import os
import subprocess
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from evidencekit.delivery.io import Rejected, atomic_write, canonical, load_json, read_bytes
from evidencekit.delivery.verify import (
    TrustPolicy,
    inspect_payload,
    preflight,
    verify_attestation,
    verify_release,
)


@pytest.mark.parametrize(
    "document", [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b"\xff", b"{", b"[" * 1500]
)
def test_invalid_json(tmp_path: Path, document: bytes) -> None:
    """Reject parser ambiguities and excessive nesting without executing any content."""
    path = tmp_path / "input.json"
    path.write_bytes(document)
    with pytest.raises(Rejected):
        load_json(path)


def test_bounded_files(tmp_path: Path) -> None:
    """Reject missing/oversized/nonregular files and enforce finite canonical JSON."""
    path = tmp_path / "file"
    path.write_bytes(b"1234")
    assert read_bytes(path, 4) == b"1234"
    with pytest.raises(Rejected):
        read_bytes(path, 3)
    with pytest.raises(Rejected):
        read_bytes(tmp_path)
    with pytest.raises(Rejected):
        read_bytes(tmp_path / "missing")
    with pytest.raises(ValueError):
        canonical({"value": float("nan")})
    assert canonical({"b": 2, "a": 1}) == b'{"a":1,"b":2}\n'


def test_atomic_failure_preserves_destination(tmp_path: Path) -> None:
    """A failed replacement must leave the previous good pointer unchanged."""
    path = tmp_path / "state"
    atomic_write(path, b"old")
    with (
        patch("evidencekit.delivery.io.os.replace", side_effect=OSError("fixture disk failure")),
        pytest.raises(OSError),
    ):
        atomic_write(path, b"new")
    assert read_bytes(path) == b"old"
    assert [item.name for item in tmp_path.iterdir()] == ["state"]


@pytest.mark.parametrize(
    "changes",
    [
        {"repository": "bad"},
        {"repository": "owner/repo;echo"},
        {"commit": "a" * 39},
        {"commit": "A" * 40},
        {"version": "01.0.0"},
        {"version": "1.0.0-rc1"},
        {"version": "../1"},
        {"workflow": "../evil.yml"},
        {"workflow": ".github/workflows/release.yml;id"},
    ],
)
def test_policy_rejection(policy: TrustPolicy, changes: dict[str, str]) -> None:
    """Arguments must not become shell expressions, arbitrary paths or ambiguous versions."""
    values = {
        "repository": policy.repository,
        "commit": policy.commit,
        "version": policy.version,
        "workflow": policy.workflow,
    } | changes
    with pytest.raises(Rejected):
        TrustPolicy(**values)


def test_valid_preflight_is_not_authentication(release: Path, policy: TrustPolicy) -> None:
    """Good hashes alone never pass the authenticated release verifier."""
    assert preflight(release, policy)["version"] == policy.version
    with (
        patch("evidencekit.delivery.verify.shutil.which", return_value=None),
        pytest.raises(Rejected),
    ):
        verify_release(release, policy)


@pytest.mark.parametrize(
    "mutation",
    [
        "extra",
        "version",
        "commit",
        "schema",
        "asset_count",
        "duplicate",
        "name",
        "digest",
        "size",
        "fields",
        "root",
    ],
)
def test_manifest_rejections(release: Path, policy: TrustPolicy, mutation: str) -> None:
    """A manifest cannot choose its own identity, paths, asset count or accepted digest shape."""
    path = release / "release.json"
    value = load_json(path)
    if mutation == "extra":
        (release / "unexpected.py").write_bytes(b"fixture")
    elif mutation == "version":
        value["version"] = "2.0.0"
    elif mutation == "commit":
        value["source"]["commit"] = "b" * 40
    elif mutation == "schema":
        value["schema"] = True
    elif mutation == "asset_count":
        value["assets"].pop()
    elif mutation == "duplicate":
        value["assets"][1] = value["assets"][0]
    elif mutation == "name":
        value["assets"][0]["name"] = "../outside"
    elif mutation == "digest":
        value["assets"][0]["sha256"] = 123
    elif mutation == "size":
        value["assets"][0]["size"] = True
    elif mutation == "fields":
        value["assets"][0]["extra"] = 1
    else:
        value = []
    atomic_write(path, canonical(value))
    with pytest.raises(Rejected):
        preflight(release, policy)


def test_payload_tamper(release: Path, policy: TrustPolicy) -> None:
    """Changing one payload byte without changing its manifest is rejected immediately."""
    path = release / f"release-probe-{policy.version}.pyz"
    data = bytearray(read_bytes(path))
    data[-1] ^= 1
    path.write_bytes(data)
    with pytest.raises(Rejected):
        preflight(release, policy)


@pytest.mark.parametrize("kind", ["invalid", "traversal", "duplicate", "linked", "oversized"])
def test_archive_boundary(tmp_path: Path, release: Path, policy: TrustPolicy, kind: str) -> None:
    """Reject malformed/extra-member/link/bomb archives before any application execution."""
    target = tmp_path / "archive.pyz"
    if kind == "invalid":
        target.write_bytes(b"invalid zip")
    else:
        with zipfile.ZipFile(release / f"release-probe-{policy.version}.pyz") as original:
            members = {entry.filename: original.read(entry) for entry in original.infolist()}
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in members.items():
                entry = zipfile.ZipInfo(name)
                entry.external_attr = (
                    0o120777 if kind == "linked" and name == "LICENSE" else 0o100644
                ) << 16
                archive.writestr(
                    entry, b"x" * 600_000 if kind == "oversized" and name == "LICENSE" else data
                )
            if kind == "traversal":
                archive.writestr("../outside.py", b"fixture")
            if kind == "duplicate":
                with pytest.warns(UserWarning):
                    archive.writestr("LICENSE", b"fixture")
    with pytest.raises(Rejected):
        inspect_payload(target)


def test_attestation_invocation(release: Path, policy: TrustPolicy) -> None:
    """Unit fake checks CLI policy flags; actual cryptographic tests run in the release job."""
    with (
        patch("evidencekit.delivery.verify.shutil.which", return_value="/trusted/gh"),
        patch(
            "evidencekit.delivery.verify.subprocess.run",
            return_value=subprocess.CompletedProcess([], 0),
        ) as run,
    ):
        verify_release(release, policy)
    assert run.call_count == 4
    command = run.call_args.args[0]
    assert command[command.index("--source-ref") + 1] == "refs/tags/v1.0.0"
    assert command[command.index("--source-digest") + 1] == policy.commit
    assert "--deny-self-hosted-runners" in command
    assert "--signer-digest" in command and "--signer-workflow" in command
    assert "shell" not in run.call_args.kwargs


@pytest.mark.parametrize("failure", ["nonzero", "missing", "timeout", "oserror"])
def test_attestation_fails_closed(release: Path, policy: TrustPolicy, failure: str) -> None:
    """Offline, unavailable, timed-out or rejected verification must never accept a release."""
    error = (
        subprocess.TimeoutExpired("gh", 60)
        if failure == "timeout"
        else OSError("fixture")
        if failure == "oserror"
        else None
    )
    with (
        patch(
            "evidencekit.delivery.verify.shutil.which",
            return_value=None if failure == "missing" else "/trusted/gh",
        ),
        patch(
            "evidencekit.delivery.verify.subprocess.run",
            side_effect=error,
            return_value=subprocess.CompletedProcess([], 1),
        ),
        pytest.raises(Rejected),
    ):
        verify_attestation(release / "release.json", policy)


def test_final_link_rejection(tmp_path: Path) -> None:
    """Exercise link rejection without requiring Windows symlink creation privileges."""
    path = tmp_path / "file"
    path.write_bytes(b"fixture")
    with patch.object(Path, "is_symlink", return_value=True), pytest.raises(Rejected):
        read_bytes(path)
    if os.name != "nt":
        linked = tmp_path / "linked"
        linked.symlink_to(path)
        with pytest.raises(Rejected):
            read_bytes(linked)
