"""Owned CLI startup and delivery wiring tests by Jason Stys. Index: docs/CODE_INDEX.md."""

import json

from evidencekit.__main__ import main


def test_cli_delivery_wiring(tmp_path, monkeypatch):
    """A unit fake isolates receipt writing; real cryptographic verification is tested separately."""
    monkeypatch.setattr(
        "evidencekit.__main__.verify_release", lambda directory, policy: {"version": policy.version}
    )
    path = tmp_path / "receipt.json"
    args = [
        "verify-delivery",
        "--directory",
        str(tmp_path),
        "--commit",
        "a" * 40,
        "--version",
        "1.0.0",
        "--output",
        str(path),
    ]
    assert main(args) == 0
    receipt = json.loads(path.read_bytes())
    assert receipt["authenticated"] is True
    assert receipt["policy"]["repository"] == "JasonStys/secure-delivery-pipeline-lab"
    assert main(args) == 1


def test_owned_cli_service(tmp_path, monkeypatch):
    """Simulate normal interruption of only the created loopback service and both browser settings."""
    folder = tmp_path / "web/dist"
    folder.mkdir(parents=True)
    (folder / "index.html").write_text("App", encoding="utf-8")
    monkeypatch.setattr("evidencekit.__main__.ROOT", tmp_path)
    opened = []
    monkeypatch.setattr("evidencekit.__main__.webbrowser.open", lambda url: opened.append(url))

    def interrupted(self, poll_interval):
        """End the owned service before it accepts clients, like a user pressing Ctrl+C."""
        raise KeyboardInterrupt

    monkeypatch.setattr("evidencekit.server.WorkbenchServer.serve_forever", interrupted)
    assert main(["serve"]) == 0
    assert len(opened) == 1 and opened[0].startswith("http://127.0.0.1:")
    assert main(["serve", "--no-browser"]) == 0
    assert len(opened) == 1
    monkeypatch.setattr("evidencekit.__main__.ROOT", tmp_path / "absent")
    assert main(["serve", "--no-browser"]) == 1
