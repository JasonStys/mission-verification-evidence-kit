"""Run only the fixed authored recorder suite and gate its real JUnit evidence by Jason Stys.

Function main; variables source, output, completed and definition hash. Index: docs/CODE_INDEX.md.
No user-selected commands, shell interpolation, artifact uploads or network are used.
"""

import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

from evidencekit.delivery.io import canonical
from evidencekit.engine import analyze
from evidencekit.junit import import_junit


def main() -> None:
    """Create a new local CI evidence folder, record reviewed tests, then require a passing matrix."""
    root = Path(__file__).resolve().parents[1]
    output = root / ".runtime/ci-evidence"
    output.mkdir(parents=True, exist_ok=False)
    source = (
        os.environ.get("GITHUB_SHA")
        or subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, timeout=15
        ).strip()
    )
    suite = root / "tests/test_recorder_demo.py"
    definition = hashlib.sha256(suite.read_bytes()).hexdigest()
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--no-cov",
            str(suite),
            "--junitxml",
            str(output / "junit.xml"),
        ],
        cwd=root,
        check=True,
        timeout=60,
    )
    value = import_junit(output / "junit.xml", source, int(time.time()), definition)
    (output / "input.json").write_bytes(canonical(value))
    report = analyze(value)
    (output / "report.json").write_bytes(canonical(report))
    if not report["summary"]["ready"]:
        raise SystemExit("Actual recorder evidence gate blocked")
    print("Actual recorder JUnit -> declared input -> independent SQL -> passing gate")


if __name__ == "__main__":
    main()
